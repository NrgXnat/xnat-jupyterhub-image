import logging
import os
import requests

from requests.auth import HTTPBasicAuth

logger = logging.getLogger("xnat2jupyterhub")


# Pre Spawn Hook for mounting XNAT data to the container
def pre_spawn_hook(spawner):
    """
    This function is called before the single-user Jupyter container is spawned. It calls the XNAT REST API and
    retrieves configuration options for the users Jupyter container. The pre_spawn_hook will:
        - mounted XNAT data
        - set environmental variables:
            - XNAT_HOST
            - XNAT_USER
            - XNAT_PASS
            - XNAT_XSI_TYPE
            - XNAT_ITEM_ID
        - set container labels

    Environmental variables required in JupyterHub to run the pre_spawn_hook:
        - JH_XNAT_URL        The root XNAT url
        - JH_XNAT_USERNAME   JupyterHub service account username on XNAT
        - JH_XNAT_PASSWORD   JupyterHub service account password on XNAT
    """

    # Request user_options from XNAT
    logger.debug(f'Requesting user options from XNAT for user {spawner.user.name}')
    xnat_url = f'{os.environ["JH_XNAT_URL"]}/xapi/jupyterhub/users/{spawner.user.name}/server/user-options'
    r = requests.get(xnat_url, auth=HTTPBasicAuth(os.environ['JH_XNAT_USERNAME'],
                                                  os.environ['JH_XNAT_PASSWORD']))

    volumes = {}
    environment_variables = {}

    if r.ok:
        json = r.json()

        logger.info(f'User options for user {spawner.user.name} server {spawner.name} retrieved from XNAT.')

        mounts = json['mounts']
        environment_variables = json['environment-variables']

        container_spec = json['container-spec']
        spawner.image = container_spec['image']
        spawner.extra_container_spec.update(container_spec)

        for mount in mounts:
            mount_name = mount['name']
            container_host_path = mount['containerHostPath']
            jupyterhub_host_path = mount['jupyterHostPath']
            mode = 'rw' if mount['writable'] else 'ro'
            volumes[container_host_path] = {'bind': jupyterhub_host_path, 'mode': mode}

            if mount_name == "user-workspace":
                environment_variables['JUPYTERHUB_ROOT_DIR'] = jupyterhub_host_path

    else:
        logger.error(f'Failed to get user options from XNAT for user {spawner.user.name}')
        raise Exception(f'Failed to get user options from XNAT for user {spawner.user.name}')

    spawner.volumes.update(volumes)
    spawner.environment.update(environment_variables)

    # Install user requirements.txt after the single user server has started
    # spawner.post_start_cmd = f"sh -c '[ -f /workspace/{spawner.user.name}/requirements.txt ] && pip install " \
    #                          f"--requirement /workspace/{spawner.user.name}/requirements.txt' "
