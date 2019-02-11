from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateiSCSIvNIC",
    task_name="Create iSCSI vNIC",
    task_desc="Create iSCSI vNIC from vNIC template in UCS",
    task_type="UCSM"
)


class UCSCreateiSCSIvNIC:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("create_iSCSI_vNIC")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateiSCSIvNIC(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("create_iSCSI_vNIC")

        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeleteiSCSIvNIC(inputs, logfile)

        obj.release_ucs_handle()
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

    def getVLANs(self, keys):
        vlan_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()

        if fabricid is None:
            ret.setResult(vlan_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        ret = result()
        vlan_obj = handle.query_classid("fabricVlan")
        for vlan in vlan_obj:
            if vlan.switch_id == "dual" and vlan.name != "default":
                vlan_list.append(
                    {"id": vlan.name, "selected": "0", "label": vlan.name})
        ucsm_logout(handle)
        ret.setResult(vlan_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret


class UCSCreateiSCSIvNICInputs:
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
        helptext='',
        api="getlanconpolicylist()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="LAN Policy",
        mapval="1",
        name="policy_name",
        static="False",
        svalue="__t223.UCSCreateLANConnectivityPolicy.lan_conn_policy_name",
        mandatory='1',
        static_values="",
        order=2)
    vnic_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="vnic_name",
        static="False",
        svalue="iSCSI-A-vNIC",
        mandatory='1',
        static_values="",
        order=3,
        recommended="1")
    adaptor_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Adaptor policy name',
        api="getadapterpolicy()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Adapter Policy",
        mapval="0",
        name="adaptor_policy_name",
        static="False",
        svalue="default",
        mandatory='1',
        static_values="",
        order=4)
    overlay_vnic = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Overlay vNIC',
        api="getvnictemplate()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Overlay vNIC",
        mapval="1",
        name="overlay_vnic",
        static="False",
        svalue="__t230.UCSCreatevNICiSCSI_A.vnic_name",
        mandatory='1',
        static_values="",
        order=5)
    vlan_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='VLAN name',
        api="getVLANs()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="VLAN",
        mapval="1",
        name="vlan_name",
        static="False",
        svalue="__t210.UCSCreateiSCSIVLAN.vlan_name",
        mandatory='1',
        static_values="",
        order=6,
        recommended="1")


class UCSCreateiSCSIvNICOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vnic_name = Output(dt_type="string", name="vnic_name",
                       tvalue="iSCSI-A-vNIC")
