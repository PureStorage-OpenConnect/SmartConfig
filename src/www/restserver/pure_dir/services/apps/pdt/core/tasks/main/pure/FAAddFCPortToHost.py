from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *

metadata = dict(
    task_id="FAAddFCPortToHost",
    task_name="Add ports to host",
    task_desc="Adds ports to host",
    task_type="PURE"
)


class FAAddFCPortToHost:

    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        """
         :param taskinfo: task input for FAAddFCPortToHost
         :type taskinfo: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing mapped FC ports to hosts.
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

        result = obj.add_port_to_host(taskinfo['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

    def rollback(self, inputs, outputs, logfile):
        """
         :param inputs: task input for FAAddFCPortToHost
         :type inputs: dict
         :param outputs: task output for FAAddFCPortToHost
         :type outputs: dict
         :param logfile: for printing logs
         :type logfile: function

         """

        cred = get_device_credentials(
            key="mac", value=inputs['pure_id'])
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result = obj.remove_port_from_host(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

    def get_ports(self, pureid, blade_cnt):
        """Lists the FC ports for mapping

            :param pureid: id of flash array
            :type pureid: str

            :returns: FC ports
            :rtype: list

            """

        loginfo("comes into get_ports with keys : {}".format(pureid))
        port_list = []
        wwn_list = []
        res = result()
        if pureid == None:
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
        result_data = obj.get_ports(blade_cnt, fc_ports=True)
        for portDict in result_data.getResult():
            if portDict['target'] is not None:
                wwn_list.append(portDict['wwn'])
            else:
                loginfo("target in get_ports is null")
        new_list = list(set(wwn_list))
        for unique_wwn in new_list:
            # port_list.append(
                # {"id": str(unique_wwn), "selected": "0", "label": str(unique_wwn)})
            port_list.append(str(unique_wwn))
        obj.release_pure_handle()
        loginfo("get port list going is : {}".format(port_list))
        res.setResult(port_list, PTK_OKAY, "Success")
        return port_list

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
        loginfo("enters into prepare function")
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        pure_id = getGlobalArg(inputs, 'pure_id')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsm_get_associated_sp_cnt(
            keys)  # self.ucsmbladeservers(keys)
        blade_list = res.getResult()
        val = ''
        blade_len = 0
        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        host_prefix = ""
        mports = self.get_ports(pure_id, blade_len)
        loginfo("orig ports in prepare : {}".format(mports))
        mports.sort()
        loginfo("ports after sorting".format(mports))
        final_list = []
        for pp in mports:
            for i in range(0, len(mports)):
                if pp[-2:] == mports[i][-2:] and pp[-3:] != mports[i][-3:]:
                    loginfo("final_list before adding : {}".format(final_list))
                    if pp in final_list:
                        pass
                    else:
                        final_list.append(pp)
                        final_list.append(mports[i])
        ports = final_list
        loginfo("final ports in prepare is : {}".format(ports))
        mdata = ""
        k = 0
        port_list = []
        mhosts = "{'hosts': {'ismapped': '0', 'value':'"
        mports = "'ports': {'ismapped': '0', 'value':'"
        for pre in range(1, blade_len + 1):
            host_prefix = "VM-Host-FC-" + str(pre).zfill(2)
            port_list = []
            if k < len(ports) - 1:
                port_list.append(ports[k])
                k = k + 1
                port_list.append(ports[k])
                k = k + 1
            mdata += mhosts + host_prefix + "'}," + mports + \
                str(port_list[0] + "," + port_list[1]) + "'}}|"
        loginfo("mdata going is : {}".format(mdata[:-1]))
        job_input_save(jobid, texecid, 'host_set', mdata[:-1])
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

        '''jobid = str([arg['value'] for args in keys.values() for arg in args if arg['key'] == "jobid"][0])
        if jobid == "":
            res.setResult([], PTK_OKAY, "success")
            return res

        hostname = get_field_value_from_jobid(jobid, 'FACreateMultipleHosts', 'name')'''

        blade_len = 0
        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        mdata = []
        for pre in range(1, blade_len + 1):
            host = 'VM-Host-FC-' + str(pre).zfill(2)
            mdata.append(
                {"id": str(host), "selected": "0", "label": str(host)})

        res.setResult(mdata, PTK_OKAY, "success")
        return res

    def getPortApi(self, keys):
        res = result()
        pure_id = getArg(keys, 'pure_id')
        res = self.ucsm_get_associated_sp_cnt(
            keys)  # self.ucsmbladeservers(keys)
        blade_list = res.getResult()

        blade_len = 0
        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        host_prefix = ""
        mports = self.get_ports(pure_id, blade_len)
        loginfo("orig ports in prepare : {}".format(mports))
        mports.sort()
        loginfo("ports after sorting".format(mports))
        final_list = []
        for pp in mports:
            for i in range(0, len(mports)):
                if pp[-2:] == mports[i][-2:] and pp[-3:] != mports[i][-3:]:
                    loginfo("final_list before adding : {}".format(final_list))
                    if pp in final_list:
                        pass
                    else:
                        final_list.append(pp)
                        final_list.append(mports[i])
        ports = final_list
        loginfo("final ports in prepare is : {}".format(ports))
        mdata = []
        k = 0
        port_list = []
        for pre in range(1, blade_len + 1):
            port_list = []
            if k < len(ports) - 1:
                port_list.append(ports[k])
                k = k + 1
                port_list.append(ports[k])
                k = k + 1
            mdata.append({"id": str(port_list[0] + "," + port_list[1]),
                          "selected": "0", "label": str(port_list[0] + "," + port_list[1])})
        print "port list goin in advanced ", mdata
        res.setResult(mdata, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res


class FAAddFCPortToHostInputs:
    pure_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", static_values="", mandatory="0", order=1)

    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=2)

    hosts = Dropdown(hidden='False', isbasic='True', helptext='Host List', dt_type="string", static="False", api="getHostApi()|[fabric_id:1:fabric_id.value]",
                     name="hosts", label="Hosts", svalue="", mandatory="0", static_values="", mapval="", group_member="1", order=3)

    ports = Dropdown(hidden='False', isbasic='True', helptext='Volume List', dt_type="string", static="False", api="getPortApi()|[fabric_id:1:fabric_id.value|pure_id:1:pure_id.value]",
                     name="ports", label="Port List", svalue="", group_member="1", static_values="", mapval="", mandatory="0", order=4)

    host_set = Group(validation_criteria='', hidden='False', isbasic='True', helptext='Adding Port to Host', dt_type="string", static="False", api="",
                     name="host_set", label="Host Port Mapping", svalue="", static_values="", mapval="", mandatory="0", members=["hosts", "ports"], add="True", order=5)


class FAAddFCPortToHostOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")