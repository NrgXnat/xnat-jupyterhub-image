ARG JH_VERSION=3.0.0
FROM xnat/datascience-notebook:1.0.0

#USER root

RUN curl -fsSL https://code-server.dev/install.sh | sh -s -- --prefix=/usr/local
#RUN rm -rfd /home/${NB_USER}/.cache/code-server
#
#USER ${NB_UID}

COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/

RUN python3 -m pip install --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}" && \
    rm /tmp/requirements.txt

CMD ["sh", "-c", "code-server --install-extension ms-python.python --install-extension ms-toolsai.jupyter --install-extension oderwat.indent-rainbow && jhsingle-native-proxy --port 8888 --destport 8505 code-server --auth none --disable-telemetry --disable-update-check --bind-addr 0.0.0.0:8888 --user-data-dir /workspace/$JUPYTERHUB_USER -vvv"]
# "command": "sh -c code-server --install-extension ms-python.python --install-extension ms-toolsai.jupyter --install-extension oderwat.indent-rainbow && jhsingle-native-proxy --destport 8505 code-server {--}auth none {--}disable-telemetry {--}disable-update-check {--}bind-addr 0.0.0.0:{port} {--}user-data-dir / {-}vvv"
#CMD ["jhsingle-native-proxy", "--port", "8888", "--destport", "8505", "code-server", "--auth", "none", "--disable-telemetry", "--disable-update-check", "--bind-addr", "0.0.0.0:8888", "--user-data-dir", "/workspace", "-vvv"]