#####################################################################
#!/usr/bin/env python3
# Project_Name    :SmartConfig
# title           :topology.py
# description     :Flashstack Topology
# author          :Guruprasad
# version         :1.0
#####################################################################

#from pycsco.nxos.device import Device
#from pycsco.nxos import error
#from pycsco.nxos.utils.nxapi_lib import get_feature_list
from pure_dir.components.compute.ucs import ucs_info_netmiko
from pure_dir.components.compute.ucs.ucs_info import UCSInfo
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.components.storage.flashblade.flashblade_tasks import FlashBladeTasks
from pure_dir.components.storage.flashblade.flashblade_report import get_fb_lag_list
from pure_dir.components.storage.mds.mds import MDS
from purestorage import PureHTTPError
from purestorage import FlashArray
from ucsmsdk.ucsexception import UcsException
from ucsmsdk.ucshandle import UcsHandle
import xmltodict
import json
#import urllib2, urllib3
# For Python3
import urllib.error
import re
import string
# For Python3
import queue
from threading import Thread

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import decrypt
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration import *

settings = "/mnt/system/pure_dir/pdt/settings.xml"
static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'


def get_fi_server_interfaces(fi_object, fi_tags):
    server_ifaces = {}
    server_conn = fi_object.get_fi_server_connections()
    if server_conn is None:
        loginfo("Unable to get the FI server interfaces")
        return server_ifaces    

    [conn.update({'local_device': [fi['name'] for fi in fi_tags if fi['tag'] ==
                                   conn['local_device'].split('-')[1]][0]}) for conn in server_conn]
    for fi in fi_tags:
        server_ifaces[fi['name']] = [
            conn for conn in server_conn if conn['local_device'] == fi['name']]
    server_ifaces = {
        fi: [
            iface if iface.pop(
                'local_device',
                None) else None for iface in ifaces] for fi,
        ifaces in server_ifaces.items()}
    return server_ifaces


def get_flogi_database(obj):
    try:
        flogi_sess_list = obj.get_flogi_sessions().getResult()
        keys_list = ["pwwn", "iface_id", "nwwn"]
        flogi_list = [dict((k, flogi[k]) for k in keys_list) for flogi in flogi_sess_list]
        return flogi_list
    except Exception as e:
        loginfo("Unable to login to the san switch. %s" % str(e))
        return None


def get_pc_fc_list(obj, pc_id):
    try:
        fc_pc_list = obj.get_fc_list(pc_id).getResult()
        keys_list = ["iface_id"]
        fc_pc_list = [fc[k] for k in keys_list for fc in fc_pc_list]
        return fc_pc_list
    except Exception as e:
        loginfo("Unable to login to the switch. %s" % str(e))
        return None


def get_nexus_fa_connectivity(nx_obj, fa_obj):
    nx_mac_table = nx_obj.get_mac_address_table()
    nx_mac_table = [mac for mac in nx_mac_table if mac['disp_type'] in ['Primary_entry', '* ']]
    fa_nw_ifaces = fa_obj.get_iscsi_port_list().getResult()
    nx_fa_list = []
    for mac_entry in nx_mac_table:
        for hwaddr_entry in fa_nw_ifaces:
            if mac_entry['disp_mac_addr'].replace(
                    '.', '').lower() == hwaddr_entry['hwaddr'].replace(
                    ':', '').lower():
                # print  mac_entry['disp_port'], mac_entry['disp_mac_addr'].replace('.',
                # '').lower(), hwaddr_entry['hwaddr'].replace(':', '').lower()
                intf_details = nx_obj.get_interface_details(mac_entry['disp_port'])
                nx_fa_entry = dict(local_interface=mac_entry['disp_port'],
                                   remote_interface=hwaddr_entry['name'],
                                   speed=intf_details['speed'],
                                   state=intf_details['state'],
                                   type=intf_details['type'])
                nx_fa_list.append(nx_fa_entry)
    return nx_fa_list


