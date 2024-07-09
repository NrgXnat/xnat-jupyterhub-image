import os
import sys
import logging
import requests

from jupyterhub.auth import Authenticator
from requests.auth import HTTPBasicAuth

c = get_config()

# Logging config
logger = logging.getLogger("xnat-jupyterhub")
logger.propagate = False
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s %(asctime)s %(name)s %(module)s:%(lineno)d] %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)

# JupyterHub config
c.JupyterHub.bind_url = 'http://:8000/jupyterhub'
c.JupyterHub.hub_bind_url = 'http://:8081/jupyterhub'
c.JupyterHub.hub_connect_url = 'http://jupyterhub:8081/jupyterhub'
c.JupyterHub.allow_named_servers = True
c.JupyterHub.shutdown_on_logout = True
c.JupyterHub.template_paths = ['/srv/jupyterhub/templates']

# Create service account for XNAT
c.JupyterHub.services = [
    {
        "name": "xnat",
        "api_token": os.environ['JH_XNAT_SERVICE_TOKEN']
    },
]

c.JupyterHub.load_roles = [
    {
        "name": "admin-hub-role",
        "scopes": [
            "admin:servers", "admin:users", "read:hub", "tokens"
        ],
        "services": [
            "xnat"
        ],
    }
]

# Run jupyter notebook servers with the specified UID and GID
if 'NB_UID' in os.environ and 'NB_GID' in os.environ:
    if os.environ['NB_UID'] and os.environ['NB_GID']:
        environment = {'NB_UID': os.environ['NB_UID'],
                       'NB_GID': os.environ['NB_GID']}
        c.SwarmSpawner.environment.update(environment)
        c.SwarmSpawner.extra_container_spec = {'user': '0'}

# Spawner config
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
c.Spawner.start_timeout = int(os.environ['JH_START_TIMEOUT'])
c.Spawner.http_timeout = int(os.environ['JH_HTTP_TIMEOUT'])
c.SwarmSpawner.network_name = os.environ['JH_NETWORK']  # Spawn single-user containers into this Docker network
c.Spawner.environment.update({"JUPYTERHUB_ALLOW_TOKEN_IN_URL": "1"})

# TLS Config
tls_config = {}

if 'JH_TLS_CLIENT_CERT' in os.environ and 'JH_TLS_CLIENT_KEY' in os.environ:
    logger.info('TLS client certificate and key found. Adding to TLS config.')
    tls_config['client_cert'] = (os.environ['JH_TLS_CLIENT_CERT'], os.environ['JH_TLS_CLIENT_KEY'])

if 'JH_TLS_CA_CERT' in os.environ:
    logger.info('TLS CA certificate found. Adding to TLS config.')
    tls_config['ca_cert'] = os.environ['JH_TLS_CA_CERT']

if 'JH_TLS_VERIFY' in os.environ:
    logger.info('TLS verify found. Adding to TLS config.')
    tls_config['verify'] = os.environ['JH_TLS_VERIFY']

if tls_config:
    logger.info('TLS config found. Adding to SwarmSpawner.')
    c.SwarmSpawner.tls_config = tls_config

# Authentication config
class XnatAuthenticator(Authenticator):
    """
    Used to authenticate a user with XNAT

    Requires the environmental variable JH_XNAT_URL to contain the URL of the XNAT to authenticate the user with.
    """

    async def authenticate(self, handler, data):
        xnat_url = f'{os.environ["JH_XNAT_URL"]}'
        xnat_auth_api = f'{xnat_url}/data/services/auth'

        logger.debug(f'User {data["username"]} is attempting to login.')

        response = requests.put(xnat_auth_api, data=f'username={data["username"]}&password={data["password"]}')

        if response.status_code == 200:
            logger.info(f'User {data["username"]} authenticated with XNAT.')
            return {'name': data['username'], 'allowed': True}
        else:
            logger.info(f'Failed to authenticate user {data["username"]} with XNAT.')
            return None

    def check_allowed(self, username, authentication=None):
        return authentication['allowed']

c.JupyterHub.authenticator_class = XnatAuthenticator


