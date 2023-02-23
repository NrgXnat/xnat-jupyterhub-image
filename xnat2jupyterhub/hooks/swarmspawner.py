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

            spawner.extra_resources_spec.update(resources)

        if 'container_spec' in task_template:
            container_spec = task_template['container_spec']

            if 'image' in container_spec:
                spawner.image = container_spec['image']

            if 'env' in container_spec:
                env = container_spec['env']
                spawner.environment.update(env)

            if 'mounts' in container_spec:
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
