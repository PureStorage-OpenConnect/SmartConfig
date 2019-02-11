from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pytz import common_timezones
metadata = dict(
    task_id="UCSSynchronizeUCStoNTP",
    task_name="Synchronize UCS to NTP",
    task_desc="Synchronize UCS to NTP in UCS",
    task_type="UCSM"
)


class UCSSynchronizeUCStoNTP:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("synchronize ucs to ntp")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsSynchronizeUCStoNTP(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("synchronize ucs to ntp rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsRollbackSynchronizeUCStoNTP(
            inputs, outputs, logfile)
        obj.release_ucs_handle()

        return res

    def gettimezones(self, keys):
        res = result()
        tzlist = []
        for tz in common_timezones:
            tz_entity = {"id": tz, "label": tz, "selected": "0"}
            tzlist.append(tz_entity)
        res.setResult(tzlist, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSSynchronizeUCStoNTPInputs:
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
        mandatory="1",
        static_values="",
        order=1)
    zone = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Time Zone',
        api="gettimezones()",
        dt_type="string",
        label="Time Zone",
        mandatory="1",
        mapval="0",
        name="zone",
        static="False",
        static_values="",
        svalue="Asia/Kolkata",
        order=2)
    ntp = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='NTP Server',
        api="",
        dt_type="string",
        label="NTP Server",
        mandatory="1",
        mapval="0",
        name="ntp",
        static="False",
        svalue="192.168.10.29",
        static_values="",
        order=3)


class UCSSynchronizeUCStoNTPOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
