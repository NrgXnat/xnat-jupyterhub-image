import os

postgres_db = os.environ['POSTGRES_DB']
postgres_user = os.environ['POSTGRES_USER']
postgres_pass = os.environ['POSTGRES_PASSWORD']
postgres_host = os.environ['POSTGRES_HOST']
postgres_port = os.environ['POSTGRES_PORT']

c.JupyterHub.db_url = f'postgresql+psycopg2://{postgres_user}:{postgres_pass}@{postgres_host}:{postgres_port}/{postgres_db}'
