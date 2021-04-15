#!/usr/bin/env python
# Project_Name    :SmartConfig
# title           :ucs_info.py
# description     :UCS helper functions for getting ucs info
# author          :Guruprasad
# version         :1.0
#####################################################################

import re

from pure_dir.infra.logging.logmanager import loginfo

from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException


# class UCSInfo(UCSTasks, object):
class UCSInfo:
    def __init__(self, ipaddress='', username='', password=''):
        try:
            if ipaddress:
                #super(UCSInfo, self).__init__(ipaddress, username, password)
                self.handle = UcsHandle(ipaddress, username, password)
                self.handle_status = self.handle.login()
                topInfoPolicy = self.handle.query_dn('sys/info-policy')
                topInfoPolicy.state = 'enabled'
                self.handle.set_mo(topInfoPolicy)
                self.handle.commit()
        except Exception as e:
            loginfo("Failed to create handle in UCSInfo" + str(e))
            self.handle = None

    def release_ucs_handle(self):
        try:
            topInfoPolicy = self.handle.query_dn('sys/info-policy')
            topInfoPolicy.state = 'disabled'
            self.handle.set_mo(topInfoPolicy)
            self.handle.commit()
            #super(UCSInfo, self).release_ucs_handle()
            self.handle.logout()
            # return None

        except Exception as e:
            loginfo("Failed to release handle in UCSInfo" + str(e))
            return None

    def ucsmtopology(self):
        fi_connections = []
        fabrics = self.handle.query_classid("networkelement")
        for fabric in fabrics:
            mgmts = self.handle.query_classid("MgmtEntity")
            for mgmt in mgmts:
                if fabric.id == mgmt.id:
                    leadership = mgmt.leadership
            fi_connections.append(
                dict(
                    name=fabric.rn,
                    type="fi",
                    id=fabric.id,
                    leadership=leadership))

        bladelist = self.handle.query_classid("ComputeBlade")
        blades = []
        for blade in bladelist:
            # print blade
            blades.append(
                dict(
                    name=blade.rn,
                    type="blade",
                    serial_no=blade.serial,
                    model=blade.model,
                    id=blade.slot_id,
                    association=blade.association,
                    discovery=blade.discovery,
                    chassis_id=blade.chassis_id,
                    operability=blade.operability,
                    status=blade.oper_state,
                    power=blade.oper_power))
        print(blades)

        chassislist = self.handle.query_classid("EquipmentChassis")
        for chassis in chassislist:
            # print chassis
            chassis_blades = [blade for blade in blades if blade['chassis_id'] == chassis.id]
            fi_connections.append(
                dict(
                    name=chassis.rn,
                    type="chassis",
                    serial_no=chassis.serial,
                    acknowledged=chassis.admin_state,
                    discovery=chassis.discovery,
                    model=chassis.model,
                    id=chassis.id,
                    fi_conn=chassis.conn_path,
                    operability=chassis.operability,
                    status=chassis.oper_state,
                    power="on" if chassis.power == "ok" else chassis.power,
                    blades=chassis_blades))

        # TODO: Unit testing not done as lab environment does not have FEX
        fexs = self.handle.query_classid("equipmentFex")
        for fex in fexs:
            parent = "fabric" + "|" + fex.switch_id
            fi_connections.append(dict(name=fex.rn, type="fex", id=fex.id, parent=parent))

        servers = self.handle.query_classid("ComputeRackUnit")
        for server in servers:
            fi_connections.append(
                dict(
                    name=server.rn,
                    type="rack-server",
                    serial_no=server.serial,
                    model=server.model,
                    id=server.id,
                    fi_conn=server.conn_path,
                    operability=server.operability,
                    status=server.oper_state,
                    power=server.oper_power))
        return fi_connections

    def get_fi_server_connections(self):
        if self.handle is None or self.handle_status != True:
            return None

        try:
            fi_connections = []
            fi_server_ports = [x for x in self.handle.query_classid(
                'EtherPIo') if x.if_role == 'server']
            for sport in fi_server_ports:
                local_interface = "Ethernet" + sport.slot_id + "/" + sport.port_id
                if sport.oper_state != "up" or sport.peer_dn is '':
                    print(
                        "Either server port " +
                        local_interface +
                        " is down or peer is not connected")
                    continue
                conn = {}
                remote_device = sport.peer_dn.split('/')[1]
                if remote_device.split('-')[0] == 'rack':
                    adaptor_info = re.search('adaptor-(.+)/ext-eth-(.+)', sport.peer_dn)
                    if adaptor_info is not None:
                        remote_port = adaptor_info.groups()
                        remote_interface = "Ethernet" + remote_port[0] + "/" + remote_port[1]
                    else:
                        loginfo(
                            "Unable to get the adaptor details for the server %s" %
                            remote_device)
                        remote_interface = ''
                elif remote_device.split('-')[0] == 'chassis':
                    remote_interface = "IOM" + sport.peer_slot_id + "/" + sport.peer_port_id
                else:
                    remote_interface = None
                conn = dict(
                    local_interface=local_interface,
                    local_device=sport.dn.split('/')[1],
                    remote_interface=remote_interface,
                    remote_device=remote_device,
                    type='Server',
                    state=sport.oper_state,
                    speed=sport.oper_speed)
                fi_connections.append(conn)
            return fi_connections
        except UcsException as e:
            loginfo(str(e))
            return None
        except Exception as e:
            loginfo(str(e))
            return None

    def get_fc_port_detail(self, switch_id, fc_id):
        if self.handle is None or self.handle_status != True:
            return None

        try:
            mo = self.handle.query_classid('FcPIo')
            slot, port = [re.sub(r"\D", "", x) for x in fc_id.split('/')]
            fc_detail = [{'interface_id': fc_id,
                          'speed': k.oper_speed,
                          'state': k.oper_state,
                          'type': k.transport.upper(),
                          'pc_member': k.is_port_channel_member,
                          'pc': {'id': 'Po' + re.compile('pc-(.+)/ep-slot').search(k.ep_dn).group(1),
                                 'type': 'FC PC'} if (k.is_port_channel_member and k.is_port_channel_member != 'no') else None,
                          'unified_port': k.unified_port} for k in mo if k.slot_id == slot and k.port_id == port and k.switch_id == switch_id][0]
            return fc_detail
        except UcsException as e:
            loginfo(str(e))
            return None

    def get_ethernet_port_detail(self, switch_id, ether_id):
        if self.handle is None or self.handle_status != True:
            return None

        try:
            mo = self.handle.query_classid('EtherPIo')
            slot, port = [re.sub(r"\D", "", x) for x in ether_id.split('/')]
            ether_detail = [
                {
                    'interface_id': ether_id,
                    'speed': k.oper_speed,
                    'state': k.oper_state,
                    'type': 'Ethernet' if k.transport == 'ether' else k.transport,
                    'pc': {
                        'id': 'Po' + re.compile('pc-(.+)/ep-slot').search(
                            k.ep_dn).group(1),
                        'type': 'Eth PC'} if (
                        k.is_port_channel_member and k.is_port_channel_member != 'no') else None} for k in mo if k.slot_id == slot and k.port_id == port and k.switch_id == switch_id][0]
            return ether_detail
        except UcsException as e:
            loginfo(str(e))
            return None

    def get_lan_neighbors(self, switch_id):
        lan_neighbors = []
        if self.handle is None or self.handle_status != True:
            return None

        parent_mo = "sys/switch-" + switch_id + "/lan-neighbors"
        try:
            mo = self.handle.query_dn(parent_mo)
            if mo is None:
                print("Unable to fetch lan-neighbors")
                return lan_neighbors

            LNlist = self.handle.query_children(in_mo=mo)
            keys_list = [
                "device_id",
                "system_name",
                "serial_number",
                "local_interface",
                "remote_interface"]
            cdp_remote_list = [dict((k, getattr(hw, k)) for k in keys_list) for hw in LNlist]

            for hw in cdp_remote_list:
                neighbor = {}
                port_detail = self.get_ethernet_port_detail(switch_id, hw['local_interface'])
                neighbor = {'local_interface': hw['local_interface'],
                            'remote_interface': hw['remote_interface'],
                            'remote_device': re.compile(r'(.+)\(').search(hw['device_id']).group(1),
                            'type': port_detail['type'],
                            'speed': port_detail['speed'],
                            'pc': port_detail['pc'],
                            'state': port_detail['state']}
                lan_neighbors.append(neighbor)

            return lan_neighbors

        except UcsException as e:
            loginfo(str(e))
            return None

    def get_san_neighbors(self, switch_id):
        san_neighbors = []
        if self.handle is None or self.handle_status != True:
            return None

        parent_mo = "sys/switch-" + switch_id + "/san-neighbors"
        try:
            mo = self.handle.query_dn(parent_mo)
            if mo is None:
                print("Unable to fetch san-neighbors")
                return san_neighbors

            SNlist = self.handle.query_children(in_mo=mo)
            keys_list = [
                "my_pwwn",
                "my_nwwn",
                "local_interface",
                "fabric_mgmt_addr",
                "fabric_pwwn",
                "fabric_nwwn"]
            san_neighbors = [dict((k, getattr(hw, k)) for k in keys_list) for hw in SNlist]
            return san_neighbors
        except UcsException as e:
            loginfo(str(e))
            return None

    def get_san_pc_members(self, switch_id, pc_id):
        if self.handle is None or self.handle_status != True:
            return None

        try:
            mo = self.handle.query_classid('FcPIo')
            pc_fc_list = [k for k in mo if k.is_port_channel_member ==
                          "yes" and re.compile('pc-(.+)/ep-slot').search(k.ep_dn).group(1) == pc_id]
            pc_fc_list = ["fc" + k.slot_id + "/" + k.port_id for k in pc_fc_list]
            return pc_fc_list
        except UcsException as e:
            loginfo(str(e))
            return None