def get_fa_nexus_connectivity(fa_obj, nx_obj):
    fa_nw_ifaces = fa_obj.get_iscsi_port_list().getResult()
    nx_mac_table = nx_obj.get_mac_address_table()
    nx_mac_table = [mac for mac in nx_mac_table if mac['disp_type'] in ['Primary_entry', '* ']]
    # print "nx-mac", nx_mac_table
    fa_nx_list = []
    for hwaddr_entry in fa_nw_ifaces:
        for mac_entry in nx_mac_table:
            if hwaddr_entry['hwaddr'].replace(
                    ':', '').lower() == mac_entry['disp_mac_addr'].replace(
                    '.', '').lower():
                intf_details = [iface for iface in fa_obj.get_hardware_conf(
                ) if iface['name'] == hwaddr_entry['name']][0]
                #intf_details = nx_obj.get_interface_details(mac_entry['disp_port'])
                fa_nx_entry = dict(
                    remote_interface=mac_entry['disp_port'],
                    local_interface=hwaddr_entry['name'],
                    speed=str(
                        int(intf_details['speed'] / (
                            1000 * 1000 * 1000))) + "Gb/s",
                    state='up' if intf_details['status'] == 'ok' else intf_details['status'],
                    type='Ethernet')
                fa_nx_list.append(fa_nx_entry)
    return fa_nx_list


def get_fc_fa_connectivity(fc_switch_obj, fa_obj):
    fc_flogi_db = get_flogi_database(fc_switch_obj)
    fa_ports = fa_obj.get_fc_port_list().getResult()
    fc_fa_list = []
    for flogi in fc_flogi_db:
        for port in fa_ports:
            if flogi['pwwn'].lower().replace(':', '') == port['wwn'].lower():
                intf_details = fc_switch_obj.get_interface_details(flogi['iface_id'])
                fc_fa_entry = dict(local_interface=flogi['iface_id'],
                                   type=intf_details['type'],
                                   speed=intf_details['speed'],
                                   state=intf_details['state'],
                                   remote_interface=port['name'])
                fc_fa_list.append(fc_fa_entry)
    return fc_fa_list


def get_n5kfc_fa_connectivity(fc_switch_obj, fa_obj):
    fc_flogi_db = get_flogi_database(fc_switch_obj)
    fa_ports = fa_obj.get_fc_port_list().getResult()
    fc_fa_list = []
    for flogi in fc_flogi_db:
        for port in fa_ports:
            if flogi['pwwn'].lower().replace(':', '') == port['wwn'].lower():
                intf_details = fc_switch_obj.get_n5k_fc_interface_details(flogi['iface_id'])
                fc_fa_entry = dict(local_interface=flogi['iface_id'],
                                   type=intf_details['type'],
                                   speed=intf_details['speed'],
                                   state=intf_details['state'],
                                   remote_interface=port['name'])
                fc_fa_list.append(fc_fa_entry)
    return fc_fa_list


def get_ucs_dc_fc_fa_connectivity(fi_dict, fa_obj, fi_tags):
    fa_ports = fa_obj.get_fc_port_list().getResult()
    fc_fa_list = {}
    fi_flogi_db = {}
    for fi in fi_tags:
        fc_fa_list[fi['name']] = []
        fi_flogi_db[fi['name']] = ucs_info_netmiko.get_flogi_sessions(
            fi_dict['vipaddress'], fi_dict['username'], decrypt(fi_dict['password']), fi['tag'])
        for flogi in fi_flogi_db[fi['name']]:
            for port in fa_ports:
                if flogi['pwwn'].lower().replace(':', '') == port['wwn'].lower():
                    intf_details = fi_dict['object'].get_fc_port_detail(
                        fi['tag'], flogi['iface_id'])
                    fc_fa_entry = dict(local_interface=flogi['iface_id'],
                                       type=intf_details['type'],
                                       speed=intf_details['speed'],
                                       state=intf_details['state'],
                                       remote_interface=port['name'])
                    fc_fa_list[fi['name']].append(fc_fa_entry)
    return fc_fa_list


def get_ucs_dc_iscsi_fa_connectivity(fi_dict, fa_obj, fi_tags):
    fa_nw_ifaces = fa_obj.get_iscsi_port_list().getResult()
    fi_fa_list = {}
    fi_iscsi_intf = {}
    for fi in fi_tags:
        fi_fa_list[fi['name']] = []
        fi_iscsi_intf[fi['name']] = ucs_info_netmiko.get_mac_address_table(
            fi_dict['vipaddress'], fi_dict['username'], decrypt(fi_dict['password']), fi['tag'])
        for mac_entry in fi_iscsi_intf[fi['name']]:
            for hwaddr_entry in fa_nw_ifaces:
                if mac_entry['mac'].replace(
                        '.', '').lower() == hwaddr_entry['hwaddr'].replace(
                        ':', '').lower():
                    intf_details = [iface for iface in fa_obj.get_hardware_conf(
                    ) if iface['name'] == hwaddr_entry['name']][0]
                    fi_fa_entry = dict(
                        local_interface=mac_entry['iface_id'],
                        remote_interface=hwaddr_entry['name'],
                        speed=str(
                            int(intf_details['speed'] / (
                                1000 * 1000 * 1000))) + "Gb/s",
                        state='up' if intf_details['status'] == 'ok' else intf_details['status'],
                        type='Ethernet')
                    fi_fa_list[fi['name']].append(fi_fa_entry)
    return fi_fa_list


