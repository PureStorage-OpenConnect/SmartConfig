#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :mds.py
# description     :MDS class for helper functions
# author          :Guruprasad
# version         :1.0
#####################################################################

from pycsco.nxos.device import Device
from pycsco.nxos import error
import json
import urllib2
import re

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo 


class MDS:
    def __init__(self, ipaddr, uname, passwd):
        """
        Constructor - MDS Handler

        :param ipaddress: Switch ip
        :param username : Switch username
        :param password : Switch password
        :param port     : Switch port
        """
        self.handle = Device(ip=ipaddr, username=uname,
                             password=passwd, port='8080')

    def mds_switch_info(self):
        """
        Gets the MDS switch details

        :return: Returns the name, mac address and model
        """
        switch = {}
        switch['name'] = self.get_switchname()
        switch['mac_addr'] = self.get_mac_address()
        switch['model'], switch['serial_no'] = self.get_model_and_serial()
        if all(switch.values()):
            loginfo("MDS Switch details: %s" % str(switch))
            return switch
        else:
            loginfo("MDS partial switch details: %s" % str(switch))
            loginfo("Failed to retrieve mds switch details fully")
            return switch

    def get_switchname(self):
        """
        Gets the MDS switch name

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
        Gets the MDS switch mac address

        :return: Returns the mac address
        """
        try:
            sys_op = self.handle.show('show interface mgmt0', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                mac_op = op_dict['ins_api']['outputs']['output']['body']['TABLE_interface_mgmt']['ROW_interface_mgmt']['address']
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
        Gets the MDS switch model and serial number

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
                model = "Cisco M" + sys_output['productid']
                serial_no = sys_output['serialnum']
                return model, serial_no

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return None

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return None

    def get_mds_version(self):
        """
        Gets the firmware version for the MDS switch

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

    def get_interface_list(self):
        """
        Gets the list of interfaces in MDS switch

        :return: Returns the interface list
        """
        obj = result()
        fc_list = self.get_fc_list().getResult()
        pc_list = self.get_portchannel_list().getResult()
        obj.setResult(fc_list + pc_list, PTK_OKAY, "Success")
        return obj

    def get_interface_details(self, iface_id):
        """
        Gets the interface details in MDS switch

        :param iface_id: Interface id

        :return: Returns the interface list
        """
        obj = result()
        iface_details = {}
        try:
            iface_op = self.handle.show(
                'show interface %s' % iface_id, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(iface_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(iface_op[1])
                iface_details['pwwn'] = op_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']['port_wwn']
                if 'port_mode' in op_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']:
                    iface_details['descr'] = op_dict['ins_api']['outputs']['output']['body']['TABLE_interface']['ROW_interface']['port_mode']
                else:
                    iface_details['descr'] = ""
                obj.setResult(iface_details, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(iface_details, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(iface_details, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def get_fc_list(self, pc_bind=""):
        """
        Gets the list of FC interfaces in MDS switch

        :param pc_bind: If True it returns the FC interfaces which are binded to port-channel

        :return: Returns the interface list
        """
        obj = result()
        iface_list = []
        try:
            pc_op = self.handle.show('show interface brief', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(pc_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(pc_op[1])
                iface_output = op_dict['ins_api']['outputs']['output']['body']['TABLE_interface_brief_fc']['ROW_interface_brief_fc']
                for iface in iface_output:
                    iface_dict = {}
                    iface_dict['iface_id'] = iface['interface_fc']
                    iface_dict['iface_status'] = iface['status']
                    iface_dict['iface_vsan'] = iface['vsan_brief']
                    iface_dict['iface_trunk_mode'] = iface['admin_trunk_mode']
                    #iface_extra = self.get_interface_details(iface_dict['iface_id']).getResult()
                    #iface_dict['iface_pwwn'] = iface_extra['pwwn']
                    #iface_dict['iface_descr'] = iface_extra['descr']
                    iface_dict['iface_pc'] = iface['port_channel']
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
                            "MDS interface list which are binded to port channel: " +
                            str(iface_pc_list))
                        obj.setResult(iface_pc_list, PTK_OKAY, "Success")
                        return obj
                    elif pc_bind == False:
                        loginfo(
                            "MDS interface list which are not binded to port channel: " +
                            str(iface_notpc_list))
                        obj.setResult(iface_notpc_list, PTK_OKAY, "Success")
                        return obj
                    else:
                        loginfo(
                            "MDS interface list: Invalid parameter %s" % pc_bind)
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

    def get_portchannel_list(self):
        """
        Gets the list of port-channels in MDS switch

        :return: Returns the port-channel list
        """
        obj = result()
        iface_list = []
        try:
            pc_op = self.handle.show('show interface brief', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(pc_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(pc_op[1])
                if 'TABLE_interface_brief_portchannel' not in op_dict['ins_api']['outputs']['output']['body']:
                    loginfo("MDS port-channel interface list: " + str(iface_list))
                    obj.setResult(iface_list, PTK_OKAY, "Success")
                    return obj
                pc_output = op_dict['ins_api']['outputs']['output']['body'][
                    'TABLE_interface_brief_portchannel']['ROW_interface_brief_portchannel']
                if isinstance(pc_output, dict):
                    iface_output = []
                    iface_output.append(pc_output)
                else:
                    iface_output = pc_output

                for iface in iface_output:
                    iface_dict = {}
                    iface_dict['iface_id'] = iface['interface']
                    iface_dict['iface_status'] = iface['status']
                    iface_dict['iface_vsan'] = iface['vsan_brief']
                    iface_dict['iface_trunk_mode'] = iface['admin_trunk_mode']
                    #iface_extra = self.get_interface_details(iface_dict['iface_id']).getResult()
                    #iface_dict['iface_pwwn'] = iface_extra['pwwn']
                    #iface_dict['iface_descr'] = iface_extra['descr']
                    iface_dict['iface_pc'] = iface['interface']
                    iface_list.append(iface_dict)
                loginfo("MDS port-channel interface list: " + str(iface_list))
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

    def configure_fcports(self, port_dict):
        """
        Configures the FC ports in MDS switch

        :param ports_dict: List of Dictionary(Port id, Port description)

        :return: Returns the port configuration status
        """
        obj = result()
	output_dict = {}
        for key, value in port_dict.items():
            commands = ['interface fc %s' % key, 'switchport description %s' % value,
                        'port-license acquire', 'no shutdown']
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: " + cmds_to_string)
            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("MDS: FC Port %s configured successfully" % key)

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(output_dict, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(output_dict, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(output_dict, PTK_OKAY,
                      "FC ports %s configured" % (str(port_dict.keys())))
        return obj

    def configure_fcport(self, fc_id, descr=""):
        """
        Configures the FC port in MDS switch

        :param fc_id: FC port id
        :param descr: FC port description

        :return: Returns the port configuration status
        """
        obj = result()
        if descr == "":
            commands = ['interface %s' % fc_id,
                        'port-license acquire', 'no shutdown']
        else:
            commands = ['interface %s' % fc_id, 'switchport description %s' % descr,
                        'port-license acquire', 'no shutdown']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: " + cmds_to_string)
        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: FC Port %s configured successfully" % fc_id)

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

    def get_vsan_list(self):
        """
        Gets the list of VSANs in MDS switch

        :return: Returns the VSAN list
        """
        obj = result()
        try:
            vsan_list = []
            vsan_op = self.handle.show('show vsan usage', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(vsan_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(vsan_op[1])
                vsan_output = op_dict['ins_api']['outputs']['output']['body']['configured_range_of_vsans']
                for vsan in vsan_output.split(','):
                    vsan_list.append(vsan)
                loginfo("MDS vsan list: " + str(vsan_list))
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

    def get_device_aliases(self):
        """
        Gets the list of device aliases in MDS switch

        :return: Returns the device-alias list
        """
        obj = result()
        try:
            devalias_list = []
            pc_op = self.handle.show('show device-alias database', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(pc_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(pc_op[1])
                devalias_output = op_dict['ins_api']['outputs']['output']['body'][
                    'TABLE_device_alias_database']['ROW_device_alias_database']
                for devalias in devalias_output:
                    devalias_dict = {}
                    devalias_dict['dev_alias_name'] = devalias['dev_alias_name']
                    devalias_dict['dev_pwwn'] = devalias['pwwn']
                    devalias_list.append(devalias_dict)
                loginfo("MDS device-alias list: " + str(devalias_list))
                obj.setResult(devalias_list, PTK_OKAY, "Success")
                return obj

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            obj.setResult(devalias_list, PTK_CLIERROR, str(e.err))
            return obj

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            obj.setResult(devalias_list, PTK_NOTEXIST,
                          "Could not connect to switch")
            return obj

    def get_flogi_sessions(self):
        """
        Gets the list of FLOGI sessions in MDS switch

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
                if row.startswith('fc') or row.startswith('port-channel'):
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

    def get_feature_list(self):
        """
        Gets the list of features available in MDS switch

        :return: Returns the feature list
        """
        feature_list = []
        try:
            sys_op = self.handle.show('show feature', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(sys_op[1])
                flist = op_dict['ins_api']['outputs']['output']['body']['TABLE_cfcFeatureCtrl2Table']['ROW_cfcFeatureCtrl2Table']
                for feature in flist:
                    feature_list.append(feature['cfcFeatureCtrlName2'])
                return feature_list

        except error.CLIError as e:
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return feature_list

        except urllib2.URLError as e:
            loginfo("Error msg: " + str(e.reason))
            return feature_list

    def enable_features(self, feature_list):
        """
        Enables features in MDS switch

        :param feature_list: List of features

        :return: Returns the status
        """
        obj = result()
        for fname in feature_list:
            try:
                conf_op = self.handle.config('feature %s' % fname, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Feature %s enabled successfully" % fname)

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(True, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY,
                      "Features %s enabled successfully" % str(feature_list))
        return obj

    def disable_features(self, feature_list):
        """
        Disables features in MDS switch

        :param feature_list: List of features

        :return: Returns the status
        """
        obj = result()
        for fname in feature_list:
            try:
                conf_op = self.handle.config(
                    'no feature %s' % fname, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Feature %s disabled successfully" % fname)

            except error.CLIError as e:
                loginfo("CLI Error: " + str(e.err))
                loginfo("Error msg: " + str(e.msg))
                obj.setResult(False, PTK_CLIERROR, str(e.err))
                return obj

            except urllib2.URLError as e:
                loginfo("Error msg: " + str(e.reason))
                obj.setResult(True, PTK_NOTEXIST,
                              "Could not connect to switch")
                return obj

        obj.setResult(True, PTK_OKAY,
                      "Features %s disabled successfully" % str(feature_list))
        return obj

    def create_portchannel(self, pc_id, descr=""):
        """
        Creates port-channel in MDS switch

        :param pc_id: Port-Channel id
        :param descr: Port-Channel description

        :return: Returns the status
        """
        obj = result()
        if descr == "":
            commands = ['interface port-channel %s' % pc_id,
                        'channel mode active', 'switchport rate-mode dedicated']
        else:
            commands = ['interface port-channel %s' % pc_id, 'switchport description' % descr,
                        'channel mode active', 'switchport rate-mode dedicated']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: " + cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
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

    def delete_portchannel(self, pc_id):
        """
        Deletes port-channel in MDS switch

        :param pc_id: Port-Channel id

        :return: Returns the status
        """
        obj = result()
        commands = ['no interface port-channel %s' % pc_id]
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: " + cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
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

    def configure_portchannel(self, pc_id, interface_list):
        """
        Configures port-channel in MDS switch

        :param pc_id         : Port-Channel id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['interface %s' %
                        iface, 'channel-group %s force' % pc_id]
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: " + cmds_to_string)
            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("Port channel %s configured with interface " %
                            pc_id + iface + " successfully")
                    if self.configure_fcport(fc_id=iface).getStatus() == PTK_OKAY:
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

    def unconfigure_portchannel(self, pc_id, interface_list):
        """
        Unbinds the interfaces from the port-channel in MDS switch

        :param pc_id         : Port-Channel id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['interface %s' %
                        iface, 'no channel-group %s' % pc_id]
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: " + cmds_to_string)
            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
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

    def create_vsan(self, vsan_id):
        """
        Creates VSAN in MDS switch

        :param vsan_id: VSAN id

        :return: Returns the status
        """
        obj = result()
        commands = ['vsan database', 'vsan %s' % vsan_id,
                    'exit', 'zone smart-zoning enable vsan %s' % vsan_id]
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: " + cmds_to_string)
        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
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

    def delete_vsan(self, vsan_id):
        """
        Deletes VSAN in MDS switch

        :param vsan_id: VSAN id

        :return: Returns the status
        """
        obj = result()
        commands = ['vsan database', 'no vsan %s' % vsan_id, 'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: " + cmds_to_string)
        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
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

    def configure_vsan(self, vsan_id, interface_list):
        """
        Configures VSAN by adding the interfaces to VSAN in MDS switch

        :param vsan_id       : VSAN id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['vsan database', 'vsan %s interface %s' %
                        (vsan_id, iface), 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: " + cmds_to_string)

            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("VSAN %s configured with interface %s successfully" % (
                        vsan_id, iface))
                    if 'fc' in iface:
                        if self.configure_fcport(fc_id=iface).getStatus() == PTK_OKAY:
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

    def unconfigure_vsan(self, vsan_id, interface_list):
        """
        Unconfigures VSAN by removing the interfaces from VSAN in MDS switch

        :param vsan_id       : VSAN id
        :param interface_list: Interfaces to be added to port-channel

        :return: Returns the status
        """
        obj = result()
        for iface in interface_list:
            commands = ['vsan database', 'no vsan %s interface %s' %
                        (vsan_id, iface), 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: " + cmds_to_string)

            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
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

    def create_device_aliases(self, flogi_list):
        """
        Creates device aliases for pwwn in MDS switch

        :param flogi_list: List of FLOGI

        :return: Returns the status
        """
        obj = result()
        for flogi in flogi_list:
            obj = self.create_alias(flogi['alias'], flogi['pwwn'])
            if obj.getStatus() != PTK_OKAY:
                loginfo("MDS: Device alias creation for %s failed" %
                        flogi['pwwn'])
                return obj
            else:
                loginfo("MDS: Device alias %s created for pwwn %s successfully" % (
                    flogi['alias'], flogi['pwwn']))

        loginfo("MDS: Device Aliases created based on flogi database")
        obj.setResult(True, PTK_OKAY, "Success")
        return obj

    def delete_device_aliases(self, alias_list):
        """
        Deletes device aliases in MDS switch

        :param alias_list: List of device aliases

        :return: Returns the status
        """
        obj = result()
        for alias in alias_list:
            obj = self.delete_alias(alias)
            if obj.getStatus() != PTK_OKAY:
                loginfo("MDS: Device alias deletion for %s failed" % alias)
                return obj
            else:
                loginfo("MDS: Device alias %s deleted successfully" % alias)

        loginfo("MDS: Device Aliases %s deleted successfully" %
                str(alias_list))
        obj.setResult(True, PTK_OKAY, "Success")
        return obj

    def create_alias(self, name, pwwn):
        """
        Creates device aliase for a pwwn in MDS switch

        :param name: Alias name
        :param pwwn: Port WWN

        :return: Returns the status
        """
        obj = result()
        commands = ['device-alias database', 'device-alias name %s pwwn %s' % (name, pwwn),
                    'exit', 'device-alias commit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS create_device_alias: %s" % cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo(
                    "MDS: Device alias %s for pwwn  %s created successfully" % (name, pwwn))
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

    def delete_alias(self, name):
        """
        Deletes device aliase for a pwwn in MDS switch

        :param name: Alias name

        :return: Returns the status
        """
        obj = result()
        commands = ['device-alias database', 'no device-alias name %s' % name,
                    'exit', 'device-alias commit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS delete_device_alias: %s" % cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo(
                    "MDS: Device alias %s deleted successfully" % name)
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

    def rename_alias(self, old_name, new_name):
        """
        Renames a device alias in MDS switch

        :param old_name: Old alias name
        :param new_name: New alias name

        :return: Returns the status
        """
        obj = result()
        commands = ['device-alias database', 'device-alias rename %s %s' % (old_name, new_name),
                    'exit', 'device-alias commit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS rename_device_alias: %s" % cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Device alias %s renamed to %s created successfully" % (
                    old_name, new_name))
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

    def get_zone_list(self):
        """
        Gets the zone list in MDS switch

        :return: Returns the zone list
        """
        obj = result()
        try:
            zone_list = []
            zone_op = self.handle.show('show zone', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(zone_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(zone_op[1])
                zone_output = op_dict['ins_api']['outputs']['output']['body']['TABLE_zone']['ROW_zone']
                for zone in zone_output:
                    zone_dict = {}
                    zone_dict['name'] = zone['zone_name']
                    zone_dict['vsan_id'] = zone['zone_vsan_id']
                    zone_list.append(zone_dict)
                loginfo("MDS zone list: " + str(zone_list))
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

    def get_vsan_zones(self, vsan_id):
        """
        Gets the zone list for a particular VSAN in MDS switch

        :param vsan_id: VSAN id

        :return: Returns the zone list
        """
        # CLI: self.handle.show('show zone vsan %s' % vsan_id, fmat='json')
        vsan_zones = []
        zone_list = self.get_zone_list()
        for zone in zone_list:
            if zone['vsan_id'] == vsan_id:
                zone_dict = {}
                zone_dict['name'] = zone['name']
                zone_dict['vsan_id'] = zone['vsan_id']
                vsan_zones.append(zone_dict)
        loginfo("MDS vsan zone list: " + str(vsan_zones))
        return vsan_zones

    def create_zone(self, name, vsan_id):
        """
        Creates a VSAN zone in MDS switch

        :param name   : Name of the zone
        :param vsan_id: VSAN id

        :return: Returns the zone creation status
        """
        obj = result()
        commands = ['zone name %s vsan %s' % (name, vsan_id), 'exit']
        cmds_to_string = ' ; '.join(commands)
        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Zone name %s created with %s successfully" %
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

    def add_to_zone(self, zone_name, members, vsan_id=''):
        """
        Configure a VSAN zone in MDS switch by adding ports' pwwn to the zone

        :param zone_name: Name of the zone
        :param members  : List of zone pwwn/device-aliases
        :param vsan_id  : VSAN id

        :return: Returns the status
        """
        obj = result()
        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zone(zone_name)
            if vsan_id == -1:
                loginfo("MDS: Zone %s not present" % zone_name)
                obj.setResult(False, PTK_NOTEXIST, "Zone not present in MDS")
                return obj

        for member in members:
            commands = ['zone name %s vsan %s' % (
                zone_name, vsan_id), 'member device-alias %s' % member, 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: add_to_zone: %s" % cmds_to_string)
            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("MDS: Device %s added to zone %s successfully" %
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

    def delete_zone(self, name, vsan_id=""):
        """
        Deletes a VSAN zone in MDS switch

        :param name   : Name of the zone
        :param vsan_id: VSAN id

        :return: Returns the zone deletion status
        """
        obj = result()
        if vsan_id == "":
            vsan_id = self.get_vsanid_for_zone(name)
            if vsan_id == -1:
                loginfo("MDS: Zone %s not present" % name)
                obj.setResult(False, PTK_NOTEXIST, "Zone not present in MDS")
                return obj

        try:
            conf_op = self.handle.config(
                'no zone name %s vsan %s' % (name, vsan_id), fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Zone name %s deleted with %s successfully" %
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

    def get_vsanid_for_zone(self, name):
        """
        Gets a VSAN id for a zone in MDS switch

        :param name: Name of the zone

        :return: Returns the VSAN id
        """
        zone_list = self.get_zone_list()
        for zone in zone_list:
            if zone['name'] == name:
                return zone['vsan_id']
        loginfo("MDS: Zone %s not present" % name)
        return -1

    def get_zoneset_list(self):
        """
        Gets the zoneset list in MDS switch

        :return: Returns the zoneset list
        """
        obj = result()
        try:
            zoneset_list = []
            zoneset_op = self.handle.show('show zoneset', fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(zoneset_op[1]))
            if cli_error:
                raise cli_error
            else:
                op_dict = json.loads(zoneset_op[1])
                zoneset_output = op_dict['ins_api']['outputs']['output']['body']['TABLE_zoneset']['ROW_zoneset']
                for zoneset in zoneset_output:
                    zoneset_dict = {}
                    zoneset_dict['name'] = zoneset['zoneset_name']
                    zoneset_dict['vsan_id'] = zoneset['zoneset_vsan_id']
                    zoneset_list.append(zoneset_dict)
                loginfo("MDS zoneset list: " + str(zoneset_list))
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

    def get_vsan_zonesets(self, vsan_id):
        """
        Gets the zoneset list for a particular VSAN in MDS switch

        :param vsan_id: VSAN id

        :return: Returns the zoneset list
        """
        # CLI: self.handle.show('show zoneset vsan %s' % vsan_id, fmat='json')
        vsan_zonesets = []
        zoneset_list = self.get_zoneset_list()
        for zoneset in zoneset_list:
            if zoneset['vsan_id'] == vsan_id:
                zoneset_dict = {}
                zoneset_dict['name'] = zoneset['name']
                zoneset_dict['vsan_id'] = zoneset['vsan_id']
                vsan_zonesets.append(zoneset_dict)
        return vsan_zonesets

    def create_zoneset(self, name, vsan_id):
        """
        Creates a VSAN zoneset in MDS switch

        :param name   : Name of the zoneset
        :param vsan_id: VSAN id

        :return: Returns the zoneset creation status
        """
        obj = result()
        commands = ['zoneset name %s vsan %s' % (name, vsan_id), 'exit']
        cmds_to_string = ' ; '.join(commands)
        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Zoneset name %s created with %s successfully" %
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

    def add_to_zoneset(self, zoneset_name, members, vsan_id=''):
        """
        Configure a VSAN zoneset in MDS switch by adding zones to the zoneset

        :param zoneset_name: Name of the zoneset
        :param members     : List of zones
        :param vsan_id     : VSAN id

        :return: Returns the status
        """
        obj = result()

        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("MDS: Zoneset %s not present" % zoneset_name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in MDS")
                return obj

        for member in members:
            commands = ['zoneset name %s vsan %s' %
                        (zoneset_name, vsan_id), 'member %s' % member, 'exit']
            cmds_to_string = ' ; '.join(commands)
            loginfo("MDS: add_to_zoneset: %s" % cmds_to_string)
            try:
                conf_op = self.handle.config(cmds_to_string, fmat='json')
                cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    raise cli_error
                else:
                    loginfo("MDS: Zone %s added to zoneset %s successfully" %
                            (member, zoneset_name))

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

    def delete_zoneset(self, name, vsan_id=""):
        """
        Deletes a VSAN zoneset in MDS switch

        :param name   : Name of the zoneset
        :param vsan_id: VSAN id

        :return: Returns the zoneset creation status
        """
        obj = result()
        if vsan_id == "":
            vsan_id = self.get_vsanid_for_zoneset(name)
            if vsan_id == -1:
                loginfo("MDS: Zoneset %s not present" % name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in MDS")
                return obj

        try:
            conf_op = self.handle.config(
                'no zoneset name %s vsan %s' % (name, vsan_id), fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Zoneset %s with vsan %s deleted successfully" %
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

    def activate_zoneset(self, zoneset_name, vsan_id=''):
        """
        Activate a VSAN zoneset in MDS switch

        :param zoneset_name: Name of the zoneset
        :param vsan_id     : VSAN id

        :return: Returns the zoneset activation status
        """
        obj = result()

        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("MDS: Zoneset %s not present" % zoneset_name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in MDS")
                return obj

        commands = ['zoneset activate name %s vsan %s' %
                    (zoneset_name, vsan_id), 'copy run start', 'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: activate_zoneset: %s" % cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Zoneset %s activated successfully" %
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

    def deactivate_zoneset(self, zoneset_name, vsan_id=''):
        """
        Deactivate a VSAN zoneset in MDS switch

        :param zoneset_name: Name of the zoneset
        :param vsan_id     : VSAN id

        :return: Returns the zoneset deactivation status
        """
        obj = result()

        if vsan_id == '':
            vsan_id = self.get_vsanid_for_zoneset(zoneset_name)
            if vsan_id == -1:
                loginfo("MDS: Zoneset %s not present" % zoneset_name)
                obj.setResult(False, PTK_NOTEXIST,
                              "Zoneset not present in MDS")
                return obj

        commands = ['no zoneset activate name %s vsan %s' %
                    (zoneset_name, vsan_id), 'copy run start', 'exit']
        cmds_to_string = ' ; '.join(commands)
        loginfo("MDS: deactivate_zoneset: %s" % cmds_to_string)

        try:
            conf_op = self.handle.config(cmds_to_string, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                raise cli_error
            else:
                loginfo("MDS: Zoneset %s deactivated successfully" %
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

    def get_vsanid_for_zoneset(self, name):
        """
        Gets a VSAN id for a zoneset in MDS switch

        :param name: Name of the zoneset

        :return: Returns the VSAN id
        """
        zoneset_list = self.get_zoneset_list()
        for zoneset in zoneset_list:
            if zoneset['name'] == name:
                return zoneset['vsan_id']
        loginfo("MDS: Zoneset %s not present" % name)
        return -1

    def enable_nxapi(self):
        """
        Enable nxapi feature in MDS switch

        :return: Returns the status
        """
        try:
            loginfo("Enabling nxapi feature for mds switch")
            conf_op = self.switch.config(
                'feature nxapi', fmat='json')
            op_dict = json.loads(conf_op[1])
            cli_error = self.switch.cli_error_check(op_dict)
            if cli_error:
                loginfo("Failed to enable nxapi")

        except error.CLIError as e:
            loginfo("CLI Error while enabling nxapi: " + str(e.err))
            loginfo("Error msg while enabling nxapi: " + str(e.msg))
            return

        except urllib2.URLError as e:
            loginfo("Error msg while enabling nxapi:: " + str(e.reason))
            return

    def change_password(self, password):
        """
        Changes the MDS password

        :return: Returns the status
        """
        try:
            cmd = "username admin password %s" % password
            sys_op = self.handle.config(cmd, fmat='json')
            cli_error = self.handle.cli_error_check(json.loads(sys_op[1]))
            if cli_error:
                loginfo("Failed to set MDS password")
                loginfo("CLI error")
                return False
            else:
                return True

        except error.CLIError as e:
            loginfo("Failed to set MDS password")
            loginfo("CLI Error: " + str(e.err))
            loginfo("Error msg: " + str(e.msg))
            return False

        except urllib2.URLError as e:
            loginfo("Failed to set MDS password")
            loginfo("Error msg: " + str(e.reason))
            return False
