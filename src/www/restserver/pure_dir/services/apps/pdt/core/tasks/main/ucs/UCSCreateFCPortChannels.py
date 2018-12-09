from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateFCPortChannels",
    task_name="Create FC Port Channels",
    task_desc="Create FC Port channels in UCS",
    task_type="UCSM"
)


class UCSCreateFCPortChannels:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Create_FC_Port_Channel")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateFCPortChannels(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS rollback FC Port Channel")

        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeleteFCPortChannels(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def ucsfcports(self, keys):
        ports_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            ret.setResult(ports_list, PTK_OKAY, "success")
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        res = result()
        value = fabricid.split("-")[-1].upper()
        switch_id = 'sys/switch-' + value
        ports_dn = switch_id + "/slot-1/switch-fc"
        ports = handle.query_dn(ports_dn)
        ports_list_obj = handle.query_children(in_mo=ports)
        selected = "1"
        for port in ports_list_obj:
            if ports_list:
                selected = "0"
            ports_list.append(
                {"id": port.port_id, "selected": selected, "label": "Port " + port.port_id})
        ucsm_logout(handle)
        res.setResult(ports_list, PTK_OKAY, "success")
        return res

    def getvsan(self, keys):
        temp_list = []
	ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        ucs_fabricid = getArg(keys, 'ucs_fabric_id')
        if ucs_fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret
        handle = res.getResult()
        res = result()
        vsan_list = handle.query_classid("fabricVsan")
        selected = "1"
        for vsan in vsan_list:
            if temp_list:
                selected = "0"
            if vsan.switch_id == ucs_fabricid:
                temp_list.append(
                    {"id": vsan.name, "selected": selected, "label": vsan.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def ucsgetfcports(self, keys):
        ports_list = []
        res = result()
        # TODO:returning first 16 ports that can be configured as Unified Ports Change later
        for i in range(1, 17):
            ports_entity = {
                "id": str(i), "selected": "0", "label": "Port " + str(i)}
            ports_list.append(ports_entity)
        res.setResult(ports_list, PTK_OKAY, "success")
        return res


class UCSCreateFCPortChannelsInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', api="getfilist()", dt_type="string", label="UCS Fabric Name", mapval="0",
                         mandatory="1", name="fabric_id", static_values="None", static="False", svalue="", order=1)
    fc_port_channel_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='FC Port Channel Name', dt_type="string",  static="False",  static_values="None", api="",
                                   name="fc_port_channel_name", label="FC Port Channel Name", mapval="0", svalue="", mandatory='1', order=2, recommended="1")
    port_id = Textbox(validation_criteria='',  hidden='False', isbasic='True', helptext='Port ID', dt_type="string", static="False", static_values="None", api="",
                      name="port_id", label="ID", svalue="", mandatory='1', mapval="0", order=3)
    ucs_fabric_id = Dropdown(hidden='True', isbasic='True', helptext='Primary or Subordinate FI', dt_type="string",  static="True", mandatory="1", static_values="A:0:Fabric Interconnect A(primary)|B:1:Fabric Interconnect B(subordinate)",
                             api="", name="ucs_fabric_id", label="fabric id ", svalue="", mapval="0", order=4)
    port_list = Multiselect(hidden='False', isbasic='True', helptext='FC Port List', dt_type="string",  static="False", mandatory="1", static_values="None",
                            api="ucsgetfcports()|[fabric_id:1:fabric_id.value]", name="port_list", label="FC Port List", svalue="", mapval="0", order=5, recommended="1")
    admin_speed = Dropdown(hidden='False', isbasic='True', helptext='Port channel admin Speed', dt_type="string",  static="True",  static_values="auto:1:Auto|1gbps:0:1 Gbps|2gbps:0:2 Gbps|4gbps:0:4Gbps|8gbps:0:8 Gbps|16gbps:0:16 Gbps",
                           api="", name="admin_speed", label="Port Channel Admin Speed", svalue="", mandatory='1', mapval="0", order=6)
    vsan_name = Dropdown(hidden='False', isbasic='True', helptext='VSAN Name', dt_type="string",  api="getvsan()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
                        static="False", mapval="1", static_values="None", name="vsan_name", label="VSAN",  svalue="", mandatory='1', order=7)


class UCSCreateFCPortChannelsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    fc_port_channel_name = Output(
        dt_type="string", name="fc_port_channel_name", tvalue="po2")
