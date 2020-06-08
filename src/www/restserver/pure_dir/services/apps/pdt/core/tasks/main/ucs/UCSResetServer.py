from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSResetServer",
    task_name="Reset UCS server",
    task_desc="Reset UCS Server",
    task_type="UCSM"
)


class UCSResetServer:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("reset_ucs_server")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsServerReset(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Reset Server rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSResetServerInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        static_values="",
        mandatory="1",
        order=1)


class UCSResetServerOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
