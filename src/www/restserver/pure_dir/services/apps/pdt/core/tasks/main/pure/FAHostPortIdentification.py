from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *

metadata = dict(
    task_id="FAHostPortIdentification",
    task_name="Identify Host Ports",
    task_desc="Identifying host initiator ports",
    task_type="PURE"
)


class FAHostPortIdentification:

    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        """
        :param taskinfo: task input for FAHostPortIdentification
        :type taskinfo: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the list of hosts created
        :rtype: dict

        """
        loginfo("pure host create, input is : {} ".format(input))

        dicts = {}
        dicts['status'] = "Success"
        res = result()
        res.setResult(dicts, PTK_OKAY, "Success")
        obj.release_pure_handle()
        return parseTaskResult(res)

    def get_ports(self, pureid):
        loginfo("comes into get_ports with pure id : {}".format(pureid))
        port_list = []
        wwn_list = []
        res = result()
        if pureid is None:
            res.setResult(port_list, PTK_OKAY, "success")
            return res

        cred = get_device_credentials(
            key="mac", value=pureid)
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of FlashArray")
            return res

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])
        result_data = obj.get_ports()
        for portDict in result_data.getResult():
            if portDict['target'] is not None:
                wwn_list.append(portDict['wwn'])
            else:
                loginfo("target is null")
        new_list = list(set(wwn_list))
        for unique_wwn in new_list:
            port_list.append(str(unique_wwn))
        obj.release_pure_handle()
        res.setResult(port_list, PTK_OKAY, "Success")
        return port_list

    def rollback(self, inputs, outputs, logfile):
        loginfo("host create rollback")
        return 0

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

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type logfile: str
        :param inputs: input from global variables
        :type logfile: dict

        """
        loginfo("enters into prepare function")
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        iqn_prefix = getGlobalArg(inputs, 'IQN-Prefix')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsmbladeservers(keys)
        blade_list = res.getResult()
        val = ''
        blade_len = 0
        if len(blade_list) > 0:
            blade_len = len(blade_list)

        for pre in range(1, blade_len + 1):
            mport += str(iqn_prefix) + ":ucs-host:" + str(pre) + "|"
        loginfo("port list in host port identification is ".format(mport))
        job_input_save(jobid, texecid, 'ports', mport[:-1])
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
        if fabricid is None:
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

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type logfile: str
        :param inputs: input from global variables
        :type logfile: dict

        """
        loginfo("enters into prepare function")
        res = result()
        pure_id = getGlobalArg(inputs, 'pure_id')
        ports = sorted(self.get_ports(pure_id))
        port_list = '|'.join(x for x in ll)
        loginfo("port list in host port identification is ".format(port_list))
        job_input_save(jobid, texecid, 'ports', port_list)
        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, "success")
        return res


class FAHostPortIdentificationInputs:
    pure_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="purelist()",
        name="pure_id",
        label="FlashArray",
        svalue="",
        mapval="",
        static_values="",
        mandatory="0",
        order=1)

    iqn_pool_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="",
        name="iqn_pool_name",
        label="IQN Pool Name",
        svalue="IQN-Pool",
        mandatory="0",
        static_values="",
        mapval="",
        order=2,
        recommended="1")

    ports = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="",
        name="ports",
        label="Initiator Name",
        svalue="",
        static_values="",
        mapval="",
        mandatory="0",
        order=3)


class FAHostPortIdentificationOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
