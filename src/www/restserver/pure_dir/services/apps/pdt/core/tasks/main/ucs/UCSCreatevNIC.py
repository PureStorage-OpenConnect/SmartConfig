from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreatevNIC",
    task_name="Create vNIC",
    task_desc="Create vNIC from vNIC template in UCS",
    task_type="UCSM"
)


class UCSCreatevNIC:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("create_vNIC")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatevNIC(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("UCS Creating vNIC rollback")
        res = get_ucs_handle(inputs['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucsDeletevNIC(inputs, outputs, logfile)
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getadapterpolicy(self, keys):
        res = result()
        adapter_pol = [
            {
                "id": "linux", "selected": "0", "label": "Linux"}, {
                "id": "smbclient", "selected": "0", "label": "SMBCLient"}, {
                "id": "smbserver", "selected": "0", "label": "SMBServer"}, {
                    "id": "sriov", "selected": "0", "label": "SRIOV"}, {
                        "id": "solaris", "selected": "0", "label": "Solaris"}, {
                            "id": "VMWare", "selected": "1", "label": "VMWare"}, {
                                "id": "VMWarePassThrough", "selected": "0", "label": "VMWarePassThrough"}, {
                                    "id": "Windows", "selected": "0", "label": "Windows"}, {
                                        "id": "default", "selected": "0", "label": "default"}, {
                                            "id": "usNIC", "selected": "0", "label": "usNIC"}, {
                                                "id": "usNICOracleRAC", "selected": "0", "label": "usNICOracleRAC"}]
        res.setResult(adapter_pol, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getlanconpolicylist(self, keys):
        lan_policy_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(lan_policy_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()
        policies = handle.query_classid("VnicLanConnPolicy")
        for lanpolicy in policies:
            lan_policy_list.append(
                {"id": lanpolicy.rn, "selected": "0", "label": lanpolicy.rn})
        lan_policy_list.append(
            {"id": "not-set", "selected": "1", "label": "not-set"})
        ucsm_logout(handle)
        res.setResult(lan_policy_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getvnictemplate(self, keys):
        vnic_templ_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(vnic_templ_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()

        vnic_templ_obj = handle.query_classid("vnicLanConnTempl")
        for vnic_templ in vnic_templ_obj:
            vnic_templ_list.append(
                {"id": vnic_templ.name, "selected": "0", "label": vnic_templ.name})
        vnic_templ_list.append(
            {"id": "not-set", "selected": "1", "label": "not-set"})
        ucsm_logout(handle)
        ret.setResult(vnic_templ_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret


class UCSCreatevNICInputs:
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
    policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='LAN Connectivity Policy name',
        api="getlanconpolicylist()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="LAN Policy",
        mapval="1",
        name="policy_name",
        static="False",
        svalue="__t214.UCSCreateLANConnectivityPolicy.lan_conn_policy_name",
        mandatory='1',
        static_values="",
        order=2)
    vnic_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='vNIC Name',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="vnic_name",
        static="False",
        svalue="00-Mgmt-A",
        mandatory='1',
        static_values="",
        order=3,
        recommended="1")
    adaptor_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Adapter policy',
        api="getadapterpolicy()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Adapter Policy",
        mapval="0",
        name="adaptor_policy_name",
        static="False",
        svalue="VMWare",
        mandatory='1',
        static_values="",
        order=4)
    nw_templ_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='vNIC Template name',
        api="getvnictemplate()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="vNIC Template",
        mapval="1",
        name="nw_templ_name",
        static="False",
        svalue="__t207.UCSCreateMgmtvNiCTemplateForFabricA.mgmt_vnic_templ_name",
        mandatory='1',
        static_values="",
        order=5)


class UCSCreatevNICOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vnic_name = Output(dt_type="string", name="vnic_name", tvalue="00-Mgmt-A")