def get_fa_ucs_dc_fc_connectivity(fa_obj, fi_dict, fi_tags):
    fa_ports = fa_obj.get_fc_port_list().getResult()
    fa_fc_list = []
    fi_flogi_db = {}
    for fi in fi_tags:
        fi_flogi_db[fi['name']] = ucs_info_netmiko.get_flogi_sessions(
            fi_dict['vipaddress'], fi_dict['username'], decrypt(fi_dict['password']), fi['tag'])
    for port in fa_ports:
        for fi, flogi_list in fi_flogi_db.items():
            for flogi in flogi_list:
                if port['wwn'].lower() == flogi['pwwn'].lower().replace(':', ''):
                    intf_details = [
                        iface for iface in fa_obj.get_hardware_conf() if iface['name'] == port['name']][0]
                    fa_fc_entry = dict(
                        remote_interface=flogi['iface_id'],
                        remote_device=fi,
                        type='FC',
                        speed=str(
                            int(intf_details['speed'] / (
                                1000 * 1000 * 1000))) + "Gb/s",
                        state='up' if intf_details['status'] == 'ok' else intf_details['status'],
                        local_interface=port['name'])
                    fa_fc_list.append(fa_fc_entry)
    return fa_fc_list


def get_fa_ucs_dc_iscsi_connectivity(fa_obj, fi_dict, fi_tags):
    fa_nw_ifaces = fa_obj.get_iscsi_port_list().getResult()
    fa_fi_list = []
    fi_iscsi_intf = {}
    for fi in fi_tags:
        fi_iscsi_intf[fi['name']] = ucs_info_netmiko.get_mac_address_table(
            fi_dict['vipaddress'], fi_dict['username'], decrypt(fi_dict['password']), fi['tag'])
    for hwaddr_entry in fa_nw_ifaces:
        for fi, iscsi_ifaces in fi_iscsi_intf.items():
            for iscsi_if in iscsi_ifaces:
                if hwaddr_entry['hwaddr'].replace(
                        ':', '').lower() == iscsi_if['mac'].replace(
                        '.', '').lower():
                    intf_details = [iface for iface in fa_obj.get_hardware_conf(
                    ) if iface['name'] == hwaddr_entry['name']][0]
                    fa_fi_entry = dict(
                        remote_interface=iscsi_if['iface_id'],
                        remote_device=fi,
                        type='Ethernet',
                        speed=str(
                            int(intf_details['speed'] / (
                                1000 * 1000 * 1000))) + "Gb/s",
                        state='up' if intf_details['status'] == 'ok' else intf_details['status'],
                        local_interface=hwaddr_entry['name'])
                    fa_fi_list.append(fa_fi_entry)
    return fa_fi_list


def get_fa_fc_connectivity(fa_obj, fc_switch_obj):
    fa_ports = fa_obj.get_fc_port_list().getResult()
    fc_flogi_db = get_flogi_database(fc_switch_obj)
    fa_fc_list = []
    for port in fa_ports:
        for flogi in fc_flogi_db:
            if port['wwn'].lower() == flogi['pwwn'].lower().replace(':', ''):
                intf_details = [
                    iface for iface in fa_obj.get_hardware_conf() if iface['name'] == port['name']][0]
                fa_fc_entry = dict(
                    remote_interface=flogi['iface_id'],
                    type='FC',
                    speed=str(
                        int(intf_details['speed'] / (
                            1000 * 1000 * 1000))) + "Gb/s",
                    state='up' if intf_details['status'] == 'ok' else intf_details['status'],
                    local_interface=port['name'])
                fa_fc_list.append(fa_fc_entry)
    return fa_fc_list


