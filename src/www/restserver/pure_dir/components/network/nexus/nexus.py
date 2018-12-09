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

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *


class Nexus:
    def __init__(self, ipaddress='', username='', password=''):
        # TODO: Get the switch details from xml
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
        if all(switch.values()) == True:
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
        except:
            return eth_intf

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
        except:
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

            for interface in interfaces[0]:
                if "Ethernet" in interface['interface'] and interface['interface'].split('/')[0][-1] == slot:
                    tmp_list.append(int(interface['interface'].split('/')[0][-1]))

            eth_list = sorted(list(set(tmp_list)))

            details = {}
            slot_info = {"min_range": str(eth_list[0]), "max_range": str(eth_list[-1]), "max_fixed": "true",
                         "min_interval": "8"}
            details['label'] = ""
            details['id'] = ""
            details['selected'] = str(eth_list[0]) + "-" + str(eth_list[-1])
            details['extrafields'] = json.dumps(slot_info)
            intf_list.append(details)
            return intf_list

        except:
            return intf_list

    def get_features_list(self):
        """
        Gets the list of features available in nexus switch

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
        except:
            return flist

    def get_feature_list_n5k(self):
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

    def configure_portchannel(self, handle, pc_id, interface_list):
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

        obj.setResult(True, PTK_OKAY, "Port channel %s configured with interface list %s successfully" % (
            pc_id, str(interface_list)))
        return obj

    def configure_fcport(self, handle, fc_id, descr=""):
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
                        tmp_list = [x for x in row.split(' ') if x != '']
                        iface_dict = {}
                        iface_dict['iface_id'] = tmp_list[1].encode('utf-8')
                        iface_list.append(iface_dict)

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

    def getfc_list(self, slot, ports):
        obj = result()
        iface_list = [{'iface_id': "fc" + slot + "/" + str(i)} for i in
                      range(int(ports.split('-')[0]), int(ports.split('-')[1]) + 1)]
        obj.setResult(iface_list, PTK_OKAY, "Success")
        return obj

    def get_fc_list(self, pc_bind=""):
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
                        iface_dict['iface_status'] = tmp_list[4].encode('utf-8')
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
                    if pc_bind == True:
                        loginfo(
                                "Nexus interface list which are binded to port channel: " + str(iface_pc_list))
                        obj.setResult(iface_pc_list, PTK_OKAY, "Success")
                        return obj
                    elif pc_bind == False:
                        loginfo(
                                "Nexus interface list which are not binded to port channel: " + str(iface_notpc_list))
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

        obj.setResult(True, PTK_OKAY, "VSAN %s configured with interface list %s successfully" % (
            vsan_id, str(interface_list)))
        return obj

    def unconfigure_vsan(self, handle, vsan_id, interface_list):
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
        obj = result()
        if vsan_id == "":
            vsan_id = get_vsanid_for_zone(name)
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
        obj = result()
        if vsan_id == "":
            vsan_id = get_vsanid_for_zoneset(name)
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
                vsan_list = [lst.split(':')[1].encode('utf-8').split(',') for lst in vsan_output.split('\n') if
                             'configured vsans:' in lst][0]
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
        zone_list = get_zone_list()
        for zone in zone_list:
            if zone['name'] == name:
                return zone['vsan_id']
        loginfo("Nexus: Zone %s not present" % name)
        return -1

    def get_vsanid_for_zoneset(self, name):
        zoneset_list = get_zoneset_list()
        for zoneset in zoneset_list:
            if zoneset['name'] == name:
                return zoneset['vsan_id']
        loginfo("Nexus: Zoneset %s not present" % name)
        return -1

    def get_zone_list(self):
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
        obj = result()
        if vsan_id == '':
            vsan_id = get_vsanid_for_zone(zone_name)
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
        obj = result()

        if vsan_id == '':
            vsan_id = get_vsanid_for_zoneset(zoneset_name)
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
                    loginfo("Nexus: Zone %s added to zoneset %s successfully" % (member, zoneset_name))

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
        obj = result()

        if vsan_id == '':
            vsan_id = get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("Nexus: Zoneset %s not present" % name)
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
        obj = result()

        if vsan_id == '':
            vsan_id = get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("Nexus: Zoneset %s not present" % name)
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
        try:
            val = int(value)
            return True, ""
        except ValueError:
            return False, "Enter Valid Number"

    def get_allowed_vlans(self, vlan_list):
        vlans = vlan_list.split('|')
	allowed_vlans = []
        for vlan in vlans:
            data = eval(vlan)
            allowed_vlans.append(data['vlan']['value'])
        return (',').join(allowed_vlans)

    def change_password(self, password):
        """
        Changes the Nexus password

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


