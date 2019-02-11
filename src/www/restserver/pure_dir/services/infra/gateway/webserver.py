#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :webserver.py
# description     :Gateway connexion app
# author          :Guruprasad
# version         :1.0
############################################################

import flask
import requests
import json
from flask import jsonify, request, redirect, url_for
from xml.dom.minidom import parse
import connexion

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *

service_registry = "/tmp/services.json"
sessions_registry = "/tmp/sessions.xml"
cookie_name = "pure-storage"

gateway_app = connexion.App(__name__, swagger_ui=False)

# For rendering index.html page when http://<ip> is accessed


@gateway_app.route('/')
def index():
    return redirect(url_for('html_handler', page='index.html'))

# For rendering all UI information (html, js, json, etc.)


@gateway_app.route('/<string:page>')
def html_handler(page):
    return flask.render_template(page)

# For handling all API


@gateway_app.route("/<string:basepath>/<string:api>", methods=['GET', 'POST', 'PUT', 'DELETE'])
def indexapi(basepath, api):

    service_port, api_scope = getRequestDetails(basepath, api)

    if service_port == -1:
        response = {}
        response['status'] = {}
        response['status']['code'] = PTK_NOTEXIST
        response['status']['message'] = "Service not registered..."
        return jsonify(response)
    else:
        new_path = "http://127.0.0.1:" + \
            str(service_port) + "/" + basepath + "/" + api

        # Make a REST call to the appropriate service
        if request.remote_addr == '127.0.0.1':
            loginfo("Request through localhost")
            return(call_api(new_path, request))
        else:
            loginfo("Request through ip address")
            if api_scope == "Private":
                status = authenticate(request)
                if status is False:
                    return authentication_error()
            return(call_api(new_path, request))


# Function to get the service port
def getRequestDetails(service_bp, api_name):
    service_port = -1
    api_scope = ""
    with open(service_registry) as data_file:
        services_data = json.load(data_file)
    for service, details in services_data.items():
        if services_data[service]['basepath'] == service_bp:
            service_port = services_data[service]['port']
            for api in services_data[service]['apis']:
                if api['name'] == api_name:
                    api_scope = api['scope']
                    break
            break

    return service_port, api_scope


# Function for basic authentication check
def user_verify(request):
    user = {}
    user['name'] = request.authorization['username']
    user['password'] = request.authorization['password']
    # request.headers.get('authorization') - To get "Basic Z3vyDt=="

    path = "http://127.0.0.1/pure/UserVerify"
    headers = {'Content-type': 'application/json'}
    res = requests.post(path, data=json.dumps(user), headers=headers)
    response = json.loads(res.content)
    if response['status']['code'] == PTK_OKAY:
        loginfo("User verification succeeded")
        return True
    else:
        loginfo("User verification failed")
        return False


# Function for cookie authentication check
def is_session_valid(cookie):
    doc = parse(sessions_registry)
    sessions = doc.documentElement.getElementsByTagName("session")
    for session in sessions:
        if session.getAttribute('login_key') == cookie:
            return True

    return False

# Function for authentication


def authenticate(request):
    if request.authorization:
        loginfo("Basic Authentication")
        isValid = user_verify(request)
        if isValid:
            loginfo("Authentication succeeded - Basic")
            return True
        else:
            loginfo("Authentication failed - Basic")
            return False
    elif request.cookies:
        loginfo("Cookie Authentication")
        if is_session_valid(request.cookies.get(cookie_name)):
            loginfo("Cookie authentication succeeded")
            return True
        else:
            loginfo("Cookie authentication failed")
            return False
    else:
        loginfo("Authentication failed - Neither cookie nor basic")
        return False

# Function to make a REST call to other services


def call_api(new_path, request):
    if request.method == "GET":
        r = requests.get(new_path, params=request.args.to_dict(),
                         headers=request.headers)
    elif request.method == "DELETE":
        r = requests.delete(new_path, params=request.args.to_dict(), data=request.data,
                            headers=request.headers)
    elif request.method == "PUT":
        r = requests.put(new_path, params=request.args.to_dict(), data=request.data,
                         headers=request.headers)
    elif request.method == "POST":
        if request.files:
            filestorage_dict = {}
            filestorage_dict[request.files.keys()[0]] = (
                request.files.values()[0].filename, request.files.values()[0])
            if request.form:
                # TODO: Have to check the combination of form data and query string/post data
                r = requests.post(
                    new_path, files=filestorage_dict, data=request.form)
            else:
                r = requests.post(new_path, files=filestorage_dict)
        else:
            r = requests.post(new_path, params=request.args.to_dict(),
                              data=request.data, headers=request.headers)
    return r.text


def authentication_error():
    return jsonify({'status': {'code': -20, 'message': 'Authentication failed'}})
