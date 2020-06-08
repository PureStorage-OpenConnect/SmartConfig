#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :gateway.wsgi
# description     :WSGI app for Gateway service
# author          :Guruprasad
# version         :1.0
############################################################

import sys
import json
import logging

# Python virtual environment for this service
python_home = '/var/www/restserver/venv/'
activate_this = python_home + 'bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Importing Infra Code
from pure_dir.infra.logging.logmanager import loginfo

# Importing utils code
py_basepath = "/var/www/restserver/pure_dir/services"
sys.path.insert(0, py_basepath)

loginfo("Starting gateway...")

# Load the service config file
config_file = py_basepath + '/infra/gateway/config.json'
with open(config_file) as data_file:
    config_data = json.load(data_file)


# Start the gateway service through connexion app
sys.path.append(config_data['service_syspath'])
from webserver import gateway_app as application
sys.stdout = sys.stderr
logging.basicConfig(stream=sys.stderr)

loginfo("Started gateway service...")
