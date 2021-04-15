#!/usr/bin/env python
# Project_Name    :SmartConfig
# title           :ucs_info_netmiko.py
# description     :UCS helper functions for getting ucs info that cannot be done with ucsmsdk
# author          :Guruprasad
# version         :1.0
##############################################################################################


from __future__ import print_function, unicode_literals

from netmiko import Netmiko


def netmiko_connect(ip, username, password, tag):
    my_device = {
        "host": ip,
        "username": username,
        "password": password,
        "device_type": "cisco_nxos",
    }

    print(my_device)
    net_connect = Netmiko(**my_device)
    cmd_nxos = "connect nxos " + tag
    net_connect.send_command(cmd_nxos, expect_string=r"#")
    return net_connect


def execute_remote_command_netmiko(net_connect, command):
    output = net_connect.send_command(command)
    net_connect.disconnect()
    return output


def get_flogi_sessions(ipaddress, username, password, tag):
    flogi_sessions = []
    nc = netmiko_connect(ipaddress, username, password, tag)
    flogi_output = execute_remote_command_netmiko(nc, "show flogi database")
    for row in flogi_output.split('\n'):
        if row.startswith('fc'):
            tmp_list = [x for x in row.split(' ') if x != '']
            flogi_dict = {}
            flogi_dict['iface_id'] = tmp_list[0]
            flogi_dict['vsan_id'] = tmp_list[1]
            flogi_dict['fcid'] = tmp_list[2]
            flogi_dict['pwwn'] = tmp_list[3]
            flogi_dict['nwwn'] = tmp_list[4]
            flogi_sessions.append(flogi_dict)
    return flogi_sessions


def get_mac_address_table(ipaddress, username, password, tag):
    iscsi_sessions = []
    nc = netmiko_connect(ipaddress, username, password, tag)
    iscsi_output = execute_remote_command_netmiko(nc, "show mac address-table")
    for row in iscsi_output.split('\n'):
        if 'Eth' in row:
            tmp_list = [x for x in row.split(' ') if x != '']
            iscsi_dict = {}
            iscsi_dict['vlan_id'] = tmp_list[1]
            iscsi_dict['mac'] = tmp_list[2]
            iscsi_dict['type'] = tmp_list[3]
            iscsi_dict['iface_id'] = tmp_list[7]
            iscsi_sessions.append(iscsi_dict)
    return iscsi_sessions


def get_san_neighbors(ipaddress, username, password, tag):
    san_pc_list = []
    san_neighbors = []
    nc = netmiko_connect(ipaddress, username, password, tag)
    san_pc_db_output = execute_remote_command_netmiko(nc, "show san-port-channel database")
    for row in san_pc_db_output.split('\n'):
        if row.startswith('san-port-channel'):
            tmp_list = [x for x in row.split(' ') if x != '']
            san_pc_list.append(int(tmp_list[1]))

    for san_po in san_pc_list:
        nc = netmiko_connect(ipaddress, username, password, tag)
        cmd = "show npv internal info external-interface san-port-channel %d" % san_po
        san_nbors_output = execute_remote_command_netmiko(nc, cmd)
        try:
            s = san_nbors_output.find(' ifindex: San-po')
            e = san_nbors_output.find('Pinned Server Intf Count')
            san_nbors_output = san_nbors_output[s:e]
            for row in san_nbors_output.split('\n'):
                if ' ifindex: San-po' in row:
                    san_neighbor_dict = {}
                    san_neighbor_dict['local_interface'] = row.split(',')[0].split(':')[1].strip()
                if 'fabric mgmt addr:' in row:
                    san_neighbor_dict['fabric_mgmt_addr'] = row.split(':')[1].strip()
                if 'fabric pwwn:' in row:
                    det = row.split(',')
                    san_neighbor_dict['fabric_pwwn'] = det[0].split(':', 1)[1].strip()
                    san_neighbor_dict['fabric_nwwn'] = det[1].split(':', 1)[1].strip()
                if 'my pwwn:' in row:
                    det = row.split(',')
                    san_neighbor_dict['my_pwwn'] = det[0].split(':', 1)[1].strip()
                    san_neighbor_dict['my_nwwn'] = det[1].split(':', 1)[1].strip()
                    san_neighbors.append(san_neighbor_dict)
            san_neighbors = [i for n, i in enumerate(
                san_neighbors) if i not in san_neighbors[n + 1:]]
            return san_neighbors
        except BaseException:
            return None
    return san_neighbors

def netmiko_obj(ipaddress, username, password):
    '''
    create netmiko object for given credentials
    '''
    my_device = {
            "host": ipaddress,
            "username": username,
            "password": password,
            "device_type": "cisco_nxos",
        }
    netmiko_connect = Netmiko(**my_device)
    return netmiko_connect