def get_san_ucs_connectivity(switch_type, san_obj, fi_list):
    san_flogi_db = get_flogi_database(san_obj)
    fi_dict = [fi for fi in fi_list if fi['leadership'] == 'primary'][0]
    ucs_san_list = []
    for fi in fi_list:
        san_neighbors = fi_dict['object'].get_san_neighbors(fi['tag'])
        #TODO: Unable to fetch san-neighbors from FI6454 through cli/ucsm
        if not san_neighbors: 
            san_neighbors = ucs_info_netmiko.get_san_neighbors(
                fi_dict['vipaddress'], fi_dict['username'], decrypt(fi_dict['password']), fi['tag'])
        [hw.update({'tag': fi['tag'], 'name':fi['name']}) for hw in san_neighbors]
        ucs_san_list.extend(san_neighbors)
    # Getting pc id on the san switch side for the matched pwwn
    san_pc_intf = [
        intf_san for intf_san in san_flogi_db for intf_ucs in ucs_san_list if intf_san['pwwn'] == intf_ucs['my_pwwn']]
    san_pc = re.compile('(port-channel|San-po)(.+)').search(san_pc_intf[0]['iface_id']).group(2)
    san_fc_list = get_pc_fc_list(san_obj, san_pc)
    # Getting pc id on the ucs side for the matched pwwn
    ucs_pc_intf = [
        intf_ucs for intf_ucs in ucs_san_list for intf_san in san_flogi_db if intf_san['pwwn'] == intf_ucs['my_pwwn']]
    ucs_pc = re.compile('(san-port-channel |San-po)(.+)').search(ucs_pc_intf[0]['local_interface']).group(2)
    ucs_det_for_san_intf = [
        intf_ucs for intf_san in san_flogi_db for intf_ucs in ucs_san_list if intf_san['pwwn'] == intf_ucs['my_pwwn']][0]
    ucs_fc_list = fi_dict['object'].get_san_pc_members(ucs_det_for_san_intf['tag'], ucs_pc)

    san_ucs_list = []
    for idx, val in enumerate(san_fc_list):
        conn = {}
        if switch_type == 'Nexus 5k':
            intf_details = san_obj.get_n5k_fc_interface_details(san_fc_list[idx])
        else:
            intf_details = san_obj.get_interface_details(san_fc_list[idx])
            # print "intf", intf_details
        conn = {'local_interface': san_fc_list[idx],
                'remote_device': ucs_det_for_san_intf['name'],
                'remote_interface': ucs_fc_list[idx],
                'pc': intf_details['pc'],
                'speed': intf_details['speed'],
                'type': intf_details['type'],
                'state': intf_details['state']
                }
        san_ucs_list.append(conn)
    return san_ucs_list


def get_ucs_san_connectivity(fi_dict, fi_obj, fi_tags):
    ucs_san_list = {}
    for fi in fi_tags:
        ucs_san_neighbors_list = fi_obj.get_san_neighbors(fi['tag'])
        #TODO: Unable to fetch san-neighbors from FI6454 through cli/ucsm
        if not ucs_san_neighbors_list:
            ucs_san_neighbors_list = ucs_info_netmiko.get_san_neighbors(
                fi_dict['vipaddress'], fi_dict['username'], decrypt(fi_dict['password']), fi['tag'])
        ucs_san_list[fi['name']] = get_ucs_san_pc_interfaces(
            fi_obj, ucs_san_neighbors_list, fi['tag'])
    return ucs_san_list


def get_ucs_san_pc_interfaces(fi_obj, ucs_san_list, fi_tag):
    ucs_san_pc_interfaces = []
    for neighbor in ucs_san_list:
        if 'san-port-channel' or 'San-po' in neighbor['local_interface']:
            ucs_san_pc = re.compile(
                '(san-port-channel |San-po)(.+)').search(neighbor['local_interface']).group(2)
            ucs_fc_list = fi_obj.get_san_pc_members(fi_tag, ucs_san_pc)
            # get username and password from  devices.xml for the matched ip address
            san_hw = [dev for dev in fs_objs if dev['ipaddress'] == neighbor['fabric_mgmt_addr']][0]
            fc_flogi_list = get_flogi_database(san_hw['object'])
            fc_interface = [flogi for flogi in fc_flogi_list if flogi['pwwn'] == neighbor['my_pwwn']
                            and flogi['nwwn'] == neighbor.get('my_nwwn', neighbor.get('fabric_pwwn', None))]
            if fc_interface:
                fc_san_pc = re.compile(
                    'port-channel(.+)|San-po(.+)').search(fc_interface[0]['iface_id']).group(1)
                san_fc_list = get_pc_fc_list(san_hw['object'], fc_san_pc)
                for idx, val in enumerate(ucs_fc_list):
                    ucs_san_pc = {}
                    port_detail = fi_obj.get_fc_port_detail(fi_tag, ucs_fc_list[idx])
                    ucs_san_pc = {'local_interface': ucs_fc_list[idx],
                                  'remote_interface': san_fc_list[idx],
                                  'remote_device': san_hw['name'],
                                  'pc': port_detail['pc'],
                                  'type': port_detail['type'],
                                  'speed': port_detail['speed'],
                                  'state': port_detail['state']}
                    ucs_san_pc_interfaces.append(ucs_san_pc)
    return ucs_san_pc_interfaces


