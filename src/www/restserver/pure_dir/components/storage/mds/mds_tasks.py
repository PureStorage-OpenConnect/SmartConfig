#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :mds_tasks.py
# description     :MDSTasks class for handling tasks
# author          :Guruprasad
# version         :1.0
#####################################################################

import time

from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import getAsList
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.storage.mds.mds import *


class MDSTasks:
    def __init__(self, ipaddress='', username='', password=''):
        """
        Constructor - MDS Handler

        :param ipaddress: Switch ip
        :param username : Switch username
        :param password : Switch password
        """
        self.helper = MDS(ipaddr=ipaddress, uname=username, passwd=password)

    def enable_features(self, input_dict, logfile):
        """
        Task - Enables Features

        :param input_dict: Dictionary(feature_list)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        feature_list = input_dict['feature_list'].split('|')

        res = self.helper.enable_features(feature_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to enable features", logfile)

        else:
            op_feature_list = tuple(feature_list)
            customlogs("Features %s enabled successfully" %
                       str(op_feature_list), logfile)
            output_dict['status'] = "SUCCESS"

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def disable_features(self, input_dict, logfile):
        """
        Rollback - Disable Features

        :param input_dict: Dictionary(feature_list)
        :param logfile   : Log file handler

        :return: Returns the status
        """
        obj = result()
        output_dict = {}

        feature_list = input_dict['feature_list'].split('|')

        res = self.helper.disable_features(feature_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to disable features", logfile)

        else:
            op_feature_list = tuple(feature_list)
            customlogs("Features %s disabled successfully" %
                       str(op_feature_list), logfile)
            output_dict['status'] = "SUCCESS"

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

        res = self.helper.create_portchannel(input_dict['portchannel_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['portchannel_id'] = ""
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to create portchannel", logfile)

        else:
            customlogs("Port channel '%s' created successfully" %
                       input_dict['portchannel_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['portchannel_id'] = input_dict['portchannel_id']

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

        res = self.helper.delete_portchannel(input_dict['portchannel_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['portchannel_id'] = ""
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to delete portchannel", logfile)

        else:
            customlogs("Port channel '%s' deleted successfully" %
                       input_dict['portchannel_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['portchannel_id'] = input_dict['portchannel_id']

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
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

        res = self.helper.configure_portchannel(
            input_dict['portchannel_id'], fc_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to configure portchannel", logfile)

        else:
            op_fc_list = tuple(fc_list)
            customlogs("Port channel '%s' configured with interfaces %s" %
                       (input_dict['portchannel_id'], str(op_fc_list)), logfile)
            output_dict['status'] = "SUCCESS"

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

        res = self.helper.unconfigure_portchannel(
            input_dict['portchannel_id'], fc_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to remove portchannel configuration", logfile)

        else:
            op_fc_list = tuple(fc_list)
            customlogs("Port channel '%s' with interfaces %s removed" %
                       (input_dict['portchannel_id'], str(op_fc_list)), logfile)
            output_dict['status'] = "SUCCESS"

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

        res = self.helper.create_vsan(input_dict['vsan_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['vsan_id'] = ""
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to create VSAN", logfile)

        else:
            customlogs("VSAN '%s' created successfully" %
                       input_dict['vsan_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['vsan_id'] = input_dict['vsan_id']

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

        res = self.helper.delete_vsan(input_dict['vsan_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['vsan_id'] = ""
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to delete VSAN", logfile)

        else:
            customlogs("VSAN '%s' deleted successfully" %
                       input_dict['vsan_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['vsan_id'] = input_dict['vsan_id']

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

        interface_list = input_dict['fc_list'].split('|')

        tmp_pc_list = input_dict['pc_list'].split('|')
        for pc in tmp_pc_list:
            interface_list.append("port-channel " + pc)

        loginfo("Configuring vsan %s with interfaces %s" %
                (input_dict['vsan_id'], str(interface_list)))
        res = self.helper.configure_vsan(input_dict['vsan_id'], interface_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to configure VSAN", logfile)

        else:
            op_interface_list = tuple(interface_list)
            customlogs("VSAN '%s' configured with interfaces %s successfully" %
                       (input_dict['vsan_id'], str(op_interface_list)), logfile)
            output_dict['status'] = "SUCCESS"

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

        interface_list = input_dict['fc_list'].split('|')

        tmp_pc_list = input_dict['pc_list'].split('|')
        for pc in tmp_pc_list:
            interface_list.append("port-channel " + pc)

        loginfo("Unconfiguring vsan %s with interfaces %s" %
                (input_dict['vsan_id'], str(interface_list)))
        res = self.helper.unconfigure_vsan(
            input_dict['vsan_id'], interface_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to remove VSAN configuration", logfile)

        else:
            op_interface_list = tuple(interface_list)
            customlogs("Interfaces %s removed from VSAN '%s' successfully" %
                       (str(op_interface_list), input_dict['vsan_id']), logfile)
            output_dict['status'] = "SUCCESS"

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
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

        res = self.helper.create_device_aliases(fl_list)
        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['alias'] = str(alias_list)
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to create device aliases", logfile)

        else:
            output_dict['status'] = "SUCCESS"
            output_dict['alias'] = str(alias_list)
            op_alias_list = tuple(alias_list)
            customlogs("Device aliases %s created successfully" %
                       str(op_alias_list), logfile)

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

        res = self.helper.delete_device_aliases(alias_list)
        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['alias'] = str(alias_list)
            customlogs("%s" % res.getMsg(), logfile)
            customlogs("Failed to delete device aliases", logfile)

        else:
            output_dict['status'] = "SUCCESS"
            output_dict['alias'] = str(alias_list)
            op_alias_list = tuple(alias_list)
            customlogs("Device aliases %s deleted successfully" %
                       str(op_alias_list), logfile)

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

        for zone_dict in zones:
            zone_dict = eval(zone_dict)
            res = self.helper.create_zone(
                zone_dict['zone_name']['value'], input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("%s" % res.getMsg(), logfile)
                customlogs(
                    "Failed to create zones", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zone '%s' created successfully" %
                           zone_dict['zone_name']['value'], logfile)
                zone_members = zone_dict['zone_members']['value']
                upd_zone_members = []
                for memb in zone_members:
                    if memb == zone_dict['zone_name']['value']:
                        upd_zone_memb = memb + " init"
                    else:
                        upd_zone_memb = memb + " target"
                    upd_zone_members.append(upd_zone_memb)

                self.helper.add_to_zone(
                    zone_dict['zone_name']['value'], upd_zone_members, input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs(
                        "Failed to add members to the zone", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    op_zone_members = tuple(zone_members)
                    customlogs("Members %s added to the zone '%s' with VSAN '%s' successfully" % (
                        str(op_zone_members), zone_dict['zone_name']['value'], vsan_id), logfile)
                    zone_list.append(zone_dict['zone_name']['value'])

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

        zones = input_dict['zones'].split('|')

        for zone in zones:
            res = self.helper.delete_zone(zone, input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("%s" % res.getMsg(), logfile)
                customlogs("Failed to delete zones", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zone '%s' deleted successfully" % zone, logfile)

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

        for zoneset_dict in zonesets:
            zoneset_dict = eval(zoneset_dict)
            res = self.helper.create_zoneset(
                zoneset_dict['zoneset_name']['value'], input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("%s" % res.getMsg(), logfile)
                customlogs(
                    "Failed to create zoneset", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zoneset '%s' created successfully" %
                           zoneset_dict['zoneset_name']['value'], logfile)
                zoneset_members = getAsList(zoneset_dict['zoneset_members']['value'])
                self.helper.add_to_zoneset(
                    zoneset_dict['zoneset_name']['value'],
                    zoneset_members,
                    input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs(
                        "Failed to add members to the zoneset", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    op_zoneset_members = tuple(zoneset_members)
                    customlogs("Members %s added to the zoneset '%s' with vsan '%s' successfully" % (
                        str(op_zoneset_members), zoneset_dict['zoneset_name']['value'], vsan_id), logfile)
                    time.sleep(10)
                    res = self.helper.activate_zoneset(
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

        zonesets = input_dict['zonesets'].split('|')

        for zoneset in zonesets:
            res = self.helper.deactivate_zoneset(
                zoneset, input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("Zoneset deactivation failed", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zoneset '%s' with vsan '%s' deactivated successfully" % (
                    zoneset, input_dict['vsan_id']), logfile)
                res = self.helper.delete_zoneset(
                    zoneset, input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs("%s" % res.getMsg(), logfile)
                    customlogs("Failed to delete zoneset", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    customlogs("Zoneset '%s' deleted successfully" %
                               zoneset, logfile)

        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zonesets
        obj.setResult(output_dict, PTK_OKAY,
                      "Zonesets %s deleted successfully" % str(zonesets))
        return obj
