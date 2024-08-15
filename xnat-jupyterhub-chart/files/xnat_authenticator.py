import os
import requests
import xnat_logger

from jupyterhub.auth import Authenticator

# Logging config
logger = xnat_logger.logger


class XnatAuthenticator(Authenticator):
    """
    Used to authenticate a user with XNAT

    Requires the environmental variable JH_XNAT_URL to contain the URL of the XNAT to authenticate the user with.
    """

    async def authenticate(self, handler, data):
        xnat_url = f'{os.environ["JH_XNAT_URL"]}'
        username, password = data["username"], data["password"]

        logger.info(f'User {username} is attempting to login.')

        # Authenticate user with XNAT
        # If they can't access their own roles, they are not authenticated
        roles_response = requests.get(f'{xnat_url}/xapi/users/{username}/roles', auth=(username, password))
        if roles_response.status_code == 401:
            logger.info(f'User {username} not authenticated with XNAT.')
            return None
        elif not roles_response.ok:
            logger.error(f'Failed to authenticate user {username} with XNAT. '
                         f'Status code: {roles_response.status_code}. '
                         f'Response: {roles_response.text}')
            return None

        logger.info(f'User {username} authenticated with XNAT.')

        # Check if user has the jupyter role
        if 'jupyter' in [role.lower() for role in roles_response.json()]:
            logger.info(f'User {username} authorized to use Jupyter.')
            return {'name': username, 'allowed': True}

        # Check if allUsersCanStartJupyter preference is enabled
        prefs_response = requests.get(f'{xnat_url}/xapi/jupyterhub/preferences/allUsersCanStartJupyter',
                                      auth=(username, password))
        if prefs_response.ok and prefs_response.json().get('allUsersCanStartJupyter'):
            logger.info(f'User {username} authorized to use Jupyter.')
            return {'name': username, 'allowed': True}

        logger.info(f'User {username} not authorized to use Jupyter.')
        return None

    def check_allowed(self, username, authentication=None):
        return authentication['allowed']
