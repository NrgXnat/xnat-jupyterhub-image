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

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s %(asctime)s %(name)s %(module)s:%(lineno)d] %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

# JupyterHub configuration
c.JupyterHub.bind_url = 'http://:8000/jupyterhub'
c.JupyterHub.hub_bind_url = 'http://:8081/jupyterhub'
c.JupyterHub.hub_connect_url = 'http://jupyterhub:8081/jupyterhub'
c.JupyterHub.allow_named_servers = True
c.JupyterHub.shutdown_on_logout = True
c.Authenticator.admin_users = {'admin'}

# Spawner configuration
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
c.SwarmSpawner.network_name = os.environ['JH_NETWORK']
c.SwarmSpawner.remove = True  # Delete containers on user logout

c.SwarmSpawner.extra_host_config = {'network_mode': os.environ['JH_NETWORK']}

# Run jupyter notebook servers with the specified UID and GID
if 'JH_UID' in os.environ and 'JH_GID' in os.environ:
    if os.environ['JH_UID'] and os.environ['JH_GID']:
        environment = {'NB_UID': os.environ['JH_UID'],
                       'NB_GID': os.environ['JH_GID']}
        c.SwarmSpawner.environment.update(environment)
        c.SwarmSpawner.extra_container_spec = {'user': '0'}

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


# Pre Spawn Hook for mounting XNAT data to the container
def xnat_pre_spawn_hook(spawner):
    # Request user_options from XNAT
    xnat_url = f'{os.environ["JH_XNAT_URL"]}/xapi/jupyterhub/users/{spawner.user.name}/server/user-options'

    logger.debug(f'Requesting user options from XNAT for user {spawner.user.name}')

    r = requests.get(xnat_url, auth=HTTPBasicAuth(os.environ['JH_XNAT_USERNAME'],
                                                  os.environ['JH_XNAT_PASSWORD']))

    volumes = {}
    environment_variables = {}

    if r.ok:
        json = r.json()

        logger.debug(f'User options for user {spawner.user.name} server {spawner.name} received. user_options = {json}')

        mounts = json['mounts']
        environment_variables = json['environment-variables']
        docker_image = json['docker-image']

        spawner.image = docker_image

        for mount in mounts:
            mount_name = mount['name']
            container_host_path = mount['containerHostPath']
            jupyterhub_host_path = mount['jupyterHostPath']
            mode = 'rw' if mount['writable'] else 'ro'
            volumes[container_host_path] = {'bind': jupyterhub_host_path, 'mode': mode}

            if mount_name == "user-workspace":
                # c.SwarmSpawner.notebook_dir = jupyterhub_host_path  # this is flaky, using env var instead
                environment_variables['JUPYTERHUB_ROOT_DIR'] = jupyterhub_host_path

    else:
        logger.error(f'Failed to get user options from XNAT for user {spawner.user.name}')
        raise Exception(f'Failed to get user options from XNAT for user {spawner.user.name}')

    spawner.volumes.update(volumes)
    spawner.environment.update(environment_variables)

    # Install user requirements.txt after the single user server has started
    # spawner.post_start_cmd = f"sh -c '[ -f /workspace/{spawner.user.name}/requirements.txt ] && pip install " \
    #                          f"--requirement /workspace/{spawner.user.name}/requirements.txt' "


c.SwarmSpawner.pre_spawn_hook = xnat_pre_spawn_hook
