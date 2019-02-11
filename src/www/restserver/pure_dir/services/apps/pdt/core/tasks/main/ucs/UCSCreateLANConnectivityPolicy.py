from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateLANConnectivityPolicy",
    task_name="Create LAN Connectivity policy",
    task_desc="Create LAN Connectiviy Policy in UCS",
    task_type="UCSM"
)


class UCSCreateLANConnectivityPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("create_LAN_connectivity_policy")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateLANConnectivityPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: UCS Delete LAN Connectivity Policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteLANConnectivityPolicy(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res


class UCSCreateLANConnectivityPolicyInputs:
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
    lan_conn_policy_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='LAN Connectivity policy name',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="lan_conn_policy_name",
        static="False",
        svalue="Infra-LAN-Policy",
        mandatory='1',
        static_values="",
        order=2,
        recommended="1")
    lan_conn_policy_desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Description',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="lan_conn_policy_desc",
        static="False",
        svalue="lan-policy",
        mandatory='1',
        static_values="",
        order=3)


class UCSCreateLANConnectivityPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    lan_conn_policy_name = Output(
        dt_type="string", name="lan_conn_policy_name", tvalue="Infra-LAN-Policy")
