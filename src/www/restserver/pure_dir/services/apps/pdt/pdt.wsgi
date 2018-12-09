#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :pdt.wsgi
# description     :WSGI app for PDT service
# author          :Guruprasad
# version         :1.0
############################################################

import sys
import fcntl
import yaml
import json
import requests
import time
import logging

# Python virtual environment for this service
python_home = '/var/www/restserver/venv/'
activate_this = python_home + 'bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# Importing Infra Code
from pure_dir.infra.logging.logmanager import *

# Importing utils code
py_basepath = "/var/www/restserver/pure_dir/services"
sys.path.insert(0, py_basepath)
from utils.register import *

loginfo("Starting pdt...")

# Load the service config file
config_file = py_basepath + '/apps/pdt/config.json'
with open(config_file) as data_file:
    config_data = json.load(data_file)


# Generate target yaml file
if generate_target_yaml(config_data) == True:
    loginfo("Generated target api file for pdt")
else:
    loginfo("Failed to generate target api file for pdt")

# Start the pdt service through connexion app
sys.path.append(config_data['service_syspath'])
from webserver import pdt_app as application
sys.stdout = sys.stderr
logging.basicConfig(stream=sys.stderr)

loginfo("Started pdt service...")


# Function to register all public apis with the gateway for authentication
config_data['apis'] = get_service_apis(
    config_data['api'], config_data['service_syspath'])

descr_keys = ['api', 'service_syspath']
config_data = {key: config_data[key]
               for key in config_data if key not in descr_keys}

sd = {}
sd['service_name'] = config_data['name']
sd['service_details'] = config_data

retry = 0
while retry < 3:
    if register_with_gateway(sd) == True:
        loginfo("Registered pdt with gateway..")
        break
    else:
        loginfo("Failed to register the pdt service with gateway... Retrying")
        time.sleep(1)
        retry += 1
