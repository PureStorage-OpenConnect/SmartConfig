from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateIPPoolsForiSCSIBoot",
    task_name="Create IP Pools for iSCSI Boot",
    task_desc="Create IP Pools for iSCSI boot in UCS",
    task_type="UCSM"
)


class UCSCreateIPPoolsForiSCSIBoot:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create IP Pool for iSCSI Boot")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateIPPoolsForiSCSIBoot(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Delete IP Pool for iSCSI Boot")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeleteIPPoolsForiSCSIBoot(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateIPPoolsForiSCSIBootInputs:
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
    ip_pool_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='iSCSI IP Pool Name',
        dt_type="string",
        static="False",
        api="",
        name="ip_pool_name",
        label="Name",
        static_values="",
        svalue="iSCSI-IP-Pool-A",
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
        svalue="IP Pool",
        mapval="",
        mandatory='1',
        order=3)
    order = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Assignment order',
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
    ip_from = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='From IP Range',
        dt_type="string",
        static="False",
        api="",
        name="ip_from",
        label="From",
        static_values="",
        svalue="192.168.10.20",
        mapval="",
        mandatory="1",
        order=5)
    size = Textbox(
        validation_criteria='int|min:1|max:1000',
        hidden='False',
        isbasic='True',
        helptext='Size of IP pool',
        api="",
        dt_type="string",
        mandatory='1',
        static_values="",
        label="Size(1-1000)",
        mapval="0",
        name="size",
        static="False",
        svalue="12",
        order=6)
    mask = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Subnet Mask',
        api="",
        dt_type="string",
        mandatory='1',
        static_values="",
        label="Subnet Mask",
        mapval="0",
        name="mask",
        static="False",
        svalue="255.255.255.0",
        order=7)
    pri_dns = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Primary DNS',
        api="",
        dt_type="string",
        mandatory='1',
        static_values="",
        label="Primary DNS",
        mapval="0",
        name="pri_dns",
        static="False",
        svalue="0.0.0.0",
        order=8)
    sec_dns = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Secondary DNS',
        api="",
        dt_type="string",
        mandatory='1',
        static_values="",
        label="Secondary DNS",
        mapval="0",
        name="sec_dns",
        static="False",
        svalue="0.0.0.0",
        order=9)


class UCSCreateIPPoolsForiSCSIBootOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    ip_pool_name = Output(
        dt_type="string", name="ip_pool_name", tvalue="iSCSI-IP-Pool-A")
