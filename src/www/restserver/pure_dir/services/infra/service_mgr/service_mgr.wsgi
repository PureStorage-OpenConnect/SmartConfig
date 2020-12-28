#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :service_mgr.wsgi
# description     :WSGI app for Gateway service
# author          :Guruprasad
# version         :1.0
############################################################

from core.services import *
from pure_dir.services.utils.register import *
from pure_dir.infra.logging.logmanager import *
import sys
import json
import logging

# Python virtual environment for this service
python_home = '/var/www/restserver/venv/'
activate_this = python_home + 'bin/activate_this.py'
exec(compile(open(activate_this, "rb").read(), activate_this, 'exec'), dict(__file__=activate_this))

# Importing Infra Code

# Importing utils code
py_basepath = "/var/www/restserver/pure_dir/services"
sys.path.insert(0, py_basepath)

loginfo("Starting service manager...")

# Initialize the services.json file with a empty object for the services to register their entries
service_registry = "/tmp/services.json"
with open(service_registry, 'w') as sfile:
    sfile.write(json.dumps({}))

# Load the service config file
config_file = py_basepath + '/infra/service_mgr/config.json'
with open(config_file) as data_file:
    config_data = json.load(data_file)


# Generate target yaml file
if generate_target_yaml(config_data):
    loginfo("Generated target api file for service manager")
else:
    loginfo("Failed to generate target api file for service manager")

# Start the manager service through connexion app
sys.path.append(config_data['service_syspath'])
from webserver import servicemgr_app as application
sys.stdout = sys.stderr
logging.basicConfig(stream=sys.stderr)

loginfo("Started service manager...")

# Function to get all public apis with the gateway for authentication
config_data['apis'] = get_service_apis(
    config_data['api'], config_data['service_syspath'])

descr_keys = ['api', 'service_syspath']
config_data = {key: config_data[key]
               for key in config_data if key not in descr_keys}

# Self register the service with itself
data = {}
data['service_name'] = config_data['name']
data['service_details'] = config_data

service_register(data)
