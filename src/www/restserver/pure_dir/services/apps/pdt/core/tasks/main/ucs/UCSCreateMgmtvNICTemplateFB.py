from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateMgmtvNICTemplateFB",
    task_name="Create Management vNIC Template for FlashBlade",
    task_desc="Create Management vNIC template for FlashBlade in UCS",
    task_type="UCSM"
)


class UCSCreateMgmtvNICTemplateFB:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_Management_vNIC_Template_FB")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatevNICTemplateFB(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("create Management vNIC Template rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeletevNICTemplateFB(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

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

    def getmacpools(self, keys):
        mac_pools_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()

        if fabricid is None:
            ret.setResult(mac_pools_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        ret = result()
        mac_pool_obj = handle.query_classid("macpoolPool")
        for mac_pool in mac_pool_obj:
            mac_pools_list.append({"id": mac_pool.name, "selected": "0",
                                   "label": mac_pool.name + "(" + mac_pool.size + "/" + mac_pool.size + ")"})
        ucsm_logout(handle)
        ret.setResult(mac_pools_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret

    def getnwctrlpolicy(self, keys):
        nw_ctrl_list = []

        fabricid = getArg(keys, 'fabric_id')
        ret = result()

        if fabricid is None:
            ret.setResult(nw_ctrl_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res

        handle = res.getResult()

        ret = result()
        nw_ctrl_obj = handle.query_classid("nwctrlDefinition")
        for nw_ctrl in nw_ctrl_obj:
            if "org-root" in nw_ctrl.dn:
                nw_ctrl_list.append(
                    {"id": nw_ctrl.name, "selected": "0", "label": nw_ctrl.name})
        ucsm_logout(handle)
        ret.setResult(nw_ctrl_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret

    def getstatsthresholdpolicy(self, keys):
        res = result()
        stats_policy = [{"id": "default", "selected": "1", "label": "default"}, {
            "id": "", "selected": "0", "label": "not-set"}]
        res.setResult(stats_policy, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getpeerredundancytempl(self, keys):
        vnic_templ_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()

        if fabricid is None:
            ret.setResult(vnic_templ_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        vnic_templ_obj = handle.query_classid("vnicLanConnTempl")
        for vnic_templ in vnic_templ_obj:
            vnic_templ_list.append(
                {"id": vnic_templ.name, "selected": "0", "label": vnic_templ.name})
        vnic_templ_list.append(
            {"id": "not-set", "selected": "0", "label": "not-set"})
        ucsm_logout(handle)
        ret.setResult(vnic_templ_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B(subordinate)"}]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateMgmtvNICTemplateFBInputs:
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
    vnic_templ_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Management vnic template for FlashBlade',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="vnic_templ_name",
        static="False",
        svalue="vNIC_Mgmt_A",
        mandatory='1',
        static_values="",
        order=2,
        recommended="1")
    vnic_templ_desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Description',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="vnic_templ_desc",
        static="False",
        svalue="Mgmt vNIC Template for Fabric A",
        mandatory='1',
        static_values="",
        order=3)
    ucs_fabric_id = Radiobutton(
        hidden='True',
        isbasic='True',
        helptext='Fabric ID',
        api="getfis()",
        dt_type="string",
        label="Fabric ID",
        mapval="0",
        name="ucs_fabric_id",
        static="False",
        svalue="A",
        mandatory='1',
        static_values="",
        order=4)
    switch_id = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='Enable Failover',
        api="",
        dt_type="string",
        label="Enable Failover",
        mapval="0",
        name="switch_id",
        static="True",
        svalue="True",
        allow_multiple_values="1",
        mandatory='1',
        static_values="True@False:1:Enable Failover",
        order=5)
    redundancy_pair_type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Redundancy pair type',
        api="",
        dt_type="string",
        label="Redundancy Type",
        mapval="0",
        name="redundancy_pair_type",
        static="True",
        static_values="none:0:No Redundancy|primary:1:Primary Template|secondary:0:Secondary Template",
        svalue="none",
        mandatory='1',
        order=6)
    templ_type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Template Type",
        mapval="0",
        name="templ_type",
        static="True",
        static_values="initial-template:1:Initial Template|updating-template:0:Updating Template",
        svalue="updating-template",
        mandatory='1',
        order=7)
    peer_red_template = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Peer redundancy template',
        api="getpeerredundancytempl()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Peer Redundancy Template",
        mapval="0",
        name="peer_red_template",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=8)
    vlans = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='VLANs',
        api="getVLANs()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="VLANs",
        mapval="1",
        name="vlans",
        static="False",
        svalue="__t208.UCSCreateIBMgmtVLAN.vlan_name",
        allow_multiple_values="1",
        mandatory='1',
        static_values="",
        order=9)
    native_vlan = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Native VLAN',
        api="getVLANs()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Native VLAN",
        mapval="1",
        name="native_vlan",
        static="False",
        svalue="__t208.UCSCreateIBMgmtVLAN.vlan_name",
        mandatory='1',
        static_values="",
        order=10)
    cdn_source = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='CDN Source',
        api="",
        dt_type="string",
        label="CDN Source",
        mapval="0",
        name="cdn_source",
        static="True",
        static_values="vnic-name:1:vNIC Name|user-defined:0:User Defined",
        svalue="vnic-name",
        mandatory='1',
        order=11)
    mtu = Textbox(
        validation_criteria='int|min:1500|max:9000',
        hidden='False',
        isbasic='True',
        helptext='MTU',
        api="",
        dt_type="string",
        label="MTU",
        mapval="0",
        name="mtu",
        static="False",
        svalue="1500",
        mandatory='1',
        static_values="",
        order=12)
    ident_pool_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='MAC Pool name',
        api="getmacpools()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="MAC Pool",
        mapval="1",
        name="ident_pool_name",
        static="False",
        svalue="__t197.CreateMACAddressPoolsForFabricA.mac_name",
        mandatory='1',
        static_values="",
        order=13)
    nw_ctrl_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Network Control Policy',
        api="getnwctrlpolicy()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Network Control Policy",
        mapval="1",
        name="nw_ctrl_policy_name",
        static="False",
        svalue="__t196.CreateNetworkControlPolicy.name",
        mandatory='1',
        static_values="",
        order=14)


class UCSCreateMgmtvNICTemplateFBOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vnic_templ_name = Output(
        dt_type="string", name="vnic_templ_name", tvalue="BM-Mgmt")
