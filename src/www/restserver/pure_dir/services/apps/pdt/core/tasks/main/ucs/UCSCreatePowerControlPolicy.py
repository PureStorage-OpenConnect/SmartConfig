from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreatePowerControlPolicy",
    task_name="Create Power control Policy",
    task_desc="Create power control policy in UCS",
    task_type="UCSM"
)


class UCSCreatePowerControlPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Power Control Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatePowerControlPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Power Control Policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()
        res = obj.ucsDeletePowerControlPolicy(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreatePowerControlPolicyInputs:
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
        helptext='Power Control policy',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="No-Power-Cap",
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
        svalue="Power control policy",
        mandatory='1',
        static_values="",
        order=3)
    speed = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Fan Speed policy',
        api="",
        dt_type="string",
        label="Fan Speed Policy",
        mapval="0",
        name="speed",
        static="True",
        static_values="any:1:Any|low-power:0:Low Power|balanced:0:Balanced|performance:0:Performance|high-power:0:High Power|max-power:0:Max Power",
        svalue="any",
        mandatory='1',
        order=4)
    cap = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Power capping priority',
        api="",
        dt_type="string",
        label="Power Capping",
        mapval="0",
        name="cap",
        static="True",
        static_values="no-cap:0:No Cap|cap:1:cap",
        svalue="no-cap",
        mandatory='1',
        order=5)


class UCSCreatePowerControlPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
