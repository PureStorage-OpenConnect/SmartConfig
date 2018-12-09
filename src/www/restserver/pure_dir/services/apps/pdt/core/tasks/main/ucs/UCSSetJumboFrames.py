from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSSetJumboFrames",
    task_name="Set Jumbo frames in UCS",
    task_desc="Set Jumbo frames in UCS",
    task_type="UCSM"
)


class UCSSetJumboFrames:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Set_Jumbo_Frames")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsSetJumboFrames(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS set jumbo frames rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsResetJumboFrames(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res


class UCSSetJumboFramesInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    mtu = Textbox(validation_criteria='int|min:1500|max:9216',  hidden='False', isbasic='True', helptext='Best Effort MTU Value', api="", dt_type="string", label="Best Effort MTU", mapval="0", name="mtu",
                  static="False", svalue="9216", mandatory='1', static_values="", order=2)


class UCSSetJumboFramesOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    mtu = Output(dt_type="string", name="mtu", tvalue="9216")
