import logging
import sys

logger = logging.getLogger("xnat-jupyterhub")
logger.propagate = False
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s %(asctime)s %(name)s %(module)s:%(lineno)d] %(message)s")
sh.setFormatter(formatter)
logger.addHandler(sh)