# Pre Spawn Hook for mounting XNAT data to the container
def pre_spawn_hook(spawner):
    """
    This function is called before the single-user Jupyter container is spawned. It calls the XNAT REST API and
    retrieves configuration options for the users Jupyter container. The pre_spawn_hook will:
        - mounted XNAT data
        - set environmental variables such as:
            - XNAT_HOST
            - XNAT_USER
            - XNAT_PASS
            - XNAT_XSI_TYPE
        - set container labels

    Environmental variables required in JupyterHub to run the pre_spawn_hook:
        - JH_XNAT_URL        The root XNAT url
        - JH_XNAT_USERNAME   JupyterHub service account username on XNAT
        - JH_XNAT_PASSWORD   JupyterHub service account password on XNAT
    """

    # Request user_options from XNAT
    logger.debug(f'Requesting user options from XNAT for user {spawner.user.name} server {spawner.name}')
    xnat_url = f'{os.environ["JH_XNAT_URL"]}/xapi/jupyterhub/users/{spawner.user.name}/server/{spawner.name}/user-options'
    r = requests.get(xnat_url, auth=HTTPBasicAuth(os.environ['JH_XNAT_USERNAME'],
                                                  os.environ['JH_XNAT_PASSWORD']))

    volumes = {}

    if r.ok:
        json = r.json()

        logger.info(f'User options for user {spawner.user.name} server {spawner.name} retrieved from XNAT.')

        task_template = json['task_template']

        if 'placement' in task_template:
            placement = task_template['placement']
            spawner.extra_placement_spec.update(placement)

        if 'resources' in task_template:
            resources = task_template['resources']

            if 'cpu_limit' in resources:
                if resources['cpu_limit'] and resources['cpu_limit'] > 0:
                    spawner.cpu_limit = resources['cpu_limit']

                resources.pop('cpu_limit')

            if 'cpu_reservation' in resources:
                if resources['cpu_reservation'] and resources['cpu_reservation'] > 0:
                    spawner.cpu_guarantee = resources['cpu_reservation']

                resources.pop('cpu_reservation')

            if 'mem_limit' in resources:
                if resources['mem_limit']:
                    spawner.mem_limit = resources['mem_limit']

                resources.pop('mem_limit')

            if 'mem_reservation' in resources:
                if resources['mem_reservation']:
                    spawner.mem_guarantee = resources['mem_reservation']

                resources.pop('mem_reservation')

            # Convert generic_resources values to ints if they can be
            if 'generic_resources' in resources:
                for key, value in resources['generic_resources'].items():
                    try:
                        resources['generic_resources'][key] = int(value)
                    except ValueError:
                        pass

            spawner.extra_resources_spec.update(resources)

        if 'container_spec' in task_template:
            container_spec = task_template['container_spec']

            if 'image' in container_spec:
                spawner.image = container_spec['image']

            if 'command' in container_spec and container_spec['command']:
                command = container_spec['command']
                command = command.split(' ')
                spawner.cmd = command

            if 'env' in container_spec:
                env = container_spec['env']
                spawner.environment.update(env)

            if 'mounts' in container_spec:
                logger.info(f'Adding mounts to user {spawner.user.name} server {spawner.name} from XNAT.'
                            f' Mounts: {container_spec["mounts"]}')

                mounts = container_spec['mounts']
                for mount in mounts:
                    mode = 'ro' if mount['read_only'] else 'rw'
                    volumes[mount['source']] = {'bind': mount['target'], 'mode': mode}
    else:
        logger.error(f'Failed to get user options from XNAT for user {spawner.user.name}')
        raise Exception(f'Failed to get user options from XNAT for user {spawner.user.name}')

    spawner.volumes.update(volumes)

    # Install user requirements.txt after the single user server has started
    # spawner.post_start_cmd = f"sh -c '[ -f /workspace/{spawner.user.name}/requirements.txt ] && pip install " \
    #                          f"--requirement /workspace/{spawner.user.name}/requirements.txt' "


c.SwarmSpawner.pre_spawn_hook = pre_spawn_hook
