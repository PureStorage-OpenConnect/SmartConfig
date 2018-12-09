#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :usermanager.py
# description     :User Management
# author          :Guruprasad
# version         :1.0
############################################################
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from xml.dom.minidom import *
import hashlib
import os
from time import time

users_registry = "/mnt/system/pure_dir/users.xml"
sessions_registry = "/tmp/sessions.xml"


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def users():
    res = result()
    users_list = []

    fd = os.path.isfile(users_registry)
    if(fd != True):
        loginfo("No users are present in the device")
        res.setResult(users_list, PTK_NOTEXIST, "No users are present")
        return res

    doc = parse(users_registry)

    users = doc.documentElement.getElementsByTagName("user")
    for user in users:
        user_dict = {}
        user_dict['name'] = user.getAttribute('name')
        user_dict['isadmin'] = bool(user.getAttribute('isadmin'))
        users_list.append(user_dict)

    res.setResult(users_list, PTK_OKAY, "Success")
    return res


def usercreate(user):
    res = result()
    validate_res = [{"field": "", "msg": ""}]
    optional = []
    validate_res = validateobject(user, optional)
    if validate_res:
        res.setResult(validate_res, PTK_INTERNALERROR,
                      "Invalid Values Specified")
        return res
    if user['password'] != user['confirm_password']:
        validate_res = [{"field": "password", "msg": "Passwords mismatch"}, {
            "field": "confirm_password", "msg": "Passwords mismatch"}]
        res.setResult(validate_res, PTK_PWDMISMATCH, "Passwords mismatch")
        return res

    if os.path.exists(users_registry) == True:
        doc = parse(users_registry)

        users = doc.documentElement.getElementsByTagName("user")
        for ex_user in users:
            """if int(ex_user.getAttribute('id')) == user['id']:
                res.setResult(False, PTK_ALREADYEXIST, "User id already exist")
                return res"""
            if ex_user.getAttribute('name') == user['name'] and ex_user.getAttribute('application') == user['application']:
                res.setResult(validate_res, PTK_ALREADYEXIST,
                              "User name already exist")
                return res

        newuser = doc.createElement("user")
        newuser.setAttribute('name', user['name'])
        newuser.setAttribute('isadmin', str(user['isadmin']))
        hash_object = hashlib.md5(user['password'])
        hashed_password = hash_object.hexdigest()
        newuser.setAttribute('password', hashed_password)
        newuser.setAttribute('application', user['application'])
        doc.childNodes[0].appendChild(newuser)

    else:
        doc = Document()
        roottag = doc.createElement("users")
        newuser = doc.createElement("user")
        newuser.setAttribute('name', user['name'])
        newuser.setAttribute('isadmin', str(user['isadmin']))
        hash_object = hashlib.md5(user['password'])
        hashed_password = hash_object.hexdigest()
        newuser.setAttribute('password', hashed_password)
        newuser.setAttribute('application', user['application'])
        roottag.appendChild(newuser)
        doc.appendChild(roottag)

    fd = open(users_registry, 'w')
    fd.write(pretty_print(doc.toprettyxml(indent="")))
    fd.close()
    res.setResult(validate_res, PTK_OKAY, "Success")
    return res


def userdelete(username, application):
    res = result()
    if os.path.exists(users_registry) == False:
        res.setResult(False, PTK_NOTEXIST, "Users not exists")
        return res
    doc = parse(users_registry)
    users = doc.documentElement.getElementsByTagName("user")
    for user in users:
        if user.getAttribute('name') == username and user.getAttribute('application') == application:
            parent = user.parentNode
            parent.removeChild(user)
            f = open(users_registry, 'w')
            f.write(pretty_print(doc.toprettyxml(indent="")))
            f.close()
            res.setResult(True, PTK_OKAY, "Success")
            return res
    res.setResult(False, PTK_NOTEXIST, "User not exists")
    return res