def get_ucs_lan_neighbors(fi_obj, fi_tags):
    ucs_lan_list = {}
    for fi in fi_tags:
        ucs_lan_list[fi['name']] = fi_obj.get_lan_neighbors(fi['tag'])
    return ucs_lan_list


def get_fb_nexus_connectivity(fb_obj, nx_obj):
    fb_nx_list = []
    status, fb_lag_list, msg = get_fb_lag_list()
    [port.update({'speed': fb_lag['port_speed'] if port['state'] == 'up' else '-'}) for fb_lag in fb_lag_list for port in fb_lag['ports']]

    nx_lacp_list = nx_obj.get_lacp_list()
    nx_lacp_ifaces = [lacp['pc_ifaces'] for lacp in nx_lacp_list]
    nx_lacp_ifaces = [j for i in nx_lacp_ifaces for j in i]

    nx_matched_list = [nx_iface for fb_lag in fb_lag_list for nx_iface in nx_lacp_ifaces if nx_iface['remote_interface'] == fb_lag['mac_address']]
    nx_matched_ifaces, nx_matched_mac = [nx_iface['local_interface'] for nx_iface in nx_matched_list], nx_matched_list[0]['remote_interface'] if len(nx_matched_list) > 0 else None

    fb_nx_list = [{'local_interface': fb_lag['name'], 'local_ports': [dict((k, port[k]) for k in ['name', 'state', 'speed']) for port in fb_lag['ports']], 'remote_interface': '|'.join(nx_matched_ifaces), 'speed': fb_lag['lag_speed'], 'state': fb_lag['state'], 'type': 'Ethernet-LAG'} for fb_lag in fb_lag_list if fb_lag['mac_address'] == nx_matched_mac]

    return fb_nx_list


def get_nexus_fb_connectivity(nx_obj, fb_obj):
    nx_fb_list = []
    nx_lacp_list = nx_obj.get_lacp_list()
    [iface.update({'pc_id': nx_lacp['pc_id']}) for nx_lacp in nx_lacp_list for iface in nx_lacp['pc_ifaces']]
    nx_lacp_ifaces = [lacp['pc_ifaces'] for lacp in nx_lacp_list]
    nx_lacp_ifaces = [j for i in nx_lacp_ifaces for j in i]
    
    status, fb_lag_list, msg = get_fb_lag_list()
    [port.update({'speed': fb_lag['port_speed'] if port['state'] == 'up' else '-'}) for fb_lag in fb_lag_list for port in fb_lag['ports']]

    fb_matched_list = [fb_lag for nx_lacp in nx_lacp_ifaces for fb_lag in fb_lag_list if fb_lag['mac_address'] == nx_lacp['remote_interface']]
    fb_matched_mac = fb_matched_list[0]['mac_address'] if len(fb_matched_list) > 0 else None

    for nx_lacp in nx_lacp_ifaces:
        if nx_lacp['remote_interface'] == fb_matched_mac:
            intf_details = nx_obj.get_interface_details(nx_lacp['local_interface'])
            nx_fb_entry = dict(local_interface=nx_lacp['local_interface'],
                               remote_interface=fb_matched_list[0]['name'],
                               speed=intf_details['speed'],
                               state=intf_details['state'],
                               type=intf_details['type'])
            nx_fb_list.append(nx_fb_entry)

    return nx_fb_list


def create_object(hw):
    if hw['device_type'] == 'PURE':
        # FA RESET:
        hw_obj = PureTasks(hw['ipaddress'], hw['username'], decrypt(hw['password']))
        # return None
    elif hw['device_type'] == 'Nexus 5k' or hw['device_type'] == 'Nexus 9k':
        hw_obj = Nexus(hw['ipaddress'], hw['username'], decrypt(hw['password']))
    elif hw['device_type'] == 'MDS':
        hw_obj = MDS(hw['ipaddress'], hw['username'], decrypt(hw['password']))
    elif hw['device_type'] == 'UCSM':
        hw_obj = UCSInfo(hw['vipaddress'], hw['username'], decrypt(hw['password']))
    else:
        return None
    return hw_obj


def get_stack_details():
    obj = Orchestration()
    fs_types = obj.flashstacktype().getResult()
    status, details = get_xml_element(settings, 'stacktype')
    if status:
        stack_details = [fs for fs in fs_types if fs['value'] == details[0]['stacktype']][0]
        return stack_details


