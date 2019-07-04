from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import NEXUSTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.infra.apiresults import *

metadata = dict(
    task_id="NEXUS5kConfigureVirtualPortChannelsToUCS",
    task_name="Configure Virtual Port Channels To UCS",
    task_desc="Configure Virtual Port Channels To UCS for Nexus switch",
    task_type="NEXUS"
)


class NEXUS5kConfigureVirtualPortChannelsToUCS:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Configure Virtual Port Channels To UCS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusConfigureVirtualPortChannelsToUCS(
                    taskinfo['inputs'], logfile, "n5k")
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("NEXUS Configure Virtual Port Channels To UCS rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusUnconfigureVirtualPortChannelsToUCS(
                    inputs, logfile, "n5k")
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 5k")
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
                        res.setResult(intf_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                intf_list = obj.get_interface_list()
            else:
                loginfo("Unable to login to the Nexus")
                res.setResult(intf_list, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the Nexus")
            res.setResult(intf_list, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        res.setResult(intf_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class NEXUS5kConfigureVirtualPortChannelsToUCSInputs:
    nexus_id = Dropdown(
        hidden='True',
        isbasic='',
        helptext='',
        dt_type="string",
        static="False",
        static_values="",
        api="getnexuslist()",
        name="nexus_id",
        label="Nexus switch",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)
    slot_chassis = Multiselect(
        hidden='',
        isbasic='True',
        helptext='Select the interfaces to be configured',
        dt_type="string",
        static="False",
        api="get_intf_list()|[nexus_id:1:nexus_id.value]",
        name="slot_chassis",
        label="Interfaces",
        static_values="",
        svalue="Eth1/49",
        mapval="",
        mandatory="1",
        order=2,
        recommended="1")
    port_channel_number = Textbox(
        validation_criteria='int|min:1|max:4096',
        hidden='',
        isbasic='True',
        helptext='Port channel number to be configured',
        dt_type="string",
        static="False",
        api="",
        name="port_channel_number",
        static_values="",
        label="Port channel number (1-4096)",
        svalue="151",
        mapval="",
        mandatory="1",
        order=3,
        recommended="1")
    native_vlan_id = Textbox(
        validation_criteria='int|min:1|max:3967',
        hidden='',
        isbasic='True',
        helptext='Native virtual LAN id',
        dt_type="string",
        static="False",
        api="",
        name="native_vlan_id",
        static_values="",
        label="Native VLAN id",
        svalue="2",
        mapval="",
        mandatory="1",
        order=4,
        recommended="1")
    vlan = Textbox(
        validation_criteria='int|min:1|max:3967',
        hidden='',
        isbasic='True',
        helptext="Allowed virtual LAN id's",
        dt_type="string",
        static="False",
        api="",
        name="vlan",
        static_values="",
        label="Allowed VLAN id's",
        svalue="115,200-203",
        mapval="",
        mandatory="1",
        order=5,
        recommended="1",
        group_member="1")
    allowed_vlans_set = Group(
        validation_criteria='',
        hidden='',
        isbasic='True',
        helptext="Allowed virtual LAN id's",
        dt_type="string",
        static="False",
        api="",
        name="allowed_vlans_set",
        label="Allowed VLAN id's",
        static_values="",
        svalue="",
        mapval="",
        mandatory="1",
        members=["vlan"],
        add="True",
        order=5,
        recommended="1")
    counter_value = Textbox(
        validation_criteria='int|min:1|max:3',
        hidden='',
        isbasic='',
        helptext='Counter value',
        dt_type="string",
        static="False",
        api="",
        name="counter_value",
        static_values="",
        label="Counter (1-3)",
        svalue="3",
        mapval="",
        mandatory="1",
        order=7)
    interval_delay = Textbox(
        validation_criteria='int|min:5|max:300',
        hidden='',
        isbasic='',
        helptext='Delay interval',
        dt_type="string",
        static="False",
        api="",
        name="interval_delay",
        static_values="",
        label="Delay interval (5-300)",
        svalue="60",
        mapval="",
        mandatory="1",
        order=8)


class NEXUS5kConfigureVirtualPortChannelsToUCSOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    slot_chassis = Output(dt_type="string", name="slot_chassis", tvalue="1/51")
    port_channel_number = Output(
        dt_type="string", name="port_channel_number", tvalue="151")
    native_vlan_id = Output(
        dt_type="string", name="native_vlan_id", tvalue="2")
    counter_value = Output(dt_type="string", name="counter_value", tvalue="3")
    interval_delay = Output(
        dt_type="string", name="interval_delay", tvalue="60")
