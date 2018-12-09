#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :mds_tasks.py
# description     :MDSTasks class for handling tasks
# author          :Guruprasad
# version         :1.0
#####################################################################

from pycsco.nxos.device import Device
from pycsco.nxos import error
from pycsco.nxos.utils import nxapi_lib as nxapi_fn
import xmltodict
import time

from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.components.storage.mds.mds import *


class MDSTasks:
    def __init__(self, ipaddress='', username='', password=''):
        self.helper = MDS(ipaddr=ipaddress, uname=username, passwd=password)

    def enable_features(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        feature_list = input_dict['feature_list'].split('|')

        res = self.helper.enable_features(feature_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Enable_Features task failed", logfile)

        else:
	    op_feature_list = tuple([x.encode('utf-8') for x in feature_list])
            customlogs("Features %s enabled successfully" %
                       str(op_feature_list), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("MDS: Enable_Features task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def disable_features(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        feature_list = input_dict['feature_list'].split('|')

        res = self.helper.disable_features(feature_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Disable_Features task failed", logfile)

        else:
	    op_feature_list = tuple([x.encode('utf-8') for x in feature_list])
            customlogs("Features %s disabled successfully" %
                       str(op_feature_list), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("MDS: Disable_Features task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_portchannel(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        res = self.helper.create_portchannel(input_dict['portchannel_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['portchannel_id'] = ""
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Create_PortChannel task failed", logfile)

        else:
            customlogs("Portchannel '%s' created successfully" %
                       input_dict['portchannel_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['portchannel_id'] = input_dict['portchannel_id']

        customlogs("MDS: Create_PortChannel task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def delete_portchannel(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        res = self.helper.delete_portchannel(input_dict['portchannel_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['portchannel_id'] = ""
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Delete_PortChannel task failed", logfile)

        else:
            customlogs("Portchannel '%s' deleted successfully" %
                       input_dict['portchannel_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['portchannel_id'] = input_dict['portchannel_id']

        customlogs("MDS: Delete_PortChannel task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def configure_portchannel(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        fc_list = input_dict['fc_list'].split('|')

        res = self.helper.configure_portchannel(
            input_dict['portchannel_id'], fc_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Configure_PortChannel task failed", logfile)

        else:
	    op_fc_list = tuple([x.encode('utf-8') for x in fc_list])
            customlogs("Port-channel '%s' configured with interfaces %s" %
                       (input_dict['portchannel_id'], str(op_fc_list)), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("MDS: Configure_PortChannel task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def unconfigure_portchannel(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        fc_list = input_dict['fc_list'].split('|')

        res = self.helper.unconfigure_portchannel(
            input_dict['portchannel_id'], fc_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Unconfigure_PortChannel task failed", logfile)

        else:
	    op_fc_list = tuple([x.encode('utf-8') for x in fc_list])
            customlogs("Port-channel '%s' with interfaces %s removed" %
                       (input_dict['portchannel_id'], str(op_fc_list)), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("MDS: Unconfigure_PortChannel task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_vsan(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        res = self.helper.create_vsan(input_dict['vsan_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['vsan_id'] = ""
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Create_VSAN task failed", logfile)

        else:
            customlogs("Vsan '%s' created successfully" %
                       input_dict['vsan_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['vsan_id'] = input_dict['vsan_id']

        customlogs("MDS: Create_VSAN task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def delete_vsan(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        res = self.helper.delete_vsan(input_dict['vsan_id'])

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['vsan_id'] = ""
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Delete_VSAN task failed", logfile)

        else:
            customlogs("Vsan '%s' deleted successfully" %
                       input_dict['vsan_id'], logfile)
            output_dict['status'] = "SUCCESS"
            output_dict['vsan_id'] = input_dict['vsan_id']

        customlogs("MDS: Delete_VSAN task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def configure_vsan(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        interface_list = input_dict['fc_list'].split('|')

        tmp_pc_list = input_dict['pc_list'].split('|')
        for pc in tmp_pc_list:
            interface_list.append("port-channel " + pc)

        loginfo("MDS: Configuring vsan %s with interfaces %s" %
                (input_dict['vsan_id'], str(interface_list)))
        res = self.helper.configure_vsan(input_dict['vsan_id'], interface_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Configure_VSAN task failed", logfile)

        else:
	    op_interface_list = tuple([x.encode('utf-8') for x in interface_list])
            customlogs("Vsan '%s' configured with interfaces %s successfully" %
                       (input_dict['vsan_id'], str(op_interface_list)), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("MDS: Configure_VSAN task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def unconfigure_vsan(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        interface_list = input_dict['fc_list'].split('|')

        tmp_pc_list = input_dict['pc_list'].split('|')
        for pc in tmp_pc_list:
            interface_list.append("port-channel " + pc)

        loginfo("MDS: Unconfiguring vsan %s with interfaces %s" %
                (input_dict['vsan_id'], str(interface_list)))
        res = self.helper.unconfigure_vsan(
            input_dict['vsan_id'], interface_list)

        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Unconfigure_VSAN task failed", logfile)

        else:
	    op_interface_list = tuple([x.encode('utf-8') for x in interface_list])
            customlogs("Interfaces %s removed from vsan '%s' successfully" %
                       (str(op_interface_list), input_dict['vsan_id']), logfile)
            output_dict['status'] = "SUCCESS"

        customlogs("MDS: Unconfigure_VSAN task success\n", logfile)
        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_device_aliases(self, input_dict, logfile):
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
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Create_Device_Aliases task failed", logfile)

        else:
            output_dict['status'] = "SUCCESS"
            output_dict['alias'] = str(alias_list)
	    op_alias_list = tuple([x.encode('utf-8') for x in alias_list])
            customlogs("Device aliases %s created successfully" %
                       str(op_alias_list), logfile)
            customlogs("MDS: Create_Device_Aliases task success\n", logfile)

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def delete_device_aliases(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        alias_list = input_dict['aliases'].split('|')

        res = self.helper.delete_device_aliases(alias_list)
        if res.getStatus() != PTK_OKAY:
            output_dict['status'] = "FAILURE"
            output_dict['alias'] = str(alias_list)
            customlogs("MDS: %s" % res.getMsg(), logfile)
            customlogs("MDS: Delete_Device_Aliases task failed", logfile)

        else:
            output_dict['status'] = "SUCCESS"
            output_dict['alias'] = str(alias_list)
	    op_alias_list = tuple([x.encode('utf-8') for x in alias_list])
            customlogs("Device aliases %s deleted successfully" %
                       str(op_alias_list), logfile)
            customlogs("MDS: Delete_Device_Aliases task success\n", logfile)

        obj.setResult(output_dict, res.getStatus(), res.getMsg())
        return obj

    def create_zones(self, input_dict, logfile):
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
                customlogs("MDS: %s" % res.getMsg(), logfile)
                customlogs(
                    "MDS: Create_Zones task failed with zone creation", logfile)
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
                        "MDS: Create_Zones task failed with adding members to zone", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
	            op_zone_members = tuple([x.encode('utf-8') for x in zone_members])
                    customlogs("Members %s added to the zone '%s' with vsan '%s' successfully" % (str(op_zone_members),
                                                                                                    zone_dict['zone_name']['value'], vsan_id), logfile)
                    zone_list.append(zone_dict['zone_name']['value'])

        customlogs("MDS: Create_Zones task success\n", logfile)
        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zone_list
        obj.setResult(output_dict, PTK_OKAY,
                      "Zones %s created successfully" % str(zone_list))
        return obj

    def delete_zones(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        zones = input_dict['zones'].split('|')

        for zone in zones:
            res = self.helper.delete_zone(zone, input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("MDS: %s" % res.getMsg(), logfile)
                customlogs("MDS: Delete_Zones task failed", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zone '%s' deleted successfully" % zone, logfile)

        customlogs("MDS: Delete_Zones task success\n", logfile)
        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zones
        obj.setResult(output_dict, PTK_OKAY,
                      "Zones %s deleted successfully" % str(zones))
        return obj

    def create_zonesets(self, input_dict, logfile):
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
                customlogs("MDS: %s" % res.getMsg(), logfile)
                customlogs(
                    "MDS: Create_Zoneset task failed with zoneset creation", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zoneset '%s' created successfully" %
                           zoneset_dict['zoneset_name']['value'], logfile)
                zoneset_members = zoneset_dict['zoneset_members']['value']
                self.helper.add_to_zoneset(
                    zoneset_dict['zoneset_name']['value'], zoneset_dict['zoneset_members']['value'], input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs(
                        "MDS: Create_Zoneset task failed with adding members to zoneset", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
	            op_zoneset_members = tuple([x.encode('utf-8') for x in zoneset_members])
                    customlogs("Members %s added to the zoneset '%s' with vsan '%s' successfully" % (str(op_zoneset_members),
                                                                                                       zoneset_dict['zoneset_name']['value'], vsan_id), logfile)
                    time.sleep(10)
                    res = self.helper.activate_zoneset(
                        zoneset_dict['zoneset_name']['value'], input_dict['vsan_id'])
                    if res.getStatus() != PTK_OKAY:
                        output_dict['status'] = "FAILURE"
                        customlogs(
                            "MDS: Zoneset activation failed", logfile)
                        obj.setResult(
                            output_dict, res.getStatus(), res.getMsg())
                        return obj
                    else:
                        customlogs("Zoneset '%s' with vsan '%s' activated successfully" % (
                            zoneset_dict['zoneset_name']['value'], input_dict['vsan_id']), logfile)
                        zoneset_list.append(
                            zoneset_dict['zoneset_name']['value'])

            customlogs("MDS: Create_Zoneset task success\n", logfile)
            output_dict['status'] = 'SUCCESS'
            output_dict['zoneset_list'] = zoneset_list
            obj.setResult(output_dict, PTK_OKAY,
                          "Zonesets %s created successfully" % str(zoneset_list))
            return obj

    def delete_zonesets(self, input_dict, logfile):
        obj = result()
        output_dict = {}

        zonesets = input_dict['zonesets'].split('|')

        for zoneset in zonesets:
            res = self.helper.deactivate_zoneset(
                zoneset, input_dict['vsan_id'])
            if res.getStatus() != PTK_OKAY:
                output_dict['status'] = "FAILURE"
                customlogs("MDS: Zoneset deactivation failed", logfile)
                obj.setResult(output_dict, res.getStatus(), res.getMsg())
                return obj
            else:
                customlogs("Zoneset '%s' with vsan '%s' deactivated successfully" % (
                    zoneset, input_dict['vsan_id']), logfile)
                res = self.helper.delete_zoneset(
                    zoneset, input_dict['vsan_id'])
                if res.getStatus() != PTK_OKAY:
                    output_dict['status'] = "FAILURE"
                    customlogs("MDS: %s" % res.getMsg(), logfile)
                    customlogs("MDS: Delete_Zonesets task failed", logfile)
                    obj.setResult(output_dict, res.getStatus(), res.getMsg())
                    return obj
                else:
                    customlogs("Zoneset '%s' deleted successfully" %
                               zoneset, logfile)

        customlogs("MDS: Delete_Zonesets task success\n", logfile)
        output_dict['status'] = 'SUCCESS'
        output_dict['zone_list'] = zonesets
        obj.setResult(output_dict, PTK_OKAY,
                      "Zonesets %s deleted successfully" % str(zonesets))
        return obj
