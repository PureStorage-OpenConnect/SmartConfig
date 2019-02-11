from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateNCPForAppliancePorts",
    task_name="Create network control policy for appliance ports",
    task_desc="Create network control policy for appliance ports",
    task_type="UCSM"
)


class UCSCreateNCPForAppliancePorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Network Control Policy for appliance port")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateNCPForAppliancePort(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Network Control Policy for appliance port rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()
        res = obj.ucsDeleteNCPForAppliancePorts(
            inputs, outputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateNCPForAppliancePortsInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        static_values="",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)
    name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="Enable-CDP",
        mandatory='1',
        static_values="",
        order=2)
    descr = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="descr",
        static="False",
        svalue="Network Control Policy",
        mandatory='1',
        static_values="",
        order=3)
    cdp = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='CDP',
        api="",
        dt_type="string",
        label="CDP",
        mapval="0",
        name="cdp",
        static="True",
        static_values="enabled:1:Enabled|disabled:0:Disabled",
        svalue="enabled",
        mandatory='1',
        order=4)
    mac_mode = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='MAC Register mode',
        api="",
        dt_type="string",
        label="MAC Register Mode",
        mapval="0",
        name="mac_mode",
        static="True",
        static_values="only-native-vlan:1:Only Native VLAN|all-host-vlans:0:All Host VLANs",
        svalue="only-native-vlan",
        mandatory='1',
        order=5)
    uplink_fail = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Action on uplink fail',
        api="",
        dt_type="string",
        label="Action on Uplink Fail",
        mapval="0",
        name="uplink_fail",
        static="True",
        static_values="link-down:0:Link Down|warning:1:Warning",
        svalue="link-down",
        mandatory='1',
        order=6)
    forge = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='MAC Security forge',
        api="",
        dt_type="string",
        label="MAC Security Forge",
        mapval="0",
        name="forge",
        static="True",
        static_values="allow:1:Allow|deny:0:Deny",
        svalue="allow",
        mandatory='1',
        order=7)
    lldp_tra = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='LLD Transmit',
        api="",
        dt_type="string",
        label="LLDP Transmit",
        mapval="0",
        name="lldp_tra",
        static="True",
        static_values="disabled:1:Disabled|enabled:0:Enabled",
        svalue="disabled",
        mandatory='1',
        order=8)
    lldp_rec = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='LLDP Receive',
        api="",
        dt_type="string",
        label="LLDP Receive",
        mapval="0",
        name="lldp_rec",
        static="True",
        static_values="disabled:1:Disabled|enabled:0:Enabled",
        svalue="disabled",
        mandatory='1',
        order=9)


class UCSCreateNCPForAppliancePortsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="Enable-CDP")
