from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.components.common import *
from pycsco.nxos.device import Device
from pycsco.nxos import error
from pure_dir.services.utils.miscellaneous import *
from pure_dir.components.network.nexus.nexus import *
import json
import time


class NEXUSTasks:
    def __init__(self, ipaddress, username, password):
        """
        Constructor - Nexus Handler

        :param ipaddress: Switch ip 
        :param username : Switch username
        :param password : Switch password
        """
        self.switch = Device(
            ip=ipaddress, username=username, password=password)

    def nexusEnableFeaturesAndSettings(self, inputdict, logfile):
        """
        Enable the necessary features and configure spanning tree in nexus switch

        :param inputdict: Dictionary (feature, spanning)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusEnableFeaturesAndSettings")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['features'] = inputdict['feature']
        dicts['spanning'] = inputdict['spanning']
        features = inputdict['feature'].split('|')
        for feature in features:
            try:
                msg = "Enabling feature %s" % feature
                customlogs(msg, logfile)
                conf_op = self.switch.config(
                    'feature %s' % feature, fmat='json')
                op_dict = json.loads(conf_op[1])
                cli_error = self.switch.cli_error_check(op_dict)
                if cli_error:
                    dicts['status'] = "FAILURE"
                    msg = "Failed to enable feature %s" % feature
                    customlogs(msg, logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Enable features and settings failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                msg = "Failed to enable feature %s" % feature
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Enable features and settings failed")
                return obj

            msg = "Feature %s enabled successfully\n" % feature
            customlogs(msg, logfile)

        if inputdict['spanning']:
            if inputdict['spanning'] == "Yes":
                try:
                    customlogs("Configuring spanning tree", logfile)
                    commands = ['spanning-tree port type network default',
                                'spanning-tree port type edge bpduguard default',
                                'spanning-tree port type edge bpdufilter default ']
                    cmds_to_string = ' ; '.join(commands)
                    conf_op = self.switch.config(cmds_to_string, fmat='json')
                    op_dict = json.loads(conf_op[1])
                    cli_error = self.switch.cli_error_check(op_dict)
                    if cli_error:
                        dicts['status'] = "FAILURE"
                        customlogs(
                            "Failed to configuring spanning tree", logfile)
                        customlogs(str(cli_error), logfile)
                        obj.setResult(dicts, PTK_INTERNALERROR,
                                      "Enable features and settings failed")
                        return obj
                except error.CLIError as e:
                    dicts['status'] = "FAILURE"
                    customlogs("Failed to configuring spanning tree", logfile)
                    customlogs(str(e.msg), logfile)
                    customlogs(str(e.err), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Enable features and settings failed")
                    return obj
            customlogs("Spanning tree configured successfully\n", logfile)

        dicts['status'] = "SUCCESS"
        customlogs(
            "Enable features and settings completed\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Enable features and settings completed")
        return obj

    def nexusDisableFeaturesAndSettings(self, inputdict, logfile):
        """
        Disable the features and unconfigure spanning tree in nexus switch

        :param inputdict: Dictionary (feature, spanning)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusDisableFeaturesAndSettings")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['features'] = inputdict['feature']
        dicts['spanning'] = inputdict['spanning']
        features = inputdict['feature'].split('|')
        for feature in features:
            try:
                msg = "Disabling feature %s" % feature
                customlogs(msg, logfile)
                conf_op = self.switch.config(
                    'no feature %s' % feature, fmat='json')
                op_dict = json.loads(conf_op[1])
                cli_error = self.switch.cli_error_check(op_dict)
                if cli_error:
                    dicts['status'] = "FAILURE"
                    msg = "Failed to disable feature %s" % feature
                    customlogs(msg, logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Disable features and settings failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                msg = "Failed to disable feature %s" % feature
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Disable features and settings failed")
                return obj

            msg = "Feature %s disabled successfully\n" % feature
            customlogs(msg, logfile)

        if inputdict['spanning']:
            if inputdict['spanning'] == "Yes":
                try:
                    customlogs("Removing spanning tree configuration", logfile)
                    commands = ['no spanning-tree port type network default',
                                'no spanning-tree port type edge bpduguard default',
                                'no spanning-tree port type edge bpdufilter default ']
                    cmds_to_string = ' ; '.join(commands)
                    conf_op = self.switch.config(cmds_to_string, fmat='json')
                    op_dict = json.loads(conf_op[1])
                    cli_error = self.switch.cli_error_check(op_dict)
                    if cli_error:
                        dicts['status'] = "FAILURE"
                        customlogs(
                            "Failed to remove spanning tree configuration", logfile)
                        customlogs(str(cli_error), logfile)
                        obj.setResult(dicts, PTK_INTERNALERROR,
                                      "Disable features and settings failed")
                        return obj
                except error.CLIError as e:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove spanning tree configuration", logfile)
                    customlogs(str(e.msg), logfile)
                    customlogs(str(e.err), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Disable features and settings failed")
                    return obj
            customlogs(
                "Spanning tree configuration removed successfully\n", logfile)

        dicts['status'] = "SUCCESS"
        customlogs(
            "Disable features and settings completed\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Disable features and settings completed")
        return obj

    def nexusSetGlobalConfigurations(self, inputdict, logfile, device_type):
        """
        Sets the global configurations for nexus switch

        :param inputdict: Dictionary (route, gateway, ntp)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusSetGlobalConfigurations")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['route'] = inputdict['route']
        dicts['gateway'] = inputdict['gateway']
        dicts['ntp'] = inputdict['ntp']

        if device_type == "n9k":
            try:
                port_op = self.switch.config(
                    'port-channel load-balance src-dst l4port', fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(port_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs("Failed to set global configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Setting global configuration failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs("Failed to set global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Setting global configuration failed")
                return obj
        else:
            dicts['mtu_value'] = inputdict['mtu_value']
            try:
                commands = ['policy-map type network-qos jumbo', 'class type network-qos class-default',
                            'mtu %s' % inputdict['mtu_value'],
                            'system qos', 'service-policy type network-qos jumbo']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                op_dict = json.loads(conf_op[1])
                cli_error = self.switch.cli_error_check(op_dict)
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs("Failed to set global configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Setting global configuration failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs("Failed to set global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Setting global configuration failed")
                return obj

        try:
            route_op = self.switch.config('ip route %s %s' % (
                inputdict['route'], inputdict['gateway']), fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(route_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to set global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Setting global configuration failed")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to set global configuration", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Setting global configuration failed")
            return obj
        try:
            ntp_op = self.switch.config(
                'ntp server %s use-vrf management' % inputdict['ntp'], fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(ntp_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to set global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Setting global configuration failed")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to set global configuration", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Setting global configuration failed")
            return obj

        dicts['status'] = "SUCCESS"
        customlogs("Setting global configuration successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Setting global configuration successful")
        return obj

    def nexusRemoveGlobalConfigurations(self, inputdict, logfile, device_type):
        """
        Removes the global configurations for nexus switch

        :param inputdict: Dictionary (route, gateway, ntp)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusRemoveGlobalConfigurations")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['route'] = inputdict['route']
        dicts['gateway'] = inputdict['gateway']
        dicts['ntp'] = inputdict['ntp']

        if device_type == "n9k":
            try:
                port_op = self.switch.config(
                    'no port-channel load-balance src-dst l4port', fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(port_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove global configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Removing Global configuration failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs("Failed to remove global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Removing global configuration failed")
                return obj
        else:
            dicts['mtu_value'] = inputdict['mtu_value']
            try:
                commands = ['system qos', 'no service-policy type network-qos jumbo',
                            'policy-map type network-qos jumbo',
                            'class type network-qos class-default', 'no mtu %s' % inputdict['mtu_value'],
                            'no policy-map type network-qos jumbo']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                op_dict = json.loads(conf_op[1])
                cli_error = self.switch.cli_error_check(op_dict)
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove global configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Removing global configuration failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs("Failed to remove global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Removing global configuration failed")
                return obj

        try:
            route_op = self.switch.config('ip route %s %s' % (
                inputdict['route'], inputdict['gateway']), fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(route_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to remove global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Removing global configuration failed")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to remove global configuration", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Removing global configuration failed")
            return obj
        try:
            ntp_op = self.switch.config(
                'ntp server %s use-vrf management' % inputdict['ntp'], fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(ntp_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to remove global configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Removing global configuration failed")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to remove global configuration", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Removing global configuration failed")
            return obj

        dicts['status'] = "SUCCESS"
        customlogs("Global configuration removed successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Removing global configuration successful")
        return obj

    def nexusCreateVLAN(self, inputdict, logfile):
        """
        Create necessary VLAN's in nexus switch

        :param inputdict: Dictionary (vlan_id, vlan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusCreateVLAN")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['vlan_set'] = inputdict['vlan_set']

        vlan_datas = inputdict['vlan_set'].split('|')

        for vlan_data in vlan_datas:
            data = {}
            data = eval(vlan_data)
            try:
                msg = "Creating VLAN %s " % data['vlan_name']['value']
                customlogs(msg, logfile)
                commands = ['vlan %s' % data['vlan_id']['value'],
                            'name %s' % data['vlan_name']['value'], 'exit']
                cmds_to_string = ' ; '.join(commands)
                vlan_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(vlan_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    msg = "Failed to create VLAN %s " % data['vlan_name']['value']
                    customlogs(msg, logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Create VLAN failed")
                    return obj

            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                msg = "Failed to create VLAN %s " % data['vlan_name']['value']
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR, "Create VLAN failed")
                return obj
            msg = "VLAN %s created successfully\n" % data['vlan_name']['value']
            customlogs(msg, logfile)

        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      "VLAN creation completed")
        return obj

    def nexusDeleteVLAN(self, inputdict, logfile):
        """
        Delete VLAN's in nexus switch

        :param inputdict: Dictionary (vlan_id, vlan_name)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusDeleteVLAN")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['vlan_set'] = inputdict['vlan_set']

        vlan_datas = inputdict['vlan_set'].split('|')

        for vlan_data in vlan_datas:
            data = {}
            data = eval(vlan_data)
            try:
                msg = "Deleting VLAN %s " % data['vlan_name']['value']
                customlogs(msg, logfile)
                vlan_op = self.switch.config(
                    'no vlan %s' % data['vlan_id']['value'], fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(vlan_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    msg = "Failed to delete VLAN %s " % data['vlan_name']['value']
                    customlogs(msg, logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Delete VLAN failed")
                    return obj

            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                msg = "Failed to delete VLAN %s " % data['vlan_name']['value']
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR, "Delete VLAN failed")
                return obj
            msg = "VLAN %s deleted successfully\n" % data['vlan_name']['value']
            customlogs(msg, logfile)

        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      "VLAN deletion completed")
        return obj

    def nexusAddIndividualPortDescription(self, inputdict, logfile):
        """
        Add Description for individual ports in nexus switch

        :param inputdict: Dictionary (id, desc, interface)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusAddIndividualPortDescription")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['port_set'] = inputdict['port_set']

        port_datas = inputdict['port_set'].split('|')

        for port_data in port_datas:
            data = {}
            data = eval(port_data)
            try:
                msg = "Adding description for %s %s" % (
                    data['interface']['value'], data['id']['value'])
                customlogs(msg, logfile)
                if data['interface']['value'] == "Vlan":
                    commands = ['interface Vlan%s' % data['id']['value'],
                                'description %s' % data['desc']['value'], 'exit']
                elif data['interface']['value'] == "port-channel":
                    commands = ['interface port-channel %s' % data['id']['value'],
                                'description %s' % data['desc']['value'], 'exit']
                elif data['interface']['value'] == "Eth":
                    commands = ['interface Eth%s' % data['id']['value'],
                                'description %s' % data['desc']['value'], 'exit']
                cmds_to_string = ' ; '.join(commands)
                port_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(port_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    msg = "Failed to add description for %s %s" % (
                        data['interface']['value'], data['id']['value'])
                    customlogs(msg, logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Add Individual Port Description failed")
                    return obj
                msg = "Description added for %s %s\n" % (
                    data['interface']['value'], data['id']['value'])
                customlogs(msg, logfile)

            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                msg = "Failed to add description for %s %s" % (
                    data['interface']['value'], data['id']['value'])
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Add Individual Port Description failed")
                return obj

        dicts['status'] = "SUCCESS"
        customlogs(
            "Add Individual Port Description completed\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Add Individual Port Description successful")
        return obj

    def nexusRemoveIndividualPortDescription(self, inputdict, logfile):
        """
        Remove Description for individual ports in nexus switch

        :param inputdict: Dictionary (id, desc, interface)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusRemoveIndividualPortDescription")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['port_set'] = inputdict['port_set']

        port_datas = inputdict['port_set'].split('|')

        for port_data in port_datas:
            data = {}
            data = eval(port_data)
            try:
                msg = "Removing description for %s %s" % (
                    data['interface']['value'], data['id']['value'])
                customlogs(msg, logfile)
                if data['interface']['value'] == "Vlan":
                    port_op = self.switch.config(
                        'no interface Vlan%s' % data['id']['value'], fmat='json')
                elif data['interface']['value'] == "port-channel":
                    port_op = self.switch.config(
                        'no interface port-channel %s' % data['id']['value'], fmat='json')
                elif data['interface']['value'] == "Eth":
                    commands = ['interface Eth%s' % data['id']['value'],
                                'no description', 'exit']
                    cmds_to_string = ' ; '.join(commands)
                    port_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(port_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    msg = "Failed to remove description for %s %s" % (
                        data['interface']['value'], data['id']['value'])
                    customlogs(msg, logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Remove Individual Port Description failed")
                    return obj
                msg = "Description removed for %s %s\n" % (
                    data['interface']['value'], data['id']['value'])
                customlogs(msg, logfile)

            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                msg = "Failed to remove description for %s %s" % (
                    data['interface']['value'], data['id']['value'])
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Remove Individual Port Description failed")
                return obj

        dicts['status'] = "SUCCESS"
        customlogs(
            "Remove Individual Port Description completed\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Remove Individual Port Description successful")
        return obj

    def nexusAddNTPDistributionInterface(self, inputdict, logfile, ip):
        """
        Add NTP distribution interface to redistribute NTP to In-Band networks from their Out of Band network source

        :param inputdict: Dictionary (route, gateway, vlan_id, mask_length)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusAddNTPDistributionInterface")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['ip'] = ip
        dicts['gateway'] = inputdict['gateway']
        dicts['vlan_id'] = inputdict['vlan_id']
        dicts['mask_length'] = inputdict['mask_length']
        dicts['stratum_no'] = inputdict['stratum_no']
        dicts['route'] = inputdict['route']
        try:
            commands = ['ntp source %s' % ip, 'ntp master 3',
                        'ip route %s %s' % (inputdict['route'], inputdict['gateway']), 'interface Vlan%s' %
                        inputdict['vlan_id'], 'no shutdown', 'no ip redirects',
                        ' ip address %s/%s' % (ip, inputdict['mask_length']), 'no ipv6 redirects']
            cmds_to_string = ' ; '.join(commands)
            add_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(add_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to add NTP Distribution Interface")
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Add NTP Distribution Interface failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs(
                    "Add NTP Distribution Interface completed\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "Add NTP Distribution Interface successful")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to add NTP Distribution Interface")
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Add NTP Distribution Interface failed")
            return obj

    def nexusRemoveNTPDistributionInterface(self, inputdict, logfile, ip):
        """
        Remove NTP distribution interface to redistribute NTP to In-Band networks from their Out of Band network source

        :param inputdict: Dictionary (route, gateway, vlan_id, mask_length)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusRemoveNTPDistributionInterface")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['ip'] = ip
        dicts['gateway'] = inputdict['gateway']
        dicts['vlan_id'] = inputdict['vlan_id']
        dicts['mask_length'] = inputdict['mask_length']
        dicts['stratum_no'] = inputdict['stratum_no']
        dicts['route'] = inputdict['route']
        try:
            commands = ['no ntp source %s' % ip, 'no ntp master 3',
                        'no interface Vlan%s' % inputdict['vlan_id']]
            cmds_to_string = ' ; '.join(commands)
            add_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(add_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to remove NTP Distribution Interface configuration")
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Remove NTP Distribution Interface configuration failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs(
                    "NTP Distribution Interface configuration removed successfully\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "Remove NTP Distribution Interface configuration successful")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs(
                "Failed to remove NTP Distribution Interface configuration", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Remove NTP Distribution Interface configuration failed")
            return obj

    def nexusCreateVPCDomain(self, inputdict, logfile):
        """
        Create VPC Domain in nexus switch

        :param inputdict: Dictionary (vpc_id, vpc_role, delay, ip_a, ip_b)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSCreateVPCDomain")
        dicts = {}
        ip_a = get_device_credentials(key="mac", value=inputdict['ip_a'])
        ip_b = get_device_credentials(key="mac", value=inputdict['ip_b'])

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['vpc_id'] = inputdict['vpc_id']
        dicts['vpc_role'] = inputdict['vpc_role']
        dicts['ip_a'] = ip_a['ipaddress']
        dicts['ip_b'] = ip_b['ipaddress']
        dicts['delay'] = inputdict['delay']
        try:
            commands = ['vpc domain %s' % inputdict['vpc_id'], 'peer-switch',
                        'role priority %s' % inputdict['vpc_role'], 'peer-keepalive destination %s source %s' %
                        (ip_b['ipaddress'], ip_a['ipaddress']
                         ), ' delay restore %s' % inputdict['delay'],
                        'peer-gateway', 'auto-recovery', 'ip arp synchronize', 'exit']
            cmds_to_string = ' ; '.join(commands)
            vpc_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(vpc_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to create VPC domain", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Create VPC domain failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs("VPC domain created successfully\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "VPC domain created successfully")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to create VPC domain", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Create VPC domain failed")
            return obj

    def nexusDeleteVPCDomain(self, inputdict, logfile):
        """
        Delete VPC Domain in nexus switch

        :param inputdict: Dictionary (vpc_id, vpc_role, delay, ip_a, ip_b)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSDeleteVPCDomain")
        dicts = {}
        ip_a = get_device_credentials(key="mac", value=inputdict['ip_a'])
        ip_b = get_device_credentials(key="mac", value=inputdict['ip_b'])

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['vpc_id'] = inputdict['vpc_id']
        dicts['vpc_role'] = inputdict['vpc_role']
        dicts['ip_a'] = ip_a['ipaddress']
        dicts['ip_b'] = ip_b['ipaddress']
        dicts['delay'] = inputdict['delay']
        try:
            vpc_op = self.switch.config(
                'no vpc domain %s' % inputdict['vpc_id'], fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(vpc_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to remove VPC domain configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Remove VPC domain configuration failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs(
                    "VPC domain configuration removed successfully\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "VPC domain configuration removed successfully")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to delete VPC domain configuration", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Remove VPC domain configuration failed")
            return obj

    def nexusConfigurePortChannelMemberInterfaces(self, inputdict, logfile):
        """
        Configure Port channel member Interfaces for peer link between nexus switches

        :param inputdict: Dictionary (slot_chassis, port_channel_number, native_vlan_id, allowed_vlans)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSConfigurePortChannelMemberInterfaces")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['slot_chassis'] = inputdict['slot_chassis']
        dicts['port_channel_number'] = inputdict['port_channel_number']
        dicts['native_vlan_id'] = inputdict['native_vlan_id']
        dicts['allowed_vlans_set'] = inputdict['allowed_vlans_set']

        helper = Nexus()
        allowed_vlans = helper.get_allowed_vlans(
            inputdict['allowed_vlans_set'])
        ethernets = inputdict['slot_chassis'].split('|')
        for ethernet in ethernets:
            try:
                commands = ['interface %s' % ethernet, 'channel-group %s force mode active' %
                            inputdict['port_channel_number'], 'no shut']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to configure port channel member interfaces", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Configure Port Channel Member Interfaces failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to configure port channel member interfaces", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Configure Port Channel Member Interfaces failed")
                return obj

        try:
            commands = ['interface port-channel %s' % inputdict['port_channel_number'], 'switchport mode trunk',
                        'switchport trunk native vlan %s' %
                        inputdict['native_vlan_id'], 'switchport trunk allowed vlan %s' % allowed_vlans,
                        'vpc peer-link', 'exit']
            cmds_to_string = ' ; '.join(commands)
            conf_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to configure port channel member interfaces", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Configure Port Channel Member Interfaces failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs(
                    "Configuring Port Channel Member Interfaces successful\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "Configure Port Channel Member Interfaces succesful")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs(
                "Failed to configure port channel member interfaces", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Configure Port Channel Member Interfaces failed")
            return obj

    def nexusUnconfigurePortChannelMemberInterfaces(self, inputdict, logfile):
        """
        Unconfigure Port channel member Interfaces for peer link between nexus switches

        :param inputdict: Dictionary (slot_chassis, port_channel_number, native_vlan_id, allowed_vlans)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSUnconfigurePortChannelMemberInterfaces")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['slot_chassis'] = inputdict['slot_chassis']
        dicts['port_channel_number'] = inputdict['port_channel_number']
        dicts['native_vlan_id'] = inputdict['native_vlan_id']
        dicts['allowed_vlans_set'] = inputdict['allowed_vlans_set']

        time.sleep(20)
        helper = Nexus()
        allowed_vlans = helper.get_allowed_vlans(
            inputdict['allowed_vlans_set'])
        ethernets = inputdict['slot_chassis'].split('|')
        for ethernet in ethernets:
            try:
                commands = ['no interface port-channel %s' % inputdict['port_channel_number'],
                            'interface %s' % ethernet, 'no switchport mode trunk',
                            'no switchport trunk native vlan %s' %
                            inputdict['native_vlan_id'],
                            'no switchport trunk allowed vlan %s' % allowed_vlans, 'shut']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove port channel member interfaces configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Failed to remove port channel member interfaces configuration")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to remove port channel member interfaces configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to remove port channel member interfaces configuration")
                return obj

        dicts['status'] = "SUCCESS"
        customlogs(
            "Port Channel Member Interfaces configuration removed successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Port Channel Member Interfaces configuration removed successfully")
        return obj

    def nexusConfigureVirtualPortChannelsToUCS(self, inputdict, logfile, device_type):
        """
        Configure Virtual Port Channels to UCS from nexus

        :param inputdict: Dictionary (port_channel_number, native_vlan_id, allowed_vlans, mtu_value, counter_value, interval_delay)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSConfigureVirtualPortChannelsToUCS_A")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts = inputdict

        helper = Nexus()
        allowed_vlans = helper.get_allowed_vlans(
            inputdict['allowed_vlans_set'])
        ethernets = inputdict['slot_chassis'].split('|')
        for ethernet in ethernets:
            try:
                commands = ['interface %s' % ethernet, 'channel-group %s force mode active' %
                            inputdict['port_channel_number'], 'no shut']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to configure virtual port channels to UCS", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Configure Virtual Port Channels To UCS Fabric failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to configure virtual port channels to UCS", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Configure Virtual Port Channels To UCS Fabric failed")
                return obj

        try:
            if device_type == "n5k":
                commands = ['interface port-channel %s' % inputdict['port_channel_number'], 'switchport mode trunk',
                            'switchport trunk native vlan %s' % inputdict['native_vlan_id'],
                            'switchport trunk allowed vlan %s' % allowed_vlans,
                            'spanning-tree port type edge trunk',
                            'load-interval counter %s %s' % (
                                inputdict['counter_value'], inputdict['interval_delay']),
                            'vpc %s' % inputdict['port_channel_number'], 'exit']
            else:
                commands = ['interface port-channel %s' % inputdict['port_channel_number'], 'switchport mode trunk',
                            'switchport trunk native vlan %s' % inputdict['native_vlan_id'],
                            'switchport trunk allowed vlan %s' % allowed_vlans,
                            'spanning-tree port type edge trunk', 'mtu %s' % inputdict['mtu_value'],
                            'load-interval counter %s %s' % (
                                inputdict['counter_value'], inputdict['interval_delay']),
                            'vpc %s' % inputdict['port_channel_number'], 'exit']

            cmds_to_string = ' ; '.join(commands)
            conf_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to configure virtual port channels to UCS", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Configure Virtual Port Channels To UCS Fabric failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs(
                    "Configuring Virtual Port Channels To UCS Fabric successful\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "Configure Virtual Port Channels To UCS Fabric succesful")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs(
                "Failed to configure virtual port channels to UCS", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Configure Virtual Port Channels To UCS Fabric failed")
            return obj

    def nexusUnconfigureVirtualPortChannelsToUCS(self, inputdict, logfile, device_type):
        """
        Unconfigure Virtual Port Channels to UCS from nexus

        :param inputdict: Dictionary (port_channel_number, native_vlan_id, allowed_vlans, mtu_value, counter_value, interval_delay)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSUnconfigureVirtualPortChannelsToUCS_A")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts = inputdict

        helper = Nexus()
        allowed_vlans = helper.get_allowed_vlans(
            inputdict['allowed_vlans_set'])
        ethernets = inputdict['slot_chassis'].split('|')
        for ethernet in ethernets:
            try:
                if device_type == "n5k":
                    commands = ['interface port-channel %s' % inputdict['port_channel_number'],
                                'no load-interval counter %s %s' % (
                                    inputdict['counter_value'], inputdict['interval_delay']),
                                'no interface port-channel %s' % inputdict['port_channel_number'],
                                'interface %s' % ethernet, 'no switchport mode trunk',
                                'no switchport trunk native vlan %s' % inputdict['native_vlan_id'],
                                'no switchport trunk allowed vlan %s' % allowed_vlans, 'shut']
                else:
                    commands = ['interface port-channel %s' % inputdict['port_channel_number'],
                                'no load-interval counter %s %s' % (
                                    inputdict['counter_value'], inputdict['interval_delay']),
                                'no interface port-channel %s' % inputdict['port_channel_number'],
                                'interface %s' % ethernet, 'no switchport mode trunk',
                                'no switchport trunk native vlan %s' % inputdict['native_vlan_id'],
                                'no switchport trunk allowed vlan %s' % allowed_vlans, 'no mtu', 'shut']

                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove virtual port channels to UCS configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Failed to remove virtual port channels to UCS configuration")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to remove virtual port channels to UCS configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to remove virtual port channels to UCS configuration")
                return obj

        dicts['status'] = "SUCCESS"
        customlogs(
            "Virtual Port Channels To UCS configuration removed successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Virtual Port Channels To UCS configuration removed successfully")
        return obj

    def nexusConfigureVirtualPortChannelsToNetworkSwitch(self, inputdict, logfile):
        """
        Configures the Virtual Port channels to upstream network switch from nexus

        :param inputdict: Dictionary (port_channel_number, slot_chassis, vlan_id, native_vlan_id, allowed_vlans)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSConfigureVirtualPortChannelsToNetworkSwitch")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts = inputdict

        helper = Nexus()
        allowed_vlans = helper.get_allowed_vlans(
            inputdict['allowed_vlans_set'])
        ethernets = inputdict['slot_chassis'].split('|')
        for ethernet in ethernets:
            try:
                commands = ['interface %s' % ethernet,
                            'channel-group %s force mode active' % inputdict['port_channel_number'], 'no shut']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to configure virtual port channels to network switch", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Configure Virtual Port Channels To Upstream Network Switch failed")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to configure virtual port channels to network switch", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Configure Virtual Port Channels To Upstream Network Switch failed")
                return obj
        try:
            commands = ['interface port-channel %s' % inputdict['port_channel_number'],
                        'switchport mode trunk', 'switchport trunk native vlan %s' % inputdict[
                            'native_vlan_id'],
                        'switchport trunk allowed vlan %s' % allowed_vlans,
                        'vpc %s' % inputdict['port_channel_number'], 'exit']
            cmds_to_string = ' ; '.join(commands)
            conf_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to configure virtual port channels to network switch", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Configure Virtual Port Channels To Upstream Network Switch failed")
                return obj
            else:
                dicts['status'] = "SUCCESS"
                customlogs(
                    "Configuring Virtual Port Channels To Upstream Network Switch successful\n", logfile)
                obj.setResult(dicts, PTK_OKAY,
                              "Configure Virtual Port Channels To Upstream Network Switch succesful")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs(
                "Failed to configure virtual port channels to network switch", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Configure Virtual Port Channels To Upstream Network Switch failed")
            return obj

    def nexusUnconfigureVirtualPortChannelsToNetworkSwitch(self, inputdict, logfile):
        """
        Unconfigures the Virtual Port channels to upstream network switch from nexus

        :param inputdict: Dictionary (port_channel_number, slot_chassis, vlan_id, native_vlan_id, allowed_vlans)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSUnconfigureVirtualPortChannelsToNetworkSwitch")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts = inputdict

        helper = Nexus()
        allowed_vlans = helper.get_allowed_vlans(
            inputdict['allowed_vlans_set'])
        ethernets = inputdict['slot_chassis'].split('|')
        for ethernet in ethernets:
            try:
                commands = ['no interface port-channel %s' % inputdict['port_channel_number'],
                            'interface %s' % ethernet, 'no switchport mode trunk',
                            'no switchport trunk native vlan %s' % inputdict['native_vlan_id'],
                            'no switchport trunk allowed vlan %s' % allowed_vlans, 'shut']
                cmds_to_string = ' ; '.join(commands)
                conf_op = self.switch.config(cmds_to_string, fmat='json')
                cli_error = self.switch.cli_error_check(json.loads(conf_op[1]))
                if cli_error:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove virtual port channels to network switch configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(cli_error), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Failed to remove virtual port channels to network switch configuration")
                    return obj
            except error.CLIError as e:
                dicts['status'] = "FAILURE"
                customlogs(
                    "Failed to remove virtual port channels to network switch configuration", logfile)
                customlogs("Error message is :", logfile)
                customlogs(str(e.msg), logfile)
                customlogs(str(e.err), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to remove virtual port channels to network switch configuration")
                return obj

        dicts['status'] = "SUCCESS"
        customlogs(
            "Virtual Port Channels To Upstream Network Switch configuration removed successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Virtual Port Channels To Upstream Network Switch configuration removed successfully")
        return obj

    def nexusConfigureiSCSIInterface(self, inputdict, logfile, device_type):
        """
        Configures the iSCSI Interface in nexus switch

        :param inputdict: Dictionary (slot_chassis, vlan_id, mtu_value)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSConfigureiSCSIInterface")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['intf_set'] = inputdict['intf_set']

        intfs = inputdict['intf_set'].split('|')

        for intf in intfs:
            data = {}
            data = eval(intf)
            ethernets = []
            if isinstance(data['slot_chassis']['value'], list):
                ethernets = data['slot_chassis']['value']
            else:
                ethernets.append(data['slot_chassis']['value'])
            for ethernet in ethernets:
                try:
                    if device_type == "n9k":
                        commands = ['interface %s' % ethernet,
                                    'switchport access vlan %s' % data['vlan_id']['value'],
                                    'spanning-tree port type edge', 'mtu %s' % inputdict['mtu_value'], 'no shutdown']
                        dicts['mtu_value'] = inputdict['mtu_value']
                    else:
                        commands = ['interface %s' % ethernet,
                                    'switchport access vlan %s' % data['vlan_id']['value'],
                                    'spanning-tree port type edge', 'no shutdown']

                    cmds_to_string = ' ; '.join(commands)
                    add_op = self.switch.config(cmds_to_string, fmat='json')
                    cli_error = self.switch.cli_error_check(
                        json.loads(add_op[1]))
                    if cli_error:
                        dicts['status'] = "FAILURE"
                        customlogs("iSCSI Interface configuration failed")
                        customlogs("Error message is :", logfile)
                        customlogs(str(cli_error), logfile)
                        obj.setResult(dicts, PTK_INTERNALERROR,
                                      "iSCSI Interface configuration failed")
                        return obj

                except error.CLIError as e:
                    dicts['status'] = "FAILURE"
                    customlogs("Failed to configure iSCSI Interface", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(e.msg), logfile)
                    customlogs(str(e.err), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "iSCSI Interface configuration failed")
                    return obj

        dicts['status'] = "SUCCESS"
        customlogs("iSCSI Interface configuration successful\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "iSCSI Interface configuration successful")
        return obj

    def nexusUnconfigureiSCSIInterface(self, inputdict, logfile, device_type):
        """
        Unconfigures the iSCSI Interface in nexus switch

        :param inputdict: Dictionary (slot_chassis, vlan_id, mtu_value)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("NEXUSUnconfigureiSCSIInterface")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)

        dicts['intf_set'] = inputdict['intf_set']

        intfs = inputdict['intf_set'].split('|')

        for intf in intfs:
            data = {}
            data = eval(intf)
            ethernets = []
            if isinstance(data['slot_chassis']['value'], list):
                ethernets = data['slot_chassis']['value']
            else:
                ethernets.append(data['slot_chassis']['value'])
            for ethernet in ethernets:
                try:
                    if device_type == "n9k":
                        commands = ['interface %s' % ethernet,
                                    'no switchport access vlan %s' % data['vlan_id']['value'],
                                    'no spanning-tree port type edge', 'no mtu %s' % inputdict['mtu_value'], 'shut']
                        dicts['mtu_value'] = inputdict['mtu_value']
                    else:
                        commands = ['interface %s' % ethernet,
                                    'no switchport access vlan %s' % data['vlan_id']['value'],
                                    'no spanning-tree port type edge', 'shut']

                    cmds_to_string = ' ; '.join(commands)
                    add_op = self.switch.config(cmds_to_string, fmat='json')
                    cli_error = self.switch.cli_error_check(
                        json.loads(add_op[1]))
                    if cli_error:
                        dicts['status'] = "FAILURE"
                        customlogs(
                            "Failed to remove iSCSI Interface configuration")
                        customlogs("Error message is :", logfile)
                        customlogs(str(cli_error), logfile)
                        obj.setResult(dicts, PTK_INTERNALERROR,
                                      "Failed to remove iSCSI Interface configuration")
                        return obj

                except error.CLIError as e:
                    dicts['status'] = "FAILURE"
                    customlogs(
                        "Failed to remove iSCSI Interface configuration", logfile)
                    customlogs("Error message is :", logfile)
                    customlogs(str(e.msg), logfile)
                    customlogs(str(e.err), logfile)
                    obj.setResult(dicts, PTK_INTERNALERROR,
                                  "Failed to remove iSCSI Interface configuration")
                    return obj

        dicts['status'] = "SUCCESS"
        customlogs(
            "iSCSI Interface configuration removed successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "iSCSI Interface configuration removed successfully")
        return obj

    def nexusConfigureUnifiedPorts(self, inputdict, logfile, ip, username, password):
        """
        Configure Unified ports in Nexus 5k switches

        :param inputdict: Dictionary (slot, ports, port_type)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusConfigureUnifiedPorts")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['slot'] = inputdict['slot']
        dicts['ports'] = inputdict['ports']
        dicts['port_type'] = inputdict['port_type']

        try:
            commands = ["slot %s" % inputdict['slot'], "port %s type %s" % (inputdict['ports'], inputdict['port_type']),
                        "copy running-config startup-config"]
            cmds_to_string = ' ; '.join(commands)
            add_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(add_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to Configure Unified ports")
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to Configure Unified ports")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to Configure Unified ports", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to Configure Unified ports")
            return obj

        customlogs("Ports configuration done", logfile)
        try:
            rel = self.switch.config("reload", fmat='json')
        except Exception as e:
            customlogs("Switch reload started", logfile)

        customlogs("Waiting for switch to be up", logfile)
        time.sleep(300)
        retry = 0
        while retry < 5:
            (err_res, status) = execute_remote_command(
                ip, username, password, "show version")
            if status is False:
                time.sleep(30)
                retry += 1
            else:
                break
        if status is False:
            dicts['status'] = "FAILURE"
            customlogs("Timeout reached. Nexus switch is still down", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to Configure Unified ports")
            return obj

        customlogs("Switch is up", logfile)
        dicts['status'] = "SUCCESS"
        customlogs(
            "Unified ports configured successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Unified ports configured successfully")
        return obj

    def nexusUnconfigureUnifiedPorts(self, inputdict, logfile, ip, username, password):
        """
        Unconfigures Unified ports in Nexus 5k switches

        :param inputdict: Dictionary (slot, ports, port_type)
        :param logfile: Logfile name
        :return: Returns the status of the execution
        """
        obj = result()
        loginfo("nexusUnconfigureUnifiedPorts")
        dicts = {}

        loginfo("Parameters =")
        loginfo(inputdict)
        message = ""

        dicts['slot'] = inputdict['slot']
        dicts['ports'] = inputdict['ports']
        dicts['port_type'] = inputdict['port_type']

        try:
            commands = ["slot %s" % inputdict['slot'], "port %s type ethernet" % inputdict['ports'],
                        "copy running-config startup-config"]
            cmds_to_string = ' ; '.join(commands)
            add_op = self.switch.config(cmds_to_string, fmat='json')
            cli_error = self.switch.cli_error_check(json.loads(add_op[1]))
            if cli_error:
                dicts['status'] = "FAILURE"
                customlogs("Failed to Unconfigure Unified ports")
                customlogs("Error message is :", logfile)
                customlogs(str(cli_error), logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to Unconfigure Unified ports")
                return obj
        except error.CLIError as e:
            dicts['status'] = "FAILURE"
            customlogs("Failed to Unconfigure Unified ports", logfile)
            customlogs("Error message is :", logfile)
            customlogs(str(e.msg), logfile)
            customlogs(str(e.err), logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to Unconfigure Unified ports")
            return obj

        customlogs("Ports configuration removed", logfile)
        try:
            rel = self.switch.config("reload", fmat='json')
        except Exception as e:
            customlogs("Switch reload started", logfile)

        customlogs("Waiting for switch to be up", logfile)
        time.sleep(300)
        retry = 0
        while retry < 5:
            (err_res, status) = execute_remote_command(
                ip, username, password, "show version")
            if status is False:
                time.sleep(30)
                retry += 1
            else:
                break
        if status is False:
            dicts['status'] = "FAILURE"
            customlogs("Timeout reached. Nexus switch is still down", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to Unconfigure Unified ports")
            return obj

        customlogs("Switch is up", logfile)
        dicts['status'] = "SUCCESS"
        customlogs(
            "Unified ports unconfigured successfully\n", logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Unified ports unconfigured successfully")
        return obj

    def configure_portchannel(self, input_dict, logfile):
        """
        Task - Configure Port-Channel

        :param input_dict: Dictionary(fc_list, portchannel_id)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        fc_list = input_dict['fc_list'].split('|')

        helper = Nexus()
        res = helper.configure_portchannel(self.switch,
                                           input_dict['portchannel_id'], fc_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to configure port channel", logfile)

        else:
            customlogs("Port-channel '%s' with interfaces '%s'" %
                       (input_dict['portchannel_id'], str(fc_list)), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("Configure port channel completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def unconfigure_portchannel(self, input_dict, logfile):
        """
        Rollback - Unconfigure Port-Channel

        :param input_dict: Dictionary(fc_list, portchannel_id)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        fc_list = input_dict['fc_list'].split('|')

        helper = Nexus()
        res = helper.unconfigure_portchannel(self.switch,
                                             input_dict['portchannel_id'], fc_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to unconfigure port channel", logfile)

        else:
            customlogs("Port-channel '%s' with interfaces '%s' removed" %
                       (input_dict['portchannel_id'], str(fc_list)), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("Unconfigure port channel completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_vsan(self, input_dict, logfile):
        """
        Task - Create VSAN

        :param input_dict: Dictionary(vsan_id)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        helper = Nexus()
        res = helper.create_vsan(self.switch, input_dict['vsan_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['vsan_id'] = ""
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to create vsan", logfile)

        else:
            customlogs("Vsan '%s' created successfully" %
                       input_dict['vsan_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['vsan_id'] = input_dict['vsan_id']

        customlogs("Create vsan completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def delete_vsan(self, input_dict, logfile):
        """
        Rollback - Delete VSAN

        :param input_dict: Dictionary(vsan_id)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        helper = Nexus()
        res = helper.delete_vsan(self.switch, input_dict['vsan_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['vsan_id'] = ""
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to delete vsan", logfile)

        else:
            customlogs("Vsan '%s' deleted successfully" %
                       input_dict['vsan_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['vsan_id'] = input_dict['vsan_id']

        customlogs("Delete vsan completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def configure_vsan(self, input_dict, logfile):
        """
        Task - Configure VSAN

        :param input_dict: Dictionary(vsan_id, fc_list, pc_list)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        helper = Nexus()
        interface_list = input_dict['fc_list'].split('|')

        tmp_pc_list = input_dict['pc_list'].split('|')
        for pc in tmp_pc_list:
            interface_list.append("san-port-channel " + pc)

        loginfo("Configuring vsan %s with interfaces %s" %
                (input_dict['vsan_id'], str(interface_list)))
        res = helper.configure_vsan(
            self.switch, input_dict['vsan_id'], interface_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to configure vsan", logfile)

        else:
            customlogs("Vsan '%s' configured with interfaces '%s' successfully" %
                       (input_dict['vsan_id'], str(interface_list)), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("Configure vsan completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def unconfigure_vsan(self, input_dict, logfile):
        """
        Rollback - Unconfigure VSAN

        :param input_dict: Dictionary(vsan_id, fc_list, pc_list)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        helper = Nexus()
        interface_list = input_dict['fc_list'].split('|')

        tmp_pc_list = input_dict['pc_list'].split('|')
        for pc in tmp_pc_list:
            interface_list.append("san-port-channel " + pc)

        loginfo("Unconfiguring vsan %s with interfaces %s" %
                (input_dict['vsan_id'], str(interface_list)))
        res = helper.unconfigure_vsan(
            self.switch, input_dict['vsan_id'], interface_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to unconfigure vsan", logfile)

        else:
            customlogs("Interfaces '%s' removed from vsan '%s' successfully" %
                       (str(interface_list), input_dict['vsan_id']), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("Unconfigure vsan completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_portchannel(self, input_dict, logfile):
        """
        Task - Create Port-Channel

        :param input_dict: Dictionary(portchannel_id)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        helper = Nexus()
        res = helper.create_portchannel(
            self.switch, input_dict['portchannel_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['portchannel_id'] = ""
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to create port channel", logfile)

        else:
            customlogs("Portchannel '%s' created successfully" %
                       input_dict['portchannel_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['portchannel_id'] = input_dict['portchannel_id']

        customlogs("Create port channel completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def delete_portchannel(self, input_dict, logfile):
        """
        Rollback - Delete Port-Channel

        :param input_dict: Dictionary(portchannel_id)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        helper = Nexus()
        res = helper.delete_portchannel(
            self.switch, input_dict['portchannel_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['portchannel_id'] = ""
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to delete port channel", logfile)

        else:
            customlogs("Portchannel '%s' deleted successfully" %
                       input_dict['portchannel_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['portchannel_id'] = input_dict['portchannel_id']

        customlogs("Delete portchannel completed successfully\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_zones(self, input_dict, logfile):
        """
        Task - Create Zones

        :param input_dict: Dictionary(vsan_id, zones)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}
        zone_list = []

        vsan_id = input_dict['vsan_id']
        zones = input_dict['zones'].split('|')

        helper = Nexus()
        for zone_dict in zones:
            zone_dict = eval(zone_dict)
            res = helper.create_zone(self.switch,
                                     zone_dict['zone_name']['value'], input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("Error message is : %s" % res.getMsg(), logfile)
                customlogs(
                    "Create zones failed with zone creation", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zone '%s' created successfully" %
                           zone_dict['zone_name']['value'], logfile)
                zone_members = zone_dict['zone_members']['value']

                helper.add_to_zone(self.switch,
                                   zone_dict['zone_name']['value'], zone_members, input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs(
                        "Create zones failed with adding members to zone", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    customlogs("Members '%s' added to the zone '%s' with vsan '%s' successfully" % (
                        str(zone_dict['zone_members']['value']),
                        zone_dict['zone_name']['value'], vsan_id), logfile)
                    zone_list.append(zone_dict['zone_name']['value'])

        customlogs("Create zones completed successfully\n", logfile)
        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zone_list
        obj.setResult(output_dict, PTK_OKAY,
                      "Zones %s created successfully" % str(zone_list))
        return obj

    def delete_zones(self, input_dict, logfile):
        """
        Rollback - Delete Zones

        :param input_dict: Dictionary(vsan_id, zones)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        vsan_id = input_dict['vsan_id']
        zones = input_dict['zones'].split('|')

        helper = Nexus()
        for zone in zones:
            res = helper.delete_zone(self.switch, zone, input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("Error message is : %s" % res.getMsg(), logfile)
                customlogs("Failed to delete zones", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zone '%s' deleted successfully" % zone, logfile)

        customlogs("Delete zones completed successfully\n", logfile)
        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zones
        obj.setResult(output_dict, PTK_OKAY,
                      "Zones %s deleted successfully" % str(zones))
        return obj

    def create_zonesets(self, input_dict, logfile):
        """
        Task - Create Zoneset

        :param input_dict: Dictionary(vsan_id, zoneset)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}
        zoneset_list = []

        vsan_id = input_dict['vsan_id']
        zonesets = input_dict['zoneset'].split('|')

        helper = Nexus()
        for zoneset_dict in zonesets:
            zoneset_dict = eval(zoneset_dict)
            res = helper.create_zoneset(self.switch,
                                        zoneset_dict['zoneset_name']['value'], input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("Error message is : %s" % res.getMsg(), logfile)
                customlogs(
                    "Create zoneset failed with zoneset creation", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zoneset '%s' created successfully" %
                           zoneset_dict['zoneset_name']['value'], logfile)
                helper.add_to_zoneset(self.switch,
                                      zoneset_dict['zoneset_name']['value'], zoneset_dict['zoneset_members']['value'],
                                      input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs(
                        "Create zoneset failed with adding members to zoneset", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    customlogs("Members '%s' added to the zoneset '%s' with vsan '%s' successfully" % (
                        str(zoneset_dict['zoneset_members']['value']),
                        zoneset_dict['zoneset_name']['value'], vsan_id), logfile)
                    time.sleep(10)
                    res = helper.activate_zoneset(self.switch,
                                                  zoneset_dict['zoneset_name']['value'], input_dict['vsan_id'])
                    if res.getStatus() != PTK_OKAY:
                        output_dict['status'] = "FAILURE"
                        customlogs(
                            "Zoneset activation failed", logfile)
                        obj.setResult(
                            output_dict, res.getStatus(), res.getMsg())
                        return obj
                    else:
                        customlogs("Zoneset '%s' with vsan '%s' activated successfully" % (
                            zoneset_dict['zoneset_name']['value'], input_dict['vsan_id']), logfile)
                        zoneset_list.append(
                            zoneset_dict['zoneset_name']['value'])

            customlogs("Zoneset creation completed successfully\n", logfile)
            output_dict['status'] = 'SUCCESS'
            output_dict['zoneset_list'] = zoneset_list
            obj.setResult(output_dict, PTK_OKAY,
                          "Zonesets %s created successfully" % str(zoneset_list))
            return obj

    def delete_zonesets(self, input_dict, logfile):
        """
        Rollback - Delete Zoneset

        :param input_dict: Dictionary(vsan_id, zonesets)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        vsan_id = input_dict['vsan_id']
        zonesets = input_dict['zonesets'].split('|')

        helper = Nexus()
        for zoneset in zonesets:
            res = helper.deactivate_zoneset(self.switch,
                                            zoneset, input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("Failed to delete zonesets", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zoneset '%s' with vsan '%s' deleted successfully" % (zoneset, input_dict['vsan_id']),
                           logfile)
                res = helper.delete_zoneset(
                    self.switch, zoneset, input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs("Error message is : %s" % res.getMsg(), logfile)
                    customlogs("Failed to delete zonesets", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    customlogs("Zoneset '%s' deleted successfully" %
                               zoneset, logfile)

        customlogs("Delete zonesets completed successfully\n", logfile)
        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zonesets
        obj.setResult(output_dict, PTK_OKAY,
                      "Zonesets %s deleted successfully" % str(zonesets))
        return obj

    def create_device_aliases(self, input_dict, logfile):
        """
        Task - Create Device Aliases

        :param input_dict: Dictionary([pwwn, alias_name])
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}
        fl_list = []
        alias_list = []

        flogi_list = input_dict['flogi_list'].split('|')

        for fl_sess in flogi_list:
            fl_sess = eval(fl_sess)
            iface = {}
            iface['pwwn'] = fl_sess['pwwn']['value']
            iface['alias'] = fl_sess['alias_name']['value']
            fl_list.append(iface)
            alias_list.append(iface['alias'])

        helper = Nexus()
        res = helper.create_device_aliases(self.switch, fl_list)
        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['alias'] = str(alias_list)
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to create device aliases ", logfile)

        else:
            output_dict['status'] = "SUCCESS"
            output_dict['alias'] = str(alias_list)
            customlogs("Device aliases '%s' created successfully" %
                       output_dict['alias'], logfile)

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def delete_device_aliases(self, input_dict, logfile):
        """
        Rollback - Delete Device Aliases

        :param input_dict: Dictionary(aliases_list)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        alias_list = input_dict['aliases'].split('|')

        helper = Nexus()
        res = helper.delete_device_aliases(self.switch, alias_list)
        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['alias'] = str(alias_list)
            customlogs("Error message is : %s" % res.getMsg(), logfile)
            customlogs("Failed to delete device aliases", logfile)

        else:
            output_dict['status'] = "SUCCESS"
            output_dict['alias'] = str(alias_list)
            customlogs("Device aliases '%s' deleted successfully" %
                       output_dict['alias'], logfile)

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj
