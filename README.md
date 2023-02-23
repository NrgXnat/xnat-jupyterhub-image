# xnat2jupyterhub and xnat/jupyterhub

xnat2jupyterhub is a Python package for integrating XNAT with JupyterHub. The xnat/jupyter image contains a 
preconfigured JupyterHub for running with XNAT.

To connect XNAT with JupyterHub, xnat2jupyterhub will:
1. Authenticate a user with XNAT
2. Configure the JupyterHub SwarmSpawner to mount XNAT data

This repo contains xnat2jupyterhub, a `Dockerfile` and `docker-compose.yml` file for the `xnat/jupyterhub` image. The 
xnat-jupyter-plugin must be installed in your XNAT for this to work. JupyterHub must also be running on a master node 
within a Docker swarm.

## Setting up JupyterHub
JupyterHub is configured with a Python script `jupyterhub_config.py` (see 
[JupyterHub Configuration Basics](https://jupyterhub.readthedocs.io/en/stable/getting-started/config-basics.html) for 
more details). A full `jupyterhub_config.py` example which uses xnat2jupyterhub can be found in 
`dockerfiles/jupyterhub`. 

### Install xnat2jupyterhub

```sh
python3 -m pip install --no-cache -i https://test.pypi.org/simple/ xnat2jupyterhub=={VERSION}
```

### Import xnat2jupyterhub
Import the XnatAuthenticator and the xnat_pre_spawn_hook from xnat2jupyterhub. 

```python
# jupyterhub_config.py
import os
import sys
import logging

from xnat2jupyterhub.auth import XnatAuthenticator
from xnat2jupyterhub.hooks.swarmspawner import pre_spawn_hook as xnat_pre_spawn_hook
...
```

### Logging Configuration
JupyterHub already logs to stdout which can be redirected to a file at startup. This will direct xnat2jupyter logging to
stdout.

```python
# jupyterhub_config.py
...
logger = logging.getLogger("xnat2jupyterhub")
logger.propagate = False
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s %(asctime)s %(name)s %(module)s:%(lineno)d] %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)
...
```

### JupyterHub Configuration:
For using a reverse proxy see the 
[JupyterHub docs](https://jupyterhub.readthedocs.io/en/stable/reference/config-proxy.html). For SSL see 
[JupyterHub security settings](https://jupyterhub.readthedocs.io/en/stable/getting-started/security-basics.html).

In this example XNAT will be reachable at http://xnat-url and Jupyterhub at http://xnat-url/jupyterhub. 
XNAT does not currently use the named servers feature. We will also shut down the single-user containers when the user 
logs out of JupyterHub.

```python
# jupyterhub_config.py
...
c.JupyterHub.bind_url = 'http://:8000/jupyterhub'
c.JupyterHub.hub_bind_url = 'http://:8081/jupyterhub'
c.JupyterHub.hub_connect_url = 'http://jupyterhub:8081/jupyterhub'
c.JupyterHub.allow_named_servers = False
c.JupyterHub.shutdown_on_logout = True
...
```

### Authentication Configuration
Enable any admin users on JupyterHub and set the authentication class to XnatAuthenticator from the xnat2jupyterhub 
package. The XnatAuthenticator uses basic password authentication. The 
[XNAT OpenID Plugin](https://bitbucket.org/xnatx/openid-auth-plugin) configured with Google OAuth was tested with the 
[GoogleOAuthenticator](https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html#the-oauthenticator). 
But there is a known [issue](https://issues.xnat.org/browse/JHP-24) getting these to work together.

```python
...
# jupyterhub_config.py
...
c.Authenticator.admin_users = {'admin'}
c.JupyterHub.authenticator_class = XnatAuthenticator
...
```


### Spawner configuration
The XNAT pre_spawn_hook has only been tested on Docker Swarm. We'd like to one day support Kubernetes. The start_timeout
will set a maximum time that JupyterHub will wait before decided that a server failed to spawn. All single-user 
containers must also run on the same Docker network. The xnat_pre_spawn_hook will call the XNAT REST API to get configuration meta-data for the container (such as mounts 
and env variables).

```python
# jupyterhub_config.py
...
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'
c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 75
c.SwarmSpawner.network_name = os.environ['JH_NETWORK']
c.SwarmSpawner.pre_spawn_hook = xnat_pre_spawn_hook 
...
```



### UID / GID
If the UID and GID of the single-user Jupyter container is not set in the single-user image it can be set in 
the JupyterHub configuration if your single-user Jupyter image is based on the 
[Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/). The UID and GID needs to match that of
XNAT. Differences could cause problems with users reading XNAT data and writing notebooks.

```python
# jupyterhub_config.py
...
if 'JH_UID' in os.environ and 'JH_GID' in os.environ:
    if os.environ['JH_UID'] and os.environ['JH_GID']:
        environment = {'NB_UID': os.environ['JH_UID'],
                       'NB_GID': os.environ['JH_GID']}
        c.SwarmSpawner.environment.update(environment)
        c.SwarmSpawner.extra_container_spec = {'user': '0'}
...
```

### XNAT Service Account
XNAT needs to have a service account with JupyterHub in order for it to spawn XNAT enabled Jupyter containers. The admin
privileges granted to XNAT are only available to admin users on XNAT
```python
# jupyterhub_config.py
...
c.JupyterHub.services = [
    {
        "name": "xnat",
        "api_token": os.environ['JH_XNAT_SERVICE_TOKEN']
    },
]

c.JupyterHub.load_roles = [
    {
        "name": "admin-hub-role",
        "scopes": [
            "admin:servers", "admin:users", "read:hub", "tokens"
        ],
        "services": [
            "xnat"
        ],
    }
]
```

## Single-User Jupyter Images
JupyterHub needs an image to use for the single-user Jupyter containers. `dockerfiles/` contains example Dockerfiles 
for creating single-user Jupyter images which are based on the 
[Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/). More info on
[building your own Docker image](https://jupyterhub-dockerspawner.readthedocs.io/en/latest/docker-image.html) can be 
found in the JupyterHub documentation. Any of the existing Jupyter Docker images can be used with JupyterHub 
provided that the version of JupyterHub in the image matches. Any Python packages which are widely used by your users 
should be added to the image otherwise users will need to install packages manually. The JupyterHub plugin for XNAT 
allows users to select an image they'd like to launch with. See the plugin settings to configure the allowed images.

## Arguments and Environmental Variables

These are the arguments and environmental variables used in the JupyterHub dockerfile, jupyterhub_config.py, the
XnatAuthenticator, and the xnat_pre_spawn_hook.

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


## Running the xnat/jupyterhub Image
These are the steps for deploying JupyterHub alongside an existing XNAT. For convenience, the 
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
     JH_XNAT_SERVICE_TOKEN: 
     JH_XNAT_USERNAME: jupyterhub
     JH_XNAT_PASSWORD: 
   ```
   
   You will also need to supply a service token for XNAT to use with JupyterHub and a password for JupyterHub to use
   with XNAT. 

3. Initiate a Docker swarm if you are not already on one. Otherwise, make sure you are on a master node.
    ```shell
    docker swarm init
    ```

4. Start JupyterHub:
    ```shell
    docker stack deploy -c docker-stack.yml jupyterhub
    ```
   
   JupyterHub should be available at http://localhost:8000/jupyterhub (or your domain name). See notes below for 
   configuring your reverse proxy if you can't find JupyterHub.
   
5. Pull single-user container images:
   ```shell
   docker image pull jupyter/scipy-notebook:hub-3.0.0
   docker image pull xnat/scipy-notebook:0.3.0
   docker image pull xnat/monai-notebook:0.3.0
   ```
   
6. View and inspect JupyterHub and the single-user NB containers:
   ```shell
   docker service ls
   docker service logs 9hzw7gu0mo79
   docker service inspect 9hzw7gu0mo79     
   ```
   
7. Stop JupyterHub 
    ```shell
    docker stack rm jupyterhub
    ```
   
### Using a reverse proxy 
JupyterHub and XNAT should live behind the same reverse proxy with XNAT at / and JupyterHub at /jupyterhub. The 
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