#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :services.py
# description     :services initialisation related functions
# author          :Guruprasad
# version         :1.0
############################################################

import json

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
service_registry = "/tmp/services.json"


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def service_register(data):
    res = result()
    loginfo("Registering service %s with service manager" %
            data['service_name'])
    with open(service_registry, 'r') as f:
        config = json.load(f)

    if data['service_name'] in config:
        loginfo("Service already registered")
        res.setResult(True, PTK_OKAY, "Success")
        return res

    config[data['service_name']] = data['service_details']
    with open(service_registry, 'w') as f:
        json.dump(config, f, indent=4)

    res.setResult(True, PTK_OKAY, "Success")
    return res
