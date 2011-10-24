from __future__ import with_statement
from fabric.api import *

env.hosts = ['dott@gc-taylor.com']

def deploy():
    """
    Pulls the latest changes on the production server. For the time being,
    you'll still need to @restart in-game to apply changes. In the future,
    we'll just: kill -s HUP <pid>.
    """
    with cd('/home/dott/dott'):
        run('git pull')

def get_db():
    """
    Pulls the latest DB from production.
    """
    local('mkdir -p db')
    get('/var/lib/couchdb/dott_accounts.couch', local_path='db')
    get('/var/lib/couchdb/dott_objects.couch', local_path='db')

