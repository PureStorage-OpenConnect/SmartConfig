#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :systemmanager.py
# description     :Service Information
# author          :Guruprasad
# version         :1.0
############################################################

import os
import xml.etree.ElementTree as ET

from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_globals import reset_global_config

info_file = "ula/pdt.txt"
build_file = "/mnt/system/pure_dir/pdt/build.xml"
settings = "/mnt/system/pure_dir/pdt/settings.xml"


def get_smartconfig_version():
    try:
        dom = ET.parse(build_file)
        version = dom.getroot().get('version')
        return version
    except BaseException:
        return "1.2"


def system_info():
    res = result()
    sysinfo = {
        'name': 'FlashStack&trade; | SmartConfig',
        'version': get_smartconfig_version(),
        'copyright': '&copy; 2018 Pure Storage Inc',
        'info': info_file
    }
    cmd = "systemctl status dhcpd"
    (error, output) = execute_local_command(cmd)
    if not error:
        if "running" in output:
            sysinfo['dhcp_status'] = "enabled"
        else:
            sysinfo['dhcp_status'] = "disabled"
    else:
        sysinfo['dhcp_status'] = "disabled"

    status, details = get_xml_element(settings, 'current_step')
    if status:
        sysinfo['deployment_settings'] = details[0]

    res.setResult(sysinfo, PTK_OKAY, "Success")
    return res


def deployment_settings(data):
    res = result()
    status, details = get_xml_element(settings, 'current_step')
    if not status:
        if add_xml_element(settings, data, element_name='deployment') == False:
            res.setResult(False, PTK_INTERNALERROR, "Failed to save settings")
    else:
        if update_xml_element(settings, 'current_step', '', data, element_name='deployment'):
            res.setResult(False, PTK_INTERNALERROR, "Failed to save settings")
    res.setResult(True, PTK_OKAY, "Success")
    return res


def networkinfo():
    res = result()
    networkinfo = network_info()
    if bool(networkinfo):
        res.setResult(networkinfo, PTK_OKAY, "Success")
    else:
        res.setResult(networkinfo, PTK_INTERNALERROR, "No information")
    return res


def pdtreset():
    res = result()
    # Removing DHCP settings
    os.system("systemctl stop dhcpd.service")
    os.system("rm -f /etc/dhcpd/dhcpd.conf")
    os.system(">/var/lib/dhcpd/dhcpd.leases")
    os.system("rm -rf /mnt/system/pure_dir/pdt/settings.xml")
    os.system("rm -rf /mnt/system/uploads/bundle/*")
    # Removing configured device settings
    os.system("rm -rf /mnt/system/pure_dir/pdt/devices.xml*")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/jobs/*.xml")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/jobs/logs/*")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/jobs/status/*")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/jobs/dumps/*")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/targets/*")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/sreq/*")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/rollback/*.xml")
    os.system(
        "rm -rf /mnt/system/pure_dir/pdt/rollback/status/*.xml")

    # Clearing out global values
    reset_global_config()
    # Removing tftp files
    os.system("rm -rf /var/lib/tftpboot/*")
    # Removing eula agreement
    os.system("rm -rf /mnt/system/pure_dir/pdt/eula_agreement.xml")
    # Clearing out logs
    os.system(">/usr/local/apache2/logs/error_log")
    os.system(">/mnt/system/pure_dir/logs/pure_dir.log")
    res.setResult(True, PTK_OKAY, "Deletion of PDT configs successful")
    return res
