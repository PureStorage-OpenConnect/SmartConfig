from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSConfigureAppliancePorts",
    task_name="Configure Ports connected to Storage Array",
    task_desc="Configure Ports connected to Storage Array as Appliance Ports",
    task_type="UCSM"
)


class UCSConfigureAppliancePorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Configure Appliance Ports")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsConfigureAppliancePorts(
            taskinfo['inputs'], logfile)
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Configure Appliance Ports rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsUnconfigureAppliancePorts(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsmethports(self, keys):
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
        switch_id = 'sys/switch-' + ucs_fabric_name
        ports_dn = switch_id + "/slot-1/switch-ether"
        ports = handle.query_dn(ports_dn)
        ports_list_obj = handle.query_children(in_mo=ports)
        for port in ports_list_obj:
            if 'aggr' in port.rn:
                continue
            ports_list.append({"id": port.port_id,
                               "selected": "0",
                               "label": "Port " + port.port_id})
        ucsm_logout(handle)
        res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSConfigureAppliancePortsInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        static_values="",
        mandatory="1",
        order=1)
    ucs_fabric_id = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='UCS Fabric ID',
        api="getfis()",
        dt_type="string",
        label="Fabric ID",
        mandatory="1",
        mapval="0",
        name="ucs_fabric_id",
        static="False",
        svalue="A",
        static_values="",
        order=2)
    ports = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Ethernet ports to configure as appliance port',
        api="ucsmethports()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
        dt_type="list",
        mandatory="1",
        label="Ethernet Ports",
        mapval="0",
        name="ports",
        static="False",
        svalue="1|2",
        static_values="",
        order=3,
        recommended="1")


class UCSConfigureAppliancePortsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
