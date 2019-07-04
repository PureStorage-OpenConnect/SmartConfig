from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSApplyPoliciesToAppliancePort",
    task_name="Apply policies to appliance ports",
    task_desc="Apply policies to appliance ports",
    task_type="UCSM"
)


class UCSApplyPoliciesToAppliancePort:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Apply policies to appliance ports")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsApplyPoliciesToAppliancePorts(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Network Control Policy rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsRemovePoliciesFromAppliancePorts(
            inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsapplianceports(self, keys):
        ports_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')
        ucs_fabric_name = getArg(keys, 'ucs_fabric_id')

        if fabricid is None:
            res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()
        ports = handle.query_classid("fabricEthEstcEp")
        for port in ports:
            ports_list.append({"id": port.port_id,
                               "selected": "0",
                               "label": "Port " + port.port_id})
        ucsm_logout(handle)
        res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsgetappliancevlan(self, keys):
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
            if vlan.name != "default" and vlan.if_role == "nas-storage":
                vlan_list.append(
                    {"id": vlan.name, "selected": "0", "label": vlan.name})
        ucsm_logout(handle)
        ret.setResult(vlan_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret


class UCSApplyPoliciesToAppliancePortInputs:
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
    ucs_fabric_id = Radiobutton(
        hidden='',
        isbasic='True',
        helptext='Primary or Subordinate FI',
        dt_type="string",
        static="True",
        api="",
        name="ucs_fabric_id",
        label="Fabric ID",
        static_values="A:1:Fabric Interconnect A(primary)|B:0:Fabric Interconnect B(subordinate)",
        svalue="",
        mapval="",
        mandatory="1",
        order=2)
    ports = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Appliance Interfaces',
        api="ucsapplianceports()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
        dt_type="list",
        mandatory="1",
        label="Appliance Interfaces",
        mapval="0",
        name="ports",
        static="False",
        svalue="1|2",
        static_values="",
        order=3,
        recommended="1")
    ncp_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Network Control Policy",
        mapval="0",
        name="ncp_name",
        static="False",
        svalue="Storage-NCP",
        mandatory='1',
        static_values="",
        order=4)
    vlan = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Appliance Interfaces',
        api="ucsgetappliancevlan()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
        dt_type="list",
        mandatory="1",
        label="Appliance Interfaces",
        mapval="0",
        name="vlan",
        static="False",
        svalue="1|2",
        static_values="",
        order=5,
        recommended="1")


class UCSApplyPoliciesToAppliancePortOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="Enable-CDP")
