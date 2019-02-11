from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *


metadata = dict(
    task_id="UCSCreatevNICvHBAPlacementPolicy",
    task_name="Create vNIC vHBA placement policy",
    task_desc="Create vNIC vHBA placement policy in UCS",
    task_type="UCSM"
)


class UCSCreatevNICvHBAPlacementPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create vNIC/vHBA Placement Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatevNICvHBAPlacementPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Create vNIC/vHBA Placement Policy rollback")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucsDeletevNICvHBAPlacementPolicy(inputs, outputs, logfile)
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreatevNICvHBAPlacementPolicyInputs:
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
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="VM-Host-Infra",
        mandatory='1',
        static_values="",
        order=2)
    scheme = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Virtual Slot Mapping Scheme",
        mapval="0",
        name="scheme",
        static="True",
        static_values="round-robin:1:Round Robin|linear-ordered:0:Linear Ordered",
        svalue="round-robin",
        mandatory='1',
        order=3)
    port_id = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Virtual Slot",
        mapval="0",
        name="port_id",
        static="True",
        static_values="1:1:1|2:0:2|3:0:3|4:0:4",
        svalue="1",
        mandatory='1',
        order=4)
    preference = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Selection Preference",
        mapval="0",
        name="preference",
        static="True",
        static_values="all:1:All|assigned-only:0:Assigned Only|exclude-dynamic:0:Exclude Dynamic|exclude-unassigned:0:Exclude Unassigned|exclude-usNIC:0:Exclude usNIC",
        svalue="assigned-only",
        mandatory='1',
        order=5)


class UCSCreatevNICvHBAPlacementPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
