from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg, getGlobalArg, job_input_save
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateServiceProfilesFromTemplate",
    task_name="Create Service Profiles from template",
    task_desc="Create Service Profiles from Template in UCS",
    task_type="UCSM"
)


class UCSCreateServiceProfilesFromTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_service_profile_from_template")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        loginfo("------------")

        res = obj.ucsCreateServiceProfilesFromTemplate(
            taskinfo['inputs'], fp)
        loginfo("-----------")
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS service profile from template rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteServiceProfilesFromTemplate(
            inputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        print ucs_list, res
        return res

    def gettemplate(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        s = handle.query_classid("lsServer")
        selected = "1"
        for w in s:
            if w.type == 'initial-template':
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": w.name, "selected": selected, "label": w.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def prepare(self, jobid, texecid, inputs):
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsmservers(keys)
        device_list = res.getResult()
        val = ''

        if len(device_list) > 0:
            val = str(len(device_list))

        job_input_save(jobid, texecid, 'instances', val)
        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsmservers(self, keys):
        servers_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid is None:
            res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()
        blades = handle.query_classid("ComputeBlade")
        server_cnt = 1
        for blade in blades:
            server_dict = {
                'id': str(server_cnt),
                "selected": "1",
                "label": str(server_cnt)}
            server_cnt += 1
            servers_list.append(server_dict)
	
	#TODO Can do a proper switch based on server type
	rack_servers = handle.query_classid("ComputeRackUnit")
        for rack_server in rack_servers:
            server_dict = {
                'id': str(server_cnt),
                "selected": "1",
                "label": str(server_cnt)}
            server_cnt += 1
            servers_list.append(server_dict)

        ucsm_logout(handle)
        res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateServiceProfilesFromTemplateInputs:
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
    profile_prefix = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="None",
        static="False",
        static_values="",
        label="Service Profile Prefix",
        name="profile_prefix",
        svalue="VM-Host-Infra-0",
        mandatory='1',
        mapval="",
        order=2,
        recommended="1")
    suffix_starting_number = Textbox(
        validation_criteria='int|min:1|max:1000',
        hidden='False',
        isbasic='True',
        helptext='Service Profile name suffix',
        dt_type="string",
        api="None",
        static="False",
        static_values="",
        name="suffix_starting_number",
        label="Name Suffix Starting Number",
        svalue="1",
        mandatory='1',
        mapval="",
        order=3)
    instances = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Number of service profile instances',
        dt_type="string",
        static="False",
        api="ucsmservers()|[fabric_id:1:fabric_id.value]",
        static_values="",
        name="instances",
        label="Number of Instances",
        svalue="2",
        mandatory='1',
        mapval="",
        order=4)
    template_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Template name',
        dt_type="list",
        static="False",
        api="gettemplate()|[fabric_id:1:fabric_id.value]",
        static_values="",
        name="template_name",
        label="Template Name",
        mapval="1",
        svalue="__t201.UCSCreateServiceProfileTemplate.serviceprofilename",
        mandatory='1',
        order=5)


class UCSCreateServiceProfilesFromTemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
