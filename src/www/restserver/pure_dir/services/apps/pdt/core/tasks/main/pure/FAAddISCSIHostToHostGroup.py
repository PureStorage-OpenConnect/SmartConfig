from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FAAddISCSIHostToHostGroup",
    task_name="Add host to host group",
    task_desc="adding host to host group",
    task_type="PURE"
)


class FAAddISCSIHostToHostGroup:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FAAddISCSIHostToHostGroup like hostgroup name, hosts
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the list of hostgroups with connected respective hosts
        :rtype: dict

        """
        cred = get_device_credentials(
            key="mac", value=inputs['inputs']['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.add_host_to_hostgroup(inputs['inputs'], logfile)
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
        """
        :param inputs: task input for FAAddISCSIHostToHostGroup like hostgroup
        :type inputs: dict
        :param outputs: task output for FAAddISCSIHostToHostGroup like hostgroup
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
                          "Unable to get the device credentials of the MDS")

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.remove_host_from_hostgroup(inputs, logfile)
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
        host_prefix = ""
        for pre in range(1, blade_len + 1):
            host_prefix += "VM-Host-iSCSI-" + str(pre).zfill(2) + "|"
        loginfo("host list for add host to hg going is : {}".format(
            host_prefix[:-1]))
        job_input_save(jobid, texecid, 'hosts', host_prefix[:-1])

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

        res.setResult(mdata, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def get_hgroup_list(self, keys):
        loginfo("FlashArray get host group list")
        hg_list = []
        pureid = getArg(keys, 'pure_id')
        res = result()
        if pureid == None:
            res.setResult(hg_list, PTK_OKAY, "success")
            return res

        cred = get_device_credentials(
            key="mac", value=pureid)

        if not cred:
            loginfo("Unable to get the device credentials of the Flash Array")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of Flash Array")
            return res

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.list_host_groups()
        for hgDict in result_data.getResult():
            hg_list.append(
                {"id": hgDict['name'], "selected": "0", "label": hgDict['name']})
        obj.release_pure_handle()
        res.setResult(hg_list, PTK_OKAY, "Success")
        return res


class FAAddISCSIHostToHostGroupInputs:

    pure_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", static_values="", mandatory="0", order=1)

    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=2)

    hgname = Dropdown(hidden='False', isbasic='True', helptext='Host Group Name', dt_type="string", static="False", api="get_hgroup_list()|[pure_id:1:pure_id.value]", name="hgname", label="Host Group Name",
                      svalue="VM-HostGroup-iSCSI", mandatory="0", static_values="", mapval="", order=3, recommended="1")

    hosts = Multiselect(hidden='False', isbasic='True', helptext='Host List', dt_type="string", static="False", api="getHostApi()|[fabric_id:1:fabric_id.value]", name="hosts", label="Hosts",
                        svalue="", mandatory="0", static_values="", mapval="", order=4)


class FAAddISCSIHostToHostGroupOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")