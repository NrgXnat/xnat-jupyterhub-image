1. Build the JupyterHub user image
    ```shell
    cd ./jupyterhub-single-user
    ./build.sh
    ```

2. Build JupyterHub:
    ```shell
    docker compose build 
    ```

3. StartJupyterHub:
    ```shell
    docker compose up -d
    ```

4. Stop JupyterHub
    ```shell
    docker compose down
    ```