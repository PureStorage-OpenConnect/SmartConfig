#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :systemmanager.py
# description     :Service Information
# author          :Guruprasad
# version         :1.0
############################################################

import os
from datetime import datetime
import xml.etree.ElementTree as ET

from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_globals import reset_global_config
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_workflow_dir
from pure_dir.global_config import get_settings_file
from pure_dir.services.apps.pdt.core.emulate import check_if_emulated
info_file = "ula/pdt.txt"
build_file = "/mnt/system/pure_dir/pdt/build.xml"
upload_path = "/var/www/html/static/images/"
settings = get_settings_file()


def get_smartconfig_version():
    try:
        dom = ET.parse(build_file)
        version = dom.getroot().get('version')
        return version
    except BaseException:
        return "1.3"


def get_blade_rack_support(stack_type):
    if stack_type[-5:] == "-rack":
        stack_type = stack_type[:-5]

    blade_path = get_workflow_dir() + "/" + stack_type
    rack_path = get_workflow_dir() + "/" + stack_type + "-rack"

    ret = {'blade': False, 'rack': False}

    if os.path.isdir(blade_path):
        ret['blade'] = True

    if os.path.isdir(rack_path):
        ret['rack'] = True

    if stack_type == 'fa-fi6454-fc' or stack_type == 'fa-fi6454-iscsi':
        ret = {'blade': True, 'rack': True}

    return ret


def system_info():
    res = result()

    sysinfo = {
        'name': 'FlashStack&trade; | SmartConfig',
        'version': get_smartconfig_version(),
        'copyright': '&copy; 2019 Pure Storage Inc',
        'info': info_file
    }
    status, details = get_xml_element(settings, 'name')
    if status:
        system = details[0]
        sysinfo['name'] = system['name']
        sysinfo['copyright'] = system['copyright']
        if 'report_logo' in system:
            sysinfo['report_logo'] = system['report_logo']

    cmd = "systemctl status dhcpd"
    (error, output) = execute_local_command(cmd)
    if not error:
        if "running" in output:
            sysinfo['dhcp_status'] = "enabled"
        else:
            sysinfo['dhcp_status'] = "disabled"
    else:
        sysinfo['dhcp_status'] = "disabled"
    if check_if_emulated():
        if os.path.exists('/etc/dhcp/dhcpd.conf'):
            sysinfo['dhcp_status'] = "enabled"
        else:
            sysinfo['dhcp_status'] = "disabled"

    status, details = get_xml_element(settings, 'current_step')
    if status:
        sysinfo['deployment_settings'] = details[0]
        if 'subtype' in sysinfo['deployment_settings']:
            sysinfo['deployment_settings']['server_types'] = get_blade_rack_support(
                sysinfo['deployment_settings']['subtype'])
        else:
            sysinfo['deployment_settings']['server_types'] = {'rack': False, 'blade': False}
    if 'system' in sysinfo:
        if 'emulate' in sysinfo['system']:
            del sysinfo['system']['emulate']

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


def import_logo(uploadfile):
    res = result()

    status, details = get_xml_element(settings, 'name')
    if status:
        system = details[0]
        if 'report_logo' in system:
            os.system("rm -rf /var/www/html/static/images/" + system['report_logo'])

    cur_time = get_current_time(tmformat="%d%m%H%M")
    filename_with_time = "%s_%s.%s" % (uploadfile.filename.split(
        '.')[0], cur_time, uploadfile.filename.split('.')[1])

    if update_xml_element(settings, 'name', '', {'report_logo': filename_with_time}, 'system'):
        res.setResult(False, PTK_INTERNALERROR, "Failed to save settings")

    filepath = upload_path + filename_with_time
    save_file(uploadfile, filepath)
    res.setResult(filename_with_time, PTK_OKAY, "Success")
    return res


def save_file(uploadfile, filepath):
    with open(filepath, "ab") as f:
        f.write(uploadfile.stream.read())


def get_current_time(tmformat=""):
    dateTimeObj = datetime.now()
    tmfmt = "%d-%b-%Y-%H:%M:%S.%f" if tmformat == "" else tmformat
    timestampStr = dateTimeObj.strftime(tmfmt)
    return timestampStr


def pdtreset():
    res = result()

    status, details = get_xml_element(settings, 'name')
    if status:
        system = details[0]
        if 'report_logo' in system:
            os.system("rm -rf /var/www/html/static/images/" + system['report_logo'])

    # Removing DHCP settings
    os.system("systemctl stop dhcpd.service")
    os.system("rm -f /etc/dhcpd/dhcpd.conf")
    os.system(">/var/lib/dhcpd/dhcpd.leases")
    os.system("cp -rf /mnt/system/pure_dir/pdt/templates/settings.xml \
                      /mnt/system/pure_dir/pdt/")
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
    os.system("rm -rf /mnt/system/pure_dir/pdt/devices_reset.xml*")

    # Removing the Excel Report
    os.system(
        "rm -rf /var/www/html/static/downloads/SmartConfigReport.xlsx")

    # Removing the config backup folder
    os.system("rm -rf /mnt/system/pure_dir/pdt/configs")
    os.system(
        "rm -f /var/www/html/static/downloads/fs_configs.zip")

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
