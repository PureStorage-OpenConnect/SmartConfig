from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSConfigureFCStoragePort",
    task_name="Configure FC Storage Port",
    task_desc="Configure FC Storage Port in both FIs in FC switching mode",
    task_type="UCSM"
)


class UCSConfigureFCStoragePort:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("ucs_configure_fc_storage_port")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucs_configure_fc_storage_port(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("unconfigure_fc_storage_ports")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucs_unconfigure_fc_storage_port(inputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucs_get_fc_ports(self, keys):
        ports_list = []
        res = result()
        for i in range(1, 3):
            ports_entity = {
                "id": str(i), "selected": "0", "label": "Port " + str(i)}
            ports_list.append(ports_entity)
        res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSConfigureFCStoragePortInputs:
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
        helptext='',
        dt_type="string",
        static="True",
        mandatory="1",
        static_values="A:0:Fabric Interconnect A(primary)|B:1:Fabric Interconnect B(subordinate)",
        api="",
        name="ucs_fabric_id",
        label="Fabric ID ",
        svalue="",
        mapval="0",
        order=2)

    fc_ports = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Configure FC Storage port',
        api="ucs_get_fc_ports()|[fabric_id:1:fabric_id.value]",
        dt_type="list",
        mandatory="1",
        label="FC Ports",
        mapval="0",
        name="fc_ports",
        static="False",
        svalue="1|2",
        static_values="",
        order=3,
        recommended="1")


class UCSConfigureFCStoragePortOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
