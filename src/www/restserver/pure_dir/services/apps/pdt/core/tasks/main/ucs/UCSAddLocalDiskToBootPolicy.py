from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSAddLocalDiskToBootPolicy",
    task_name="Add local disk to boot policy",
    task_desc="Add local disk to boot policy in UCS",
    task_type="UCSM"
)


class UCSAddLocalDiskToBootPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("add_local_disk_to_boot_polcies")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.addLocalDiskToBootPolicies(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("delete_local_disk_to_boot_polcies")

        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.deleteLocalDiskToBootPolicies(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSAddLocalDiskToBootPolicyInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='UCS Fabric Name',
        api="getfilist()",
        dt_type="string",
        label="UCS Fabric Name",
        mandatory="1",
        mapval="0",
        name="fabric_id",
        static="False",
        svalue="",
        static_values="None",
        order=1)
    bootpolicyname = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Boot Policy Name',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="bootpolicyname",
        label="Boot Policy Name",
        mapval="1",
        svalue="__t201.UCSCreateBootPolicy.bootpolicyname",
        mandatory="1",
        order=2)


class UCSAddLocalDiskToBootPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
