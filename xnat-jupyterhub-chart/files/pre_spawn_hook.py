import os
import re
import requests
import xnat_logger

from requests.auth import HTTPBasicAuth

logger = xnat_logger.logger


def pre_spawn_hook(spawner):
    logger.info(f'Requesting user options from XNAT for user {spawner.user.name} server {spawner.name}')
    xnat_url = f'{os.environ["JH_XNAT_URL"]}/xapi/jupyterhub/users/{spawner.user.name}/server/{spawner.name}/user-options'
    res = requests.get(xnat_url, auth=HTTPBasicAuth(os.environ['JH_XNAT_USERNAME'],
                                                    os.environ['JH_XNAT_PASSWORD']))
    if res and res.ok:
        logger.info(f'User options for user {spawner.user.name} server {spawner.name} retrieved from XNAT.')

        user_options = res.json()

        task_template = user_options['task_template']

        if 'placement' in task_template:
            placement = task_template['placement']
            if 'constraints' in placement:
                spawner.node_selector = {i.split('==')[0]: i.split('==')[-1] for i in placement['constraints']}

        if 'resources' in task_template:
            resources = task_template['resources']
            cpu_limit, cpu_guarantee, mem_limit, mem_guarantee, generic_resources = (0, 0, 0, 0, {})
            if 'cpu_limit' in resources: cpu_limit = resources.pop('cpu_limit')
            if 'cpu_reservation' in resources: cpu_guarantee = resources.pop('cpu_reservation')
            if 'mem_limit' in resources: mem_limit = resources.pop('mem_limit')
            if 'mem_reservation' in resources: mem_guarantee = resources.pop('mem_reservation')
            if 'generic_resources' in resources: generic_resources = resources.pop('generic_resources')

            if cpu_limit: spawner.cpu_limit = cpu_limit
            if cpu_guarantee: spawner.cpu_guarantee = cpu_guarantee
            if mem_limit: spawner.mem_limit = mem_limit
            if mem_guarantee: spawner.mem_guarantee = mem_guarantee

            if generic_resources:
                if 'gpu' in generic_resources: generic_resources['nvidia.com/gpu'] = generic_resources.pop('gpu')
                spawner.extra_resource_guarantees = generic_resources
                spawner.extra_resource_limits = generic_resources

            if resources: spawner.extra_pod_config.update(resources)

        if 'container_spec' in task_template:
            container_spec = task_template['container_spec']
            if 'image' in container_spec:
                spawner.image = container_spec['image']
                spawner.image_pull_policy = 'IfNotPresent'

            if 'command' in container_spec and container_spec['command']:
                command = container_spec['command']
                command = command.split(' ')
                spawner.cmd = command

            if 'env' in container_spec: spawner.environment.update(container_spec['env'])
            spawner.environment.update({
                'NB_UID': os.environ['JH_XNAT_UID'],
                'NB_GID': os.environ['JH_XNAT_GID'],
                'NB_USER': f'{spawner.user.name}'
            })

            # Issue in JupyterHub 4.0 where cookie auth is not persisted from a token in url authenticated request
            spawner.environment.update({
                'JUPYTERHUB_SINGLEUSER_EXTENSION': '0'
            })

            if 'mounts' in container_spec:
                logger.debug(f'Adding mounts to user {spawner.user.name} server {spawner.name} from XNAT. '
                             f'Mounts: {container_spec["mounts"]}')

                v = []
                vm = []
                for m in container_spec['mounts']:
                    src = m['source']
                    tgt = m['target']

                    # Workspaces mountings are handled by JupyterHub chart
                    if '/workspace/' in tgt:
                        continue

                    # This presumes that all mounts are within the archive volume, which is not always the case.
                    # Workaround for now as the plugin does not provide the volume name.
                    if not any(i['name'] == 'archive' for i in v):
                        v.append({'name': 'archive',
                                  'persistentVolumeClaim': {'claimName': os.environ['JH_XNAT_ARCHIVE_PVC']}})
                    vm.append({'name': 'archive', 'mountPath': tgt, 'readOnly': m['read_only'], 'subPath': src})

                spawner.volumes.extend([i for i in v if i not in spawner.volumes])
                spawner.volume_mounts.extend([i for i in vm if i not in spawner.volume_mounts])

                mount_txt = f'Mounting the following volumes for user {spawner.user.name} server {spawner.name}:'
                for v in spawner.volumes:
                    mount_txt += f'\n - {v}'

                for v in spawner.volume_mounts:
                    mount_txt += f'\n - {v}'
                logger.info(mount_txt)

        spawner.working_dir = f'/workspace/{spawner.user.name}'

        logger.info('Successfully updated spawner configuration')
    else:
        logger.error(f'Failed to get user options from XNAT for user {spawner.user.name}')
        raise Exception(f'Failed to get user options from XNAT for user {spawner.user.name}')


c.KubeSpawner.pre_spawn_hook = pre_spawn_hook
