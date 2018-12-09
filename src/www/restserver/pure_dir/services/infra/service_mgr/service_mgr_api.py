#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :service_mgr_api.py
# description     :Landing place for Service Manager APIs
# author          :Guruprasad
# version         :1.0
############################################################


from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *

from core import *


def systeminfo():
    ret = systemmanager.system_info()
    return parseResult(ret)


def serviceregister(data):
    ret = services.service_register(data)
    return parseResult(ret)


def applicationinit(name):
    ret = application.application_init(name)
    return parseResult(ret)


def applicationuninit(name):
    ret = application.application_uninit(name)
    return parseResult(ret)


def applicationreset():
    ret = application.application_reset()
    return parseResult(ret)


def users():
    ret = usermanager.users()
    return parseResult(ret)


def usercreate(user):
    ret = usermanager.usercreate(user)
    return parseResult(ret)


def userinfo(id):
    ret = usermanager.userinfo(id)
    return parseResult(ret)


def userdelete(username, application):
    ret = usermanager.userdelete(username, application)
    return parseResult(ret)


def userverify(user):
    ret = usermanager.userverify(user)
    return parseResult(ret)


def userlogin(user):
    ret = usermanager.userlogin(user)
    return parseResult(ret)


def sessionuser(loginkey):
    ret = usermanager.sessionuser(loginkey)
    return parseResult(ret)


def sessionlogout(loginkey):
    ret = usermanager.sessionlogout(loginkey)
    return parseResult(ret)
