from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSUpdateDefaultMaintenancePolicy",
    task_name="Update Default Maintenance Policy",
    task_desc="Update default maintenance policy in UCS",
    task_type="UCSM"
)


class UCSUpdateDefaultMaintenancePolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Update Default Maintenance Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucsUpdateDefaultMaintenancePolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Reset default maintenance policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsResetMaintenancePolicy(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res


class UCSUpdateDefaultMaintenancePolicyInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    descr = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="Description", mapval="0", name="descr",
                    static="False", svalue="Default maintenance policy", mandatory='1', static_values="", order=2)
    timer = Dropdown(hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="Soft Shutdown Timer", mapval="0", name="timer", static="True",
                     static_values="150-Secs:1:150 Secs|never:0:never|300-Secs:0:300 Secs|600-Secs:0:600 Secs", svalue="150-Secs", mandatory='1', order=3)
    uptime = Radiobutton(hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="Reboot Policy", mapval="0", name="uptime", static="True",
                         static_values="user-ack:1:User Ack|immediate:0:Immediate|timer-automatic:0:Timer Automatic", svalue="user-ack", mandatory='1', order=4)
    trigger = Checkbox(hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="On Next Boot", mapval="0", name="trigger", static="True",
                       static_values="on-next-boot:1:On Next Boot", svalue="on-next-boot", mandatory='1', allow_multiple_values="0", order=5)


class UCSUpdateDefaultMaintenancePolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
