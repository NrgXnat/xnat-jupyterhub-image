ARG JH_VERSION=3.0.0
FROM jupyterhub/jupyterhub:$JH_VERSION
LABEL maintainer="andrewl@wustl.edu"
ARG JH_DOCKERSPAWNER_VERSION=12.1.0
ARG JH_XNAT2JUPYTERHUB_VERSION="0.2.0"
ENV JH_NETWORK="jupyterhub-network"
ENV JH_XNAT_URL="http://host.docker.internal:80"
ENV JH_XNAT_SERVICE_TOKEN="secret-token"
ENV JH_XNAT_USERNAME=jupyterhub
ENV JH_XNAT_PASSWORD=jupyterhub

RUN python3 -m pip install --no-cache dockerspawner==$JH_DOCKERSPAWNER_VERSION
RUN python3 -m pip install --no-cache xnat2jupyterhub==$JH_XNAT2JUPYTERHUB_VERSION
RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu; \
	rm -rf /var/lib/apt/lists/*; \
	gosu nobody true

COPY entrypoint.sh /srv/jupyterhub
RUN chmod +x /srv/jupyterhub/entrypoint.sh

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

CMD ["./entrypoint.sh", "jupyterhub"]