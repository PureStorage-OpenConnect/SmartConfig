#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :discovery.py
# description     :DHCP based discovery for Flashstack components
# author          :VijayKumar
# version         :1.0
###################################################################

import os
import os.path
import requests
import time
import threading
import ipaddress
import string
import copy
from operator import itemgetter
from itertools import *
from itertools import chain
from isc_dhcp_leases import IscDhcpLeases
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.utils.images import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.storage.mds.mds import MDS
from pure_dir.components.compute.ucs.ucs import UCSManager
from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.services.apps.pdt.core.orchestration.orchestration_globals import *
from pure_dir.services.apps.pdt.core.systemmanager import *
from pure_dir.components.compute.ucs.ucs_upgrade import get_version
from pure_dir.components.network.nexus.nexus_setup import NEXUSSetup
from pure_dir.components.storage.mds.mds_setup import MDSSetup
from pure_dir.components.storage.purestorage.fa_setup import FASetup
from pure_dir.components.common import *
from pure_dir.infra.logging.logmanager import loginfo
from scapy.all import *
from filelock import FileLock
from xml.dom.minidom import parse, Document
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.global_config import get_settings_file, get_discovery_store

settings = get_settings_file()
dhcp_conf_template = "/mnt/system/pure_dir/pdt/templates/discovery/dhcpd.conf.template"
dhcp_conf_file = "/mnt/system/pure_dir/pdt/targets/dhcpd.conf"
dhcp_config = '/etc/dhcp/dhcpd.conf'
dhcp_lease_file = '/var/lib/dhcpd/dhcpd.leases'
old_dhcp_lease_file = '/var/lib/dhcpd/dhcpd.leases.old'
static_discovery_store = get_discovery_store()
static_discovery_store_lock = '/mnt/system/pure_dir/pdt/devices.xml.lock'
workflow_flag_file = '/mnt/system/pure_dir/pdt/workflow_flag.xml'

# Maximum time to wait for configuration of FS components
max_waittime_n9k = 900
max_waittime_n5k = 3600
max_waittime_mds = 1200
max_waittime_ucs = 900
max_waittime_fa = 600


def fsnetworkrange():
    nw_range = {}

    ip_list = IpValidator().get_ips_in_range()
    cur_ip = network_info()['ip']
    ip_list = [x for x in ip_list if str(x) != cur_ip]

    nw_range['subnet'] = str(ip_list[0])
    nw_range['start'] = str(ip_list[11])
    nw_range['end'] = str(ip_list[-2])
    dhcp_range = ip_list[11:32]
    nw_range['dhcp_start'] = str(dhcp_range[0])
    nw_range['dhcp_end'] = str(dhcp_range[-1])

    return nw_range


