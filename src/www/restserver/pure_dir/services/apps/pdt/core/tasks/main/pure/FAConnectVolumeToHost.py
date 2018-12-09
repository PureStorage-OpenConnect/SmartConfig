from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FAConnectVolumeToHost",
    task_name="Connect Volume To Host",
    task_desc="Mapping volume to host",
    task_type="PURE"
)


class FAConnectVolumeToHost:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FACreateMultipleHosts
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the list of hosts created
        :rtype: dict

        """
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

        result_data = obj.connect_host(inputs['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)

    def purelist(self, keys):
        """
        :param keys: task input describing array type e.g. PURE
        :type keys: dict
        :returns: list of FlashArrays

        """
        res = result()
        pure_list = get_device_list(device_type="PURE")
        res.setResult(pure_list, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("connect host with volume rollback")
        return 0

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type logfile: str
        :param inputs: input from global variables
        :type logfile: dict

        """
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsmbladeservers(keys)
        blade_list = res.getResult()
        val = ''

        if len(blade_list) > 0:
            blade_len = len(blade_list)
        mhosts = "{'hostname': {'ismapped': '0', 'value':'"
        mvols = "'volumename': {'ismapped': '0', 'value':'"
        host_prefix = ""
        vol_prefix = ""
        mdata = ""
        for pre in range(1, blade_len + 1):
            host_prefix = 'VM-Host-FC-' + str(pre).zfill(2)
            vol_prefix = 'VM-Vol-FC-' + str(pre).zfill(2)
            mdata += mhosts + host_prefix + "'}, "+mvols+vol_prefix+"'}}|"

        job_input_save(jobid, texecid, 'hvmap_set', mdata[:-1])

        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, "success")
        return res

    def ucsmbladeservers(self, keys):
        """
        :param keys: key for fabric id value
        :type taskinfo: str
        :returns: list of blade servers
        :rtype: list

        """
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


class FAConnectVolumeToHostInputs:
    pure_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", static_values="", mandatory="0", order=1)

    hostname = Dropdown(hidden='False', isbasic='True', helptext='Host Name', dt_type="string", static="False", api="", name="hostname", label="Host Name",
                        svalue="", mandatory="0", group_member="1", static_values="", mapval="", order=2)

    volumename = Dropdown(hidden='False', isbasic='True', helptext='Volume Name', dt_type="string", static="False", api="", name="volumename", label="Volume Name",
                          svalue="", mandatory="0", static_values="", group_member="1", mapval="", order=3)

    hvmap_set = Group(validation_criteria='', hidden='False', isbasic='True', helptext='Connecting Volume to Host', dt_type="string", static="False", api="", name="hvmap_set", label="Connect volume to host", svalue="", mapval="0", static_values="",
                      mandatory="0", members=["hostname", "volumename"], add="True", order=4)


class FAConnectVolumeToHostOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
