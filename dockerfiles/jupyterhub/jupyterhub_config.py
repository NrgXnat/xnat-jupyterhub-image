import os
import sys
import logging

from xnat2jupyterhub.auth import XnatAuthenticator
from xnat2jupyterhub.hooks.swarmspawner import pre_spawn_hook as xnat_pre_spawn_hook

c = get_config()

# Logging config
logger = logging.getLogger("xnat2jupyterhub")
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
c.JupyterHub.allow_named_servers = False
c.JupyterHub.shutdown_on_logout = True

# Authentication config
c.Authenticator.admin_users = {'admin'}
c.JupyterHub.authenticator_class = XnatAuthenticator

# Spawner config
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 75
c.SwarmSpawner.network_name = os.environ['JH_NETWORK']  # Spawn single-user containers into this Docker network
c.SwarmSpawner.pre_spawn_hook = xnat_pre_spawn_hook  # mount's xnat archive

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
        "name": "admin-hub-role",
        "scopes": [
            "admin:servers", "admin:users", "read:hub", "tokens"
        ],
        "services": [
            "xnat"
        ],
    }
]
