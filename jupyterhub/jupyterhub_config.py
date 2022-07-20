import os
import sys
import logging
import requests

from jupyterhub.auth import Authenticator
from requests.auth import HTTPBasicAuth

c = get_config()

# Setup Logging
logger = logging.getLogger("jupyterhub_config")
logger.propagate = False
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('/srv/jupyterhub/jupyterhub_config.log')
sh = logging.StreamHandler(sys.stdout)
fh.setLevel(logging.DEBUG)
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s %(asctime)s %(name)s %(module)s:%(lineno)d] %(message)s")
fh.setFormatter(formatter)
sh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh)

# JupyterHub configuration
c.JupyterHub.bind_url = 'http://jupyterhub:8000/jupyterhub/'
c.JupyterHub.hub_bind_url = 'http://jupyterhub:8081/jupyterhub/'
c.JupyterHub.hub_connect_url = 'http://jupyterhub:8081/jupyterhub/'
c.JupyterHub.allow_named_servers = True
c.JupyterHub.shutdown_on_logout = True
c.Authenticator.admin_users = {'admin'}

# Spawner configuration
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = os.environ['JH_USER_NB_IMG']
c.DockerSpawner.network_name = os.environ['JH_NETWORK']
c.DockerSpawner.remove = True  # Delete containers on user logout

# Run jupyter notebook servers with the specified UID and GID
if 'JH_UID' in os.environ and 'JH_GID' in os.environ:
    if os.environ['JH_UID'] and os.environ['JH_GID']:
        environment = {'NB_UID': os.environ['JH_UID'],
                       'NB_GID': os.environ['JH_GID']}
        c.DockerSpawner.environment.update(environment)
        c.DockerSpawner.extra_create_kwargs = {'user': 'root'}

# Create service account for XNAT
c.JupyterHub.services = [
    {
        "name": "xnat",
        "api_token": os.environ['JH_XNAT_SERVICE_TOKEN']
    },
]

c.JupyterHub.load_roles = [
    {
        "name": "admin-servers-role",
        "scopes": [
            "admin:servers", "admin:users", "read:hub"
        ],
        "services": [
            "xnat"
        ],
    }
]


# Authenticate user with XNAT
class XnatAuthenticator(Authenticator):
    async def authenticate(self, handler, data):
        xnat_url = f'{os.environ["JH_XNAT_URL"]}'
        xnat_auth_api = f'{xnat_url}/data/services/auth'

        logger.info(f'User {data["username"]} is attempting to login.')

        response = requests.put(xnat_auth_api, data=f'username={data["username"]}&password={data["password"]}')

        if response.status_code == 200:
            logger.info(f'User {data["username"]} authenticated.')
            return {'name': data['username']}
        else:
            logger.info(f'Failed to authenticate user {data["username"]} with XNAT.')
            return None


c.JupyterHub.authenticator_class = XnatAuthenticator


# Pre Spawn Hook for mounting users projects to the container
def xnat_pre_spawn_hook(spawner):
    # User options sent from XNAT
    user_options = spawner.user_options

    # Get configuration from XNAT
    xnat_url = f'{os.environ["JH_XNAT_URL"]}/xapi/jupyterhub/users/{spawner.user.name}/server/config?' \
               f'xsiType={user_options["xsiType"]}&id={user_options["id"]}'
    logger.debug(f'Requesting server config from XNAT for user {spawner.user.name} at {xnat_url}')
    r = requests.get(xnat_url, auth=HTTPBasicAuth(os.environ['JH_XNAT_USERNAME'],
                                                  os.environ['JH_XNAT_PASSWORD']))

    volumes = {}
    environment_variables = {}

    if r.ok:
        logger.debug(f'Server config for user {spawner.user.name} received.')

        json = r.json()
        mounts = json['mounts']

        for mount in mounts:
            mount_name = mount['name']
            container_host_path = mount['containerHostPath']
            jupyterhub_host_path = mount['jupyterHostPath']
            mode = 'rw' if mount['writable'] else 'ro'
            volumes[container_host_path] = {'bind': jupyterhub_host_path, 'mode': mode}

            if mount_name == "user-workspace":
                c.DockerSpawner.notebook_dir = jupyterhub_host_path

        environment_variables = json['environment-variables']

    else:
        logger.error(f'Failed to get server config from XNAT for user {spawner.user.name}')

    spawner.volumes.update(volumes)
    spawner.environment.update(environment_variables)

    # Install user requirements.txt after the single user server has started
    spawner.post_start_cmd = f"sh -c '[ -f /workspace/{spawner.user.name}/requirements.txt ] && pip install " \
                             f"--requirement /workspace/{spawner.user.name}/requirements.txt' "


c.DockerSpawner.pre_spawn_hook = xnat_pre_spawn_hook