def get_stack_obj():
    status, details = get_xml_element(static_discovery_store, 'device_type')
    if status:
        obj = {}
        for device in details:
            if device.get('leadership', None) != 'subordinate':
                device['object'] = create_object(device)

        return details


def get_connection(speed, media_type):
    speed_ops = re.compile(r'^(\d+)( ?)(\w{2})(.*)').search(speed.lower())
    speed_num = speed_ops.group(1)
    speed_measure = speed_ops.group(3)[0].upper() + speed_ops.group(3)[1:]
    if media_type == 'Ethernet' or media_type == 'Server':
        connection = speed_num + speed_measure + 'E'
    elif media_type in ['FC', 'Fibre Channel']:
        connection = speed_num + speed_measure + ' FC'
    else:
        connection = speed
    return connection


def topology_n9k(switch_name, switch_object, switch_type, stacktype, fs_objs, queue):
    cdp_nbors = fa_neighbors = fb_neighbors = []
    try:
        cdp_nbors = switch_object.get_cdp_neighbours()
        if stacktype['tag'] == 'iSCSI':
            fa = [hw for hw in fs_objs if hw['device_type'] == 'PURE'][0]
            fa_neighbors = get_nexus_fa_connectivity(switch_object, fa['object'])
            [intf.update({'remote_device': fa['name']}) for intf in fa_neighbors]
        elif stacktype['tag'] == 'NFS':
            fb = [hw for hw in fs_objs if hw['device_type'] == 'FlashBlade'][0]
            fb_neighbors = get_nexus_fb_connectivity(switch_object, fb['object'])
            [intf.update({'remote_device': fb['name']}) for intf in fb_neighbors]
        queue.put({switch_name: cdp_nbors + fa_neighbors + fb_neighbors})
    except Exception as e:
        loginfo(str(e))
        queue.put({switch_name: cdp_nbors + fa_neighbors + fb_neighbors})
    return


def topology_n5k(switch_name, switch_object, switch_type, stacktype, fs_objs, queue):
    cdp_nbors = switch_object.get_cdp_neighbours()
    fa = [hw for hw in fs_objs if hw['device_type'] == 'PURE'][0]
    fi_tags = [hw for hw in fs_objs if hw['device_type'] == 'UCSM']
    if stacktype['tag'] == 'iSCSI':
        fa_neighbors = get_nexus_fa_connectivity(switch_object, fa['object'])
        neighbors = fa_neighbors
    elif stacktype['tag'] == 'FC':
        fa_neighbors = get_n5kfc_fa_connectivity(switch_object, fa['object'])
        fi_neighbors = get_san_ucs_connectivity(switch_type, switch_object, fi_tags)
        neighbors = fa_neighbors + fi_neighbors
    [intf.update({'remote_device': fa['name']}) for intf in fa_neighbors]
    queue.put({switch_name: cdp_nbors + neighbors})
    return


def topology_mds(switch_name, switch_object, switch_type, stacktype, fs_objs, queue):
    fa_neighbors = fi_neighbors = []
    try:
        fa = [hw for hw in fs_objs if hw['device_type'] == 'PURE'][0]
        fa_neighbors = get_fc_fa_connectivity(switch_object, fa['object'])
        [intf.update({'remote_device': fa['name']}) for intf in fa_neighbors]
        fi_tags = [hw for hw in fs_objs if hw['device_type'] == 'UCSM']
        fi_neighbors = get_san_ucs_connectivity(switch_type, switch_object, fi_tags)
        queue.put({switch_name: fa_neighbors + fi_neighbors})
    except Exception as e:
        loginfo(str(e))
        queue.put({switch_name: fa_neighbors + fi_neighbors})
    return


