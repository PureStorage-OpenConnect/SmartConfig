#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :mds_tasks.py
# description     :MDSTasks class for handling tasks
# author          :Parithi
# version         :1.0
#####################################################################

from itertools import zip_longest

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.storage.mds.mds import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_global_wf_config_file
from pure_dir.components.common import get_device_credentials
from pure_dir.services.utils.miscellaneous import *
import xmltodict
import copy
import urllib.error
from pure_dir.global_config import get_settings_file

g_hw_details = {}


def get_device_details(hw_type):
    try:
        stacktype = get_xml_element(
            get_settings_file(), "stacktype")[1][0]['subtype']

        fd = open(get_global_wf_config_file(), 'r')
        doc = xmltodict.parse(fd.read())

        for htype in doc['globals']['htype']:
            if htype['@stacktype'] != stacktype:
                continue
            for input_val in htype['input']:
                if input_val['@name'] in [
                    'nexus_switch_a',
                    'nexus_switch_b',
                    'mds_switch_a',
                    'mds_switch_b',
                    'ucs_switch_a',
                    'ucs_switch_b',
                        'pure_id']:
                    g_hw_details[input_val['@name']] = input_val['@value']
        for key, val in g_hw_details.items():
            if key != hw_type:
                continue
            cred = get_device_credentials(
                key="mac", value=val)
            return cred

    except urllib.error.URLError as e:
        loginfo("Failed during MDS Report Generation" + str(e))

    return None


def _mds_handler(switch_name):
    ucs_creden = {}
    ucs_creden = get_device_details(switch_name)
    try:
        handle = MDS(ipaddr=ucs_creden['ipaddress'],
                     uname=ucs_creden['username'],
                     passwd=ucs_creden['password'])
        return handle
    except BaseException:
        loginfo("Failed to get mds handler")
        return None


def mds_switch_info():
    """
    fetches mds switch info includes: switchname, hardware name, version,time
    """
    mds_sys_info = []
    switch_name = ["mds_switch_a", "mds_switch_b"]
    for switch in switch_name:
        helper = _mds_handler(switch)
        mds_info = helper.mds_switch_version()
        mds_uptime = helper.mds_uptime()
        mds_info['ip_address'] = get_device_details(switch)['ipaddress']
        mds_info.update(mds_uptime)
        mds_sys_info.append(mds_info)
    return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")


def mds_version(args={}):
    '''
    returns: serial number, host name, model, bios version, kickstart version, sys ver, hw version, uptime, ipaddress
    '''
    method = "MDS SAN Switch System Information"
    mds_sys_info = []
    switch_name = ['mds_switch_a', 'mds_switch_b']
    for switch in switch_name:
        helper = _mds_handler(switch)
        mds_init = {
            'serial_num': '',
            'host_name': '',
            'model': '',
            'bios_version': '',
            'kickstart_version': '',
            'sys_ver': '',
            'hw_version': '',
            'uptime': '',
            'ipaddress': ''}
        mds_sys = copy.deepcopy(mds_init)
        if helper is not None:
            mds_show_hw = helper.mds_command('show hardware',
                                             ['serial_num',
                                              'host_name',
                                              'chassis_id',
                                              'hw_ver',
                                              'bios_ver_str',
                                              'rr_sys_ver',
                                              'kickstart_ver_str',
                                              'sys_ver_str'])
            mds_show_ut = helper.mds_command(
                'show system uptime', [
                    'sys_up_days', 'sys_up_hrs', 'sys_up_mins', 'sys_up_secs'])
            mds_sys['serial_num'] = mds_show_hw['serial_num'][0]
            mds_sys['host_name'] = mds_show_hw['host_name'][0]
            mds_sys['model'] = mds_show_hw['chassis_id'][0]
            mds_sys['bios_version'] = mds_show_hw['rr_sys_ver'][0]
            mds_sys['kickstart_version'] = mds_show_hw['kickstart_ver_str'][0]
            mds_sys['sys_ver'] = mds_show_hw['sys_ver_str'][0]
            mds_sys['hw_version'] = mds_show_hw['hw_ver'][0]
            mds_sys['uptime'] = (str(mds_show_ut['sys_up_days'][0]) + " days, " +
                                 str(mds_show_ut['sys_up_hrs'][0]) + " hrs, " +
                                 str(mds_show_ut['sys_up_mins'][0]) + " mins, " +
                                 str(mds_show_ut['sys_up_secs'][0]) + " secs")
            mds_sys['ipaddress'] = get_device_details(switch)['ipaddress']
            mds_sys_info.append(mds_sys.copy())
        else:
            return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"
    if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
        return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method


