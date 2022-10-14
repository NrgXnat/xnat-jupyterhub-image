import logging
import os
import requests

from jupyterhub.auth import Authenticator

logger = logging.getLogger("xnat2jupyterhub")


# Authenticate user with XNAT
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
            return {'name': data['username']}
        else:
            logger.info(f'Failed to authenticate user {data["username"]} with XNAT.')
            return None