def topology_fi(switch_name, switch_object, switch_type, stacktype, fs_objs, queue):
    fi_neighbors = {}
    ucs_lan_neighbors = ucs_san_neighbors = ucs_server_interfaces = ucs_fa_neighbors = {}
    fi_dict = [hw for hw in fs_objs if hw['device_type']
               == 'UCSM' and hw['leadership'] == 'primary'][0]
    fi_tags = [{'tag': hw['tag'], 'name':hw['name']}
               for hw in fs_objs if hw['device_type'] == 'UCSM']
    try:
        ucs_server_interfaces = get_fi_server_interfaces(switch_object, fi_tags)
        ucs_lan_neighbors = get_ucs_lan_neighbors(switch_object, fi_tags)
        if stacktype['tag'] == 'FC':
            ucs_san_neighbors = get_ucs_san_connectivity(fi_dict, switch_object, fi_tags)
            if 'ucsmini' in stacktype['value']:
                fa = [hw for hw in fs_objs if hw['device_type'] == 'PURE'][0]
                ucs_fa_neighbors = get_ucs_dc_fc_fa_connectivity(fi_dict, fa['object'], fi_tags)
                {fi: [intf.update({'remote_device': fa['name']}) for intf in intf_list]
                 for fi, intf_list in ucs_fa_neighbors.items()}
        elif stacktype['tag'] == 'iSCSI':
            if 'ucsmini' in stacktype['value']:
                fa = [hw for hw in fs_objs if hw['device_type'] == 'PURE'][0]
                ucs_fa_neighbors = get_ucs_dc_iscsi_fa_connectivity(fi_dict, fa['object'], fi_tags)
                {fi: [intf.update({'remote_device': fa['name']}) for intf in intf_list]
                 for fi, intf_list in ucs_fa_neighbors.items()}
        for fi in fi_tags:
            fi_neighbors[fi['name']] = ucs_lan_neighbors.get(fi['name'], []) + ucs_san_neighbors.get(
                fi['name'], []) + ucs_server_interfaces.get(fi['name'], []) + ucs_fa_neighbors.get(fi['name'], [])
        queue.put(fi_neighbors)
    except Exception as e:
        loginfo(str(e))
        for fi in fi_tags:
            fi_neighbors[fi['name']] = ucs_lan_neighbors.get(fi['name'], []) + ucs_san_neighbors.get(
                fi['name'], []) + ucs_server_interfaces.get(fi['name'], []) + ucs_fa_neighbors.get(fi['name'], [])
        queue.put(fi_neighbors)
    return


def topology_fa(switch_name, switch_object, switch_type, stacktype, fs_objs, queue):
    fa_neighbors = []
    try:
        if stacktype['tag'] == 'FC':
            fc_hws = [hw for hw in fs_objs if hw['device_type'] in ['Nexus 5k', 'MDS']]
            for fc_switch in fc_hws:
                fa_nbors = get_fa_fc_connectivity(switch_object, fc_switch['object'])
                [intf.update({'remote_device': fc_switch['name']}) for intf in fa_nbors]
                fa_neighbors = fa_neighbors + fa_nbors
            if 'ucsmini' in stacktype['value']:
                fi_tags = [{'tag': hw['tag'], 'name':hw['name']}
                           for hw in fs_objs if hw['device_type'] == 'UCSM']
                fi_dict = [hw for hw in fs_objs if hw['device_type']
                           == 'UCSM' and hw['leadership'] == 'primary'][0]
                fa_neighbors = fa_neighbors + \
                    get_fa_ucs_dc_fc_connectivity(switch_object, fi_dict, fi_tags)
        elif stacktype['tag'] == 'iSCSI':
            iscsi_hws = [hw for hw in fs_objs if hw['device_type'] in ['Nexus 5k', 'Nexus 9k']]
            for iscsi_switch in iscsi_hws:
                fa_nbors = get_fa_nexus_connectivity(switch_object, iscsi_switch['object'])
                [intf.update({'remote_device': iscsi_switch['name']}) for intf in fa_nbors]
                fa_neighbors = fa_neighbors + fa_nbors
            if 'ucsmini' in stacktype['value']:
                fi_tags = [{'tag': hw['tag'], 'name':hw['name']}
                           for hw in fs_objs if hw['device_type'] == 'UCSM']
                fi_dict = [hw for hw in fs_objs if hw['device_type']
                           == 'UCSM' and hw['leadership'] == 'primary'][0]
                fa_neighbors = fa_neighbors + \
                    get_fa_ucs_dc_iscsi_connectivity(switch_object, fi_dict, fi_tags)
        queue.put({switch_name: fa_neighbors})
    except Exception as e:
        loginfo(str(e))
        queue.put({switch_name: fa_neighbors})
    return


def topology_fb(switch_name, switch_object, switch_type, stacktype, fs_objs, queue):
    fb_neighbors = []
    try:
        if stacktype['tag'] == 'NFS':
            nx_hws = [hw for hw in fs_objs if hw['device_type'] == 'Nexus 9k']
            for nx_switch in nx_hws:
                fb_nbors = get_fb_nexus_connectivity(switch_object, nx_switch['object'])
                [intf.update({'remote_device': nx_switch['name']}) for intf in fb_nbors]
                fb_neighbors = fb_neighbors + fb_nbors
        queue.put({switch_name: fb_neighbors})
    except Exception as e:
        loginfo(str(e))
        queue.put({switch_name: fb_neighbors})
    return


