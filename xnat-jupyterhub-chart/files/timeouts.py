import os

c.Spawner.start_timeout = int(os.environ['JH_START_TIMEOUT'])
c.Spawner.http_timeout = int(os.environ['JH_HTTP_TIMEOUT'])