def mds_san_info(args={}):
    '''
    returns: status domains, time, name, ntp, syslog, tacacs, npiv, scheduler, dns
    '''
    mds_sys_info = []
    method = "MDS SAN Global Switch Information"
    switch_name = ['mds_switch_a', 'mds_switch_b']
    for switch in switch_name:
        helper = _mds_handler(switch)
        mds_init = {
            'domain': '',
            'time': '',
            'name': '',
            'syslog': '',
            'tacacs': '',
            'scheduler': '',
            'dns': '',
            'ntp': '',
            'npiv': ''}
        mds_sys = copy.deepcopy(mds_init)
        if helper is not None:
            try:
                mds_show_dns = helper.mds_command('show hosts', ['TABLE_vrf'])
                mds_sys['domain'] = mds_show_dns['TABLE_vrf'][0]['ROW_vrf']['defaultdomains']

            except IndexError:
                mds_show_dns = helper.mds_command('show hosts', ['dnsnameservice'])
                mds_sys['domain'] = ""

            finally:
                mds_show_ntp = helper.mds_command('show ntp peers', ['PeerIPAddress'])
                mds_show_tacacs = helper.mds_command(
                    'show feature', ['ROW_cfcFeatureCtrl2Table'], cfcFeatureCtrlName2='tacacs')
                mds_show_scheduler = helper.mds_command(
                    'show feature', ['ROW_cfcFeatureCtrl2Table'], cfcFeatureCtrlName2='scheduler')
                mds_show_npiv = helper.mds_command(
                    'show feature',
                    ['ROW_cfcFeatureCtrl2Table'],
                    cfcFeatureCtrlName2='npiv')
                mds_name = helper.mds_command('show hardware', ['host_name'])
                mds_timezone = helper.mds_cmd_cli_err('show clock')
                mds_sys['time'] = mds_timezone['ins_api']['outputs']['output']['body']['simple_time'].split(' ')[
                    1] if mds_timezone else 'UTC'
                mds_sys['name'] = mds_name['host_name'][0]
                mds_sys['ntp'] = mds_show_ntp['PeerIPAddress'][0].strip()
                mds_sys['syslog'] = ""
                mds_sys['tacacs'] = mds_show_tacacs[0]['cfcFeatureCtrlOpStatus2']
                mds_sys['npiv'] = mds_show_npiv[0]['cfcFeatureCtrlOpStatus2']
                mds_sys['scheduler'] = mds_show_scheduler[0]['cfcFeatureCtrlOpStatus2']
                mds_sys['dns'] = ""
                mds_sys_info.append(mds_sys.copy())
        else:
            return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"
    if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
        return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method


def mds_snmp_agent(args={}):
    mds_sys_info = []
    switch_name = ['mds_switch_a', 'mds_switch_b']
    mds_sys = {}
    for switch in switch_name:
        mds_sys = {}
        helper = _mds_handler(switch)
        if helper is not None:
            mds_show_snmp = helper.mds_command('show snmp user', ['user', 'group'])
            mds_show_hostname = helper.mds_command('show hardware', ['host_name'])
            mds_sys['hostname'] = mds_show_hostname['host_name'][0]
            mds_sys['user'] = mds_show_snmp['user'][0].strip()
            mds_sys['group'] = mds_show_snmp['group'][0].strip()
            mds_sys['credential_type'] = "user"
            mds_sys_info.append(mds_sys.copy())
        else:
            return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"
    if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
        return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method