def construct_topology(stacktype, fs_objs):
    fs_connections = {}
    q = queue.Queue()
    threads = []
    for component in fs_objs:
        if component['device_type'] == 'Nexus 9k':
            t = Thread(
                name=component['name'],
                target=topology_n9k,
                args=(
                    component['name'],
                    component['object'],
                    component['device_type'],
                    stacktype,
                    fs_objs,
                    q))
            t.start()
        elif component['device_type'] == 'Nexus 5k':
            t = Thread(
                name=component['name'],
                target=topology_n5k,
                args=(
                    component['name'],
                    component['object'],
                    component['device_type'],
                    stacktype,
                    fs_objs,
                    q))
            t.start()
        elif component['device_type'] == 'MDS':
            t = Thread(
                name=component['name'],
                target=topology_mds,
                args=(
                    component['name'],
                    component['object'],
                    component['device_type'],
                    stacktype,
                    fs_objs,
                    q))
            t.start()
        elif component['device_type'] == 'UCSM' and component['leadership'] == 'primary':
            t = Thread(
                name=component['name'],
                target=topology_fi,
                args=(
                    component['name'],
                    component['object'],
                    component['device_type'],
                    stacktype,
                    fs_objs,
                    q))
            t.start()
        elif component['device_type'] == 'PURE':
            t = Thread(
                name=component['name'],
                target=topology_fa,
                args=(
                    component['name'],
                    component['object'],
                    component['device_type'],
                    stacktype,
                    fs_objs,
                    q))
            t.start()
        elif component['device_type'] == 'FlashBlade':
            t = Thread(
                name=component['name'],
                target=topology_fb,
                args=(
                    component['name'],
                    component['object'],
                    component['device_type'],
                    stacktype,
                    fs_objs,
                    q))
            t.start()
        else:
            continue
        threads.append(t)
    for t in threads:
        print("Waiting for thread: ", t.name)
        t.join()

    fs_connections = {}
    [fs_connections.update(q.get()) for _ in threads]
    [x.update({'connection': get_connection(x[y], x['type'])}) for hw, conn in fs_connections.items()
     for x in conn for y, z in list(x.items()) if y == 'speed' and x[y] != 'indeterminate']
    return fs_connections


'''
TODO:
1. Remove FA_RESET
2. try Exception for create_object
'''


def fs_connectivity():
    res = result()
    try:
        components = connections = {}
        stack = get_stack_details()
        print("Stack: ", stack)
        global fs_objs
        fs_objs = get_stack_obj()
        hw_types = set([comp['device_type'] for comp in fs_objs])
        components = {
            hw_type: [
                {
                    k: v for k,
                    v in comp.items() if k in [
                        'name',
                        'ipaddress',
                        'mac',
                        'serial_no',
                        'leadership',
                        'model',
                        'vipaddress']} for comp in fs_objs if hw_type in comp['device_type']] for hw_type in hw_types}
        fi_object = [component for component in fs_objs if component['device_type']
                     == 'UCSM' and component['leadership'] == 'primary'][0]['object']
        fi_server_components = fi_object.ucsmtopology()
        fi_server_types = ['chassis', 'rack-server']
        fi_server_components = {fi_server_type.upper(): [{k: v for k, v in comp.items(
        )} for comp in fi_server_components if fi_server_type in comp['type']] for fi_server_type in fi_server_types}
        print(fi_server_components)
        components.update(fi_server_components)
        connections = construct_topology(stack, fs_objs)
        fi_object.release_ucs_handle()

        '''
        Sometimes a fabric interconnect can be a part of two or more flashstacks atleast in in-house labs.
        In that case, the cabling information may have that connectivity info also as part of it.
        To avoid this, the cabling info is filtered only to have the current flashstack components.
        '''
        fs_comp_names = [x['name'] for x in sum([hw for hw in components.values()], [])]
        connections = {hw: [conn for conn in conns if conn['remote_device']
                            in fs_comp_names] for hw, conns in connections.items()}

        fs_connectivity = {
            'stacktype': stack['value'],
            'components': components,
            'connections': connections}
        res.setResult(fs_connectivity, PTK_OKAY, "Success")
    except Exception as e:
        print("Failed", str(e))
        res.setResult({'stacktype': stack['value'],
                       'components': components,
                       'connections': {}},
                      PTK_INTERNALERROR,
                      "Failed to get cabling information")
    return res
