from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateApplicationvNICTemplate",
    task_name="Create Application vNIC Template",
    task_desc="Create application vNIC template in UCS",
    task_type="UCSM"
)


class UCSCreateApplicationvNICTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("create_Application_vNIC_Template")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateApplicationvNICTemplate(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("create Application vNIC Template rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteApplicationvNICTemplate(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B(subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        print "results are", res.getResult()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def getpeerredundancytempl(self, keys):
        vnic_templ_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(vnic_templ_list, PTK_OKAY, "success")
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
            {"id": "not-set", "selected": "1", "label": "not-set"})
        ucsm_logout(handle)
        ret.setResult(vnic_templ_list, PTK_OKAY, "success")
        return ret

    def getVLANs(self, keys):
        vlan_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(vlan_list, PTK_OKAY, "success")
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        vlan_obj = handle.query_classid("fabricVlan")
        for vlan in vlan_obj:
            if vlan.switch_id == "dual" and vlan.name != "default":
                vlan_list.append(
                    {"id": vlan.name, "selected": "0", "label": vlan.name})
        ucsm_logout(handle)
        ret.setResult(vlan_list, PTK_OKAY, "success")
        return ret

    def getmacpools(self, keys):
        mac_pools_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(mac_pools_list, PTK_OKAY, "success")
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        mac_pool_obj = handle.query_classid("macpoolPool")
        for mac_pool in mac_pool_obj:
            mac_pools_list.append({"id": mac_pool.name, "selected": "0",
                                   "label": mac_pool.name + "(" + mac_pool.size + "/" + mac_pool.size + ")"})
        ucsm_logout(handle)
        ret.setResult(mac_pools_list, PTK_OKAY, "success")
        return ret

    def getnwctrlpolicy(self, keys):
        nw_ctrl_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(nw_ctrl_list, PTK_OKAY, "success")
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        nw_ctrl_obj = handle.query_classid("nwctrlDefinition")
        for nw_ctrl in nw_ctrl_obj:
            if "org-root" in nw_ctrl.dn:
                nw_ctrl_list.append(
                    {"id": nw_ctrl.name, "selected": "0", "label": nw_ctrl.name})
        ucsm_logout(handle)
        ret.setResult(nw_ctrl_list, PTK_OKAY, "success")
        return ret

    def getstatsthresholdpolicy(self, keys):
        res = result()
        stats_policy = [{"id": "default", "selected": "1", "label": "default"}, {
            "id": "", "selected": "0", "label": "not-set"}]
        res.setResult(stats_policy, PTK_OKAY, "success")
        return res


class UCSCreateApplicationvNICTemplateInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    application_vnic_templ_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Application vNIC Template', api="", dt_type="string", label="Name", mapval="0", name="application_vnic_templ_name",
                                          static="False", svalue="vNIC_App_A", mandatory='1', static_values="", order=2)
    application_vnic_templ_desc = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Description', api="", dt_type="string", label="Description", mapval="0",
                                          name="application_vnic_templ_desc", static="False", svalue="", mandatory='1', static_values="", order=3)
    ucs_fabric_id = Radiobutton(hidden='False', isbasic='True', helptext='Fabric ID', api="getfis()", dt_type="string", label="Fabric ID", mapval="0",
                                name="ucs_fabric_id", static="False", svalue="A", mandatory='1', static_values="", order=4)
    redundancy_pair_type = Radiobutton(hidden='False', isbasic='True', helptext='redundancy pair type', api="", dt_type="string", label="Redundancy Type", mapval="0", name="redundancy_pair_type", static="True",
                                       static_values="none:0:No Redundancy|primary:1:Primary Template|secondary:0:Secondary Template", svalue="primary", mandatory='1', order=5)
    templ_type = Radiobutton(hidden='False', isbasic='True', helptext='template type', api="", dt_type="string", label="Template Type", mapval="0", name="templ_type", static="True",
                             static_values="initial-template:1:Initial Template|updating-template:0:Updating Template", svalue="updating-template", mandatory='1', order=6)
    peer_red_template = Dropdown(hidden='False', isbasic='True', helptext='peer redundancy template', api="getpeerredundancytempl()|[fabric_id:1:fabric_id.value]", dt_type="string", label="Peer Redundancy Template",
                                 mapval="0", name="peer_red_template", static="False", svalue="", mandatory='1', static_values="", order=7)
    vlans = Checkbox(hidden='False', isbasic='True', helptext='VLANs', api="getVLANs()|[fabric_id:1:fabric_id.value]", dt_type="string", label="VLANs", mapval="1", name="vlans",
                     static="False", svalue="__t212.UCSCreateTrafficVLAN.vlan_name|__t213.UCSCreateTrafficVLAN.vlan_name|__t214.UCSCreateTrafficVLAN.vlan_name", mandatory='1', static_values="", allow_multiple_values="1", order=8)
    native_vlan = Checkbox(hidden='False', isbasic='True', helptext='Native VLAN', api="", dt_type="string", label="Native VLAN", mapval="0",
                           name="native_vlan", static="True", svalue="default", mandatory='1', static_values="default:1:default", allow_multiple_values="0", order=9)
    cdn_source = Radiobutton(hidden='False', isbasic='True', helptext='CDN Source', api="", dt_type="string", label="CDN Source", mapval="0", name="cdn_source", static="True",
                             static_values="vnic-name:1:vNIC Name|user-defined:0:User Defined", svalue="vnic-name", mandatory='1', order=10)
    mtu = Textbox(validation_criteria='int|min:1500|max:9000',  hidden='False', isbasic='True', helptext='MTU', api="", dt_type="string", label="MTU", mapval="0", name="mtu",
                  static="False", svalue="9000", static_values="", mandatory='1', order=11)
    ident_pool_name = Dropdown(hidden='False', isbasic='True', helptext='MAC Pools', api="getmacpools()|[fabric_id:1:fabric_id.value]", dt_type="string", label="MAC Pool", mapval="1",
                               name="ident_pool_name", static="False", svalue="__t197.CreateMACAddressPoolsForFabricA.mac_name", mandatory='1', static_values="", order=12)
    nw_ctrl_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Network Control policy', api="getnwctrlpolicy()|[fabric_id:1:fabric_id.value]", dt_type="string", label="Network Control Policy", mapval="1",
                                   name="nw_ctrl_policy_name", static="False", svalue="__t196.CreateNetworkControlPolicy.name", mandatory='1', static_values="", order=13)


class UCSCreateApplicationvNICTemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    application_vnic_templ_name = Output(
        dt_type="string", name="application_vnic_templ_name", tvalue="vNIC_App_A")
