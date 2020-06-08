from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateSANConnectivityPolicy",
    task_name="Create SAN connectivity policy",
    task_desc="Create SAN connectivity policy in UCS",
    task_type="UCSM"
)


class UCSCreateSANConnectivityPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_SAN_connectivity_policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateSANConnectivityPolicy(
            taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS SAN connectivity policy rollback")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeleteSANConnectivityPolicy(
            inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getwwpn(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        s = handle.query_classid("fcpoolInitiators")
        selected = "1"
        for w in s:
            if temp_list:
                selected = "0"
            if w.purpose == "port-wwn-assignment":
                temp_list.append(
                    {"id": w.name, "selected": selected, "label": w.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getwwnn(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        s = handle.query_classid("fcpoolInitiators")
        selected = "1"
        for w in s:
            if temp_list:
                selected = "0"
            if w.purpose == "node-wwn-assignment":
                temp_list.append(
                    {"id": w.name, "selected": selected, "label": w.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateSANConnectivityPolicyInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        api="getfilist()",
        dt_type="string",
        label="UCS Fabric Name",
        mandatory="1",
        mapval="0",
        name="fabric_id",
        static="False",
        svalue="",
        static_values="None",
        order=1)
    san_conn_policy_name = Textbox(
        validation_criteria='str|min:1|max:16',
        hidden='False',
        isbasic='True',
        helptext='SAN Connectivity policy',
        dt_type="string",
        api="",
        static="False",
        static_values="None",
        name="san_conn_policy_name",
        label="Name",
        svalue="",
        mapval="0",
        mandatory='1',
        order=2,
        recommended="1")
    san_conn_policy_desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Description',
        dt_type="string",
        api="",
        static="False",
        static_values="None",
        name="san_conn_policy_desc",
        label="Description",
        svalue="",
        mapval="0",
        mandatory='1',
        order=3)
    ident_pool_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='WWNN Assignment',
        dt_type="string",
        static="False",
        api="getwwnn()|[fabric_id:1:fabric_id.value]",
        mapval="1",
        static_values="None",
        name="ident_pool_name",
        label="WWNN Assignment",
        svalue="",
        mandatory='1',
        order=4)


class UCSCreateSANConnectivityPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    san_conn_policy_name = Output(
        dt_type="string", name="san_conn_policy_name", tvalue="Infra-SAN-Policy")
