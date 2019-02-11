#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :application.py
# description     :applications initialisation related functions
# author          :Guruprasad
# version         :1.0
############################################################

import json
import importlib
from xml.dom.minidom import *
from filelock import FileLock
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.client.pdtclient import *

service_registry = "/tmp/services.json"
services_xml = "/mnt/system/pure_dir/services.xml"
applications_xml = "/mnt/system/pure_dir/applications.xml"
setup_xml = "/mnt/system/pure_dir/system.xml"

ui_templates = "/var/www/html/templates/"
static_fldr = "/mnt/apps/"

orig_httpd_conf = "/usr/local/apache2/conf/httpd.conf"
tmp_httpd_conf = "/tmp/httpd.conf"


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def _is_init():
    doc = parse(setup_xml)
    try:
        isInit = doc.getElementsByTagName("APP")[0].getAttribute("INIT")
        app = doc.getElementsByTagName("APP")[0].getAttribute("NAME")
        return isInit, app
    except BaseException:
        loginfo("Setup sequence has to be completed")
        return "0", ""


def _write_init(app_name):
    doc = parse(setup_xml)
    try:
        node = doc.createElement("APP")
        node.setAttribute("NAME", app_name)
        node.setAttribute("INIT", "1")

        doc.childNodes[0].appendChild(node)

        with FileLock(setup_xml):
            o = open(setup_xml, "w")
            o.write(pretty_print(doc.toprettyxml(indent="")))
            o.close()

        doc.unlink()
        return 0

    except BaseException:
        loginfo("Failed to initialize the application")
        return -1


def _remove_init():
    doc = parse(setup_xml)
    try:
        doc.documentElement.removeChild(doc.getElementsByTagName("APP")[0])
        with FileLock(setup_xml):
            o = open(setup_xml, "w")
            o.write(pretty_print(doc.toprettyxml(indent="")))
            o.close()

        doc.unlink()
        return 0

    except BaseException:
        loginfo("Failed to uninitialize the application")
        return -1


def _enable_services(services):
    if len(services) == 0:
        return 0

    for service in services:
        conf_inc_cmd = "sed -i '/^#Include.*%s.conf/s/^#//' %s" % (
            service, tmp_httpd_conf)
        (error, output) = execute_local_command(conf_inc_cmd)
        if not error:
            status, details = get_xml_element(
                file_name=services_xml, attribute_key="name", attribute_value=service)
            if status:
                port_listen_cmd = "sed -i '/^#Listen.*:%s/s/^#//' %s" % (
                    details[0]['port'], tmp_httpd_conf)
                (error, output) = execute_local_command(port_listen_cmd)
                if error:
                    loginfo("Unable to make changes to the apache conf")
                    return -1
            else:
                loginfo("Unable to start the service")
                return -1
        else:
            loginfo("Unable to make changes to the apache conf")
            return -1

    loginfo("Services '%s' enabled" % str(services))
    return 0


def _disable_services(services):
    if len(services) == 0:
        return 0

    for service in services:
        conf_inc_cmd = "sed -i '/^Include.*%s.conf/s/^/#/' %s" % (
            service, tmp_httpd_conf)
        (error, output) = execute_local_command(conf_inc_cmd)
        if not error:
            status, details = get_xml_element(
                file_name=services_xml, attribute_key="name", attribute_value=service)
            if status:
                port_listen_cmd = "sed -i '/^Listen.*:%s/s/^/#/' %s" % (
                    details[0]['port'], tmp_httpd_conf)
                (error, output) = execute_local_command(port_listen_cmd)
                if error:
                    loginfo("Unable to make changes to the apache conf")
                    return -1
            else:
                loginfo("Unable to stop the service")
                return -1
        else:
            loginfo("Unable to make changes to the apache conf")
            return -1

    loginfo("Services '%s' disabled" % str(services))
    return 0