def userinfo(id):
    res = result()
    doc = parse(users_registry)

    uinfo = {}
    users = doc.documentElement.getElementsByTagName("user")
    for user in users:
        if int(user.getAttribute('id')) == id:
            uinfo['id'] = id
            uinfo['name'] = user.getAttribute('name')
            uinfo['isadmin'] = bool(user.getAttribute('isadmin'))
            uinfo['application'] = user.getAttribute('application')

    if uinfo:
        res.setResult(uinfo, PTK_OKAY, "Success")
        return res
    else:
        res.setResult(uinfo, PTK_NOTEXIST, "No such user")
        return res


def userverify(user):
    res = result()

    fd = os.path.isfile(users_registry)
    if(fd != True):
        loginfo("No users are present in the device")
        res.setResult(False, PTK_NOTEXIST, "No users are present")
        return res

    doc = parse(users_registry)
    users = doc.documentElement.getElementsByTagName("user")
    for user_ent in users:
        if user_ent.getAttribute('name') == user['name'] and user_ent.getAttribute('application') == user['application']:
            hash_object = hashlib.md5(user['password'])
            hashed_password = hash_object.hexdigest()
            if user_ent.getAttribute('password') == hashed_password:
                res.setResult(True, PTK_OKAY, "Success")
                return res
            else:
                res.setResult(False, PTK_NOTEXIST, "No such user")
                return res

    res.setResult(False, PTK_NOTEXIST, "No such user")
    return res


import json


def userlogin(user):
    res = result()
    muser = json.loads(json.dumps(user))
    musername = muser['name']
    mpassword = muser['password']
    validate_cred = []
    if musername == "":
        validate_cred.append(
            {"field": "name", "msg": "username cannot be empty"})
    if mpassword == "":
        validate_cred.append(
            {"field": "password", "msg": "password cannot be empty"})
    if musername == "" or mpassword == "":
        res.setResult(validate_cred, PTK_INTERNALERROR,
                      "Values Not specified as expected")
        return res
    user_valid = userverify(user)
    if user_valid.result == True:
        loggedinkey = _generate_login_key()
        if os.path.exists(sessions_registry) == True:
            doc = parse(sessions_registry)
            session = doc.createElement("session")
            session.setAttribute('username', user['name'])
            session.setAttribute('login_key', loggedinkey)
            session.setAttribute('loggedin_time', str(time()))
            doc.childNodes[0].appendChild(session)
        else:
            doc = Document()
            roottag = doc.createElement("sessions")
            session = doc.createElement("session")
            session.setAttribute('username', user['name'])
            session.setAttribute('login_key', loggedinkey)
            session.setAttribute('loggedin_time', str(time()))
            roottag.appendChild(session)
            doc.appendChild(roottag)
        fd = open(sessions_registry, 'w')
        fd.write(pretty_print(doc.toprettyxml(indent="")))
        fd.close()
        key_data = [{"key": loggedinkey}]
        res.setResult(key_data, PTK_OKAY, "User logged in")
        #res.setResult(loggedinkey, PTK_OKAY, "User logged in")
    else:
        key_data = [{"key": ""}]
        res.setResult(key_data, PTK_NOTEXIST, "Invalid credentials")
    return res


def sessionuser(loginkey):
    res = result()
    if os.path.exists(sessions_registry) == False:
        res.setResult("", PTK_NOTEXIST, "Not a valid session")
        return res

    doc = parse(sessions_registry)

    sessions = doc.documentElement.getElementsByTagName("session")
    for session in sessions:
        if session.getAttribute('login_key') == loginkey:
            res.setResult(session.getAttribute(
                'username'), PTK_OKAY, "Success")
            return res

    res.setResult("", PTK_NOTEXIST, "Not a valid session")
    return res


def sessionlogout(loginkey):
    res = result()
    doc = parse(sessions_registry)

    sessions = doc.documentElement.getElementsByTagName("session")
    for session in sessions:
        if session.getAttribute('login_key') == loginkey:
            uname = session.getAttribute('username')
            session.parentNode.removeChild(session)
            fd = open(sessions_registry, 'w')
            doc.writexml(fd)
            fd.close()
            res.setResult(uname, PTK_OKAY, "User %s logged out" % uname)
            return res

    res.setResult("", PTK_NOTEXIST, "Not a valid session")
    return res


def _generate_login_key():
    import random
    import string
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in
        range(32))
