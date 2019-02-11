from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="USAddiSCSIBoot",
    task_name="Add iSCSI Boot to boot policy",
    task_desc="Add iSCSI Boot to boot policy in UCS",
    task_type="UCSM"
)


class UCSAddiSCSIBoot:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("add_iSCSI_boot_to_boot_policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.addiSCSIBoot(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("add_iSCSI_boot_to_boot_policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.deleteiSCSIBoot(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSAddiSCSIBootInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
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
    iSCSI_A_vNIC = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='iSCSI-A-vNIC',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="iSCSI_A_vNIC",
        label="iSCSI vNIC",
        svalue="iSCSI-A-vNIC",
        mandatory="1",
        mapval="0",
        order=2)
    iSCSI_B_vNIC = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='iSCSI-B-vNIC',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="iSCSI_B_vNIC",
        label="iSCSI vNIC",
        svalue="iSCSI-B-vNIC",
        mandatory="1",
        mapval="0",
        order=3)
    bootpolicyname = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Boot policy name',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="bootpolicyname",
        label="Boot Policy Name",
        mapval="1",
        svalue="__t201.UCSCreateBootPolicy.bootpolicyname",
        mandatory="1",
        order=4)


class UCSAddiSCSIBootOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
