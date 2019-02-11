from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSSetStorageVSANToFCPorts",
    task_name="Assign VSAN to FC Storage Port",
    task_desc="Assign VSAN to FC Storage Port in both FIs",
    task_type="UCSM"
)


class UCSSetStorageVSANToFCPorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("ucs_assign_vsan_fc_storage_port")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
	res = obj.ucs_assign_vsan_fc_storage_port(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("ucs_assign_default_vsan_fc_storage_port")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucs_assign_default_vsan_fc_storage_port(inputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def ucs_get_fc_ports(self, keys):
        ports_list = []
        res = result()
        for i in range(1,7):
            ports_entity = {
                "id": str(i), "selected": "0", "label": "Port " + str(i)}
            ports_list.append(ports_entity)
        res.setResult(ports_list, PTK_OKAY, "success")
        return res

    def getstoragevsan(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        ucs_fabricid = getArg(keys, 'ucs_fabric_id')
        if ucs_fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret
        handle = res.getResult()
        res = result()
        vsan_list = handle.query_classid("fabricVsan")
        selected = "1"
        for vsan in vsan_list:
            if temp_list:
                selected = "0"
            if vsan.switch_id == ucs_fabricid and vsan.if_role == 'storage':
                temp_list.append(
                    {"id": vsan.name, "selected": selected, "label": vsan.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res


class UCSSetStorageVSANToFCPortsInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", svalue="", mapval="", static_values="", mandatory="1", order=1)
    ucs_fabric_id = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="True",
        mandatory="1",
        static_values="A:0:Fabric Interconnect A(primary)|B:1:Fabric Interconnect B(subordinate)",
        api="",
        name="ucs_fabric_id",
        label="Fabric ID",
        svalue="",
        mapval="0",
        order=2)

    fc_ports = Multiselect(hidden='False', isbasic='True', helptext='Configure FC Storage port', api="ucs_get_fc_ports()|[fabric_id:1:fabric_id.value]", dt_type="list",
                               mandatory="1", label="FC Ports", mapval="0", name="fc_ports", static="False", svalue="1|2", static_values="", order=3, recommended="1")
    vsan_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getstoragevsan()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
        mapval="1",
        name="vsan_name",
        static_values="None",
        label="Select Storage VSAN",
        svalue="",
        mandatory='1',
        order=4)




class UCSSetStorageVSANToFCPortsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
