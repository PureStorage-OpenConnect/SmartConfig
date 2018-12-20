from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FAAddHostToHostGroup",
    task_name="Add host to host group",
    task_desc="adding host to host group",
    task_type="PURE"
)


class FAAddHostToHostGroup:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        cred = get_device_credentials(
            key="mac", value=inputs['inputs']['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.add_host_to_hostgroup(inputs['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)

    def purelist(self, keys):
        res = result()
        pure_list = get_device_list(device_type="PURE")
        res.setResult(pure_list, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("Add Host to hostgroup rollback")
        return 0

    def prepare(self, jobid, texecid, inputs):
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsmbladeservers(keys)
        blade_list = res.getResult()
        val = ''

        if len(blade_list) > 0:
            blade_len = len(blade_list)
        host_prefix = ""
        for pre in range(1, blade_len + 1):
            host_prefix += "VM-Host-FC-" + str(pre).zfill(2) + "|"
        print "host list for add host to hg going is ", host_prefix[:-1]
        job_input_save(jobid, texecid, 'hosts', host_prefix[:-1])

        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, "success")
        return res

    def ucsmbladeservers(self, keys):
        servers_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            res.setResult(servers_list, PTK_OKAY, "success")
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()
        blades = handle.query_classid("ComputeBlade")
        blade_server_cnt = 1
        for blade in blades:
            server_dict = {
                'id': str(blade_server_cnt),
                "selected": "1",
                "label": str(blade_server_cnt)}
            blade_server_cnt += 1
            servers_list.append(server_dict)
        ucsm_logout(handle)
        res.setResult(servers_list, PTK_OKAY, "success")
        return res


class FAAddHostToHostGroupInputs:

    pure_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", static_values="", mandatory="0", order=1)

    hgname = Textbox(validation_criteria='str|min:1|max:64', hidden='False', isbasic='True', helptext='Host Group Name', dt_type="string", static="False", api="", name="hgname", label="Host Group Name",
                     svalue="VM-HostGroup-FC", mandatory="0", static_values="", mapval="", order=2)

    hosts = Multiselect(hidden='False', isbasic='True', helptext='Host List', dt_type="string", static="False", api="", name="hosts", label="Hosts",
                        svalue="", mandatory="0", static_values="", mapval="", order=3)


class FAAddHostToHostGroupOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