def application_init(name):
    res = result()

    with open(service_registry, 'r') as f:
        services = json.load(f)

    status, details = get_xml_element(
        file_name=applications_xml, attribute_key="name", attribute_value=name)

    if status:
        init, app = _is_init()
        if init == "1":
            if app in services:
                if app == name:
                    res.setResult(True, PTK_OKAY,
                                  "Application '%s' is already running" % name)
                    return res
                else:
                    res.setResult(False, PTK_ALREADYEXIST,
                                  "An application is already running")
                    return res
            else:
                res.setResult(False, PTK_INTERNALERROR,
                              "Initialized application may take few seconds to start")
                return res

        loginfo("Application not yet started")
        if 'depends' in details[0]:
            deps_list = filter(None, details[0]['depends'].split(','))
        else:
            deps_list = []

        cmd = "cp -f %s %s" % (orig_httpd_conf, tmp_httpd_conf)
        (error, output) = execute_local_command(cmd)
        if not error:
            if _enable_services(deps_list) == 0:
                loginfo("Dependency services enabled successfully")
                if _enable_services([name]) == 0:
                    loginfo("Application '%s' enabled successfully" % name)
                else:
                    loginfo("Unable to enable the application service '%s'" % name)
                    res.setResult(
                        False,
                        PTK_INTERNALERROR,
                        "Failed to enable the application service '%s'" %
                        name)
                    return res
            else:
                loginfo("Unable to enable the dependency services in '%s'" % str(
                    deps_list))
                res.setResult(False, PTK_INTERNALERROR,
                              "Failed to enable the dependency services in '%s'" % str(deps_list))
                return res
        else:
            loginfo("Unable to make the changes to apache conf")
            res.setResult(False, PTK_INTERNALERROR,
                          "Failed to enable the apache conf parameters")
            return res

        """cmd = "rm -f %s/*.html; cp -f %s/%s/* %s/." % (
            ui_templates, static_fldr, name, ui_templates)
        os.system(cmd)"""
        cmd = "cp -f %s %s" % (tmp_httpd_conf, orig_httpd_conf)
        (error, output) = execute_local_command(cmd)
        if not error:
            cmd = "systemctl reload apache2.service"
            (error, output) = execute_local_command(cmd)
            if not error:
                _write_init(name)
                res.setResult(True, PTK_OKAY,
                              "Application started successfully")
                return res
            else:
                res.setResult(False, PTK_INTERNALERROR,
                              "Failed to start the application. Apache error.")
                return res
        else:
            res.setResult(False, PTK_INTERNALERROR,
                          "Failed to start the application. Configuration copy error.")
            return res

    else:
        loginfo("Invalid application")
        res.setResult(False, PTK_NOTEXIST, "No such application")
        return res

    res.setResult(True, PTK_OKAY, "Success")
    return res


def application_uninit(name):
    res = result()

    with open(service_registry, 'r') as f:
        services = json.load(f)

    status, details = get_xml_element(
        file_name=applications_xml, attribute_key="name", attribute_value=name)

    if status:
        init, app = _is_init()
        if init == "1" and app in services:
            if app == name:
                if 'depends' in details[0]:
                    deps_list = filter(None, details[0]['depends'].split(','))
                else:
                    deps_list = []

                cmd = "cp -f %s %s" % (orig_httpd_conf, tmp_httpd_conf)
                (error, output) = execute_local_command(cmd)
                if not error:
                    if _disable_services([name]) == 0:
                        loginfo("Application '%s' disabled successfully" % name)
                        if _disable_services(deps_list) == 0:
                            loginfo("Dependency services disabled successfully")
                        else:
                            loginfo("Unable to disable the dependency services in '%s'" % str(
                                deps_list))
                            res.setResult(
                                False,
                                PTK_INTERNALERROR,
                                "Failed to disable the dependency services in '%s'" %
                                str(deps_list))
                            return res
                    else:
                        loginfo(
                            "Unable to disable the application service '%s'" % name)
                        res.setResult(
                            False,
                            PTK_INTERNALERROR,
                            "Failed to disable the application service '%s'" %
                            name)
                        return res
                else:
                    loginfo("Unable to make the changes to apache conf")
                    res.setResult(False, PTK_INTERNALERROR,
                                  "Failed to disable the apache conf parameters")
                    return res

                """cmd = "rm -f %s/*.html; cp -f %s/pure/* %s/." % (
                    ui_templates, static_fldr, ui_templates)
                os.system(cmd)"""
                cmd = "cp -f %s %s" % (tmp_httpd_conf, orig_httpd_conf)
                (error, output) = execute_local_command(cmd)
                if not error:
                    cmd = "systemctl reload apache2.service"
                    (error, output) = execute_local_command(cmd)
                    if not error:
                        _remove_init()
                        res.setResult(True, PTK_OKAY,
                                      "Application stopped successfully")
                        return res
                    else:
                        res.setResult(
                            False,
                            PTK_INTERNALERROR,
                            "Failed to stop the application. Apache error.")
                        return res
                else:
                    res.setResult(
                        False,
                        PTK_INTERNALERROR,
                        "Failed to stop the application. Configuration copy error.")
                    return res
            else:
                res.setResult(False, PTK_NOTEXIST,
                              "Application '%s' is not running" % name)
                return res
        else:
            res.setResult(False, PTK_NOTEXIST, "No applications are running")
            return res

    else:
        loginfo("Invalid application")
        res.setResult(False, PTK_NOTEXIST, "No such application")
        return res


def application_reset():
    res = result()
    init, app = _is_init()
    if init == "1":
        obj_path = "pure_dir.services.apps." + app + ".client." + app + "client"
        obj = importlib.import_module(obj_path)

        operation = app.upper() + "Reset_request"
        method = getattr(obj, operation)
        res = method()
        if res.getResult()['status']['code'] != PTK_OKAY:
            loginfo("There is some problem in cleaning up the application contents")
            res.setResult(False, PTK_INTERNALERROR, "Application reset failed")
            return res
        else:
            loginfo("Application contents removed. Resetting...")
            return application_uninit(app)
    else:
        res.setResult(False, PTK_NOTEXIST, "No applications are running")
        return res

    res.setResult(True, PTK_OKAY, "Success")
    return res