def fscomponents(mac, initStage):
    res = result()
    component_list = []
    unconfigured_list = []

    # Get the list of unconfigured FS Components from dhcpd.leases file
    sysinfo_output = system_info()
    if sysinfo_output.getStatus() == PTK_OKAY:
        sys_info = sysinfo_output.getResult()
        if sys_info['dhcp_status'] == 'enabled' and initStage == False:
            unconfigured_list = get_unconfigured_device_list()

    # Get the list of configured FS Components whose details are saved to
    # static_discovery_store xml file
    configured_list, mac_list = get_configured_device_list()

    if len(unconfigured_list) > 0:
        unconfigured_list = remove_duplicate_clients(
            unconfigured_list, mac_list)

    component_list = unconfigured_list + configured_list
    if len(component_list) == 0:
        res.setResult(component_list, PTK_OKAY,
                      _("PDT_NO_ACTIVE_COMPONENTS"))
        return res

    threading.Thread(target=fs_update_device_status, args=()).start()
    if mac:
        info_list = []
        mac_addrs = eval(mac)

        for mac_addr in mac_addrs:
            for component in component_list:
                if component['mac_address'].lower() == mac_addr.lower():
                    info_list.append(component)
        info_list = sorted(info_list, key=sort_by_device_type)
        res.setResult(info_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    else:
        component_list = sorted(component_list, key=sort_by_device_type)
        res.setResult(component_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


def sort_by_device_type(comp_list):
    if comp_list['device_type'] == "UCSM":
        return 0
    elif comp_list['device_type'] == "Nexus 9k":
        return 1
    elif comp_list['device_type'] == "Nexus 5k":
        return 2
    elif comp_list['device_type'] == "MDS":
        return 3
    elif comp_list['device_type'] == "PURE":
        return 4
    else:
        return 5


def freeip():
    res = result()
    free_ip_list = get_available_static_ips()
    res.setResult(free_ip_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def get_unconfigured_device_list():
    dhcp_clients = []

    if os.path.exists(dhcp_lease_file) is True:

        leases = IscDhcpLeases(dhcp_lease_file)
        active_leases = leases.get_current()

        for key, value in active_leases.items():
            client = {}
            identifiers = value.sets
            # TODO Need to get Serial from FlashArray
            if "-ct1" in value.hostname:
                pass
            elif "vendor-string" not in identifiers or "serial" not in identifiers:
                loginfo(
                    "Skipping dhcp client as vendor details and serial number are not available")
                loginfo(identifiers)
                continue
            client['mac_address'] = key.upper()
            client['ip_address'] = value.ip
            client['vendor_model'] = identifiers['vendor-string']
            # TODO Need to get Serial from FlashArray
            if identifiers.get('serial'):
                client['serial_number'] = identifiers['serial'][4:15]
            else:
                client['serial_number'] = "Unknown"
            if "N9K" in identifiers['vendor-string']:
                client['config_state'] = is_nexus(value.ip, "Unconfigured")
                client['device_type'] = "Nexus 9k"
            elif "N5K" in identifiers['vendor-string']:
                client['config_state'] = is_nexus(value.ip, "Unconfigured")
                client['device_type'] = "Nexus 5k"
            elif "MDS" in identifiers['vendor-string']:
                client['config_state'] = is_mds(value.ip, "Unconfigured")
                client['device_type'] = "MDS"
            elif "FlashArray" in identifiers['vendor-string']:
                client['config_state'], client['serial_number'] = is_pure(value.ip, "Unconfigured")
                client['device_type'] = "PURE"
            elif "UCS" in identifiers['vendor-string']:
                client['config_state'] = is_ucsm(value.ip, "Unconfigured")
                client['device_type'] = "UCSM"
                if client['config_state'] == 'Unknown':
                    continue
                if client['config_state'] == "Unconfigured":
                    status, data = get_xml_element(
                        static_discovery_store, "mac", client['mac_address'])
                    if status:
                        orig_ip_key = [
                            k for k in data[0].keys() if 'orig_ip' in k][0]
                        if data[0]['configured'] != "Configured" and data[0][orig_ip_key] != client['ip_address']:
                            loginfo(
                                "Updating the DHCP ip for the FI '%s' which is in Re-validate state" %
                                client['serial_number'])
                            update_xml_element(
                                static_discovery_store, "mac", client['mac_address'], {
                                    orig_ip_key: client['ip_address']})
            else:
                client['config_state'] = "Unknown"
                client['device_type'] = "Unknown"
            client['reachability'] = ""
            dhcp_clients.append(client)
        return dhcp_clients

    else:
        loginfo("Unable to read the leases file to get unconfigured list of devices")
        return dhcp_clients


def get_configured_device_list():
    static_list = []
    mac_list = []

    if os.path.exists(static_discovery_store) is True:

        doc = parse_xml(static_discovery_store)
        for subelement in doc.getElementsByTagName("device"):
            client = {}

            client['config_state'] = subelement.getAttribute("configured")
            client['device_type'] = subelement.getAttribute("device_type")
            client['mac_address'] = subelement.getAttribute("mac").upper()
            client['ip_address'] = subelement.getAttribute("ipaddress")
            client['serial_number'] = subelement.getAttribute("serial_no")
            client['vendor_model'] = subelement.getAttribute("model")
            client['reachability'] = subelement.getAttribute("reachability")
            if subelement.hasAttribute("reval_msg"):
                client['reval_msg'] = subelement.getAttribute("reval_msg")
            if subelement.hasAttribute("validated"):
                client['validated'] = True if subelement.getAttribute(
                    "validated") == "1" else False
            static_list.append(client)

            if client['config_state'] == "In-progress" or client['config_state'] == "Configured" or client[
                    'config_state'] == "Re-validate":
                if subelement.hasAttribute('image_version'):
                    client['image_version'] = subelement.getAttribute(
                        "image_version")

            if client['device_type'] == "UCSM" and subelement.getAttribute("infra_image") != "":
                client['infra_image'] = get_version(
                    subelement.getAttribute("infra_image"))

            mac_list.append(client['mac_address'])

        return static_list, mac_list

    else:
        loginfo("Unable to read the file to get configured list of devices")
        return static_list, mac_list


def check_configured_device_status(device_type, max_waittime, subelement):
    client = {}
    client['device_type'] = device_type
    if "Configured" in is_configured(subelement.getAttribute("ipaddress"), device_type):
        if "Nexus" in device_type:
            loginfo("Setting password for Nexus")
            obj = Nexus(subelement.getAttribute("ipaddress"), "admin", "admin")
            obj.change_password(decrypt(subelement.getAttribute("password")))
        elif "MDS" in device_type:
            loginfo("Setting password for MDS")
            obj = MDS(subelement.getAttribute("ipaddress"), "admin", "admin")
            obj.change_password(decrypt(subelement.getAttribute("password")))
        #elif "PURE" in device_type:
        #    loginfo("Setting password for FlashArray")
        #    obj = PureTasks(subelement.getAttribute("ipaddress"), "pureuser", "pureuser")
        #    obj.change_password("pureuser", "pureuser", decrypt(subelement.getAttribute("password")))
        client['config_state'] = "Configured"
        update_device_details(key="mac", key_value=subelement.getAttribute(
            "mac"), tag="configured", tag_value="Configured")
        conf_cleanup(device_type, subelement)
        remove_dhcp_lease(subelement.getAttribute("mac"))
        loginfo("Conf clean up done for %s" %
                subelement.getAttribute("ipaddress"))
    else:
        diff_seconds = int(time.time()) - \
            int(float(subelement.getAttribute("timestamp")))
        if diff_seconds > max_waittime:
            loginfo("There is some problem with the configuration of %s. Please check the console"
                    % subelement.getAttribute("ipaddress"))
            update_device_details(key="mac", key_value=subelement.getAttribute(
                "mac"), tag="configured", tag_value="Re-validate")
            update_device_details(key="mac", key_value=subelement.getAttribute(
                "mac"), tag="previous_state", tag_value="In-progress")
            update_device_details(
                key="mac",
                key_value=subelement.getAttribute("mac"),
                tag="reval_msg",
                tag_value="Configuration failed. Please retry the configuration")
            client['config_state'] = "Re-validate"
        else:
            client['config_state'] = subelement.getAttribute(
                "configured")
    """
    # Earlier case of identifying hardware factory reset done through console
    else:
        status, ipaddr = check_if_lease_exist(
                key="mac", value=subelement.getAttribute("mac"), ip_list=unconfigured_list)
        if status == True and "Unconfigured" in is_configured(subelement.getAttribute("ipaddress"), device_type):
            loginfo("Device %s seems to have gone into factory reset state"
                    % subelement.getAttribute("ipaddress"))
            update_device_details(key="mac", key_value=subelement.getAttribute(
                    "mac"), tag="configured", tag_value="Re-validate")
            update_device_details(key="mac", key_value=subelement.getAttribute(
                    "mac"), tag="previous_state", tag_value="Configured")
            update_device_details(key="mac", key_value=subelement.getAttribute(
                    "mac"), tag="reval_msg", tag_value="Device has gone into factory reset state")
            client['config_state'] = "Re-validate"
        else:
            client['config_state'] = "Configured"
    """
    return client


def fs_update_device_status():
    loginfo("fs status update thread started")
    if os.path.exists(static_discovery_store):
        doc = parse_xml(static_discovery_store)
        for subelement in doc.getElementsByTagName("device"):
            ip = subelement.getAttribute("ipaddress")
            loginfo("Checking reachability for %s" % ip)
            ipv = IpValidator()
            isUp = ipv.is_ip_up(ip)
            if isUp is True:
                status = "Up"
            else:
                status = "Down"
            update_device_details(
                key="ipaddress", key_value=ip, tag="reachability", tag_value=status)
            loginfo("Checking configuration status for %s" % ip)
            if "N9K" in subelement.getAttribute(
                    "model") and subelement.getAttribute("configured") == "In-progress":
                client = check_configured_device_status(
                    device_type="Nexus 9k", max_waittime=max_waittime_n9k, subelement=subelement)
                loginfo(client)

            elif "N5K" in subelement.getAttribute("model") and subelement.getAttribute("configured") == "In-progress":
                client = check_configured_device_status(
                    device_type="Nexus 5k", max_waittime=max_waittime_n5k, subelement=subelement)
                loginfo(client)

            elif "MDS" in subelement.getAttribute("model") and subelement.getAttribute("configured") == "In-progress":
                client = check_configured_device_status(
                    device_type="MDS", max_waittime=max_waittime_mds, subelement=subelement)
                loginfo(client)

            elif "FlashArray" in subelement.getAttribute("model") and subelement.getAttribute("configured") == "In-progress":
                client = check_configured_device_status(
                    device_type="PURE", max_waittime=max_waittime_fa, subelement=subelement)
                loginfo(client)

            elif "UCS" in subelement.getAttribute("model") and subelement.getAttribute("configured") == "In-progress" and subelement.getAttribute("infra_image") == "":
                client = check_configured_device_status(
                    device_type="UCSM", max_waittime=max_waittime_ucs, subelement=subelement)
                loginfo(client)
            loginfo("Configuration status for %s updated" % ip)

        loginfo("fs status update thread finished")
        return
    loginfo("fs status update thread finished")
    return


def dhcpenable(data):
    res = result()
    ret = []

    msg, status, arg = dhcpvalidate(data)
    if not status:
        res.setResult(arg, PTK_INTERNALERROR, msg)
        return res

    dhcp_conf = {}
    dhcp_conf['subnet'] = data['subnet']
    dhcp_conf['netmask'] = data['netmask']
    dhcp_conf['subnet_mask'] = data['netmask']
    dhcp_conf['gateway'] = data['gateway']
    dhcp_conf['start_ip'] = data['dhcp_start']
    dhcp_conf['end_ip'] = data['dhcp_end']
    dhcp_conf['server_ip'] = data['server_ip']
    dhcp_conf['dns_ip'] = data['server_ip']

    status = gen_from_template(dhcp_conf_template, dhcp_conf, dhcp_conf_file)

    retry = 0
    while retry < 2:
        retry += 1
        dhcp_status = check_dhcpserver_presence()
        if dhcp_status:
            res.setResult(ret, PTK_INTERNALERROR,
                          _("PDT_DHCP_ALREADY_EXISTS_ERR_MSG"))
            return res
    cmd = "cp %s %s" % (dhcp_conf_file, dhcp_config)
    execute_local_command(cmd)
    cmd = "systemctl start dhcpd"
    (error, output) = execute_local_command(cmd)
    if not error:
        if delete_xml_element(settings, 'dhcp_start', element_name='network') == False:
            res.setResult(ret, PTK_INTERNALERROR,
                          _("PDT_NETWORK_SETTINGS_SAVE_FAILED_ERR_MSG"))
        xml_data = dict((key, value) for key, value in data.iteritems() if key in [
            'dhcp_start', 'dhcp_end', 'start', 'end', 'subnet'])
        add_xml_element(settings, xml_data, element_name='network')
        res.setResult(ret, PTK_OKAY, _("PDT_DHCP_ENABLED_MSG"))
        return res
    cmd = "rm -rf %s" % dhcp_config
    (error, output) = execute_local_command(cmd)
    res.setResult(ret, PTK_INTERNALERROR,
                  _("PDT_DHCP_ENABLE_FAILED__ERR_MSG"))
    return res


def dhcpvalidate(data):
    ret = []
    ret = validate_input_data({'subnet': 'Subnet', 'netmask': 'Netmask', 'gateway': 'Gateway',
                               'dhcp_start': 'DHCP Start IP', 'dhcp_end': 'DHCP End IP',
                               'start': 'Start IP',
                               'end': 'End IP', 'server_ip': 'IP address'}, data)

    if len(ret) > 0:
        return "Please fill all mandatory fields.", False, ret

    ipv = IpValidator()
    if ipv.ip_range(data['dhcp_start'], data['netmask'], data['gateway']) == False or \
            ipv.ip_range(data['dhcp_end'], data['netmask'], data['gateway']) == False or \
            ipv.ip_range(data['start'], data['netmask'], data['gateway']) == False or \
            ipv.ip_range(data['end'], data['netmask'], data['gateway']) == False or \
            ipv.ip_range(data['subnet'], data['netmask'], data['gateway']) == False:
        return "Check the Network settings", False, ret

    if int(data['dhcp_start'].split('.')[3]) >= int(data['dhcp_end'].split('.')[3]):
        return "Check the DHCP range", False, ret

    if int(data['start'].split('.')[3]) >= int(data['end'].split('.')[3]):
        return "Check the Network range", False, ret

    return "Success", True, ret


def dhcpdisable():
    res = result()
    ret = []
    cmd = "systemctl stop dhcpd"
    (error, output) = execute_local_command(cmd)
    if not error:
        cmd = "rm -rf %s" % dhcp_config
        (error, output) = execute_local_command(cmd)
        res.setResult(ret, PTK_OKAY, _("PDT_DHCP_DISABLED_MSG"))
        return res
    res.setResult(ret, PTK_INTERNALERROR, _("PDT_FAILED_MSG"))
    return res


def dhcpinfo():
    res = result()
    dhcp_info = {}

    status, details = get_xml_element(settings, 'dhcp_start')
    if status:
        dhcp_info = details[0]
    else:
        dhcp_info = fsnetworkrange()

    nw_info = network_info()
    dhcp_info.update(nw_info)

    res.setResult(dhcp_info, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def adddevice(data):
    res = result()
    ret = []
    ret = validate_input_data({'ip': 'IP Address', 'username': 'Username',
                               'password': 'Password', 'type': 'Device type'}, data)

    if len(ret) > 0:
        res.setResult(ret, PTK_NOTEXIST, _(
            "PDT_MISSING_MANDATORY_FIELD_ERR_MSG"))
        return res

    if check_device_exists(data['ip'], "ipaddress") is True:
        res.setResult(ret, PTK_ALREADYEXIST,
                      _("PDT_DEVICE_ALREADY_EXIST_ERR_MSG"))
        return res

    ipv = IpValidator()
    if ipv.is_ip_up(data['ip']) is False:
        res.setResult(ret, PTK_NOTEXIST,
                      _("PDT_DEVICE_NOT_REACHABLE_ERR_MSG"))
        return res

    if data['type'] == "UCSM":
        status = is_ucsm(ip=data['ip'], mode="Configured",
                         username=data['username'], password=data['password'])
        if status == "Valid":
            try:
                exists = 0
                obj = UCSManager()
                details = obj.fabric_info(
                    ip=data['ip'], username=data['username'], password=data['password'])
                for detail in details:
                    if check_device_exists(detail['ip'], "ipaddress") is False:
                        save_device_details(
                            ipaddress=detail['ip'],
                            username=data['username'],
                            password=data['password'],
                            serial_no=detail['serial_no'],
                            mac=detail['mac_addr'].upper(),
                            model=detail['model'],
                            device_type=data['type'],
                            configured="Configured",
                            name=detail['name'],
                            leadership=detail['leadership'],
                            vipaddress=detail['vipaddress'],
                            reachability="Up")
                        exists = 1

                if exists == 0:
                    res.setResult(ret, PTK_ALREADYEXIST,
                                  _("PDT_DEVICE_ALREADY_EXIST_ERR_MSG"))
                    return res

                res.setResult(ret, PTK_OKAY, _("PDT_DEVICE_ADDED_MSG"))
                return res
            except BaseException:
                res.setResult(ret, PTK_NOTEXIST,
                              _("PDT_CONFIRM_SSH_CREDENTIALS_MSG"))
                return res

    elif data['type'] == "PURE":
        status, serial = is_pure(data['ip'], "Configured")
        if status == 'Configured':
            try:
                pure_tasks = PureTasks(
                    data['ip'], username=data['username'], password=data['password'])
                details = pure_tasks.flash_array_info(data['ip'])
                pure_tasks.release_pure_handle()
            except BaseException:
                res.setResult(ret, PTK_NOTEXIST,
                              _("PDT_CONFIRM_SSH_CREDENTIALS_MSG"))
                return res

    elif data['type'] == "NEXUS":
        status = is_nexus(ip=data['ip'], mode="Configured",
                          username=data['username'], password=data['password'])
        if status == "Configured":
            try:
                switch_enable_nxapi(
                    data['ip'], username=data['username'], password=data['password'])
                obj = Nexus(
                    ipaddress=data['ip'], username=data['username'], password=data['password'])
                details = obj.nexus_switch_info()
            except BaseException:
                res.setResult(ret, PTK_NOTEXIST,
                              _("PDT_CONFIRM_SSH_CREDENTIALS_MSG"))
                return res

    elif data['type'] == "MDS":
        status = is_mds(ip=data['ip'], mode="Configured",
                        username=data['username'], password=data['password'])
        if status == "Valid":
            try:
                switch_enable_nxapi(
                    data['ip'], username=data['username'], password=data['password'])
                obj = MDS(
                    ipaddr=data['ip'], uname=data['username'], passwd=data['password'])
                details = obj.mds_switch_info()
            except BaseException:
                res.setResult(ret, PTK_NOTEXIST,
                              _("PDT_CONFIRM_SSH_CREDENTIALS_MSG"))
                return res

    else:
        res.setResult(ret, PTK_NOTEXIST,
                      _("PDT_INVALID_DEVICE_TYPE_MSG"))
        return res

    if status == "Unknown":
        res.setResult(ret, PTK_NOTEXIST, _("PDT_INVALID_DEVICE_MSG"))
        return res

    elif status == "Failed":
        res.setResult(ret, PTK_NOTEXIST,
                      _("PDT_CONFIRM_SSH_CREDENTIALS_MSG"))
        return res

    save_device_details(
        ipaddress=data['ip'],
        username=data['username'],
        password=data['password'],
        serial_no=details['serial_no'],
        mac=details['mac_addr'].upper(),
        model=details['model'],
        device_type=data['type'],
        configured="Configured",
        name=details['name'],
        reachability="Up")
    res.setResult(ret, PTK_OKAY, _("PDT_DEVICE_ADDED_MSG"))
    return res


def initialconfig():
    if os.path.exists(static_discovery_store) is True:
        doc = parse_xml(static_discovery_store)
        ucsm_set = False
        loginfo("Started initial configuration")
        for subelement in doc.getElementsByTagName("device"):
            if subelement.hasAttribute("validated") and subelement.getAttribute("validated") == "1":
                if subelement.getAttribute("device_type") == "Nexus 9k":
                    obj = NEXUSSetup()
                    data = {"switch_name": subelement.getAttribute("name"),
                            "switch_mac": subelement.getAttribute("mac"),
                            "switch_serial_no": subelement.getAttribute("serial_no"),
                            "switch_vendor": subelement.getAttribute("model"),
                            "ntp_server": subelement.getAttribute("ntp_server"),
                            "switch_gateway": subelement.getAttribute("gateway"),
                            "switch_ip": subelement.getAttribute("ipaddress"),
                            "switch_netmask": subelement.getAttribute("netmask"),
                            "switch_image": subelement.getAttribute("switch_image"),
                            "domain_name": subelement.getAttribute("domain_name")}
                    loginfo("Triggering Nexus 9k Configure api")
                    loginfo(data)
                    threading.Thread(
                        target=obj.nexus9kconfigure, args=(data,)).start()
                elif subelement.getAttribute("device_type") == "Nexus 5k":
                    obj = NEXUSSetup()
                    data = {
                        "switch_name": subelement.getAttribute("name"),
                        "switch_mac": subelement.getAttribute("mac"),
                        "switch_serial_no": subelement.getAttribute("serial_no"),
                        "switch_vendor": subelement.getAttribute("model"),
                        "ntp_server": subelement.getAttribute("ntp_server"),
                        "switch_gateway": subelement.getAttribute("gateway"),
                        "switch_ip": subelement.getAttribute("ipaddress"),
                        "switch_netmask": subelement.getAttribute("netmask"),
                        "switch_kickstart_image": subelement.getAttribute("switch_kickstart_image"),
                        "switch_system_image": subelement.getAttribute("switch_system_image"),
                        "domain_name": subelement.getAttribute("domain_name")}
                    loginfo("Triggering Nexus 5k Configure api")
                    loginfo(data)
                    threading.Thread(
                        target=obj.nexus5kconfigure, args=(data,)).start()
                elif subelement.getAttribute("device_type") == "MDS":
                    obj = MDSSetup()
                    data = {
                        "switch_name": subelement.getAttribute("name"),
                        "switch_mac": subelement.getAttribute("mac"),
                        "switch_serial_no": subelement.getAttribute("serial_no"),
                        "switch_vendor": subelement.getAttribute("model"),
                        "ntp_server": subelement.getAttribute("ntp_server"),
                        "switch_gateway": subelement.getAttribute("gateway"),
                        "switch_ip": subelement.getAttribute("ipaddress"),
                        "switch_netmask": subelement.getAttribute("netmask"),
                        "switch_kickstart_image": subelement.getAttribute("switch_kickstart_image"),
                        "switch_system_image": subelement.getAttribute("switch_system_image"),
                        "domain_name": subelement.getAttribute("domain_name")}
                    loginfo("Triggering MDSConfigure api")
                    loginfo(data)
                    threading.Thread(target=obj.mdsconfigure,
                                     args=(data,)).start()
                elif subelement.getAttribute("device_type") == "PURE":
                    obj = FASetup()
                    data = {
                        "model": subelement.getAttribute("model"),
                        "mac": subelement.getAttribute("mac"),
                        "serial_number": subelement.getAttribute("serial_no"),
                        "orig_ip": subelement.getAttribute("orig_ip"),
                        "array_name": subelement.getAttribute("name"),
                        "ct0_ip": subelement.getAttribute("ct0_ip"),
                        "ct1_ip": subelement.getAttribute("ct1_ip"),
                        "vir0_ip": subelement.getAttribute("vir0_ip"),
                        "netmask": subelement.getAttribute("netmask"),
                        "gateway": subelement.getAttribute("gateway"),
                        "ntp_server": subelement.getAttribute("ntp_server"),
                        "dns": subelement.getAttribute("dns"),
                        "domain_name": subelement.getAttribute("domain_name"),
                        "timezone": subelement.getAttribute("timezone"),
                        "relay_host": subelement.getAttribute("relay_host"),
                        "alert_emails": subelement.getAttribute("alert_emails"),
                        "sender_domain": subelement.getAttribute("sender_domain"),
                        "organization": subelement.getAttribute("organization"),
                        "full_name": subelement.getAttribute("full_name"),
                        "job_title": subelement.getAttribute("job_title")}
                    loginfo("Triggering FAConfigure api")
                    loginfo(data)
                    threading.Thread(target=obj.faconfigure,
                                     args=(data,)).start()
                elif subelement.getAttribute("device_type") == "UCSM" and not ucsm_set:
                    ucsm_set = True
                    obj = UCSManager()
                    for element in doc.getElementsByTagName("device"):
                        if element.hasAttribute("validated") and element.getAttribute(
                                "validated") == "1" and element.getAttribute("leadership") == "subordinate":
                            subordinate_data = element
                        if element.hasAttribute("validated") and element.getAttribute(
                                "validated") == "1" and element.getAttribute("leadership") == "primary":
                            primary_data = element
                    data = {"pri_switch_mac": primary_data.getAttribute("mac"),
                            "pri_switch_serial_no": primary_data.getAttribute("serial_no"),
                            "pri_switch_vendor": primary_data.getAttribute("model"),
                            "pri_setup_mode": primary_data.getAttribute("pri_setup_mode"),
                            "pri_cluster": primary_data.getAttribute("pri_cluster"),
                            "pri_id": primary_data.getAttribute("pri_id"),
                            "ipformat": primary_data.getAttribute("ipformat"),
                            "pri_name": primary_data.getAttribute("name"),
                            "pri_passwd": decrypt(primary_data.getAttribute("password")),
                            "pri_ip": primary_data.getAttribute("ipaddress"),
                            "pri_orig_ip": primary_data.getAttribute("pri_orig_ip"),
                            "netmask": primary_data.getAttribute("netmask"),
                            "gateway": primary_data.getAttribute("gateway"),
                            "ntp_server": subelement.getAttribute("ntp_server"),
                            "virtual_ip": primary_data.getAttribute("vipaddress"),
                            "dns": primary_data.getAttribute("dns"),
                            "domain_name": primary_data.getAttribute("domain_name"),
                            "sec_switch_mac": subordinate_data.getAttribute("mac"),
                            "sec_switch_serial_no": subordinate_data.getAttribute("serial_no"),
                            "sec_switch_vendor": subordinate_data.getAttribute("model"),
                            "sec_cluster": subordinate_data.getAttribute("sec_cluster"),
                            "os_install": primary_data.getAttribute("os_install"),
                            "esxi_file": primary_data.getAttribute("esxi_file"),
                            "sec_orig_ip": subordinate_data.getAttribute("sec_orig_ip"),
                            "sec_ip": subordinate_data.getAttribute("ipaddress"),
                            "sec_id": subordinate_data.getAttribute("sec_id"),
                            "conf_passwd": decrypt(primary_data.getAttribute("password")),
                            "ucs_upgrade": subordinate_data.getAttribute("ucs_upgrade"),
                            "infra_image": subordinate_data.getAttribute("infra_image")}
                    loginfo("Triggering UCSMFIConfigure api")
                    loginfo({key:value for key, value in data.items() if key not in ["pri_passwd", "conf_passwd"]})
                    #loginfo({key:data[key] for key in data.keys() if key not in ["pri_passwd", "conf_passwd"]})
                    threading.Thread(target=obj.ucsmficonfigure,
                                     args=("cluster", data)).start()
        loginfo("Completed triggering all the apis")

    obj = result()
    obj.setResult([], PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def delete_pwd_in_logs(data):
    if 'conf_passwd' in data and 'pri_passwd' in data:
        del data['conf_passwd']
        del data['pri_passwd']
        loginfo(data)


def save_config(stacktype, datas):

    # Saving the global values
    loginfo("Saving the global values")
    try:
        for config in copy.deepcopy(datas):
            details = eval(datas[config])
            if isinstance(details, list):
                for data in details:
                    delete_pwd_in_logs(data)
            elif isinstance(details, dict):
                delete_pwd_in_logs(details)
    except BaseException:
        loginfo("Error in logging the global values")
    obj = result()
    for config in datas:
        if config == "nexus_9k" or config == "nexus_5k":
            details = eval(datas[config])
            for data in details:
                ret = set_globals_api(stacktype,
                                      {"nexus_switch_" + data['tag'].lower(): data['switch_mac'],
                                       "netmask": data['switch_netmask'],
                                          "gateway": data['switch_gateway'],
                                          "ntp": data['ntp_server']})
                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj
        elif config == "mds":
            details = eval(datas[config])
            for data in details:
                ret = set_globals_api(stacktype,
                                      {"mds_switch_" + data['tag'].lower(): data['switch_mac'],
                                       "netmask": data['switch_netmask'],
                                          "gateway": data['switch_gateway'],
                                          "ntp": data['ntp_server']})
                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj

        elif config == "pure":
            details = eval(datas[config])
            for data in details:
                ret = set_globals_api(stacktype,
                                      {"pure_id": data['mac'],
                                       "netmask": data['netmask'],
                                          "gateway": data['gateway'],
                                          "ntp": data['ntp_server']})
                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj

        elif config == "ucsm":
            data = eval(datas[config])
            if 'pri_cluster' in data:
                create_wfflag(data['os_install'])
                if data['blade_image'] == "":
                    if data['esxi_file'] != "":
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                               "netmask": data['netmask'],
                                                  "gateway": data['gateway'],
                                                  "ntp": data['ntp_server'],
                                                  "remote_file": data['esxi_file'],
                                                  "upgrade": "No"})
                    else:
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                               "netmask": data['netmask'],
                                                  "gateway": data['gateway'],
                                                  "ntp": data['ntp_server'],
                                                  "upgrade": "No"})

                else:
                    if data['esxi_file'] != "":
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                               "netmask": data['netmask'],
                                                  "gateway": data['gateway'],
                                                  "ntp": data['ntp_server'],
                                                  "remote_file": data['esxi_file'],
                                                  "firmware": data['blade_image'],
                                                  "upgrade": "Yes"})
                    else:
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                               "netmask": data['netmask'],
                                                  "gateway": data['gateway'],
                                                  "ntp": data['ntp_server'],
                                                  "firmware": data['blade_image'],
                                                  "upgrade": "Yes"})

                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj
            if 'sec_cluster' in data:
                ret = set_globals_api(
                    stacktype, {"ucs_switch_b": data['sec_switch_mac']})
                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj

    # Removing the validated attribute from all devices.
    loginfo("Removing the validated attribute for all devices")
    if os.path.exists(static_discovery_store) is True:
        doc = parse_xml(static_discovery_store)
        for subelement in doc.getElementsByTagName("device"):
            if subelement.hasAttribute("validated"):
                subelement.removeAttribute("validated")
        lock = FileLock(static_discovery_store + ".lock")
        with lock.acquire(timeout=-1):
            o = open(static_discovery_store, "w")
            o.write(pretty_print(doc.toprettyxml(indent="")))
            o.close()
            doc.unlink()

    # Saving the configuration
    loginfo("Saving the configuration")
    for config in datas:

        if config == "nexus_9k":
            obj = NEXUSSetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['switch_mac'], "mac"):
                    delete_xml_element(static_discovery_store,
                                       "mac", data['switch_mac'])
                obj._save_nexus_9k_details(
                    ipaddress=data['switch_ip'],
                    netmask=data['switch_netmask'],
                    gateway=data['switch_gateway'],
                    ntp_server=data['ntp_server'],
                    username="admin",
                    password=encrypt(
                        data['pri_passwd']),
                    serial_no=data['switch_serial_no'],
                    mac=data['switch_mac'],
                    model=data['switch_vendor'],
                    device_type="Nexus 9k",
                    image_version=re.search(
                        'nxos.(.+?).bin',
                        data['switch_image']).group(1),
                    switch_image=data['switch_image'],
                    configured="Unconfigured",
                    name=data['switch_name'],
                    tag=data['tag'],
                    reachability="",
                    validated="1",
                    domain_name=data['domain_name'])

        elif config == "nexus_5k":
            obj = NEXUSSetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['switch_mac'], "mac"):
                    delete_xml_element(static_discovery_store,
                                       "mac", data['switch_mac'])
                obj._save_nexus_5k_details(
                    ipaddress=data['switch_ip'],
                    netmask=data['switch_netmask'],
                    gateway=data['switch_gateway'],
                    ntp_server=data['ntp_server'],
                    username="admin",
                    password=encrypt(
                        data['pri_passwd']),
                    serial_no=data['switch_serial_no'],
                    mac=data['switch_mac'],
                    model=data['switch_vendor'],
                    device_type="Nexus 5k",
                    image_version=re.search(
                        'n5000-uk9.(.+?).bin',
                        data['switch_system_image']).group(1),
                    switch_kickstart_image=data['switch_kickstart_image'],
                    switch_system_image=data['switch_system_image'],
                    configured="Unconfigured",
                    name=data['switch_name'],
                    tag=data['tag'],
                    reachability="",
                    validated="1",
                    domain_name=data['domain_name'])

        elif config == "mds":
            obj = MDSSetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['switch_mac'], "mac"):
                    delete_xml_element(static_discovery_store,
                                       "mac", data['switch_mac'])
                obj._save_mds_details(
                    ipaddress=data['switch_ip'],
                    netmask=data['switch_netmask'],
                    gateway=data['switch_gateway'],
                    ntp_server=data['ntp_server'],
                    username="admin",
                    password=encrypt(
                        data['pri_passwd']),
                    serial_no=data['switch_serial_no'],
                    mac=data['switch_mac'],
                    model=data['switch_vendor'],
                    device_type="MDS",
                    image_version=re.search(
                        'mz.(.*).bin',
                        data['switch_kickstart_image']).group(1),
                    switch_kickstart_image=data['switch_kickstart_image'],
                    switch_system_image=data['switch_system_image'],
                    tag=data['tag'],
                    configured="Unconfigured",
                    name=data['switch_name'],
                    reachability="",
                    validated="1",
                    domain_name=data['domain_name'])

        elif config == "pure":
            obj = FASetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['mac'], "mac"):
                    delete_xml_element(static_discovery_store,
                                       "mac", data['mac'])
                if data['domain_name'] == "":
                    domain_name = "purestorage.com"
                else:
                    domain_name = data['domain_name']
                device_data = {
                    "name": data['array_name'],
		    "username": "pureuser",
                    "password": encrypt('pureuser'),
                    "ct0_ip": data['ct0_ip'],
                    "ct1_ip": data['ct1_ip'],
                    "vir0_ip": data['vir0_ip'],
                    "ipaddress": data['vir0_ip'],
                    "orig_ip": data['orig_ip'],
                    "serial_no": data['serial_number'],
                    "mac": data['mac'],
                    "netmask": data['netmask'],
                    "gateway": data['gateway'],
                    "dns": data['dns'],
                    "domain_name": domain_name,
                    "relay_host": data['relay_host'],
                    "sender_domain": data['sender_domain'],
                    "alert_emails": data['alert_emails'],
                    "ntp_server": data['ntp_server'],
                    "timezone": data['timezone'],
                    "organization": data['organization'],
                    "full_name": data['full_name'],
                    "job_title": data['job_title'],
                    "model": data['model'],
                    "tag": "",
                    "device_type": "PURE",
                    "configured": "Unconfigured",
                    "reachability": "",
                    "validated": "1",
		    "isZTP":"1",
                    "timestamp": str(time.time())}
                add_xml_element(static_discovery_store, device_data)

        elif config == "ucsm":
            obj = UCSManager()
            data = eval(datas[config])
            if 'pri_cluster' in data:
                if check_device_exists(data['pri_switch_mac'], "mac"):
                    delete_xml_element(static_discovery_store,
                                       "mac", data['pri_switch_mac'])
                if data['esxi_file'] != "":
                    bundl_status = iso_binding(
                        data['esxi_file'], data['esxi_kickstart'])
                    if not bundl_status:
                        loginfo("Failed to bundle esx iso and kickstart.")
                        res = result()
                        ret = []
                        ret.append({'field': 'esxi_kickstart',
                                    'msg': 'Unable to bind ESXi kickstart file with ESXi image'})
                        res.setResult(ret, PTK_INTERNALERROR,
                                      "ESXi kickstart file binding failed")
                        return res

                obj._save_ucsm_primary_details(
                    ipaddress=data['pri_ip'],
                    username="admin",
                    password=encrypt(
                        data['pri_passwd']),
                    serial_no=data['pri_switch_serial_no'],
                    mac=data['pri_switch_mac'],
                    model=data['pri_switch_vendor'],
                    device_type="UCSM",
                    configured="Unconfigured",
                    name=data['pri_name'] + "-A",
                    vipaddress=data['virtual_ip'],
                    leadership="primary",
                    reachability="",
                    dns=data['dns'],
                    domain_name=data['domain_name'],
                    gateway=data['gateway'],
                    ntp_server=data['ntp_server'],
                    ipformat=data['ipformat'],
                    netmask=data['netmask'],
                    pri_cluster=data['pri_cluster'],
                    pri_id=data['pri_id'],
                    tag="A",
                    pri_orig_ip=data['pri_orig_ip'],
                    pri_setup_mode=data['pri_setup_mode'],
                    validated="1",
                    esxi_file=data['esxi_file'],
                    esxi_kickstart=data['esxi_kickstart'],
                    os_install=data['os_install'],
                    infra_image=data['infra_image'],
                    blade_image=data['blade_image'],
                    ucs_upgrade=data['ucs_upgrade'],
                    server_type=data['server_type'])
            if 'sec_cluster' in data:
                if check_device_exists(data['sec_switch_mac'], "mac"):
                    delete_xml_element(static_discovery_store,
                                       "mac", data['sec_switch_mac'])
                obj._save_ucsm_subordinate_details(
                    ipaddress=data['sec_ip'],
                    username="admin",
                    password=encrypt(
                        data['pri_passwd']),
                    pri_ip=data['pri_ip'],
                    serial_no=data['sec_switch_serial_no'],
                    mac=data['sec_switch_mac'],
                    model=data['sec_switch_vendor'],
                    device_type="UCSM",
                    configured="Unconfigured",
                    name=data['pri_name'] + "-B",
                    vipaddress=data['virtual_ip'],
                    gateway=data['gateway'],
                    ntp_server=data['ntp_server'],
                    netmask=data['netmask'],
                    leadership="subordinate",
                    reachability="",
                    sec_cluster=data['sec_cluster'],
                    sec_id=data['sec_id'],
                    tag="B",
                    infra_image=data['infra_image'],
                    blade_image=data['blade_image'],
                    ucs_upgrade=data['ucs_upgrade'],
                    sec_orig_ip=data['sec_orig_ip'],
                    server_type=data['server_type'],
                    validated="1")

            if data['server_type'] == "Rack":
                status, details = get_xml_element(settings, "stacktype")
                if status and 'fi6454' in details[0]['subtype']:
                    rack_servertype = details[0]['subtype']
                    if 'rack' not in details[0]['subtype']:
                        rack_servertype = details[0]['subtype'] + '-rack'
                    deployment_settings({'subtype': rack_servertype})
                else:
                    rack_servertype = details[0]['stacktype'] + "-rack"
                    deployment_settings({'subtype': rack_servertype})
            elif data['server_type'] == "Blade":
                status, details = get_xml_element(settings, "stacktype")
                if status and 'figen2' not in details[0]['subtype'] and 'fi6332' not in details[
                        0]['subtype'] and 'fi6454' not in details[0]['subtype']:
                    deployment_settings({'subtype': details[0]['stacktype']})

    obj = result()
    obj.setResult([], PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def update_config(stacktype, datas):
    obj = result()
    # Updating the global values
    loginfo("Updating the global values")
    try:
        for config in copy.deepcopy(datas):
            details = eval(datas[config])
            if isinstance(details, list):
                for data in details:
                    delete_pwd_in_logs(data)
            elif isinstance(details, dict):
                delete_pwd_in_logs(details)
    except BaseException:
        loginfo("Error in logging the global values")

    for config in datas:
        if config == "ucsm":
            data = eval(datas[config])
            if 'pri_cluster' in data:
                if data['blade_image'] == "":
                    if data['esxi_file'] != "":
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                               "remote_file": data['esxi_file'],
                                                  "upgrade": "No"})
                    else:
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                                  "upgrade": "No"})

                else:
                    if data['esxi_file'] != "":
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                               "remote_file": data['esxi_file'],
                                                  "upgrade": "Yes",
                                                  "firmware": data['blade_image']})
                    else:
                        ret = set_globals_api(stacktype,
                                              {"ucs_switch_a": data['pri_switch_mac'],
                                                  "upgrade": "Yes",
                                                  "firmware": data['blade_image']})

                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj
            if 'sec_cluster' in data:
                ret = set_globals_api(
                    stacktype, {"ucs_switch_b": data['sec_switch_mac']})
                if ret.getStatus() != PTK_OKAY:
                    obj.setResult([], PTK_INTERNALERROR,
                                  _("PDT_FAILED_TO_SET_REQUESTED_SETTINGS_MSG"))
                    return obj

    # Updating the configuration
    loginfo("Updating the configuration")
    for config in datas:

        if config == "nexus_9k":
            obj = NEXUSSetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['switch_mac'], "mac"):
                    data_to_update = {
                        "name": data['switch_name'],
                        "ipaddress": data['switch_ip'],
                        "password": encrypt(
                            data['pri_passwd']),
                        "image_version": re.search(
                            'nxos.(.+?).bin',
                            data['switch_image']).group(1),
                        "switch_image": data['switch_image'],
                        "configured": "Unconfigured"}
                    update_xml_element(static_discovery_store,
                                       "mac", data['switch_mac'], data_to_update)

        elif config == "nexus_5k":
            obj = NEXUSSetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['switch_mac'], "mac"):
                    data_to_update = {
                        "name": data['switch_name'],
                        "ipaddress": data['switch_ip'],
                        "password": encrypt(
                            data['pri_passwd']),
                        "switch_kickstart_image": data['switch_kickstart_image'],
                        "switch_system_image": data['switch_system_image'],
                        "image_version": re.search(
                            'n5000-uk9.(.+?).bin',
                            data['switch_system_image']).group(1),
                        "configured": "Unconfigured"}
                    update_xml_element(static_discovery_store,
                                       "mac", data['switch_mac'], data_to_update)

        elif config == "pure":
            obj = FASetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['mac'], "mac"):
                    data_to_update = {
                        "name": data['array_name'],
                        "ct0_ip": data['ct0_ip'],
                        "ct1_ip": data['ct1_ip'],
                        "vir0_ip": data['vir0_ip'],
                        "relay_host": data['relay_host'],
                        "sender_domain": data['sender_domain'],
                        "alert_emails": data['alert_emails'],
                        "timezone": data['timezone'],
                        "organization": data['organization'],
                        "full_name": data['full_name'],
                        "job_title": data['job_title'],
                        "configured": "Unconfigured"}
                update_xml_element(static_discovery_store,
                                   "mac", data['mac'], data_to_update)

        elif config == "mds":
            obj = MDSSetup()
            details = eval(datas[config])
            for data in details:
                if check_device_exists(data['switch_mac'], "mac"):
                    data_to_update = {
                        "name": data['switch_name'],
                        "ipaddress": data['switch_ip'],
                        "password": encrypt(
                            data['pri_passwd']),
                        "image_version": re.search(
                            'mz.(.*).bin',
                            data['switch_kickstart_image']).group(1),
                        "switch_kickstart_image": data['switch_kickstart_image'],
                        "switch_system_image": data['switch_system_image'],
                        "configured": "Unconfigured"}
                    update_xml_element(static_discovery_store,
                                       "mac", data['switch_mac'], data_to_update)

        elif config == "ucsm":
            obj = UCSManager()
            data = eval(datas[config])
            if 'pri_cluster' in data:
                if check_device_exists(data['pri_switch_mac'], "mac"):
                    data_to_update = {
                        "ipaddress": data['pri_ip'],
                        "password": encrypt(
                            data['pri_passwd']),
                        "name": data['pri_name'] + "-A",
                        "vipaddress": data['virtual_ip'],
                        "dns": data['dns'],
                        "domain_name": data['domain_name'],
                        "os_install": data['os_install'],
                        "esxi_file": data['esxi_file'],
                        "infra_image": data['infra_image'],
                        "blade_image": data['blade_image'],
                        "ucs_upgrade": data['ucs_upgrade'],
                        "server_type": data['server_type'],
                        "configured": "Unconfigured"}
                    update_xml_element(
                        static_discovery_store, "mac", data['pri_switch_mac'], data_to_update)
            if 'sec_cluster' in data:
                if check_device_exists(data['sec_switch_mac'], "mac"):
                    data_to_update = {"ipaddress": data['sec_ip'], "name": data['pri_name'] +
                                      "-B", "configured": "Unconfigured",
                                      "pri_ip": data['pri_ip'], "server_type": data['server_type']}
                    update_xml_element(
                        static_discovery_store, "mac", data['sec_switch_mac'], data_to_update)

            if data['server_type'] == "Rack":
                status, details = get_xml_element(settings, "stacktype")
                if status and 'fi6454' in details[0]['subtype']:
                    rack_servertype = details[0]['subtype']
                    if 'rack' not in details[0]['subtype']:
                        rack_servertype = details[0]['subtype'] + '-rack'
                    deployment_settings({'subtype': rack_servertype})
                else:
                    rack_servertype = details[0]['stacktype'] + "-rack"
                    deployment_settings({'subtype': rack_servertype})
            elif data['server_type'] == "Blade":
                status, details = get_xml_element(settings, "stacktype")
                if status and 'figen2' not in details[0]['subtype'] and 'fi6332' not in details[
                        0]['subtype'] and 'fi6454' not in details[0]['subtype']:
                    deployment_settings({'subtype': details[0]['stacktype']})

    obj = result()
    obj.setResult([], PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def clearconfig():
    res = result()
    status = delete_xml_element(
        static_discovery_store, matching_key='configured', matching_value='Unconfigured')
    if status:
        res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    else:
        res.setResult(False, PTK_INTERNALERROR, _("PDT_FAILED_MSG"))
    return res


def deletedevice(mac_list):
    res = result()
    mac_list = filter(None, mac_list)
    if len(mac_list) == 0:
        loginfo("Pass atleast one mac-address")
        res.setResult([], PTK_PRECHECKFAILURE, "Pass atleast one mac-address")
        return res

    del_list = []
    for mac in mac_list:
        ret = delete_xml_element(static_discovery_store, "mac", mac)
        if ret:
            del_list.append(mac)

    if len(del_list) == len(mac_list):
        res.setResult([], PTK_OKAY, _("PDT_DEVICE_DELETED_MSG"))
    else:
        undel_list = [x for x in mac_list if x not in del_list]
        res.setResult(undel_list, PTK_INTERNALERROR,
                      _("PDT_DEVICE_DELETETION_FAILED_MSG"))
    return res


def figenvalidate(filist, stacktype):
    res = result()
    if len(filist) != 2:
        loginfo("FI count should be 2")
        res.setResult(stacktype, PTK_INTERNALERROR, _("PDT_UNSUPPORTED_FI_COUNT_ERR_MSG"))
        return res

    if "FI-6332" in filist[0] and "FI-6332" in filist[1]:
        # direct connect has support for 6332 and 6324(min), identify subtype
        if stacktype == "fa-n9k-ucsmini-fc":
            stacktype = 'fa-fi6332-fc'
            deployment_settings({'subtype': stacktype})
        elif stacktype == "fa-n5k-ucsmini-iscsi":
            stacktype = 'fa-fi6332-iscsi'
            deployment_settings({'subtype': stacktype})
        loginfo("Setting stacktype to %s" % stacktype)
        res.setResult(stacktype, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    if "FI-62" in filist[0] and "FI-62" in filist[1] and "n5k" in stacktype:
        loginfo("Gen 2 FI detected")
        if "fc" in stacktype:
            stacktype = "fa-n5k-figen2-fc"
        else:
            stacktype = "fa-n5k-figen2-iscsi"
        loginfo("Setting stacktype to %s" % stacktype)
        deployment_settings({'subtype': stacktype})
        res.setResult(stacktype, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    elif "FI-63" in filist[0] and "FI-63" in filist[1]:
        res.setResult(stacktype, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    elif "FI-M-6324" in filist[0] and "FI-M-6324" in filist[1]:
        res.setResult(stacktype, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    elif "FI-6454" in filist[0] and "FI-6454" in filist[1]:
        if stacktype == "fa-n9k-fi-mds-fc":
            stacktype = 'fa-n9k-fi6454-mds-fc'
        elif stacktype == "fa-n9k-fi-iscsi":
            stacktype = 'fa-n9k-fi6454-iscsi'
        elif stacktype == "fa-fi6332-mds-fc":
            stacktype = 'fa-fi6454-mds-fc'
        loginfo("Setting stacktype to %s" % stacktype)
        deployment_settings({'subtype': stacktype})
        res.setResult(stacktype, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    res.setResult(stacktype, PTK_INTERNALERROR,
                  _("PDT_UNSUPPORTED_FI_TYPE_ERR_MSG"))
    return res


def configdefaults(data):
    res = result()
    conf_defaults = []
    for key, value in data.items():
        count = len(value)
        status, conf_hw_list = get_xml_element(
            static_discovery_store, 'device_type', key)
        if not status:
            conf_hw_cnt = 0
            conf_hw_list = []
        else:
            conf_hw_cnt = len(conf_hw_list)

        if key == "UCSM":
            conf_ucs_list = [
                x for x in conf_hw_list if x['device_type'] == "UCSM"]
            ucs_populate_lst = get_ucs_configdefaults(
                count, value, conf_ucs_list)
            conf_defaults.extend(ucs_populate_lst)

        elif key == "PURE":
            for item in value:
                hw_dict = get_fa_configdefaults(item)
                conf_defaults.append(hw_dict)

        else:
            new_hw_index = conf_hw_cnt
            for item in value:
                hw_dict = {}
                hw_dict['device_type'] = key
                hw_dict['switch_mac'] = item
                hw_dict['switch_name'] = key.split('_')[0].lower() + "-" + \
                    string.ascii_lowercase[new_hw_index]
                new_hw_index = new_hw_index + 1
                if key in ["MDS", "NEXUS_9K", "NEXUS_5K"]:
                    sw_image = get_latest_image(key)
                    if not isinstance(sw_image, str):
                        hw_dict['switch_image'] = json.dumps(sw_image)
                    else:
                        hw_dict['switch_image'] = sw_image
                conf_defaults.append(hw_dict)

    ip_list = get_available_static_ips()
    ip_cnt = 0

    try:
        # Auto-populate free IPs for all hardware (except blades)
        for hw_dict in conf_defaults:
            hw_dict['switch_ip'] = "" if ip_list == [] else ip_list[ip_cnt]
            ip_cnt = ip_cnt + 1
            if hw_dict['device_type'] == "UCSM" and 'virtual_ip' in hw_dict:
                hw_dict['virtual_ip'] = "" if ip_list == [] else ip_list[ip_cnt]
                ip_cnt = ip_cnt + 1
            elif hw_dict['device_type'] == "PURE":
                hw_dict['ct0_ip'] = "" if ip_list == [] else ip_list[ip_cnt]
                ip_cnt = ip_cnt + 1
                hw_dict['ct1_ip'] = "" if ip_list == [] else ip_list[ip_cnt]
                ip_cnt = ip_cnt + 1
                hw_dict['vir0_ip'] = "" if ip_list == [] else ip_list[ip_cnt]
                ip_cnt = ip_cnt + 1

        # Auto-populate free IPs for blades. This is done at atlast bcos a
        # consecutive range is needed
        for hw_dict in conf_defaults:
            if hw_dict['device_type'] == "UCSM" and 'kvm_console_ip' in hw_dict:
                kvm_ip_range = get_kvm_ip_range(ip_list[ip_cnt:])
                hw_dict['kvm_console_ip']['kvm_range'] = "" if kvm_ip_range == [] else kvm_ip_range[0].split(
                    '.')[-1] + "-" + str(int(kvm_ip_range[0].split('.')[-1]) + 11)
                ip_cnt = ip_cnt + 12
                hw_dict['kvm_console_ip'] = json.dumps(
                    hw_dict['kvm_console_ip'])

    except IndexError:
        res.setResult(conf_defaults, PTK_NOTEXIST,
                      _("PDT_NO_FREE_IP_ERR_MSG"))
    # Uncomment Below line for working in emulated mode- initial Config page
    #res.setResult(conf_defaults, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    # return res
    if ip_list == []:
        res.setResult(conf_defaults, PTK_NOTEXIST,
                      _("PDT_NO_FREE_IP_ERR_MSG"))
    else:
        res.setResult(conf_defaults, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def get_kvm_ip_range(ips):
    free_ip_groups = []
    ips_dict = {x.split('.')[-1]:x for x in ips}
    hosts = [int(x) for x in ips_dict.keys()]
    hosts.sort()

    for k, g in groupby(enumerate(hosts), lambda x: x[0]-x[1]):
        lst = list(map(itemgetter(1), g))
        ip_lst = [ips_dict[str(x)] for x in lst]
        free_ip_groups.append(ip_lst)

    for group in free_ip_groups:
        if len(group) >= 12:
            return group


def reconfigure(hwtype, mac, force):
    res = result()
    data_list = []
    for i in mac:
        status, data = get_xml_element(static_discovery_store, 'mac', i)
        if status is True:
            if (force == 0 and data[0]['configured'] == "Re-validate") or (
                    force == 1 and data[0]['configured'] == "Unconfigured"):
                data_list.append(data[0])
            else:
                loginfo("Device does not need a re-configure")
                res.setResult("False", PTK_INTERNALERROR,
                              _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
                return res
        else:
            res.setResult("False", PTK_NOTEXIST, _("PDT_NO_SUCH_DEVICE_MSG"))
            return res

    if hwtype == "MDS":
        status, data = MDSSetup().mdsreconfigure(data_list[0], force)
    elif hwtype == "PURE":
        status, data = FASetup().fareconfigure(data_list[0], force)
    elif hwtype[0:5] == "Nexus":
        status, data = NEXUSSetup(
        ).nexusreconfigure(data_list[0], force)
    elif hwtype == "UCSM":
        status, data = UCSManager().ucsmfireconfig(data_list, force)
    if status:
        if data != 0:
            res.setResult(data, PTK_CONFIRMCHK,
                          _("PDT_RECONFIG_MSG"))
        else:
            res.setResult("True", PTK_OKAY, _("PDT_SUCCESS_MSG"))
    else:
        for i in mac:
            update_xml_element(static_discovery_store, 'mac', i, {
                "configured": "Re-validate"})
        res.setResult("False", PTK_INTERNALERROR,
                      _("PDT_RECONFIG_FAILED_ERR_MSG") + " %s" % hwtype)
    return res


def get_fa_configdefaults(item):
    hw_dict = {}
    hw_dict['array_name'] = "FlashArray"
    hw_dict['device_type'] = "PURE"
    hw_dict['ct0_ip'] = ""
    hw_dict['ct1_ip'] = ""
    hw_dict['vir0_ip'] = ""
    hw_dict['timezone'] = "America/Los_Angeles"
    hw_dict['relay_host'] = "blackhole-smtp2.dev.purestorage.com"
    hw_dict['sender_domain'] = "purestorage.com"
    hw_dict['alert_emails'] = "admin@purestorage.com"
    hw_dict['organization'] = ""
    hw_dict['full_name'] = ""
    hw_dict['job_title'] = ""
    hw_dict['mac'] = item
    return hw_dict


def get_ucs_configdefaults(input_count, mac_lst, conf_lst):
    ucs_list = []
    conf_count = len(conf_lst)
    res = dhcpinfo()
    info = parseTaskResult(res)
    dicts = {
        "min_range": info['start'].split('.')[-1],
        "max_range": info['end'].split('.')[-1],
        "min_interval": "12",
        "max_interval": "12",
        "subnet": '.'.join(info['subnet'].split('.', 3)[:-1]),
        "kvm_range": ""
    }
    loginfo(dicts)
    if input_count == 1:
        ucs_dict = {}
        ucs_dict['device_type'] = "UCSM"
        ucs_dict['switch_mac'] = mac_lst[0]
        if conf_count == 0 or conf_count == 2:
            # primary
            ucs_dict['switch_name'] = "fi"
            ucs_dict['virtual_ip'] = ""
            ucs_dict['mode'] = "primary"
            ucs_dict['kvm_console_ip'] = dicts
        elif conf_count == 1:
            if 'vipaddress' not in conf_lst[0]:
                # standalone
                ucs_dict['switch_name'] = "fi"
                ucs_dict['mode'] = "standalone"
            else:
                # secondary
                ucs_dict['mode'] = "secondary"
        ucs_list.append(ucs_dict)
    elif input_count == 2:
        # cluster
        primary = 0
        for i in range(0, input_count):
            ucs_dict = {}
            ucs_dict['device_type'] = "UCSM"
            ucs_dict['switch_mac'] = mac_lst[i]
            if primary == 0:
                ucs_dict['switch_name'] = "fi"
                ucs_dict['virtual_ip'] = ""
                ucs_dict['mode'] = "primary"
                ucs_dict['kvm_console_ip'] = dicts
                primary = 1
            else:
                ucs_dict['mode'] = "secondary"
            ucs_list.append(ucs_dict)
    return ucs_list


def save_device_details(
        ipaddress,
        username,
        password,
        serial_no,
        mac,
        model,
        device_type,
        configured,
        name,
        reachability,
        vipaddress='',
        leadership=''):
    data = locals()
    encrypt_pwd = encrypt(password)
    data["password"] = encrypt_pwd
    if device_type == "UCSM":
        data["vipaddress"] = vipaddress
        data["leadership"] = leadership
    data["timestamp"] = str(time.time())
    data = {i: data[i] for i in data if data[i] != ''}
    add_xml_element(static_discovery_store, data)
    return


def conf_cleanup(device_type, xml_entry):
    if device_type == "MDS":
        MDSSetup().confcleanup(xml_entry.getAttribute("serial_no"))
    elif device_type == "Nexus 9k" or device_type == "Nexus 5k":
        NEXUSSetup().confcleanup(
            xml_entry.getAttribute("mac").replace(':', ''))


def update_device_details(key, key_value, tag, tag_value):
    data = {}
    data[tag] = tag_value
    update_xml_element(static_discovery_store, key, key_value, data)
    return


def delete_device_details(key, key_value):
    delete_xml_element(static_discovery_store, key, key_value)
    return


def update_discovery_list(key, value, ip_list):
    for val in ip_list:
        if 'mac' in val:
            if val['mac'] == key:
                val['configured'] = value
    return ip_list


def remove_duplicate_clients(unconfigured_list, mac_list):
    for mac in mac_list:
        for index, value in enumerate(unconfigured_list):
            if mac == value['mac_address']:
                del unconfigured_list[index]
    return unconfigured_list


def check_if_lease_exist(key, value, ip_list):
    ipaddr = ""

    for val in ip_list:
        if 'mac' in val:
            if val['mac'] == key:
                ipaddr = val['ipaddress']
                return True, ipaddr

    return False, ipaddr


def remove_dhcp_lease(mac):
    mac = mac.lower()
    if os.path.exists(dhcp_lease_file) == False:
        loginfo("Unable to open the lease file for reading")
        return False

    fh = open(dhcp_lease_file, 'r')
    if fh:
        current_leases = fh.read()
        fh.close()

        regex = r'(lease\s*[0-9\.]+\s*\{[^\{\}]*%s[^\{\}]*(.*"[^\{\}]*\}|\}))' % mac
        lease_matched = re.findall(regex, current_leases)
        if lease_matched:
            loginfo("Lease entry present for the MAC %s" % mac)
            for lease in lease_matched:
                updated_leases = current_leases.replace(lease[0], "")
            if updated_leases:
                fh = open(dhcp_lease_file, 'w')
                if fh:
                    os.system("cp %s %s" %
                              (dhcp_lease_file, old_dhcp_lease_file))
                    fh.write(updated_leases)
                    loginfo(
                        "Deleted the lease entry which matches the MAC %s" % mac)
                    fh.close()
                    return True
                else:
                    loginfo("Unable to open the lease file for writing")
                    return False
            else:
                loginfo("Failed to remove the lease entry")
                return False
        else:
            loginfo("Lease entry not present for the MAC %s" % mac)
            return True
    else:
        loginfo("Unable to open the lease file for reading")
        return False


def check_dhcpserver_presence():
    conf.checkIPaddr = False
    fam, hw = get_if_raw_hwaddr(conf.iface)
    dhcp_discover = Ether(dst="ff:ff:ff:ff:ff:ff") / IP(src="0.0.0.0", dst="255.255.255.255") / UDP(
        sport=68, dport=67) / BOOTP(chaddr=hw) / DHCP(options=[("message-type", "discover"), "end"])
    ans, unans = srp(dhcp_discover, multi=True, timeout=5)
    if len(ans) == 0:
        return False
    else:
        for pair in ans:
            p = pair[1]
        if p[IP].src == get_ip_address(get_filtered_ifnames()[0]):
            return False
        return True


def check_device_exists(value, tag):
    if os.path.exists(static_discovery_store) is True:
        doc = parse_xml(static_discovery_store)
        for subelement in doc.getElementsByTagName("device"):
            if subelement.getAttribute(tag) == value:
                return True
    return False


def create_wfflag(os_install):
    skip_option = "False" if os_install == "Yes" else "True"

    if os.path.exists(workflow_flag_file) is False:
        loginfo("Creating flag file for skipping vmedia")
        doc = Document()
        roottag = doc.createElement("wflags")
        flag = doc.createElement("wflag")
        flag.setAttribute("name", "vmedia_skip")
        flag.setAttribute("flag", skip_option)
        roottag.appendChild(flag)
        doc.appendChild(roottag)
        fd = open(workflow_flag_file, 'w')
        fd.write(pretty_print(doc.toprettyxml(indent="")))
    else:
        docr = parse(workflow_flag_file)
        subelement = docr.getElementsByTagName("wflag")
        for sub in subelement:
            inp = sub.attributes["name"].value
            if inp == "vmedia_skip":
                if sub.attributes["flag"].value != skip_option:
                    sub.attributes["flag"].value = skip_option
                    fw = open(workflow_flag_file, 'w')
                    fw.write(pretty_print(docr.toprettyxml(indent="")))


def exportdevices():
    res = result()
    data = {'filepath': ''}
    if os.path.exists(static_discovery_store) is True:
        dest = "/var/www/restserver/templates/downloads/%s" % static_discovery_store.split(
            '/')[-1]
        shutil.copy2(static_discovery_store, dest)

        dest_path = "downloads/%s" % static_discovery_store.split('/')[-1]
        data['filepath'] = dest_path

        res.setResult(data, PTK_OKAY, "Success")
        return res

    res.setResult(data, PTK_NOTEXIST, "Device list does not exist")
    return res


def get_latest_image(hw_type):
    if hw_type == "MDS":
        mds_images = MDSSetup().mdsimages().getResult()
        if len(mds_images) > 0:
            return mds_images[0]
        else:
            return "{}"
    elif hw_type == "NEXUS_9K":
        nexus_system = NEXUSSetup().nexus9kimages().getResult()
        if len(nexus_system) > 0:
            nexus_images = {}
            nexus_images['switch_system_image'] = nexus_system[0]
            return nexus_images
        else:
            return ""
    elif hw_type == "NEXUS_5K":
        nexus_system = NEXUSSetup().nexus5ksystemimages().getResult()
        if len(nexus_system) == 0:
            return "{}"
        nexus_kickstart = NEXUSSetup().nexus5kkickstartimages().getResult()
        if len(nexus_kickstart) == 0:
            return "{}"
        nexus_images = {}
        nexus_images['switch_system_image'] = nexus_system[0]
        nexus_images['switch_kickstart_image'] = nexus_kickstart[0]
        return nexus_images


def get_available_static_ips():
    free_static_range_ips = static_range_ips = configured_ips = []
    status, data = get_xml_element(settings, 'dhcp_start')
    if status:
        dhcp_range_ips = [x for x in range(ipaddress.ip_address(unicode(data[0]['dhcp_start'])),
                                  ipaddress.ip_address(unicode(data[0]['dhcp_end'])) + 1)]
  
        static_range_ips = [str(ipaddress.ip_address((x))) for x in
                            range(ipaddress.ip_address(unicode(data[0]['start'])),
                                  ipaddress.ip_address(unicode(data[0]['end'])) + 1) if x not in dhcp_range_ips]

    status, data = get_xml_element(static_discovery_store, 'ipaddress')
    if status:
        configured_ips = list(
            chain.from_iterable(
                (x['ipaddress'],
                 (x['vipaddress'] if 'vipaddress' in x else '')) for x in data if x['configured'] != 'Unconfigured'))
        configured_ips = [x for x in configured_ips if x != '']

    if static_range_ips:
        free_static_range_ips = [
            x for x in static_range_ips if x not in configured_ips]

    return free_static_range_ips


def get_config_static_ips(count):
    free_ips = []
    free_static_ips = get_available_static_ips()
    cnt = 0
    for ip in free_static_ips:
        if cnt < count:
            if IpValidator().is_ip_up(ip) == False:
                free_ips.append(ip)
                cnt = cnt + 1
        else:
            break

    return free_ips


def get_config_mode():
    status, details = get_xml_element(settings, 'config_mode')
    if status:
        return details[0]['config_mode']
    else:
        return "manual"


def is_configured(ip, device_type):
    if device_type == "Nexus 9k":
        return is_nexus(ip, "Unconfigured")
    elif device_type == "Nexus 5k":
        details = get_xml_element(
            file_name=static_discovery_store, attribute_key="ipaddress", attribute_value=ip)
        return is_nexus(ip, "", "admin", "admin")
    elif device_type == "MDS":
        return is_mds(ip, "Unconfigured")
    elif device_type == "UCSM":
        return is_ucsm(ip, "Unconfigured")
    elif device_type == "PURE":
        state, serial = is_pure(ip, "")
        return state


def is_ucsm(ip, mode, username='', password=''):
    if mode == "Unconfigured":
        url = "https://" + ip + "/cgi-bin/initial_setup_new.cgi"
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code == 200:
                if "already configured" in r.content:
                    return "Configured"
                else:
                    return "Unconfigured"
            else:
                return "Unknown"
        except BaseException:
            return "Unknown"

    else:
        try:
            (error, status) = execute_remote_command(
                ip, username, password, "show fabric-interconnect")
            if "Fabric Interconnect:" in status:
                return "Valid"
            else:
                return "Unknown"
        except BaseException:
            return "Failed"


def is_nexus(ip, mode, username='', password=''):
    if mode == "Unconfigured":
        url = "https://" + ip
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code == 401:
                return "Configured"
            else:
                return "Unknown"
        except BaseException:
            return "Unconfigured"

    else:
        try:
            (error, status) = execute_remote_command(
                ip, username, password, "show version")
            if "Cisco Nexus" in status:
                return "Configured"
            else:
                return "Unknown"
        except BaseException:
            return "Failed"


def is_mds(ip, mode, username='', password=''):
    if mode == "Unconfigured":
        # MDS works only with HTTP protocol
        url = "http://" + ip + ":8080"
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code == 401:
                return "Configured"
            else:
                return "Unknown"
        except BaseException:
            return "Unconfigured"

    else:
        try:
            (error, status) = execute_remote_command(
                ip, username, password, "show version")
            if "cisco MDS" in status:
                return "Valid"
            else:
                return "Unknown"
        except BaseException:
            return "Failed"


def is_pure(ip, mode):
    if mode == "Unconfigured":
        url = "http://" + ip + ":8081/array-initial-config"
        try:
            r = requests.get(url, timeout=5, verify=False)
            data = r.json()
            if data['status'] == "uninitialized":
                return "Unconfigured", data['serial_number']
            elif data['status'] == "initializing":
                return "Configured", data['serial_number']
	    else:
		return "Unconfigured", "Unknown"
        except BaseException:
            return "Unconfigured", "Unknown"
    else:
        url = "https://" + ip
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code == 200:
                if "Pure Storage Login" in r.content:
                    return "Configured", "Unknown"
                else:
                    return "Unconfigured", "Unknown"
            else:
                return "Unknown", "Unknown"
        except BaseException:
            return "Unconfigured", "Unknown"
