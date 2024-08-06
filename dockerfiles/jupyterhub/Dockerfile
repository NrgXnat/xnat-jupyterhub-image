ARG JH_VERSION=4.1.5
FROM quay.io/jupyterhub/jupyterhub:$JH_VERSION
LABEL maintainer="andrewl@wustl.edu"
ARG JH_DOCKERSPAWNER_VERSION=13.0.0
ENV JH_NETWORK="jupyterhub-network"
ENV JH_XNAT_URL="http://172.17.0.1:80"
ENV JH_XNAT_SERVICE_TOKEN="secret-token"
ENV JH_XNAT_USERNAME=jupyterhub
ENV JH_XNAT_PASSWORD=jupyterhub
ENV JH_START_TIMEOUT=180
ENV JH_HTTP_TIMEOUT=75

RUN python3 -m pip install --no-cache dockerspawner==$JH_DOCKERSPAWNER_VERSION
RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu; \
	rm -rf /var/lib/apt/lists/*; \
	gosu nobody true

COPY entrypoint.sh /srv/jupyterhub
COPY templates /srv/jupyterhub/templates
RUN chmod +x /srv/jupyterhub/entrypoint.sh

COPY jupyterhub_config.py /srv/jupyterhub/jupyterhub_config.py

CMD ["./entrypoint.sh", "jupyterhub"]