from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateVSANs",
    task_name="Create vSAN in UCS",
    task_desc="Create vSAN in UCS",
    task_type="UCSM"
)


class UCSCreateVSANs:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_VSAN")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucsCreateVSANs(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS rollback VSAN")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucsDeleteVSANs(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        print ucs_list, res
        return res


class UCSCreateVSANsInputs:

    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        api="getfilist()",
        dt_type="string",
        label="UCS Fabric Name",
        mapval="0",
        mandatory="1",
        name="fabric_id",
        static="False",
        svalue="",
        static_values="None",
        order=1)
    vsan_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='VSAN Name',
        dt_type="string",
        static="False",
        static_values="None",
        api="",
        name="vsan_name",
        label="Name",
        svalue="",
        mapval="0",
        mandatory='1',
        order=2)
    zoning_state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='FC Zoning',
        dt_type="string",
        static="True",
        static_values="disabled:1:Disabled|enabled:0:Enabled",
        api="",
        name="zoning_state",
        label="FC Zoning",
        svalue="",
        mapval="0",
        mandatory='1',
        order=3)
    ucs_fabric_id = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Fabric ID',
        dt_type="string",
        static="True",
        static_values="A:1:Fabric Interconnect A(primary)|B:0:Fabric Interconnect B(subordinate)",
        api="",
        name="ucs_fabric_id",
        label="Fabric id ",
        svalue="",
        mapval="0",
        mandatory='1',
        order=4)
    vsan_id = Textbox(
        validation_criteria='int|min:100|max:2067',
        hidden='False',
        isbasic='True',
        helptext='VSAN ID',
        dt_type="string",
        static="False",
        static_values="None",
        api="",
        name="vsan_id",
        label="VSAN ID",
        svalue="",
        mapval="0",
        mandatory='1',
        order=5)
    fcoe_vlan = Textbox(
        validation_criteria='int|min:100|max:2067',
        hidden='False',
        isbasic='True',
        helptext='FCoE VLAN',
        dt_type="string",
        static="False",
        static_values="None",
        api="",
        name="fcoe_vlan",
        label="FCoE VLAN",
        svalue="",
        mapval="0",
        mandatory='1',
        order=6)


class UCSCreateVSANsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vsan = Output(dt_type="string", name="vsan", tvalue="VSAN_B")
    vsan_name = Output(dt_type="string", name="vsan_name",
                       tvalue="B/net-VSAN_B")