def mds_environment_info(args={}):
    method = "MDS Environment Information"
    mds_sys_info = []
    switch_name = ['mds_switch_a', 'mds_switch_b']
    for switch in switch_name:
        mds_init = {
            'hostname': '',
            'ps_model': [],
            'ps_status': [],
            'mds_mscs': [],
            'fan_name': [],
            'fan_model': [],
            'fan_status': []}
        mds_sys = copy.deepcopy(mds_init)
        helper = _mds_handler(switch)
        if helper is not None:
            mds_show_hostname = helper.mds_command('show hardware', ['host_name'])
            mds_show_env = helper.mds_command('show environment ',
                                              ['ps_status',
                                               'psmodel',
                                               'tempmod',
                                               'sensor',
                                               'curtemp',
                                               'alarmstatus',
                                               'fanname',
                                               'fanmodel',
                                               'fanstatus'])
            mds_sys['hostname'] = mds_show_hostname['host_name']
            mds_sys['ps_model'] = mds_show_env['psmodel']
            mds_sys['ps_status'] = mds_show_env['ps_status']
            mds_show_env['tempmod'] = [i.strip() for i in mds_show_env['tempmod']]
            mds_mod = zip(
                mds_show_env['tempmod'],
                mds_show_env['sensor'],
                mds_show_env['curtemp'],
                mds_show_env['alarmstatus'])
            mds_mod = ["/".join(i) for i in mds_mod]
            mds_sys['mds_mscs'] = mds_mod
            mds_sys['fan_name'] = mds_show_env['fanname']
            mds_sys['fan_model'] = mds_show_env['fanmodel']
            mds_sys['fan_status'] = mds_show_env['fanstatus']
            mds_sys_info.append(mds_sys.copy())
        else:
            return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"
    if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
        return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method


def mds_vsan_info(args={}):
    mds_sys_info = []
    method = "MDS VSAN INFO for " + args['switch_name'][-1].upper()
    helper = _mds_handler(args['switch_name'])
    if helper is not None:
        mds_init = {
            'vsan_name': '',
            'vsan_state': '',
            'vsan_interop_mode': '',
            'vsan_load_balancing': '',
            'vsan_operational_state': ''}
        mds_sys = copy.deepcopy(mds_init)
        mds_show_vsan = helper.mds_command('show vsan', ['ROW_vsan'])
        vsan_info = mds_show_vsan['ROW_vsan']
        for vsan_list in vsan_info:
            if isinstance(vsan_list, list):
                for vsan in vsan_list:
                    if len(vsan) > 2:
                        mds_sys['vsan_name'] = vsan['vsan_name']
                        mds_sys['vsan_state'] = vsan['vsan_state']
                        mds_sys['vsan_interop_mode'] = vsan['vsan_interop_mode']
                        mds_sys['vsan_load_balancing'] = vsan['vsan_load_balancing']
                        mds_sys['vsan_operational_state'] = vsan['vsan_operational_state']
                        mds_sys_info.append(mds_sys.copy())
        if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
            return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"


def mds_flogi(args={}):
    method = "MDS FLOGI for " + args['switch_name'][-1].upper()
    mds_sys_info = []
    mds_init = {'interface': '', 'vsan_id': '', 'wwpn': '', 'wwnn': ''}
    helper = _mds_handler(args['switch_name'])
    if helper is not None:
        mds_sys = copy.deepcopy(mds_init)
        mds_show_flogi = helper.get_flogi_sessions().getResult()
        for row in mds_show_flogi:
            mds_sys['interface'] = row['iface_id']
            mds_sys['vsan_id'] = row['vsan_id']
            mds_sys['wwpn'] = row['pwwn']
            mds_sys['wwnn'] = row['nwwn']
            mds_sys_info.append(mds_sys.copy())
        if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
            return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"


