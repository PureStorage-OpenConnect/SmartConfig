#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :miscellaneous.py
# description     :General utility functions
# author          :Guruprasad
# version         :1.0
############################################################

import os
import jinja2
import socket
import fcntl
import struct
import shlex
import re
import paramiko
import netinfo
import fnmatch
import ipaddress

from confparser import *
from time import sleep
from subprocess import Popen, PIPE
from lxml import etree
from xml.dom.minidom import *
from filelock import FileLock

CONF_FILE = '/etc/sysconfig/network-scripts/static-network'
users_registry = "/mnt/system/pure_dir/users.xml"

oui_cisco = '0025B5'
oui_pure = '24A937'


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def get_xml_element(file_name, attribute_key, attribute_value=''):
    if os.path.exists(file_name) is True:
        lock = FileLock(file_name + ".lock")
        with lock.acquire(timeout=-1):
            try:
                tree = etree.parse(file_name)
            except Exception as e:
                return False, None

        if tree:
            root = tree.getroot()
            datadict = []
            for item in root:
                datadict.append(dict(zip(item.keys(), item.values())))

            matched_list = []
            for d in datadict:
                for k, v in d.items():
                    if k == attribute_key:
                        if attribute_value == '':
                            matched_list.append(d)
                        else:
                            if v == attribute_value:
                                matched_list.append(d)

            if len(matched_list) > 0:
                return True, matched_list
            else:
                return False, matched_list
        else:
            return False, None

    return False, None


def add_xml_element(file_name, data, element_name=''):
    file_basename = os.path.basename(file_name)
    if os.path.exists(file_name) == False:
        doc = Document()
        roottag = doc.createElement(file_basename[:-4])
        doc.appendChild(roottag)
    else:
        try:
            doc = parse_xml(file_name)
        except Exception as e:
            return False

    ele_name = file_basename[:-5] if element_name == '' else element_name
    node = doc.createElement(ele_name)
    for name, value in data.items():
        node.setAttribute(name, value)
    doc.childNodes[0].appendChild(node)

    lock = FileLock(file_name + ".lock")
    with lock.acquire(timeout=-1):
        o = open(file_name, "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    return True


def delete_xml_element(file_name, matching_key, matching_value='', element_name=''):
    file_basename = os.path.basename(file_name)
    if os.path.exists(file_name) is True:
        try:
            doc = parse_xml(file_name)
            ele_name = file_basename[:-
                                     5] if element_name == '' else element_name
            for subelement in doc.getElementsByTagName(ele_name):
                if matching_value == '':
                    if subelement.hasAttribute(matching_key):
                        doc.documentElement.removeChild(subelement)

                elif subelement.getAttribute(matching_key) == matching_value:
                    doc.documentElement.removeChild(subelement)

            lock = FileLock(file_name + ".lock")
            with lock.acquire(timeout=-1):
                o = open(file_name, "w+")
                o.write(pretty_print(doc.toprettyxml(indent="")))
                o.close()
            return True

        except Exception as e:
            return False
    else:
        return False


def update_xml_element(file_name, matching_key, matching_value, data, element_name=''):
    file_basename = os.path.basename(file_name)
    if os.path.exists(file_name) is True:
        try:
            doc = parse_xml(file_name)
            ele_name = file_basename[:-
                                     5] if element_name == '' else element_name
            for subelement in doc.getElementsByTagName(ele_name):
                if subelement.hasAttribute(matching_key):
                    if (matching_value == '') or (matching_value !=
                                                  '' and subelement.getAttribute(matching_key) == matching_value):
                        for name, value in data.items():
                            subelement.setAttribute(name, value)
                        lock = FileLock(file_name + ".lock")
                        with lock.acquire(timeout=-1):
                            o = open(file_name, "w+")
                            o.write(pretty_print(doc.toprettyxml(indent="")))
                            o.close()
                        return True
        except Exception as e:
            return False
    else:
        return False


def parse_xml(file_name):
    lock = FileLock(file_name + ".lock")
    with lock.acquire(timeout=-1):
        doc = parse(file_name)
        return doc


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


def gen_from_template(template, data, outfile):
    result = render(template, data)
    with open(outfile, "wb") as fh:
        fh.write(result)
    return True


def execute_local_command(command):
    try:
        command_arg_split = shlex.split(command)
        process = Popen(command_arg_split, stdout=PIPE, stderr=PIPE)
        output, error = process.communicate()
        pattern = re.compile('.+')
        if ((pattern.match(output) or output is '') and error is ''):
            status = process.returncode
            if (status > 0):
                return status, output
            else:
                return status, output
        else:
            return status, output
    except Exception:
        return -1, False


def execute_remote_command(host, username, password, command=None):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password, timeout=10)
        (stdin, stdout, stderr) = client.exec_command(command)
        status = stderr.channel.recv_exit_status()
        output = ''
        for line in stdout:
            output += line
        return status, output
    except Exception:
        return -1, False


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def parse_resolv(path):
    for line in file(path).readlines():
        if line.startswith('nameserver'):
            return line.strip().split()[1]
    return ""


