#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :register.py
# description     :Utility functions for service registration
# author          :Guruprasad
# version         :1.0
############################################################

import yaml
import json
import requests
from . import netinfo
from yamlreader import yaml_load

import collections
import pyaml
from . import miscellaneous
from pure_dir.infra.apiresults import *

# Function to find network interface


def _get_filtered_ifnames():
    ifnames = []
    for ifname in netinfo.get_ifnames():
        if ifname.startswith(('lo', 'tap', 'br', 'natbr', 'tun', 'vmnet', 'veth', 'wmaster')):
            continue
        ifnames.append(ifname)

    ifnames.sort()
    return ifnames


# Function to get all public apis
def get_service_apis(api_file, file_path):
    api_list = []
    api_yaml = file_path + "/" + api_file
    with open(api_yaml) as f:
        dataMap = yaml.safe_load(f)
        for k, v in list(dataMap['paths'].items()):
            for key, value in list(v.items()):
                api = {}
                api['name'] = k[1:]
                if key in ['get', 'post', 'put', 'delete']:
                    api['type'] = key
                # if 'security' in value and value['security'] == []:
                    api['scope'] = "Public"
                    api_list.append(api)
    return api_list


# Function to generate target yaml file
def generate_target_yaml(service_details):
    yamlconfig = {
        "info": {'version': service_details['version'], 'title': service_details['description']},
        "swagger": "2.0",
        "produces": ["application/json"],
        "consumes": ["application/json"],
        "schemes": ["http"]
    }

    yaml_dir = service_details['service_syspath'] + "/api/"
    config = yaml_load(yaml_dir, yamlconfig)

    json_file = service_details['service_syspath'] + \
        "/%s_api.json" % service_details['name'].lower()
    yaml_file = service_details['service_syspath'] + \
        "/%s_api.yaml" % service_details['name'].lower()

    with open(json_file, 'w') as outfile:
        json.dump(config, outfile)

    json_fd = open(json_file, 'r')
    with json_fd:
        yaml_fd = open(yaml_file, 'w')
        with yaml_fd:
            loaded_json = json.load(
                json_fd, object_pairs_hook=collections.OrderedDict)
            pyaml.dump(loaded_json, yaml_fd, safe=True)

    return True

# Function to register the service with gateway


def register_with_gateway(data):
    #ifnames = _get_filtered_ifnames()
    #ip = get_ip_address(ifnames[0])
    try:
        url = "http://127.0.0.1/pure/ServiceRegister"
        jdata = json.dumps(data)
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=jdata, headers=headers)

        res = json.loads(response.content)
        if res['status']['code'] == PTK_OKAY:
            return True
        else:
            if res['status']['code'] == 404:
                print("Waiting for service manager to start")
            return False

    except Exception as e:
        print("Failed to register the service: ", str(e))
        return False
