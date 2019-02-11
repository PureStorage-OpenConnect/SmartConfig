from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateWWNNPool",
    task_name="Create WWNN Pool in UCS",
    task_desc="Create WWNN pool in UCS",
    task_type="UCSM"
)


class UCSCreateWWNNPool:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create WWNN Pool")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateWWNNPool(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Delete WWNN Pool")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeleteWWNPool(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def validate(self, item):
        if ":" in item:
            first_octet = item.split(":")
            if first_octet[0] != "20":
                return False, "WWNN Prefix must start with 20"
        else:
            return False, "Invalid WWNN Prefix"
        return True, ""


class UCSCreateWWNNPoolInputs:
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
        helptext='WWNN Pool Name',
        dt_type="string",
        static="False",
        api="",
        name="name",
        label="Name",
        static_values="",
        svalue="",
        mapval="",
        mandatory='1',
        order=2)
    desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Description',
        dt_type="string",
        static="False",
        api="",
        name="desc",
        label="Description",
        static_values="",
        svalue="",
        mapval="",
        mandatory='1',
        order=3)
    order = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Assignment Order',
        dt_type="string",
        static="True",
        api="",
        name="order",
        label="Assignment Order",
        static_values="default:1:Default|sequential:0:Sequential",
        svalue="sequential",
        mapval="",
        mandatory='1',
        order=4)
    from_ip = Textbox(
        validation_criteria='function',
        hidden='False',
        isbasic='True',
        helptext='WWNN Pool From',
        dt_type="string",
        static="False",
        api="",
        name="from_ip",
        label="From",
        static_values="",
        svalue="",
        mapval="",
        mandatory='1',
        order=5)
    size = Textbox(
        validation_criteria='int|min:1|max:1000',
        hidden='False',
        isbasic='True',
        helptext='Size of WWNN Pool Block',
        dt_type="string",
        static="False",
        api="",
        name="size",
        label="Size(1-1000)",
        static_values="",
        svalue="",
        mapval="",
        mandatory='1',
        order=6)


class UCSCreateWWNNPoolOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="WWNN_Pool")
