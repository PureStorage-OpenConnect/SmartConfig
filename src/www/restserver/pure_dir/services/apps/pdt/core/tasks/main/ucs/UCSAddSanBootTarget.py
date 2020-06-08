from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSAddSanBootTarget",
    task_name="Add SAN Boot target in UCS",
    task_desc="Add SAN Boot target in UCS",
    task_type="UCSM"
)


class UCSAddSanBootTarget:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("add_san_boot_target")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.addSanBootTarget(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("delete_san_boot_target")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.deleteSanBootTarget(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSAddSanBootTargetInputs:
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
    target_lun = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Target LUN',
        dt_type="string",
        api="",
        static="False",
        static_values="None",
        label="Boot Target LUN",
        name="target_lun",
        svalue="",
        mandatory='1',
        mapval="0",
        order=2)
    wwpn = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Boot target WWPN',
        dt_type="string",
        api="",
        static="False",
        static_values="None",
        label="Boot Target WWPN",
        name="wwpn",
        mapval="1",
        svalue="",
        mandatory='1',
        order=3)
    type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='SAN Boot Type',
        dt_type="string",
        api="False",
        static="True",
        static_values="primary:1:Primary|secondary:0:Secondary",
        name="type",
        label="Type",
        svalue="primary",
        mandatory='1',
        mapval="0",
        order=4)
    bootpolicyname = Textbox(
        validation_criteria='',
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
        mandatory='1',
        order=5)
    san_type = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='SAN Type',
        dt_type="string",
        api="",
        static="False",
        static_values="None",
        name="san_type",
        label="SAN Boot Target Type",
        svalue="primary",
        mandatory='1',
        mapval="0",
        order=6)


class UCSAddSanBootTargetOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
