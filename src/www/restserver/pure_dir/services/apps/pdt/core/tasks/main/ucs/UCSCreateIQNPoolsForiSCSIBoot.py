from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import job_input_save, parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
import random
import re
import string

metadata = dict(
    task_id="UCSCreateIQNPoolsForiSCSIBoot",
    task_name="Create IQN Pools for iSCSI Boot",
    task_desc="Create IQN Pools for iSCSI boot in UCS",
    task_type="UCSM"
)


class UCSCreateIQNPoolsForiSCSIBoot:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create IQN Pool for iSCSI Boot")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateIQNPoolsForiSCSIBoot(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Delete IQN Pool for iSCSI Boot")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeleteIQNPool(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def prepare(self, jobid, texecid, inputs):
        res = result()
        iqn_address = self.gen_iqn()
        loginfo("Random iqn address:%s" % iqn_address)
        job_input_save(jobid, texecid, 'suffix', iqn_address)

        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def gen_hex(self, length):
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(length))

    def gen_iqn(self):
        iqn_pool = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        return iqn_pool

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def validate(self, item):
        if item != "" and re.match("^[0-9a-zA-Z\.:-]{0,64}$", item):
            pass
        else:
            return False, "Invalid IQN Suffix"
        return True, ""


class UCSCreateIQNPoolsForiSCSIBootInputs:
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
        helptext='IQN Pool Name',
        dt_type="string",
        static="False",
        api="",
        name="name",
        label="Name",
        static_values="",
        svalue="IQN-Pool",
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
        svalue="IQN Pool",
        mapval="",
        mandatory='1',
        order=3)
    prefix = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Prefix',
        dt_type="string",
        static="False",
        api="",
        name="prefix",
        label="Prefix",
        static_values="",
        svalue="iqn.1992-08.com.cisco",
        mapval="",
        mandatory='1',
        order=4,
        recommended="1")
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
        order=5)
    suffix = Textbox(
        validation_criteria='function',
        hidden='False',
        isbasic='True',
        helptext='Suffix',
        dt_type="string",
        static="False",
        api="",
        name="suffix",
        label="Suffix",
        static_values="",
        svalue="ucs-host",
        mapval="",
        mandatory='1',
        order=6)
    suffix_from = Textbox(
        validation_criteria='int|min:1|max:100',
        hidden='False',
        isbasic='True',
        helptext='Suffix From',
        dt_type="string",
        static="False",
        api="",
        name="suffix_from",
        label="From",
        static_values="",
        svalue="1",
        mapval="",
        mandatory='1',
        order=7)
    suffix_to = Textbox(
        validation_criteria='int|min:1|max:100',
        hidden='False',
        isbasic='True',
        helptext='Suffix To',
        dt_type="string",
        static="False",
        api="",
        name="suffix_to",
        label="To(1-1000)",
        static_values="",
        svalue="16",
        mapval="",
        mandatory='1',
        order=8)


class UCSCreateIQNPoolsForiSCSIBootOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(
        dt_type="string", name="name", tvalue="IQN-Pool")
