from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'

metadata = dict(
    task_id="UCSAcknowledgeCiscoUCSChassis",
    task_name="Acknowledge Cisco UCS Chassis",
    task_desc="Acknowledge All Chassis in UCS",
    task_type="UCSM"
)


class UCSAcknowledgeCiscoUCSChassis:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("acknowledge_cisco_ucs_chassis")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.acknowledgeUcsChassis(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Acknowledge Cicso UCS Chassis rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsmchassis(self, keys):
        chassis_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid is None:
            res.setResult(chassis_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()

        ret = result()
        chassislist = handle.query_classid("EquipmentChassis")
        selected = "1"
        for chassis in chassislist:
            if chassis_list:
                selected = "0"
            chassis_list.append(
                {"id": chassis.id, "selected": selected, "label": "Chassis " + chassis.id})
        ucsm_logout(handle)
        ret.setResult(chassis_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret


class UCSAcknowledgeCiscoUCSChassisInputs:
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
    state = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Choose Acknowledge State of UCS',
        dt_type="string",
        static="True",
        api="",
        name="state",
        label="Acknowledge state",
        static_values="re-acknowledge:1:Acknowledge Chassis|remove-chassis:0:Remove Chassis|decommission:0:Decommission Chassis",
        svalue="re-acknowledge",
        mapval="",
        mandatory="1",
        order=2)


class UCSAcknowledgeCiscoUCSChassisOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
