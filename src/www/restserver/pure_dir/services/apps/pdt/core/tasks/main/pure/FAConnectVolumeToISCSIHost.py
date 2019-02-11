from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FAConnectVolumeToISCSIHost",
    task_name="Connect Volume To Host",
    task_desc="Mapping volume to host",
    task_type="PURE"
)


class FAConnectVolumeToISCSIHost:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FAConnectVolumeToISCSIHost liek hostname, volumename
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the list of host mapped with respective volume
        :rtype: dict

        """
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
        res.setResult(pure_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def rollback(self, inputs, outputs, logfile):
        """
        :param inputs: task input for FAConnectVolumeToISCSIHost
        :type inputs: dict
        :param outputs: task output for FAConnectVolumeToISCSIHost
        :type outputs: dict
        :param logfile: for printing logs
        :type logfile: function

        """

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

        result_data = obj.disconnect_host(inputs, logfile)
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
        res = self.ucsm_get_associated_sp_cnt(keys)
        blade_list = res.getResult()
        val = ''

        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        mhosts = "{'hostname': {'ismapped': '0', 'value':'"
        mvols = "'volumename': {'ismapped': '0', 'value':'"
        host_prefix = ""
        vol_prefix = ""
        mdata = ""
        for pre in range(1, blade_len + 1):
            host_prefix = 'VM-Host-iSCSI-' + str(pre).zfill(2)
            vol_prefix = 'VM-Vol-iSCSI-' + str(pre).zfill(2)
            mdata += mhosts + host_prefix + "'}, " + mvols + vol_prefix + "'}}|"

        loginfo(
            "host and vol list for connect going is :{}".format(mdata[:-1]))
        job_input_save(jobid, texecid, 'hvmap_set', mdata[:-1])

        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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

        if fabricid is None:
            res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
        res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
            res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
        res.setResult(servers_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getHostApi(self, keys):
        res = result()
        res = self.ucsm_get_associated_sp_cnt(keys)
        blade_list = res.getResult()
        blade_len = 0
        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        mdata = []
        for pre in range(1, blade_len + 1):
            host = 'VM-Host-iSCSI-' + str(pre).zfill(2)
            mdata.append(
                {"id": str(host), "selected": "0", "label": str(host)})

        res.setResult(mdata, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getVolumeApi(self, keys):
        res = result()
        res = self.ucsm_get_associated_sp_cnt(keys)
        blade_list = res.getResult()
        blade_len = 0
        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        mdata = []
        for pre in range(1, blade_len + 1):
            host = 'VM-Vol-iSCSI-' + str(pre).zfill(2)
            mdata.append(
                {"id": str(host), "selected": "0", "label": str(host)})

        res.setResult(mdata, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res


class FAConnectVolumeToISCSIHostInputs:
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
        order=2)

    hostname = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Host Name',
        dt_type="string",
        static="False",
        api="getHostApi()|[fabric_id:1:fabric_id.value]",
        name="hostname",
        label="Host Name",
        svalue="",
        mandatory="0",
        group_member="1",
        static_values="",
        mapval="",
        order=3)

    volumename = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Volume Name',
        dt_type="string",
        static="False",
        api="getVolumeApi()|[fabric_id:1:fabric_id.value]",
        name="volumename",
        label="Volume Name",
        svalue="",
        mandatory="0",
        static_values="",
        group_member="1",
        mapval="",
        order=4)

    hvmap_set = Group(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Connecting Volume to Host',
        dt_type="string",
        static="False",
        api="",
        name="hvmap_set",
        label="Connect volume to host",
        svalue="",
        mapval="0",
        static_values="",
        mandatory="0",
        members=[
            "hostname",
            "volumename"],
        add="True",
        order=5)


class FAConnectVolumeToISCSIHostOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
