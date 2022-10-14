#!/bin/bash

if [ -n "$JH_UID" ] && [ -n "$JH_GID" ]; then
  # Create jupyterhub user and group
  USER_ID=${JH_UID}
  GROUP_ID=${JH_GID}

  groupadd -o -r jupyterhub -g ${GROUP_ID}
  useradd --uid ${USER_ID} --gid ${GROUP_ID} -d /srv/jupyterhub -s /bin/bash jupyterhub

  # Change ownership of JupyterHub's working directory
  chown -R ${USER_ID}:${GROUP_ID} /srv/jupyterhub

  # Start JupyterHub with the newly created jupyerhub user
  exec gosu jupyterhub "$@"
fi

exec "$@"
