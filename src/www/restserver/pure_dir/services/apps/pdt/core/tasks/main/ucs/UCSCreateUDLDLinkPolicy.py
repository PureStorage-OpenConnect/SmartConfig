from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateUDLDLinkPolicy",
    task_name="Create UDLD Link policy",
    task_desc="Create UDLD Link Policy in UCS",
    task_type="UCSM"
)


class UCSCreateUDLDLinkPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create UDLD Link Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateUDLDLinkPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete UDLD Link Policy rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteUDLDLinkPolicy(
            inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateUDLDLinkPolicyInputs:
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
        svalue="UDLD-Pol",
        mandatory='1',
        static_values="",
        order=2)
    admin_state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Admin State',
        api="",
        dt_type="string",
        label="Admin State",
        mapval="0",
        name="admin_state",
        static="True",
        static_values="enabled:1:Enabled|disabled:0:Disabled",
        svalue="disabled",
        mandatory='1',
        order=3)
    mode = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='UDLD Mode',
        api="",
        dt_type="string",
        label="Mode",
        mapval="0",
        name="mode",
        static="True",
        static_values="normal:1:Normal|aggressive:0:Aggressive",
        svalue="normal",
        mandatory='1',
        order=4)


class UCSCreateUDLDLinkPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="UDLD-Pol")
