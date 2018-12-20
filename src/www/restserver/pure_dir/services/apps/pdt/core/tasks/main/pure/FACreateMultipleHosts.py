from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FACreateMultipleHosts",
    task_name="Create Multiple Hosts",
    task_desc="Creates multiple hosts",
    task_type="PURE"
)


class FACreateMultipleHosts:

    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        """
         :param taskinfo: task input for FACreateMultipleHosts
         :type taskinfo: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing the list of hosts created.
         :rtype: dict

         """

        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['pure_id'])
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result = obj.create_multiple_hosts(taskinfo['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

    def rollback(self, inputs, outputs, logfile):
        """
         :param inputs: task input for FACreateMultipleHosts
         :type inputs: dict
         :param outputs: task output for FACreateMultipleHosts
         :type outputs: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing the list of hosts deleted.
         :rtype: dict

         """

        loginfo("pure host delete, input is : {} ".format(inputs))
        cred = get_device_credentials(
            key="mac", value=inputs['pure_id'])
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result = obj.delete_multiple_hosts(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

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
        :type texecid: str
        :param inputs: input from global variables
        :type inputs: dict

        """
        loginfo("comes into vol prepare function")
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsm_get_associated_sp_cnt(
            keys)  # self.ucsmbladeservers(keys)
        blade_list = res.getResult()
        val = ''

        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        loginfo("vol count going is : {} ".format(str(blade_len)))
        job_input_save(jobid, texecid, 'count', str(blade_len))

        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, "success")
        return res

    def ucsm_get_associated_sp_cnt(self, keys):
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
        service_profiles = handle.query_classid("lsServer")
        sp_cnt = []
        for sp in service_profiles:
            if sp.type != "updating-template" and sp.pn_dn != '':
                sp_cnt.append(sp.name)

        server_dict = {
            'id': str(len(sp_cnt)),
            "selected": "1",
            "label": str(len(sp_cnt))}
        servers_list.append(server_dict)
        print "server list from ucs", servers_list
        ucsm_logout(handle)
        res.setResult(servers_list, PTK_OKAY, "success")
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


class FACreateMultipleHostsInputs:
    pure_id = Dropdown(hidden='True', isbasic='True', helptext='Name of FlashArray', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", static_values="", mandatory="0", order=1)

    name = Textbox(validation_criteria='str|min:1|max:64', hidden='False', isbasic='True', helptext='Host Name Prefix', dt_type="string", static="False", api="", name="name", label="Name",
                   svalue="", mandatory="0", static_values="", mapval="", order=2, recommended="1")
    st_no = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext="Host Name's starting number", dt_type="string", static="False", api="", name="st_no", label="Start number",
                    svalue="1", mandatory="0", static_values="", mapval="", order=3, recommended="1")
    count = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext='Number of Hosts', dt_type="string", static="False", api="", name="count", label="Count",
                    svalue="2", mandatory="0", static_values="", mapval="", order=4)
    num_digits = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext='Number of digits appending for Host Name', dt_type="string",
                         static="False", api="", name="num_digits", label="Number of Digits", svalue="2", mandatory="0", static_values="", mapval="", order=5, recommended="1")


class FACreateMultipleHostsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
