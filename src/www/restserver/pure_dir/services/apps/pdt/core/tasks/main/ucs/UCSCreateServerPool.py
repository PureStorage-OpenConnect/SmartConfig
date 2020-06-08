from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg, getGlobalArg, job_input_save
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateServerPool",
    task_name="Create UCS Server Pool",
    task_desc="Create server pool in UCS",
    task_type="UCSM"
)


class UCSCreateServerPool:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Server Pool")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateServerPool(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Server Pool rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteServerPool(
            inputs, logfile)
        obj.release_ucs_handle()
        return res

    def prepare(self, jobid, texecid, inputs):
        res = result()
        # TODO for safer side. Please ensure map val set for desired fields
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsmservers(keys)
        device_list = res.getResult()
        val = ''

        for device in device_list:
            val = val + device['id'] + "|"
        if len(device_list) > 0:
            val = val[:-1]

        job_input_save(jobid, texecid, 'servers', val)
        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
        for blade in blades:
            server_dict = {
                'id': blade.dn,
                "selected": "1",
                "label": blade.dn}
            servers_list.append(server_dict)

        racks = handle.query_classid("ComputeRackUnit")
        for rack in racks:
            server_dict = {
                'id': rack.dn,
                "selected": "1",
                "label": rack.dn}
            servers_list.append(server_dict)

        ucsm_logout(handle)
        res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateServerPoolInputs:
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
    name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Server Pool name',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="Infra_Pool",
        mandatory='1',
        static_values="",
        order=2)
    desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="desc",
        static="False",
        svalue="server pool create",
        mandatory='1',
        static_values="",
        order=3)
    servers = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Blade Servers for Creating server pool',
        api="ucsmservers()|[fabric_id:1:fabric_id.value]",
        dt_type="string",
        label="Add Servers",
        mandatory="1",
        mapval="0",
        name="servers",
        static="False",
        svalue="",
        static_values="",
        order=4)


class UCSCreateServerPoolOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
