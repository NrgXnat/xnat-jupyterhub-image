ARG JH_VERSION=3.0.0
FROM xnat/scipy-notebook:0.3.0

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/

RUN python3 -m pip install --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}" && \
    rm /tmp/requirements.txt \
