# xnat/jupyterhub

The xnat/jupyter image contains a preconfigured JupyterHub for running with XNAT.

To connect XNAT with JupyterHub, a `jupyterhub_config.py` file has been created that 
1. Authenticates a user with XNAT
2. Configures the JupyterHub Docker SwarmSpawner to mount XNAT data

This repo contains a `Dockerfile`, `docker-compose.yml`, and `docker-stack.yml` file for the `xnat/jupyterhub` image. 
The [xnat-jupyter-plugin](https://bitbucket.org/xnatx/xnat-jupyterhub-plugin) must be installed in your XNAT. 
The `xnat/jupyterhub` image must also be running on a manager node within a Docker Swarm in order to spawn Jupyter 
servers as Docker containers. Note that there is one `xnat/jupyterhub` instance per XNAT.

See the [XNAT JupyterHub Plugin Wiki](https://wiki.xnat.org/jupyter-integration) for the latest documentation on this 
plugin.

## Running the xnat/jupyterhub Image
These are the steps for deploying the xnat/jupyterhub image alongside an existing XNAT. For convenience, the 
[xnat-docker-compose repository](https://github.com/NrgXnat/xnat-docker-compose/tree/features/jupyterhub) has a branch 
with JupyterHub added as a service alongside XNAT.

1. Clone repo into a directory.
   ```shell
   cd /opt
   git clone https://bitbucket.org/xnat-containers/xnat-jupyterhub.git jupyterhub
   ```
2. Configure the docker-stack.yml environmental variables.
   
   It is critical to correctly configure the UID and GID of JupyterHub (JH) and the single-user Jupyter notebook (NB) 
   containers. In general, the Tomcat/XNAT UID is used as the UID for JH and the NB containers. The Tomcat/XNAT GID is 
   used as the GID for the NB containers only. The GID for JH is the group id of the docker group.
   
   Get the id of the tomcat/xnat user 
   ```shell
   $ id tomcat
    uid=54(tomcat) gid=54(tomcat) groups=54(tomcat),992(docker)
    ```
   
   You can also find the gid of the docker socket with
   ```shell
   $ cat /etc/group | grep docker
   docker:x:992:tomcat
   ```
   Tomcat, JH and the NB containers will share this UID (54). Tomcat and the NB containers will share the same GID (54) 
   while JH will be a member of the docker group (992).

   If you have a domain name for this server we will also set the `JH_XNAT_URL` environmental variable. This 
   environmental variable is used by JupyterHub to communicate with your XNAT.
   ```shell
   # docker-stack.yml
   
   # ...
   
   environment:
     JH_NETWORK: *networkname
     JH_UID: 54
     JH_GID: 992
     NB_UID: 54
     NB_GID: 54
     JH_START_TIMEOUT: 180
     JH_XNAT_URL: http://172.17.0.1 OR https://your.xnat.org
     JH_XNAT_SERVICE_TOKEN: # create a service token for XNAT to talk to JH
     JH_XNAT_USERNAME: jupyterhub
     JH_XNAT_PASSWORD: # create a password for JH to talk to XNAT
   ```
   
   You will also need to create a service token for XNAT to use with JupyterHub and create a password for JupyterHub to 
   use with XNAT. Supplies these to JupyterHub here. Save these for later, you will need them to configure the JupyterHub
   plugin in the XNAT UI.

3. Initiate a Docker swarm if you are not already on one. Otherwise, make sure you are on a master node.
    ```shell
    docker swarm init
    ```

4. Start JupyterHub on a master node:
    ```shell
    docker stack deploy -c docker-stack.yml jupyterhub
    ```
   
   JupyterHub should be available at http://localhost:8000/jupyterhub (or your domain name). See notes below for 
   configuring your reverse proxy if you can't find JupyterHub.
   
5. Pull single-user container images:
   ```shell
   docker image pull xnat/datascience-notebook:latest
   ```
   
6. Login to XNAT and configure the JupyterHub plugin. See the documentation for all the details on how to configure the 
   plugin. You will need the service token and password you created in step 2. In XNAT the JupyterHub service account 
   needs to be enabled and the password set, and the JupyterHub URL, service token, and path translated need to be set.

7. To view and inspect JupyterHub and a running single-user notebook container:
   ```shell
   docker service ls
   docker service logs 9hzw7gu0mo79
   docker service inspect 9hzw7gu0mo79     
   ```
   
8. Stop JupyterHub 
    ```shell
    docker stack rm jupyterhub
    ```
   
### Using a reverse proxy 
JupyterHub and XNAT should live behind the same reverse proxy with XNAT at `/` and JupyterHub at `/jupyterhub`. The 
[xnat-docker-compose repo](https://github.com/NrgXnat/xnat-docker-compose/blob/features/jupyterhub/nginx/nginx.conf) has
an example of having XNAT and JupyterHub behind the same reverse proxy. This is based on the JupyterHub 
[documentation](https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html). 

Below is an example of configuring haproxy:
```shell
# haproxy.cfg example

# ...
# ...
# ...

frontend appserver
        bind 0.0.0.0:80
        bind 0.0.0.0:443 ssl crt /etc/ssl/certs/devcert.pem
        http-response replace-value Location ^http://(.*)$ https://\1
        use_backend jupyterhub if { path_beg /jupyterhub } || { path_beg /jupyterhub/ }
        use_backend web_servers if { path_beg / }
        default_backend web_servers

backend web_servers
        mode http
        balance roundrobin
        option forwardfor
        http-request set-header X-Forwarded-Port %[dst_port]
        http-response set-header location %[res.hdr(location),regsub(http://,https://)] if { status 301 302 }
        server web01 127.0.0.1:8080

backend jupyterhub
        mode http
        balance roundrobin
        option forwardfor
        http-request set-header X-Forwarded-Port %[dst_port]
        http-response set-header location %[res.hdr(location),regsub(http://,https://)] if { status 301 302 }
        server jhub01 127.0.0.1:8000
```

## Arguments and Environmental Variables

Here's a summary of the arguments and environmental variables used in the JupyterHub dockerfile.

| Variable                   | Description / Comments                                                                                                                                            |
|:---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| JH_NETWORK                 | JupyterHub and the single-user Jupyter containers must run on the same Docker network. Used in jupyterhub_config.py.                                              |
| JH_XNAT_URL                | The URL of the XNAT to connect to. Required by XnatAuthenticator and xnat_pre_spawn_hook.                                                                         |
| JH_XNAT_SERVICE_TOKEN      | XNAT needs a service account within JupyterHub inorder to spawn servers. This is the token used by XNAT for the service account. Required by xnat_pre_spawn_hook. |
| JH_XNAT_USERNAME           | JupyterHub needs an account with XNAT to retrieve the user options during the spawning process. Required by xnat_pre_spawn_hook.                                  |
| JH_XNAT_PASSWORD           | The password for JupyterHub's account on XNAT. Required by xnat_pre_spawn_hook.                                                                                   |
| JH_START_TIMEOUT           | The amount of time JupyterHub should wait (in seconds) before deciding the single user container failed to start                                                  |
| JH_UID                     | The UID to run JupyterHub with.                                                                                                                                   |
| JH_GID                     | The GID to run JupyterHub with. This group should have access to the Docker socket.                                                                               |
| NB_UID                     | The UID to run the single-user Jupyter containers with. This should match the UID of the XNAT archive.                                                            |
| NB_GID                     | The GID to run the single-user Jupyter containers with. This should match the GID of the XNAT archive.                                                            |

## Running on Kubernetes

The 'xnat-jupyterhub-chart' directory contains a Helm chart which deploys JupyterHub for an XNAT instance on Kubernetes.
The chart is based on the [Zero to JupyterHub](https://zero-to-jupyterhub.readthedocs.io/en/latest/) chart. 
The chart contains a `values.yaml` file which contains the default values needed to deploy JupyterHub for an XNAT. A 
postgres database is also deployed for JupyterHub. This chart presumes that the XNAT instance is deployed in the same
Kubernetes namespace as JupyterHub. This chart, [johnflavin/xnat-skaffold](https://gitlab.com/johnflavin/xnat-skaffold),
was used to deploy XNAT when developing this chart. The PV and PVC for the user workspaces are created by the XNAT
deployment. Be sure the JupyterHub plugin is installed in the XNAT instance.

The chart can be deployed with the following command:

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart
helm repo update
helm upgrade --install jupyterhub xnat-jupyterhub-chart/ -n xnat --create-namespace --values xnat-jupyterhub-chart/values.yaml
helm uninstall xnat-jupyterhub -n xnat
```

You may need to update the `values.yaml` file to align with your deployment and XNAT instance.
