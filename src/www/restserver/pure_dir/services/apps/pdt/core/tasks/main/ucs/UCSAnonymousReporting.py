from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
import time

metadata = dict(
    task_id="UCSAnonymousReporting",
    task_name="Configure Anonymous reporting",
    task_desc="Configure Anonymous reporting in UCS",
    task_type="UCSM"
)


class UCSAnonymousReporting:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("UCS Anonymous reporting")
	stacktype = get_xml_element(
            "/mnt/system/pure_dir/pdt/settings.xml", "stacktype")[1][0]['stacktype']
	if "ucsmini" in stacktype:
	    time.sleep(300)
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        res = obj.ucsAnonymousReporting(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Anonymous reporting rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSAnonymousReportingInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static_values="",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)
    admin = Radiobutton(
        hidden='False',
        isbasic='False',
        helptext='Enable or disable anonymous reporting',
        api="",
        dt_type="string",
        label="Anonymous Reporting",
        mapval="0",
        name="admin",
        static="True",
        static_values="on:1:Yes|off:0:No",
        svalue="on",
        mandatory='1',
        order=2)
    host = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='SMTP Host',
        api="",
        dt_type="string",
        label="SMTP Server Host",
        mandatory="1",
        static_values="",
        mapval="0",
        name="host",
        static="False",
        svalue="192.168.10.80",
        order=3)
    port = Textbox(
        validation_criteria='int|min:1|max:65535',
        hidden='False',
        isbasic='True',
        helptext='SMTP Server Port',
        api="",
        dt_type="string",
        label="SMTP Server Port",
        mandatory='1',
        mapval="0",
        static_values="",
        name="port",
        static="False",
        svalue="25",
        order=4)


class UCSAnonymousReportingOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
