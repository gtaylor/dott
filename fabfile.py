from __future__ import with_statement
from fabric.api import *

env.hosts = ['dott@gc-taylor.com']

def deploy():
    with cd('/home/dott/dott'):
        run('git pull')