def get_nameserver():
    nameservers = parse_resolv('/etc/resolv.conf')
    if nameservers:
        return nameservers
    return ""


def get_filtered_ifnames():
    ifnames = []
    for ifname in netinfo.get_ifnames():
        if ifname.startswith(('lo', 'tap', 'br', 'natbr', 'tun', 'vmnet', 'veth', 'wmaster')):
            continue
        ifnames.append(ifname)
    ifnames.sort()
    return ifnames


def get_ipconf(ifname):
    net = netinfo.InterfaceInfo(ifname)
    return net.addr, net.netmask, net.gateway


def network_info():
    ifnames = get_filtered_ifnames()
    for ifname in ifnames:
        networkinfo = {}
        networkinfo['ip'], networkinfo['netmask'], networkinfo['gateway'] = get_ipconf(
            ifname)
        if networkinfo['gateway'] is None:
            networkinfo['gateway'] = ""

        return networkinfo
    return networkinfo


def verify_network_info():
    s = []
    ifnames = get_filtered_ifnames()
    for ifname in ifnames:
        networkinfo = {}
        networkinfo['ip'], networkinfo['netmask'], networkinfo['gateway'] = get_ipconf(
            ifname)
        networkinfo['adaptor'] = ifname
        s.append(networkinfo)
    return s


def network_modify(data):
    try:
        ifnames = get_filtered_ifnames()
        for ifname in ifnames:
            value = setConfValue(CONF_FILE, "BOOTPROTO", "static", CONFSTRING)
            value = setConfValue(CONF_FILE, "IPADDR", data['ip'], CONFSTRING)
            value = setConfValue(CONF_FILE, "NETMASK",
                                 data['netmask'], CONFSTRING)
            value = setConfValue(CONF_FILE, "GATEWAY",
                                 data['gateway'], CONFSTRING)
            value = setConfValue(CONF_FILE, "ONBOOT", "yes", CONFSTRING)
            value = setConfValue(CONF_FILE, "DEVICE", ifname, CONFSTRING)
            value = setConfValue(CONF_FILE, "NAME", ifname, CONFSTRING)
            cmd = "cp %s /etc/sysconfig/network-scripts/ifcfg-%s" % (
                CONF_FILE, ifname)
            os.system(cmd)

            fp = open("/etc/resolv.conf", "w")
            config = "nameserver %s\n" % (data['nameserver'])
            fp.write(config)
            fp.close()

            sleep(0.5)
            os.system("service network restart")
            net = netinfo.InterfaceInfo(ifname)
            if not net.addr:
                return False
            return True
    except Exception:
        return False


def ipvalidation(ip):
    try:
        if len(ip.split('.')) != 4:
            return False
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def validate_input_data(req_data, input_data):
    validate_res = []
    for data in req_data:
        if data in input_data and input_data[data] != '':
            pass
        else:
            msg = ""
            msg = req_data[data] + " cannot be empty"
            validate_dict = {}
            validate_dict['field'] = data
            validate_dict['msg'] = msg
            validate_res.append(validate_dict)

    return validate_res


def validateobject(data, optional):
    validate_res = []
    obj = {"msg": "", "field": ""}
    if not data:
        obj = {"msg": "Input Validation Failed", "field": ""}
        return obj
    else:
        for k, v in data.iteritems():
            if k not in optional and data[k] == "":
                msg = k + " cannot be empty"
                validate_dict = {}
                validate_dict['field'] = k
                validate_dict['msg'] = msg
                validate_res.append(validate_dict)
    return validate_res


def deleteusers(application):
    if os.path.exists(users_registry) == False:
        return 0
    doc = parse(users_registry)
    users = doc.documentElement.getElementsByTagName("user")
    for user in users:
        if user.getAttribute('application') == application:
            parent = user.parentNode
            parent.removeChild(user)
            f = open(users_registry, 'w')
            f.write(pretty_print(doc.toprettyxml(indent="")))
            f.close()
    return 0


def get_oui(wwnn):
    wwnn_string = ''.join(wwnn.split(':'))
    if wwnn_string[0] == '1'or wwnn_string[0] == '2':
        oui = wwnn_string[4:10].upper()
    elif wwnn_string[0] == '5' or wwnn_string[0] == '6':
        oui = wwnn_string[1:7].upper()
    else:
        oui = None
    return oui


def findIPs(start, end):
    start = ipaddress.ip_address(start)
    end = ipaddress.ip_address(end)
    result = []
    while start <= end:
        result.append(str(start))
        start += 1
    return result
