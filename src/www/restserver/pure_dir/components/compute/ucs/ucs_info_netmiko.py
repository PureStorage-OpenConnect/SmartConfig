#!/usr/bin/env python
# Project_Name    :SmartConfig
# title           :ucs_info_netmiko.py
# description     :UCS helper functions for getting ucs info that cannot be done with ucsmsdk
# author          :Guruprasad
# version         :1.0
##############################################################################################


from __future__ import print_function, unicode_literals

from netmiko import Netmiko
from getpass import getpass

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
            flogi_dict['iface_id'] = tmp_list[0].encode('utf-8')
            flogi_dict['vsan_id'] = tmp_list[1].encode('utf-8')
            flogi_dict['fcid'] = tmp_list[2].encode('utf-8')
            flogi_dict['pwwn'] = tmp_list[3].encode('utf-8')
            flogi_dict['nwwn'] = tmp_list[4].encode('utf-8')
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
            iscsi_dict['vlan_id'] = tmp_list[1].encode('utf-8')
            iscsi_dict['mac'] = tmp_list[2].encode('utf-8')
            iscsi_dict['type'] = tmp_list[3].encode('utf-8')
            iscsi_dict['iface_id'] = tmp_list[7].encode('utf-8')
            iscsi_sessions.append(iscsi_dict)
    return iscsi_sessions
