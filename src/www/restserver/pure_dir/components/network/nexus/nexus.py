#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :nexus.py
# description     :Nexus class for helper functions
# author          :Guruprasad
# version         :1.0
#####################################################################

from pycsco.nxos.device import Device
from pycsco.nxos import error
from pycsco.nxos.utils.nxapi_lib import get_feature_list
import xmltodict
import json
import urllib2
import re
import copy

from pure_dir.infra.apiresults import PTK_CLIERROR, PTK_NOTEXIST, PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.utils.miscellaneous import find_dict_val, get_value


class Nexus:
    def __init__(self, ipaddress='', username='', password=''):
        """
        Constructor - Nexus Handler

        :param ipaddress: Switch ip
        :param username : Switch username
        :param password : Switch password
        """
        if ipaddress:
            self.handle = Device(
                ip=ipaddress, username=username, password=password)
        else:
            pass

    def nexus_switch_info(self):
        """
        Gets the nexus switch details

        :return: Returns the name, mac address and model
        """
        switch = {}
        switch['name'] = self.get_switchname()
        switch['mac_addr'] = self.get_mac_address()
        switch['model'], switch['serial_no'] = self.get_model_and_serial()
        if all(switch.values()):
            loginfo("Nexus Switch details: %s" % str(switch))
            return switch
        else:
            loginfo("Nexus partial switch details: %s" % str(switch))
            loginfo("Failed to retrieve nexus switch details fully")
            return switch

    def get_switchname(self):
        """
        Gets the nexus switch name

        :return: Returns the switch name
        """
        try:
            sys_op = self.handle.config('show switchname', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                switch_name = op_dict['ins_api']['outputs']['output']['body']
                return switch_name

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_mac_address(self):
        """
        Gets the nexus switch mac address

        :return: Returns the mac address
        """
        try:
            sys_op = self.handle.show('show interface mgmt0', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                mac_op = op_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface'][
                    'eth_hw_addr']
                mac_addr = ':'.join(re.findall('..', mac_op.replace('.', '')))
                return mac_addr

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_mac_address_table(self):
        """
        Gets the nexus switch name

        :return: Returns the switch name
        """
        try:
            sys_op = self.handle.show('show mac address-table', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                cdp_list = op_dict['ins_api']['outputs']['output']['body']['TABLE_mac_address']['ROW_mac_address']
                keys_list = ['disp_mac_addr', 'disp_port', 'disp_type']
                cdp_remote_list = [dict((k, hw[k])for k in keys_list) for hw in cdp_list]
                return cdp_remote_list

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_model_and_serial(self):
        """
        Gets the nexus switch model and serial number

        :return: Returns the model, serial number
        """
        try:
            sys_op = self.handle.show('show inventory chassis', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                sys_output = op_dict['ins_api']['outputs']['output']['body']['TABLE_inv']['ROW_inv']
                model = "Cisco " + sys_output['productid']
                serial_no = sys_output['serialnum']
                return model, serial_no

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_cdp_neighbours(self):
        """
        Gets the nexus switch name

        :return: Returns the switch name
        """
	neighbors = []
        try:
            sys_op = self.handle.show('show cdp neighbors', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                cdp_list = op_dict['ins_api']['outputs']['output']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
                keys_list = ['platform_id', 'device_id', 'intf_id', 'port_id']
                cdp_remote_list = [dict((k, hw[k])for k in keys_list)
                                   for hw in cdp_list if 'mgmt' not in hw['port_id']]

	        for hw in cdp_remote_list:
		    neighbor = {}
		    port_detail = self.get_interface_details(hw['intf_id'])
		    neighbor = {'local_interface': hw['intf_id'],
                                'remote_interface': hw['port_id'],
                                'remote_device': re.compile('(.+)\(').search(hw['device_id']).group(1),
			        'type': port_detail['type'],
			        'speed': port_detail['speed'],
			        'pc': port_detail['pc'],
			        'state': port_detail['state']}
		    neighbors.append(neighbor)
	        return neighbors

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_interface_list(self):
        """
        Gets the list of interfaces in nexus switch

        :return: Returns the interface list
        """
        eth_intf = []
        try:
            command = 'show interface brief'
            data = self.handle.show(command)
            data_dict = xmltodict.parse(data[1])
            interfaces = []
            intf_ret = data_dict['ins_api']['outputs']['output']['body'][
                'TABLE_interface']['ROW_interface']
            interfaces.append(intf_ret)

            for interface in interfaces[0]:
                if "Ethernet" in interface['interface']:
                    details = {}
                    details['label'] = "Eth" + interface['interface'][8:]
                    details['id'] = "Eth" + interface['interface'][8:]
                    details['selected'] = "0"
                    eth_intf.append(details)
            return eth_intf
        except BaseException:
            return eth_intf

    def get_interface_details(self, iface_id):
        """
        Gets the interface details

        :param iface_id: Interface id

        :return: Returns the interface list
        """
        iface_details = {}
        try:
            iface_op = self.handle.show(
                'show interface %s' % iface_id, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(iface_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(iface_op[1])
                iface_struct = op_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']
		iface_details['interface'] = iface_struct['interface']
                iface_details['speed'] = iface_struct['eth_speed']
                iface_details['media'] = iface_struct['eth_media']
		pc_id = iface_struct.get('eth_bundle', None)
	        if pc_id is not None:
		    iface_details['pc'] = [x for x in self.get_pc_list() if x['id']==pc_id][0]
                else:
		    iface_details['pc'] = None
                iface_details['state'] = iface_struct['state']
                iface_details['type'] = iface_struct['eth_hw_desc'].split(' ')[-1]
                return iface_details

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_n5k_fc_interface_details(self, iface_id):
        """
        Gets the interface details

        :param iface_id: Interface id

        :return: Returns the interface list
        """
        iface_details = {}
        try:
            iface_op = self.handle.show(
                'show interface %s' % iface_id, fmat='json', text=True)
            cli_error = self.handle.cli_error_check(json.loads(iface_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(iface_op[1])
                iface_struct = op_dict['ins_api']['outputs']['output']['body']
		iface_details['interface'] = re.search('(.*) is (.*)', iface_struct.split('\n')[0]).group(1) 
                iface_details['speed'] = re.search('.*Speed is (.*)\n', iface_struct).group(1)
                iface_details['media'] = re.search('.*Speed is (.*)\n', iface_struct).group(1)
		pc_id = re.search('.*Belongs to san-port-channel (.*)\n', iface_struct)
                if pc_id is not None:
		    iface_details['pc'] = [x for x in self.get_pc_list() if x['id']=='Po'+pc_id.group(1)][0]
                else:
		    iface_details['pc'] = None
                iface_details['state'] = re.search('(.*) is (.*)', iface_struct.split('\n')[0]).group(2)
                iface_details['type'] = re.search('.*Hardware is (.*),.*\n', iface_struct).group(1)
                return iface_details

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_slot_list(self):
        """
        Gets the list of slots in nexus switch

        :return: Returns the slot list
        """
        slots = []
        try:
            command = 'show interface brief'
            data = self.handle.show(command)
            data_dict = xmltodict.parse(data[1])
            interfaces = []
            intf_ret = data_dict['ins_api']['outputs']['output']['body'][
                'TABLE_interface']['ROW_interface']
            interfaces.append(intf_ret)

            tmp_list = []
            for interface in interfaces[0]:
                if "Ethernet" in interface['interface']:
                    tmp_list.append(interface['interface'].split('/')[0][-1])

            slot_list = list(set(tmp_list))
            for slot in slot_list:
                details = {}
                details['label'] = slot
                details['id'] = slot
                details['selected'] = "0"
                slots.append(details)

            return slots
        except BaseException:
            return slots

    def get_interfaces_in_slot(self, slot):
        """
        Gets the list of interfaces in a slot

        :return: Returns the list of interfaces in a slot
        """
        intf_list = []
        try:
            command = 'show interface brief'
            data = self.handle.show(command)
            data_dict = xmltodict.parse(data[1])
            interfaces = []
            intf_ret = data_dict['ins_api']['outputs']['output']['body'][
                'TABLE_interface']['ROW_interface']
            interfaces.append(intf_ret)

            tmp_list = []
            for interface in interfaces[0]:
                if "Ethernet" in interface['interface'] and interface['interface'].split(
                        '/')[0][-1] == slot:
                    tmp_list.append(
                        int(interface['interface'].split('/')[1]))

            eth_list = sorted(list(set(tmp_list)))

            details = {}
            slot_info = {"min_range": str(eth_list[0]), "max_range": str(
                eth_list[-1]), "max_fixed": "true", "min_interval": "8"}
            details['label'] = ""
            details['id'] = ""
            details['selected'] = str(eth_list[0]) + "-" + str(eth_list[-1])
            details['extrafields'] = json.dumps(slot_info)
            intf_list.append(details)
            return intf_list

        except BaseException:
            return intf_list

    def get_features_list(self):
        """
        Gets the list of features available in nexus 9k switch

        :return: Returns the feature list
        """
        flist = []
        try:
            feature_list = get_feature_list(self.handle)
            for feature in feature_list:
                details = {}
                details['label'] = feature
                details['id'] = feature
                details['selected'] = "0"
                flist.append(details)
            return flist
        except BaseException:
            return flist

    def get_feature_list_n5k(self):
        """
        Gets the list of features available in nexus 5k switch

        :return: Returns the feature list
        """
        try:
            feat_list = []
            tmp_list = []
            feat_op = self.handle.config('show feature', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(feat_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(feat_op[1])
                feat_output = op_dict['ins_api']['outputs']['output']['body']
                for row in feat_output.split('\n')[2:-1]:
                    tmp_list.append(row.partition(' ')[0].encode('utf-8'))
                feat_list = list(set(tmp_list))
                flist = []
                for feature in feat_list:
                    details = {}
                    details['label'] = feature
                    details['id'] = feature
                    details['selected'] = "0"
                    flist.append(details)
                return flist

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return flist

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return flist

    def get_nexus_version(self):
        """
        Gets the firmware version from nexus switch

        :return: Returns the version
        """
        try:
            sys_op = self.handle.show('show version', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                version_details = op_dict['ins_api']['outputs']['output']['body']
                return version_details['rr_sys_ver']

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_nexus_sys_ks_version(self):
        """
        Gets the system and kickstart version from nexus switch

        :return: Returns the version
        """
        try:
	    version_details = {}
            sys_op = self.handle.show('show version', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                version_details_dict = op_dict['ins_api']['outputs']['output']['body']
		version_details['system_version'] = version_details_dict['rr_sys_ver'] 
		version_details['kickstart_version'] = version_details_dict['kickstart_ver_str']
		return version_details
        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None


    def configure_portchannel(self, handle, pc_id, interface_list):
        """
        Configures port-channel in nexus switch

        :param handle: Login handle of nexus switch
        :param pc_id: Port-Channel id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['interface %s' %
                        iface, 'channel-group %s force' % pc_id]
            cmds_to_string = ' ; '.join(commands)
            loginfo(cmds_to_string)
            try:
                conf_op = handle.config(cmds_to_string, fmat='json')
                cli_error = handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Port channel %s configured with interface " %
                            pc_id + iface + " successfully")
                    if self.configure_fcport(handle=handle, fc_id=iface).getStatus() == PTK_OKAY:
                        loginfo("FC interface %s activated" % iface)
                    else:
                        loginfo("Failed to activate FC port %s" % iface)

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(False, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(
            True, PTK_OKAY, "Port channel %s configured with interface list %s successfully" %
            (pc_id, str(interface_list)))
        return obj

    def configure_fcport(self, handle, fc_id, descr=""):
        """
        Configures the FC port in nexus switch

        :param handle: Login handle of nexus switch
        :param fc_id: FC port id
        :param descr: FC port description
        :return: Returns the port configuration status
        """
        obj = result()
        if descr == "":
            commands = ['interface %s' % fc_id,
                        'no shutdown']
        else:
            commands = ['interface %s' % fc_id, 'switchport description %s' % descr,
                        'no shutdown']
        cmds_to_string = ' ; '.join(commands)
        loginfo("Nexus: " + cmds_to_string)
        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: FC Port %s configured successfully" % fc_id)

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

        obj.setResult(True, PTK_OKAY,
                      "FC port %s configured" % fc_id)
        return obj

    def unconfigure_portchannel(self, handle, pc_id, interface_list):
        """
        Unbinds the interfaces from the port-channel in nexus switch

        :param handle: Login handle of nexus switch
        :param pc_id: Port-Channel id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['interface %s' %
                        iface, 'no channel-group %s' % pc_id]
            cmds_to_string = ' ; '.join(commands)
            loginfo(cmds_to_string)
            try:
                conf_op = handle.config(cmds_to_string, fmat='json')
                cli_error = handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Interface %s deleted from Port channel" %
                            iface + pc_id + " successfully")

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(False, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY, "Interfaces %s deleted from Port channel %s" % (
            str(interface_list), pc_id))
        return obj

    def get_portchannel_list(self):
        """
        Gets the list of port-channels in nexus switch

        :return: Returns the port-channel list
        """
        obj = result()
        iface_list = []
        try:
            pc_op = self.handle.config('show interface brief', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(pc_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(pc_op[1])
                iface_output = op_dict['ins_api']['outputs']['output']['body']
                for row in iface_output.split('\n'):
                    if row.startswith('san-port-channel'):
			iface_dict = {}
                        tmp_list = [x for x in row.split(' ') if x != '']
                        iface_dict['iface_id'] = tmp_list[1].encode('utf-8')
                        iface_list.append(iface_dict)
		    else:
			continue

                obj.setResult(iface_list, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(iface_list, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(iface_list, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def get_ether_portchannel_list(self):
        vpc_list = []
        try:
            vpc_op = self.handle.show('show vpc brief', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(vpc_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(vpc_op[1])
                vpc = op_dict['ins_api']['outputs']['output']['body']
                vpc_interfaces = vpc['TABLE_vpc']['ROW_vpc']
                if type(vpc_interfaces) == dict:
                    vpc_interfaces = [vpc_interfaces]
                for x in vpc_interfaces:
                    if x['vpc-port-state'] in ['enabled', '1']:
                        vpc_list.append({'id':str(x['vpc-ifindex']), 'type':'vPC'})

                vpc_peer_interfaces = vpc['TABLE_peerlink']['ROW_peerlink']
                if type(vpc_peer_interfaces) == dict:
                    vpc_peer_interfaces = [vpc_peer_interfaces]
                for x in vpc_peer_interfaces:
                    if x['peer-link-port-state'] in ['enabled', '1']:
                        vpc_list.append({'id':str(x['peerlink-ifindex']), 'type':'vPC Peer'})
                return vpc_list

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return vpc_list

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return vpc_list

    def get_pc_list(self):
        fc_pc_list = self.get_portchannel_list().getResult() 
        fc_pc_list = [{'id':'Po'+str(x['iface_id']), 'type':'FC PC'} for x in fc_pc_list]
        eth_pc_list = self.get_ether_portchannel_list()
        pc_list = fc_pc_list + eth_pc_list
        return pc_list


    def getfc_list(self, slot, ports):
        """
        Gets the list of FC interfaces in nexus 5k switch

        :slot: Slot in nexus switch
        :ports: Corresponding ports in nexus switch

        :return: Returns the interface list
        """
        obj = result()
        iface_list = [{'iface_id': "fc" + slot + "/" + str(i)} for i in
                      range(int(ports.split('-')[0]), int(ports.split('-')[1]) + 1)]
        obj.setResult(iface_list, PTK_OKAY, "Success")
        return obj

    def get_fc_list(self, pc_bind=""):
        """
        Gets the list of FC interfaces in nexus 9k switch

        :param pc_bind: If True it returns the FC interfaces which are binded to port-channel

        :return: Returns the interface list
        """
        obj = result()
        iface_list = []
        try:
            pc_op = self.handle.config('show interface brief', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(pc_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(pc_op[1])
                iface_output = op_dict['ins_api']['outputs']['output']['body']
                for row in iface_output.split('\n'):
                    if row.startswith('fc'):
                        tmp_list = [x for x in row.split(' ') if x != '']
                        iface_dict = {}
                        iface_dict['iface_id'] = tmp_list[0].encode('utf-8')
                        iface_dict['iface_status'] = tmp_list[4].encode(
                            'utf-8')
                        iface_dict['iface_vsan'] = tmp_list[1].encode('utf-8')
                        iface_dict['iface_pc'] = tmp_list[-1].encode('utf-8')
                        iface_list.append(iface_dict)

                if pc_bind == "":
                    obj.setResult(iface_list, PTK_OKAY, "Success")
                    return obj
                else:
                    iface_pc_list = []
                    iface_notpc_list = []
                    for iface in iface_list:
                        if iface['iface_pc'] != "--":
                            iface_pc_list.append(iface)
                        else:
                            iface_notpc_list.append(iface)
                    if pc_bind:
                        loginfo(
                            "Nexus interface list which are binded to port channel: " + pc_bind + " are" + 
                            str([iface['iface_id'] for iface in iface_pc_list]))
                        obj.setResult(iface_pc_list, PTK_OKAY, "Success")
                        return obj
                    elif pc_bind == False:
                        loginfo(
                            "Nexus interface list which are not binded to port channel: " +
                            str([iface['iface_id'] for iface in iface_notpc_list]))
                        obj.setResult(iface_notpc_list, PTK_OKAY, "Success")
                        return obj
                    else:
                        loginfo(
                            "Nexus interface list: Invalid parameter %s" % pc_bind)
                        obj.setResult(iface_pc_list, PTK_NOTEXIST,
                                      "Invalid parameter")
                        return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(iface_list, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(iface_list, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def create_vsan(self, handle, vsan_id):
        """
        Creates VSAN in nexus switch

        :param handle: Login handle of nexus switch
        :param vsan_id: VSAN id

        :return: Returns the status
        """
        obj = result()
        commands = ['vsan database', 'vsan %s' % vsan_id,
                    'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo(cmds_to_string)
        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("VSAN %s created successfully" % vsan_id)
                obj.setResult(True, PTK_OKAY,
                              "VSAN %s created successfully" % vsan_id)
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def delete_vsan(self, handle, vsan_id):
        """
        Deletes VSAN in nexus switch

        :param handle: Login handle of nexus switch
        :param vsan_id: VSAN id

        :return: Returns the status
        """
        obj = result()
        commands = ['vsan database', 'no vsan %s' % vsan_id, 'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo(cmds_to_string)
        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("VSAN %s deleted successfully" % vsan_id)
                obj.setResult(True, PTK_OKAY,
                              "VSAN %s deleted successfully" % vsan_id)
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def configure_vsan(self, handle, vsan_id, interface_list):
        """
        Configures VSAN by adding the interfaces to VSAN in nexus switch

        :param handle: Login handle of nexus switch
        :param vsan_id: VSAN id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['vsan database', 'vsan %s interface %s' %
                        (vsan_id, iface), 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("NEXUS: " + cmds_to_string)

            try:
                conf_op = handle.config(cmds_to_string, fmat='json')
                cli_error = handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("VSAN %s configured with interface %s successfully" % (
                        vsan_id, iface))
                    if 'fc' in iface:
                        if self.configure_fcport(
                                handle=handle, fc_id=iface).getStatus() == PTK_OKAY:
                            loginfo("FC interface %s activated" % iface)
                        else:
                            loginfo("Failed to activate FC port %s" % iface)

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(False, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY, "VSAN %s configured with interface list %s successfully" % (
            vsan_id, str(interface_list)))
        return obj

    def unconfigure_vsan(self, handle, vsan_id, interface_list):
        """
        Unconfigures VSAN by removing the interfaces from VSAN in nexus switch

        :param handle: Login handle of nexus switch
        :param vsan_id: VSAN id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['vsan database', 'no vsan %s interface %s' %
                        (vsan_id, iface), 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo(": " + cmds_to_string)

            try:
                conf_op = handle.config(cmds_to_string, fmat='json')
                cli_error = handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Interface %s removed from vsan %s successfully" % (
                        iface, vsan_id))

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(False, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY, "Interfaces %s removed from VSAN %s successfully" % (
            str(interface_list), vsan_id))
        return obj

    def create_portchannel(self, handle, pc_id, descr=""):
        """
        Creates port-channel in nexus switch

        :param handle: Login handle of nexus switch
        :param pc_id: Port-Channel id
        :param descr: Port-Channel description

        :return: Returns the status
        """
        obj = result()
        if descr == "":
            commands = ['interface san-port-channel %s' % pc_id,
                        'channel mode active']
        else:
            commands = ['interface san-port-channel %s' % pc_id, 'switchport description' % descr,
                        'channel mode active']
        cmds_to_string = ' ; '.join(commands)
        loginfo(cmds_to_string)

        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Port channel %s created successfully" % pc_id)
                obj.setResult(True, PTK_OKAY,
                              "Port channel %s created successfully" % pc_id)
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def delete_portchannel(self, handle, pc_id):
        """
        Deletes port-channel in nexus switch

        :param handle: Login handle of nexus switch
        :param pc_id: Port-Channel id

        :return: Returns the status
        """
        obj = result()
        commands = ['no interface san-port-channel %s' % pc_id]
        cmds_to_string = ' ; '.join(commands)
        loginfo(cmds_to_string)

        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Port channel %s deleted successfully" % pc_id)
                obj.setResult(True, PTK_OKAY,
                              "Port channel %s deleted successfully" % pc_id)
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def create_device_aliases(self, handle, flogi_list):
        """
        Creates device aliases for pwwn in nexus switch

        :param handle: Login handle of nexus switch
        :param flogi_list: List of FLOGI

        :return: Returns the status
        """
        obj = result()
        for flogi in flogi_list:
            obj = self.create_alias(handle, flogi['alias'], flogi['pwwn'])
            if obj.getStatus() != PTK_OKAY:
                loginfo("Nexus: Device alias creation for %s failed" %
                        flogi['pwwn'])
                return obj
            else:
                loginfo("Nexus: Device alias %s created for pwwn %s successfully" % (
                    flogi['alias'], flogi['pwwn']))

        loginfo("Nexus: Device Aliases created based on flogi database")
        obj.setResult(True, PTK_OKAY, "Success")
        return obj

    def create_alias(self, handle, name, pwwn):
        """
        Creates device aliase for a pwwn in nexus switch

        :param handle: Login handle of nexus switch
        :param name: Alias name
        :param pwwn: Port WWN

        :return: Returns the status
        """
        obj = result()
        commands = ['device-alias database', 'device-alias name %s pwwn %s' % (name, pwwn),
                    'exit', 'device-alias commit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("Nexus create_device_alias: %s" % cmds_to_string)

        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo(
                    "Nexus: Device alias %s for pwwn  %s created successfully" % (name, pwwn))
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def create_zoneset(self, handle, name, vsan_id):
        """
        Creates a VSAN zoneset in nexus switch

        :param handle: Login handle of nexus switch
        :param name: Name of the zoneset
        :param vsan_id: VSAN id

        :return: Returns the zoneset creation status
        """
        obj = result()
        commands = ['zoneset name %s vsan %s' % (name, vsan_id), 'exit']
        cmds_to_string = ' ; '.join(commands)
        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: Zoneset name %s created with %s successfully" %
                        (name, vsan_id))
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def create_zone(self, handle, name, vsan_id):
        """
        Creates a VSAN zone in nexus switch

        :param handle: Login handle of nexus switch
        :param name: Name of the zone
        :param vsan_id: VSAN id

        :return: Returns the zone creation status
        """
        obj = result()
        commands = ['zone name %s vsan %s' % (name, vsan_id), 'exit']
        cmds_to_string = ' ; '.join(commands)
        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: Zone name %s created with %s successfully" %
                        (name, vsan_id))
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def delete_zone(self, handle, name, vsan_id=""):
        """
        Deletes a VSAN zone in nexus switch

        :param handle: Login handle of nexus switch
        :param name: Name of the zone
        :param vsan_id: VSAN id

        :return: Returns the zone deletion status
        """
        obj = result()
        if vsan_id == "":
            vsan_id = self.get_vsanid_for_zone(name)
            if vsan_id == -1:
                loginfo("Nexus: Zone %s not present" % name)
                obj.setResult(False, PTK_NOTEXIST, "Zone not present in Nexus")
                return obj

        try:
            conf_op = handle.config(
                'no zone name %s vsan %s' % (name, vsan_id), fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: Zone name %s deleted with %s successfully" %
                        (name, vsan_id))
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def delete_zoneset(self, handle, name, vsan_id=""):
        """
        Deletes a VSAN zoneset in nexus switch

        :param handle: Login handle of nexus switch
        :param name: Name of the zoneset
        :param vsan_id: VSAN id

        :return: Returns the zoneset creation status
        """
        obj = result()
        if vsan_id == "":
            vsan_id = self.get_vsanid_for_zoneset(name)
            if vsan_id == -1:
                loginfo("Nexus: Zoneset %s not present" % name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in Nexus")
                return obj

        try:
            conf_op = handle.config(
                'no zoneset name %s vsan %s' % (name, vsan_id), fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: Zoneset %s with vsan %s deleted successfully" %
                        (name, vsan_id))
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def delete_device_aliases(self, handle, alias_list):
        """
        Deletes device aliases in nexus switch

        :param handle: Login handle of nexus switch
        :param alias_list: List of device aliases

        :return: Returns the status
        """
        obj = result()
        for alias in alias_list:
            obj = self.delete_alias(handle, alias)
            if obj.getStatus() != PTK_OKAY:
                loginfo("Nexus: Device alias deletion for %s failed" % alias)
                return obj
            else:
                loginfo("Nexus: Device alias %s deleted successfully" % alias)

        loginfo("Nexus: Device Aliases %s deleted successfully" %
                str(alias_list))
        obj.setResult(True, PTK_OKAY, "Success")
        return obj

    def delete_alias(self, handle, name):
        """
        Deletes device aliase for a pwwn in nexus switch

        :param handle: Login handle of nexus switch
        :param name: Alias name

        :return: Returns the status
        """
        obj = result()
        commands = ['device-alias database', 'no device-alias name %s' % name,
                    'exit', 'device-alias commit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("Nexus delete_device_alias: %s" % cmds_to_string)

        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo(
                    "Nexus: Device alias %s deleted successfully" % name)
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def get_flogi_sessions(self):
        """
        Gets the list of FLOGI sessions in nexus switch

        :return: Returns the FLOGI list
        """
        obj = result()
        flogi_sessions = []
        try:
            flogi_op = self.handle.config('show flogi database', fmat='json')
            op_dict = json.loads(flogi_op[1])
            flogi_output = op_dict['ins_api']['outputs']['output']['body']
            loginfo("Getting flogi sessions")
            for row in flogi_output.split('\n'):
                if row.startswith('fc') or row.startswith('San-po'):
                    tmp_list = [x for x in row.split(' ') if x != '']
                    flogi_dict = {}
                    flogi_dict['iface_id'] = tmp_list[0].encode('utf-8')
                    flogi_dict['vsan_id'] = tmp_list[1].encode('utf-8')
                    flogi_dict['fcid'] = tmp_list[2].encode('utf-8')
                    flogi_dict['pwwn'] = tmp_list[3].encode('utf-8')
                    flogi_dict['nwwn'] = tmp_list[4].encode('utf-8')
                    flogi_sessions.append(flogi_dict)

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(flogi_sessions, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(flogi_sessions, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

        loginfo("Total flogi sessions is %s" % str(len(flogi_sessions)))
        obj.setResult(flogi_sessions, PTK_OKAY, "Success")
        return obj

    def get_vsan_list(self):
        """
        Gets the list of VSANs in nexus switch

        :return: Returns the VSAN list
        """
        obj = result()
        try:
            vsan_list = []
            vsan_op = self.handle.config('show vsan usage', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(vsan_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(vsan_op[1])
                vsan_output = op_dict['ins_api']['outputs']['output']['body']
                vsan_list = [lst.split(':')[1].encode('utf-8').split(',')
                             for lst in vsan_output.split('\n') if 'configured vsans:' in lst][0]
                loginfo("Nexus vsan list: " + str(vsan_list))
                obj.setResult(vsan_list, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(vsan_list, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(vsan_list, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def get_vsanid_for_zone(self, name):
        """
        Gets a VSAN id for a zone in nexus switch

        :param name: Name of the zone

        :return: Returns the VSAN id
        """
        zone_list = self.get_zone_list()
        for zone in zone_list:
            if zone['name'] == name:
                return zone['vsan_id']
        loginfo("Nexus: Zone %s not present" % name)
        return -1

    def get_vsanid_for_zoneset(self, name):
        """
        Gets a VSAN id for a zoneset in nexus switch

        :param name: Name of the zoneset

        :return: Returns the VSAN id
        """
        zoneset_list = self.get_zoneset_list()
        for zoneset in zoneset_list:
            if zoneset['name'] == name:
                return zoneset['vsan_id']
        loginfo("Nexus: Zoneset %s not present" % name)
        return -1

    def get_zone_list(self):
        """
        Gets the zone list in nexus switch

        :return: Returns the zone list
        """
        obj = result()
        try:
            zone_list = []
            zone_op = self.handle.config('show zone', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(zone_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(zone_op[1])
                zone_output = op_dict['ins_api']['outputs']['output']['body']
                for zone in zone_output.split('\n'):
                    if zone != "" and "not present" not in zone:
                        zone_dict = {}
                        zone_dict['name'] = zone.split(' ')[2]
                        zone_dict['vsan_id'] = zone.split(' ')[4]
                        zone_list.append(zone_dict)
                loginfo("Nexus zone list: " + str(zone_list))
                obj.setResult(zone_list, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(zone_list, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(zone_list, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def get_zoneset_list(self):
        """
        Gets the zoneset list in nexus switch

        :return: Returns the zoneset list
        """
        obj = result()
        try:
            zoneset_list = []
            zoneset_op = self.handle.config('show zoneset', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(zoneset_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(zoneset_op[1])
                zoneset_output = op_dict['ins_api']['outputs']['output']['body']
                for zoneset in zoneset_output.split('\n'):
                    if zoneset != "" and "not present" not in zoneset and "zoneset" in zoneset:
                        zoneset_dict = {}
                        zoneset_dict['name'] = zoneset.split(' ')[2]
                        zoneset_dict['vsan_id'] = zoneset.split(' ')[4]
                        zoneset_list.append(zoneset_dict)
                loginfo("Nexus zoneset list: " + str(zoneset_list))
                obj.setResult(zoneset_list, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(zoneset_list, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(zoneset_list, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def add_to_zone(self, handle, zone_name, members, vsan_id=''):
        """
        Configure a VSAN zone in nexus switch by adding ports' pwwn to the zone

        :param handle: Login handle of nexus switch
        :param zone_name: Name of the zone
        :param members: List of zone pwwn/device-aliases
        :param vsan_id: VSAN id

        :return: Returns the status
        """
        obj = result()
        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zone(zone_name)
            if vsan_id == -1:
                loginfo("Nexus: Zone %s not present" % zone_name)
                obj.setResult(False, PTK_NOTEXIST, "Zone not present in Nexus")
                return obj

        for member in members:
            commands = ['zone name %s vsan %s' % (
                zone_name, vsan_id), 'member device-alias %s' % member, 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("Nexus: add_to_zone: %s" % cmds_to_string)
            try:
                conf_op = handle.config(cmds_to_string, fmat='json')
                cli_error = handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Nexus: Device %s added to zone %s successfully" %
                            (member, zone_name))

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(False, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY, "Members %s added to zone %s successfully" % (
            str(members), zone_name))
        return obj

    def add_to_zoneset(self, handle, zoneset_name, members, vsan_id=''):
        """
        Configure a VSAN zoneset in nexus switch by adding zones to the zoneset

        :param handle: Login handle of nexus switch
        :param zoneset_name: Name of the zoneset
        :param members: List of zones
        :param vsan_id: VSAN id

        :return: Returns the status
        """
        obj = result()

        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("Nexus: Zoneset %s not present" % zoneset_name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in Nexus")
                return obj

        for member in members:
            commands = ['zoneset name %s vsan %s' %
                        (zoneset_name, vsan_id), 'member %s' % member, 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("Nexus: add_to_zoneset: %s" % cmds_to_string)
            try:
                conf_op = handle.config(cmds_to_string, fmat='json')
                cli_error = handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Nexus: Zone %s added to zoneset %s successfully" % (
                        member, zoneset_name))

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(False, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY, "Zones %s added to zoneset %s successfully" % (
            str(members), zoneset_name))
        return obj

    def activate_zoneset(self, handle, zoneset_name, vsan_id=''):
        """
        Activate a VSAN zoneset in nexus switch

        :param handle: Login handle of nexus switch
        :param zoneset_name: Name of the zoneset
        :param vsan_id: VSAN id

        :return: Returns the zoneset activation status
        """
        obj = result()

        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("Nexus: Zoneset %s not present" % zoneset_name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in Nexus")
                return obj

        commands = ['zoneset activate name %s vsan %s' %
                    (zoneset_name, vsan_id), 'copy run start', 'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("Nexus: activate_zoneset: %s" % cmds_to_string)

        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: Zoneset %s activated successfully" %
                        zoneset_name)
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def deactivate_zoneset(self, handle, zoneset_name, vsan_id=''):
        """
        Deactivate a VSAN zoneset in nexus switch

        :param handle: Login handle of nexus switch
        :param zoneset_name: Name of the zoneset
        :param vsan_id: VSAN id

        :return: Returns the zoneset deactivation status
        """
        obj = result()

        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("Nexus: Zoneset %s not present" % zoneset_name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in Nexus")
                return obj

        commands = ['no zoneset activate name %s vsan %s' %
                    (zoneset_name, vsan_id), 'copy run start', 'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("Nexus: deactivate_zoneset: %s" % cmds_to_string)

        try:
            conf_op = handle.config(cmds_to_string, fmat='json')
            cli_error = handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("Nexus: Zoneset %s deactivated successfully" %
                        zoneset_name)
                obj.setResult(True, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(False, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(False, PTK_NOTEXIST, "Could not connect to switch")
            return obj

    def fieldvalidation(self, value):
        """
        Validates whether value is an integer

        :param value: Value to be validated

        :return: Returns the status
        """
        try:
            val = int(value)
            return True, ""
        except ValueError:
            return False, "Enter Valid Number"

    def get_allowed_vlans(self, vlan_list):
        """
        Gets the allowed vlans from the vlan list

        :param vlan_list: Vlan list

        :return: Returns allowed vlans list
        """
        vlans = vlan_list.split('|')
        allowed_vlans = []
        for vlan in vlans:
            data = eval(vlan)
            allowed_vlans.append(data['vlan']['value'])
        return (',').join(allowed_vlans)

    def change_password(self, password):
        """
        Changes the Nexus password

        :param password: Password of the nexus switch

        :return: Returns the status
        """
        try:
            cmd = "username admin password %s" % password
            sys_op = self.handle.config(cmd, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                loginfo("Failed to set Nexus password")
                loginfo("CLI error")
                return False
            else:
                return True

        except error.CLIError as e:
            loginfo("Failed to set Nexus password")
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return False

        except urllib2.URLError as e:
            loginfo("Failed to set Nexus password")
            loginfo("Error msg: " + str(e.reason))
            return False

    def nexus_uptime(self):
        """
        nexus report helper function
        returns system uptime
        """
        nexus_uptime = {}
        try:
            nexus_out = self.handle.show('show system uptime', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(nexus_out[1]))
            if cli_error:
                raise cli_error
            else:
                out_dict = json.loads(nexus_out[1])
                nexus_sys = out_dict['ins_api']['outputs']['output']['body']
                nexus_uptime['uptime'] = (str(nexus_sys['sys_up_days']) + " days," + str(nexus_sys['sys_up_hrs']) + " hrs," +
                                           str(nexus_sys['sys_up_mins']) + " mins," + str(nexus_sys['sys_up_secs']) + " secs")
                return nexus_uptime
        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None


    def nexus_command(self, cmd, key, **kwargs):
        """
        report helper function helps to execute a command on mds
        return: value of given key
        """
        try:
            nexus_out = self.handle.show(cmd, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(nexus_out[1]))
            if cli_error:
                raise cli_error
            else:
                out_dict = json.loads(nexus_out[1])
                dict_value = get_value(key, out_dict, **kwargs)
                return dict_value

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def nexus_config_command(self, cmd, key, **kwargs):
        """
        report helper function helps to execute a command on mds
        return: value of given key
        """
        try:
            nexus_out = self.handle.config(cmd, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(nexus_out[1]))
            if cli_error:
                raise cli_error
            else:
                out_dict = json.loads(nexus_out[1])
                dict_value = get_value(key, out_dict, **kwargs)
                return dict_value

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def nexus_vsan_details(self):
        """
        get nexus5k vsan details
        return: vsan_name, vsan state, interoperability mode, vsan operational state
        """
        nexus_vsan_details = []
        list_out = []
        tmp_list = []
        try:
            nexus_out = self.handle.config('show vsan', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(nexus_out[1]))
            if cli_error:
                raise cli_error
            else:
                out_dict = json.loads(nexus_out[1])
                nexus_sys = out_dict['ins_api']['outputs']['output']['body']
                nexus_val = nexus_sys.encode('utf-8').split('\n')
                for val in nexus_val:
                    vsan_elem = val.strip(' ')
                    if "name" in vsan_elem:
                        rep = vsan_elem.replace('state', 'vsan_state')
                        [tmp_list.append(i) for i in rep.split(' ') if "" != i]
                    else:
                        if ":" in val:
                            tmp_list.append(val.strip())
 
                tmp_dict = {'vsan_name': [], 'vsan_interop_mode': [], 'vsan_load_balancing': [],
                            'vsan_operational_state': [], 'vsan_state': []}
                for elem in tmp_list:
                    if "name" in elem:
                        tmp_dict['vsan_name'].append(elem.split(':')[-1])
                    elif "interoperability" in elem:
                        tmp_dict['vsan_interop_mode'].append(elem.split(':')[-1])
                    elif "loadbalancing" in elem:
                        tmp_dict['vsan_load_balancing'].append(elem.split(':')[-1])
                    elif "operational" in elem:
                        tmp_dict['vsan_operational_state'].append(elem.split(':')[-1])
                    elif "vsan_state" in elem:
                        tmp_dict['vsan_state'].append(elem.split(':')[-1])
                
                final_dict={}
                for i in range(len(tmp_dict['vsan_name'])):
                    final_dict['vsan_name'] = tmp_dict['vsan_name'][i]
                    final_dict['vsan_interop_mode'] = tmp_dict['vsan_interop_mode'][i]
                    final_dict['vsan_load_balancing'] = tmp_dict['vsan_load_balancing'][i]
                    final_dict['vsan_operational_state'] = tmp_dict['vsan_operational_state'][i]
                    final_dict['vsan_state'] = tmp_dict['vsan_state'][i]
                    nexus_vsan_details.append(copy.deepcopy(final_dict))
                return nexus_vsan_details
        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def nexus_zoneset_details(self):
        """
        get nexus5k vsan details
        return: vsan_name, vsan state, interoperability mode, vsan operational state
        """
        zoneset_details = []
        tmp_list = []
        try:
            nexus_out = self.handle.config('show zone', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(nexus_out[1]))
            if cli_error:
                raise cli_error
            else:
                out_dict = json.loads(nexus_out[1])
                nexus_sys = out_dict['ins_api']['outputs']['output']['body']
                tmp_val = nexus_sys.encode('utf-8').split('\n')
                nexus_val = [i.strip() for i in tmp_val]
                for i in nexus_val:
                    if 'pwwn' in i:
                        tmp_list.append(i.split('[')[0].rstrip())
                    elif 'vsan' in i:
                        tmp_list.append(i.split('vsan')[0].rstrip().split('zone')[1].lstrip())
                    else:
                        tmp_list.append(i)

                name_l = []
                pwwn_l = []            
                for i in tmp_list:
                    if 'name' in i:
                        name_l.append(i.split(' ')[1])
                    elif 'pwwn' in i:
                        pwwn_l.append(i.split(' ')[1])
                    elif i == '':
                        pwwn_l.append(' ')
                
                for i in range(len(name_l)):
                    dicto = {'zone_name' : "", 'wwn' : []}
                    dicto['zone_name'] = name_l[i]
                    for j in range(i,i+5):
                        dicto['wwn'].append(pwwn_l[j])
                    zoneset_details.append(copy.deepcopy(dicto))
                return zoneset_details
        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def feature_list(self):
        """
        Gets the nexus feature list for nexus5k

        :return: status of lacp, vpc,interface-vlan
        """
        nexus_sys = {}
        tmp_list = []
        try:
            sys_op = self.handle.config('show feature', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                sys_output = op_dict['ins_api']['outputs']['output']['body']
                nexus_val = sys_output.encode('utf-8').split("\n")
                for i in nexus_val:
                    val=i.split(" ")
                    str_list = list(filter(None, val))
                    tmp_list.append("".join([g for g in str_list]))
                
                for i in tmp_list:
                    if "lacp" in i:
                        nexus_sys['lacp'] = i.split('lacp')[1][1:]
                    elif "vpc" in i:
                        nexus_sys['vpc'] = i.split('vpc')[1][1:]
                    elif "interface-vlan" in i:
                        nexus_sys['interface-vlan'] = i.split('interface-vlan')[1][1:]
                return nexus_sys
        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None
