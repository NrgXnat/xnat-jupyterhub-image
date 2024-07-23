ARG JH_VERSION=5.0.0
FROM quay.io/jupyter/tensorflow-notebook:hub-$JH_VERSION

USER root

RUN apt-get update && \
    apt-get clean && \
    apt-get install -y dcmtk && \
    rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/

RUN python3 -m pip install --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}" && \
    rm /tmp/requirements.txt

# This is a workaround for dashboards. The problem is that the base-notebook image has a HEALTHCHECK that \
# "works well for `lab`, `notebook`, `nbclassic`, `server`, and `retro` jupyter commands" but dashboards use different
# commands See: https://github.com/jupyter/docker-stacks/blob/main/images/base-notebook/Dockerfile#L67
HEALTHCHECK NONE