def mds_interfaces_fc(args={}):
    mds_sys_info = []
    tmp_dict = {}
    method = "MDS INTERFACES for " + args['switch_name'][-1].upper()
    mds_init = {'interface': '', 'vsan': '', 'description': '', 'smsml': ''}
    helper = _mds_handler(args['switch_name'])
    if helper is not None:
        mds_sys = copy.deepcopy(mds_init)
        mds_show_module = helper.mds_command(
            'show interface brief', [
                'fcot_info', 'ROW_interface_brief_fc', 'status', 'port_rate_mode', 'oper_speed', 'interface_fc'])
        mds_descrip = helper.mds_command('show interface description', ['ROW_interface'])
        mds_port_lic = helper.mds_port_license()
        tmp_dict['description'] = [v['sfp_desc']
                                   for v in [i[0] if isinstance(i, list) else i for i in mds_descrip['ROW_interface']]][0]
        tmp_dict['status'] = [j['status']
                              for i in mds_show_module['ROW_interface_brief_fc'] for j in i]
        tmp_dict['port_rate_mode'] = [j['port_rate_mode']
                                      for i in mds_show_module['ROW_interface_brief_fc'] for j in i]
        tmp_dict['oper_speed'] = [j['oper_speed']
                                  for i in mds_show_module['ROW_interface_brief_fc'] for j in i]
        tmp_dict['fcot_info'] = [j['fcot_info']
                                 for i in mds_show_module['ROW_interface_brief_fc'] for j in i]
        tmp_dict['interface'] = [
            "".join([v for k, v in i.items() if k == "interface"]) for i in mds_port_lic]
        tmp_dict['license'] = ["".join([v for k, v in i.items() if k == "licns"])
                               for i in mds_port_lic]

        mds_smsml = zip_longest(tmp_dict['status'], tmp_dict['port_rate_mode'],
                                tmp_dict['oper_speed'], tmp_dict['fcot_info'],
                                tmp_dict['license'], fillvalue='--')
        mds_smsml = ["/".join(i) for i in list(mds_smsml)]

        for row in mds_show_module['ROW_interface_brief_fc']:
            for x, y, z in zip(row, tmp_dict['description'], mds_smsml):
                mds_sys['interface'] = x['interface_fc']
                mds_sys['vsan'] = x['vsan_brief']
                mds_sys['description'] = y
                mds_sys['smsml'] = z
                mds_sys_info.append(mds_sys.copy())
        if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
            return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"


def mds_zoneset(args={}):
    mds_sys_info = []
    mds_init = {'zoneset_name': '', 'zoneset_vsan_id': ''}
    method = "Fabric Zone Information"
    helper = _mds_handler(args['switch_name'])
    if helper is not None:
        mds_sys = copy.deepcopy(mds_init)
        mds_zoneset_name = helper.mds_command(
            'show zoneset brief', [
                'zoneset_vsan_id', 'zoneset_name'])
        mds_sys['zoneset_name'] = mds_zoneset_name['zoneset_name'][0]
        mds_sys['zoneset_vsan_id'] = mds_zoneset_name['zoneset_vsan_id'][0]
        mds_sys_info.append(mds_sys)
        if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
            return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"


def mds_zone(args={}):
    mds_sys_info = []
    mds_init = {'wwn': '', 'zone_name': '', 'logged': ''}
    tmp_dict = {}
    helper = _mds_handler(args['switch_name'])
    method = "MDS " + args['switch_name'][-1].upper() + " Zoning"
    if helper is not None:
        mds_zone_name = helper.mds_command('show zone', ['zone_name', 'ROW_zone_member'])
        for row in range(len(mds_zone_name['ROW_zone_member'])):
            tmp_dict['wwn'] = []
            for i, j in zip(mds_zone_name['ROW_zone_member'][row], mds_zone_name['zone_name'][row]):
                tmp_dict['wwn'].append(i['wwn'])
                tmp_dict['zone_name'] = mds_zone_name['zone_name'][row]
                tmp_dict['logged'] = 'Yes'
            mds_sys_info.append(tmp_dict.copy())
        if [mds_dict for mds_dict in mds_sys_info if not mds_dict == mds_init] != []:
            return PTK_OKAY, mds_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, mds_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, mds_sys_info, "failed to get handler for mds Report Generation"
