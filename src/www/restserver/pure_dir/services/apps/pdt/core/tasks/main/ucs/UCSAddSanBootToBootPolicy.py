from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSAddSanBootToBootPolicy",
    task_name="Add SAN Boot to boot policy",
    task_desc="Add SAN boot to boot policy in UCS",
    task_type="UCSM"
)


class UCSAddSanBootToBootPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("add_san_boot_to_boot_policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.addSanBootToBootPolicy(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("delete_san_boot_to_boot_policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.deleteSanBootToBootPolicy(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        print ucs_list, res
        return res


class UCSAddSanBootToBootPolicyInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='UCS Fabric Name', api="getfilist()", dt_type="string", label="UCS Fabric Name", mandatory="1",
                         mapval="0", name="fabric_id", static="False", svalue="", static_values="None", order=1)
    vhba = Textbox(validation_criteria='',  hidden='False', isbasic='True', helptext='vHBA', dt_type="string", api="", static="False", static_values="",
                   name="vhba", label="vHBA", svalue="Fabric-A", mandatory='1', mapval="0", order=2)
    type = Radiobutton(hidden='False', isbasic='True', helptext='Type', dt_type="string", api="", static="True", static_values="primary:1:Primary|secondary:0:Secondary",
                   name="type", label="Type", svalue="primary", mandatory='1', mapval="0", order=3)
    bootpolicyname = Textbox(validation_criteria='',  hidden='False', isbasic='True', helptext='Boot Policy Name', dt_type="string", api="", static="False", static_values="", name="bootpolicyname",
                             label="Boot Policy Name", mapval="1", svalue="__t201.UCSCreateBootPolicy.bootpolicyname", mandatory='1', order=4)


class UCSAddSanBootToBootPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
