from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
import re

metadata = dict(
    task_id="UCSCreateMACAddressPools",
    task_name="Create MAC Address Pools",
    task_desc="Create MAC Address pools in UCS",
    task_type="UCSM"
)


class UCSCreateMACAddressPools:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create MAC Address Pools")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateMACAddressPools(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Create MAC Address Pools")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteMACAddressPools(
            inputs, outputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def validate(self, item):
	if item.count(":")!=5:
            return False,"Invalid MAC Address format"
        for i in item.split(":"):
            for j in i:
                if j>"F" or (j<"A" and not j.isdigit()) or len(i)!=2:
                    return False,"Invalid MAC Address"
        return True,""


class UCSCreateMACAddressPoolsInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    mac_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='MAC Address Pool Name', api="", dt_type="string", label="Name", mapval="0", name="mac_name",
                       static="False", svalue="MAC_Pool_A", mandatory='1', static_values="", order=2)
    descr = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Description', api="", dt_type="string", label="Description", mapval="0", name="descr",
                    static="False", svalue="mac pool A", mandatory='1', static_values="", order=3)
    mac_order = Radiobutton(hidden='False', isbasic='True', helptext='Assignment order', api="", dt_type="string", label="Assignment order", mapval="0", name="mac_order", static="True",
                            static_values="default:1:Default|sequential:0:Sequential", svalue="sequential", mandatory='1', order=4)
    mac_start = Textbox(validation_criteria='function',  hidden='False', isbasic='True', helptext='MAC Start Address', api="", dt_type="string", label="First MAC Address", mapval="0", name="mac_start",
                        static="False", svalue="00:25:B5:91:1A:00", mandatory='1', static_values="", order=5, recommended="1")
    size = Textbox(validation_criteria='int|min:1|max:1000',  hidden='False', isbasic='True', helptext='Size', api="", dt_type="string", label="Size(1-1000)", mapval="0", name="size",
                   static="False", svalue="32", mandatory='1', static_values="", order=6, recommended="1")


class UCSCreateMACAddressPoolsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="mac_name", tvalue="MAC_Pool_A")
