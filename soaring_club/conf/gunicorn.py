import os
import sys

# Work out the project module name and root directory, assuming that this file
# is located at [project]/conf/guinicorn.py
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(os.path.dirname(BASE_DIR))
APPS_DIR = os.path.abspath(os.path.join(BASE_DIR, '../apps'))
sys.path.append(APPS_DIR)
sys.path.append(PROJECT_DIR)
settings_module = '%s.conf.local.settings' % PROJECT_MODULE_NAME
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

bind = "127.0.0.1:31036"
workers = 1
worker_class = "gevent"

def def_post_fork(server, worker):
    from psyco_gevent import make_psycopg_green
    make_psycopg_green()
    worker.log.info("Made Psycopg Green")

post_fork = def_post_fork
