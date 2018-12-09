from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateUUIDSuffixPool",
    task_name="Create UUID Suffix pool",
    task_desc="Create UUID Suffix pool in UCS",
    task_type="UCSM"
)


class UCSCreateUUIDSuffixPool:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create UUID Suffix Pool")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateUUIDSuffixPool(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Create UUID Suffix Pool rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteUUIDSuffixPool(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res


class UCSCreateUUIDSuffixPoolInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         static_values="", label="UCS Fabric Name", svalue="", mapval="", mandatory="1", order=1)
    name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='UUID Suffix Pool name', api="", dt_type="string", label="Name", mapval="0", name="name",
                   static_values="", mandatory='1', static="False", svalue="UUID_Pool", order=2)
    desc = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Description', api="", dt_type="string", label="Description", mapval="0", name="desc",
                   static_values="", mandatory='1', static="False", svalue="uuid pool", order=3)
    prefix = Radiobutton(hidden='False', isbasic='True', helptext='Prefix', api="", dt_type="string", label="Prefix", mapval="0", name="prefix", static="True",
                         mandatory='1', static_values="derived:1:Derived|other:0:other", svalue="derived", order=4, recommended="1")
    order = Radiobutton(hidden='False', isbasic='True', helptext='Assignment Order', api="", dt_type="string", label="Assignment Order", mapval="0", name="order", static="True",
                        mandatory='1', static_values="default:1:Default|sequential:0:Sequential", svalue="sequential", order=5)
    uuid_from = Textbox(validation_criteria='',  hidden='False', isbasic='True', helptext='UUID From', api="", dt_type="string", label="From", mapval="0", name="uuid_from",
                        static="False", static_values="", mandatory='1', svalue="0000-000000000001", order=6, recommended="1")
    size = Textbox(validation_criteria='int|min:1|max:1000',  hidden='False', isbasic='True', helptext='Size of UUID block', api="", dt_type="string", label="Size(1-1000)", mapval="0", name="size",
                   static_values="", mandatory='1', static="False", svalue="32", order=7, recommended="1")


class UCSCreateUUIDSuffixPoolOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="UUID_Pool")
