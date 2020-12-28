from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.common import get_device_list

metadata = dict(
    task_id="ConfigureCiscoUCSCallHome",
    task_name="Configure Cisco UCS Create Home",
    task_desc="Configure Cisco UCS Create Home",
    task_type="UCSM"
)


class ConfigureCiscoUCSCallHome:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Call Home")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.configureCiscoUCSCallHome(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Call Home")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.UnConfigureCiscoUCSCallHome(
            inputs, logfile)
        obj.release_ucs_handle()
        return res
    
    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

class ConfigureCiscoUCSCallHomeInputs:
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
    state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='State',
        dt_type="string",
        static="True",
        api="",
        name="state",
        label="State",
        static_values="on:1:On|off:0:Off",
        svalue="",
        mandatory='1',
        mapval="",
        order=2)
    switch_priority = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="True",
        api="",
        name="switch_priority",
        label="Switch Priority",
        static_values="emergency:0:Emergencies|alert:0:Alerts|info:0:Informations|notice:0:Notificaions|warning:0:Warnings|error:0:Errors|critical:0:Critical|debug:1:Debugging",
        svalue="",
        mapval="",
        mandatory="1",
        order=3)
    throttling = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='State',
        dt_type="string",
        static="True",
        api="",
        name="throttling",
        label="Throttling",
        static_values="on:1:On|off:0:Off",
        svalue="",
        mandatory='1',
        mapval="",
        order=4)
    contact = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Contact Name',
        api="",
        dt_type="string",
        label="Contact",
        mapval="0",
        name="contact",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=5)
    phone = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Contact Number',
        api="",
        dt_type="string",
        label="Phone",
        mapval="0",
        name="phone",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=6)
    email = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Contact Email',
        api="",
        dt_type="string",
        label="Email",
        mapval="0",
        name="email",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=7)
    address = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Address',
        api="",
        dt_type="string",
        label="Address",
        mapval="0",
        name="address",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=8)
    customer_id = Textbox(
        validation_criteria='int|min:1|max:10',
        hidden='False',
        isbasic='True',
        helptext='Customer ID',
        api="",
        dt_type="string",
        label="Customer ID",
        mapval="0",
        name="customer_id",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=9)
    contract_id = Textbox(
        validation_criteria='int|min:1|max:10',
        hidden='False',
        isbasic='True',
        helptext='Contract ID',
        api="",
        dt_type="string",
        label="Contract ID",
        mapval="0",
        name="contract_id",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=10)
    site_id = Textbox(
        validation_criteria='int|min:1|max:10',
        hidden='False',
        isbasic='True',
        helptext='Site ID',
        api="",
        dt_type="string",
        label="Site ID",
        mapval="0",
        name="site_id",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=11)
    email_from = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Email From',
        api="",
        dt_type="string",
        label="From",
        mapval="0",
        name="email_from",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=12)
    reply_to = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Reply To Email ID',
        api="",
        dt_type="string",
        label="Reply To",
        mapval="0",
        name="reply_to",
        static="False",
        svalue="",
        mandatory='1',
        static_values="",
        order=13)


class ConfigureCiscoUCSCallHomeOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
