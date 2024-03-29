from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FACreateHostGroup",
    task_name="Create Host Group",
    task_desc="Creates Host Group",
    task_type="PURE"
)


class FACreateHostGroup:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FACreateHostGroup like hostgroup name
        :type inputs: str
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the name of hostgroup created
        :rtype: dict

        """
        loginfo("pure hostgroup create with inputs : {}".format(inputs))

        cred = get_device_credentials(
            key="mac", value=inputs['inputs']['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FA_LOGIN_FAILURE"))
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.create_host_group(inputs["inputs"], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type texecid: str
        :param inputs: input from global variables
        :type inputs: dict

        """
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}

        prefix = ""
        blade_len = self.ucsm_get_associated_sp_cnt(keys)
        for i in range(1, blade_len + 1):
            if i < 10:
                prefix += "VM-Host-FC-" + str(i).zfill(2) + "|"
            else:
                prefix += "VM-Host-FC-" + str(i).zfill(3) + "|"

        job_input_save(jobid, texecid, 'name', prefix)
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsm_get_associated_sp_cnt(self, keys):
        """
        :param keys: key for fabric id value
        :type taskinfo: str
        :returns: count of service profiles
        :rtype: list

        """
        fabricid = getArg(keys, 'fabric_id')

        if fabricid is None:
            return 0

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return 0

        handle = res.getResult()
        service_profiles = handle.query_classid("lsServer")
        sp_cnt = []
        for sp in service_profiles:
            if sp.type != "updating-template" and sp.pn_dn != '':
                sp_cnt.append(sp.name)

        ucsm_logout(handle)
        return len(sp_cnt)

    def purelist(self, keys):
        """
        :param keys: task input describing array type e.g. PURE
        :type keys: dict
        :returns: list of FlashArrays

        """
        res = result()
        pure_list = get_device_list(device_type="PURE")
        res.setResult(pure_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def rollback(self, inputs, outputs, logfile):
        """
        :param inputs: task input for FACreateHostGroup
        :type inputs: str
        :param outputs: task output for FACreateHostGroup
        :type outputs: str
        :param logfile: for printing logs
        :type logfile: function

        """

        loginfo("pure hostgroup delete with inputs : {}".format(inputs))

        cred = get_device_credentials(
            key="mac", value=inputs['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FA_LOGIN_FAILURE"))
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.delete_host_group(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)


class FACreateHostGroupInputs:
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

    hgname = Textbox(
        validation_criteria='str|min:1|max:64',
        hidden='False',
        isbasic='True',
        helptext='Host Group Name',
        dt_type="string",
        static="False",
        api="",
        name="hgname",
        label="Host Group Name",
        svalue="",
        mandatory="0",
        mapval="",
        static_values="",
        order=2,
        recommended="1")


class FACreateHostGroupOutputs:
    hgname = Output(dt_type="string", name="hgname", tvalue="SUCCESS")
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
