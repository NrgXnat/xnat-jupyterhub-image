XNAT JupyterHub Image 
=====================

This is a standalone JupyterHub image which:
1) Authenticates user's with an XNAT.
2) Spawns a single user Jupyter server in a Docker container with XNAT data mounted to the container.

## The single user container
JupyterHub needs an image to use for the single user server containers. `./jupyterhub-single-user` contains a Dockerfile for the single user server which is based on the [Jupyter docker stacks](https://jupyterhub-dockerspawner.readthedocs.io/en/latest/docker-image.html). Per [JupyterHub's documentations](https://jupyterhub-dockerspawner.readthedocs.io/en/latest/docker-image.html) any of the existing Jupyter docker stacks can be used with JupyterHub provided that the version of JupyterHub in the image matches. The packages in `./jupyterhub-single-user/requirements.txt` will be installed into the container. Any packages which are widely used by your users should be added to requirements.txt file otherwise users will need to install packages manually.

## Docker, DockerSwarm, Kubernetes
This image currently launches single user containers into a local Docker instance via a Docker socket mounted to the container. We plan to add support for Docker Swarm and Kubernetes in the future.

## Dockerfile Variables

| Variable                                                                             | Description / Comments                                                                                                           |
|:-------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| JH_VERSION                                                                           | The JupyterHub version.                                                                                                          |
| JH_DOCKERSPAWNER_VERSION                                                             | The version of dockerspawner to use with JupyterHub.                                                                             |
| JH_NETWORK                                                                           | JupyterHub and the single user containers must run on the same Docker network.                                                   |
| JH_USER_NB_IMG                                                                       | The single user servers are spawned from this image.                                                                             |
| JH_XNAT_URL                                                                          | The URL of the XNAT to connect to.                                                                                               |
| JH_XNAT_SERVICE_TOKEN                                                                | XNAT needs a service account within JupyterHub inorder to spawn servers. This is the token used by XNAT for the service account. |
| JH_XNAT_USERNAME                                                                     | JupyterHub needs an account with XNAT to retrieve the user options during the spawing process.                                   |
| JH_XNAT_PASSWORD                                                                     | The password for JupyterHub's account on XNAT.                                                                                   |




## Building and Running the image

1. Build the JupyterHub single user image
    ```shell
    cd ./jupyterhub-single-user
    ./build.sh
    ```

2. Build JupyterHub:
    ```shell
    docker compose build 
    ```

3. Start JupyterHub:
    ```shell
    docker compose up -d
    ```

4. Stop JupyterHub
    ```shell
    docker compose down
    ```