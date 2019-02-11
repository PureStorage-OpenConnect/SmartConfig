from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateBootPolicy",
    task_name="Create Boot policy in UCS",
    task_desc="Create UCS Boot policy",
    task_type="UCSM"
)


class UCSCreateBootPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_boot_policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.createbootpolicy(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("delete_boot_policy")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.deletebootpolicy(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        print ucs_list, res
        return res

    def purelist(self, keys):
        res = result()
        pure_list = get_device_list(device_type="PURE")
        res.setResult(pure_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateBootPolicyInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='UCS Fabric Name',
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
    boot_policy_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Boot Policy Name',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="boot_policy_name",
        label="Name",
        svalue="",
        mandatory='1',
        mapval="0",
        order=2,
        recommended="1")
    boot_policy_desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Description for Boot Policy',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="boot_policy_desc",
        label="Description",
        svalue="",
        mandatory='1',
        mapval="0",
        order=3)


class UCSCreateBootPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    bootpolicyname = Output(
        dt_type="string", name="bootpolicyname", tvalue="Boot-FC-A")
