from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.network.nexus.nexus import *
from pure_dir.components.common import *

metadata = dict(
    task_id="NEXUS9kConfigureiSCSIInterface",
    task_name="Configure iSCSI Interface",
    task_desc="Configure iSCSI Interface",
    task_type="NEXUS"
)


class NEXUS9kConfigureiSCSIInterface:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Configure iSCSI Interface")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusConfigureiSCSIInterface(
                    taskinfo['inputs'], logfile, "n9k")
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              "Connection to NEXUS failed")
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          "Failed to get NEXUS switch credentials")

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("NEXUS Configure iSCSI Interface rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusUnconfigureiSCSIInterface(
                    inputs, logfile, "n9k")
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              "Connection to NEXUS failed")
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          "Failed to get NEXUS switch credentials")

        return parseTaskResult(res)

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 9k")
        res.setResult(nexus_list, PTK_OKAY, "success")
        return res

    def get_intf_list(self, keys):
        res = result()
        intf_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(intf_list, PTK_OKAY, "success")
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                intf_list = obj.get_interface_list()
            else:
                loginfo("Unable to login to the Nexus")
                res.setResult(intf_list, PTK_INTERNALERROR,
                              "Unable to login to the Nexus")
        else:
            loginfo("Unable to get the device credentials of the Nexus")
            res.setResult(intf_list, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the Nexus")

        res.setResult(intf_list, PTK_OKAY, "success")
        return res


class NEXUS9kConfigureiSCSIInterfaceInputs:
    nexus_id = Dropdown(hidden='True', isbasic='', helptext='', dt_type="string", static="False", static_values="",
                        api="getnexuslist()",
                        name="nexus_id", label="Nexus switch", svalue="", mapval="", mandatory="1", order=1)
    slot_chassis = Multiselectdropdown(hidden='', isbasic='True', helptext='Select the interfaces to be configured',
                                       dt_type="string", static="False",
                                       api="get_intf_list()|[nexus_id:1:nexus_id.value]", name="slot_chassis",
                                       label="Interfaces", static_values="",
                                       svalue="Eth1/49", mapval="", mandatory="1", group_member="1",
                                       recommended="1")
    vlan_id = Textbox(validation_criteria='int|min:1|max:3967', hidden='', isbasic='True', helptext='Virtual LAN id',
                      dt_type="string", static="False", api="", name="vlan_id", static_values="",
                      label="VLAN id", svalue="115", mapval="", mandatory="1", group_member="1", recommended="1")
    intf_set = Group(validation_criteria='', hidden='', isbasic='True',
                     helptext='Select the interfaces to be configured and the corresponding VLAN id', dt_type="string", static="False",
                     api="", name="intf_set", label="Configure Interfaces", static_values="",
                     svalue="{'slot_chassis': {'ismapped': '0', 'value': 'Eth1/49'}, 'vlan_id': {'ismapped': '0', 'value': '901'}}|{'slot_chassis': {'ismapped': '0', 'value': 'Eth1/50'}, 'vlan_id': {'ismapped': '0', 'value': '902'}}",
                     mapval="", mandatory="1", members=["slot_chassis", "vlan_id"], add="True", order=2,
                     recommended="1")
    mtu_value = Textbox(validation_criteria='int|min:1500|max:9216', hidden='', isbasic='',
                        helptext='Maximum transfer unit', dt_type="string", static="False", api="", name="mtu_value",
                        static_values="",
                        label="MTU value (1500-9216)", svalue="9216", mapval="", mandatory="1", order=3)


class NEXUS9kConfigureiSCSIInterfaceOutputs:
    intf_set = Output(dt_type="string", name="intf_set", tvalue="")
    mtu_value = Output(dt_type="string", name="mtu_value", tvalue="9216")
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")