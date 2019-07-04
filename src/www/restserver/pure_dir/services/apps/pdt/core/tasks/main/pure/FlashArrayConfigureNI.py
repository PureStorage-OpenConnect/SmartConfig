from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list, get_device_model
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import get_ucs_login, ucsm_logout

metadata = dict(
    task_id="FlashArrayConfigureNI",
    task_name="Configuring FlashArray NI",
    task_desc="Configuring FlashArray Network Interface",
    task_type="PURE"
)

# TODO: This class needs to be updated to allow configuring multiple nics


class FlashArrayConfigureNI:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FlashArrayConfigureNI
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the list of iscsi network configured
        :rtype: dict

        """

        cred = get_device_credentials(
            key="mac", value=inputs['inputs']['pure_id'])

        if not cred:
            res = result()
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FA_LOGIN_FAILURE"))
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result = obj.set_iscsi_network_interface(inputs['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

    def get_iscsi_interfaces(self, pureid):
        """
        :param pureid: id of FlashArray
        :type pureid: str
        :returns: list of ethernet interfaces

        """

        loginfo("comes into get_iscsi_interfaces with pureid :{}".format(pureid))
        interface_list = []
        res = result()
        if pureid is None:
            res.setResult(interface_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        cred = get_device_credentials(
            key="mac", value=pureid)
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FA_LOGIN_FAILURE"))
            return res

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])
        result_data = obj.get_iscsi_network_interfaces(None, None)
        for interface in result_data.getResult():
            interface_list.append({"id": str(interface['name']).upper(
            ), "selected": "0", "label": str(interface['name']).upper()})
        obj.release_pure_handle()
        loginfo("get iscsi interface list going is :{}".format(interface_list))
        return interface_list

    def get_fa_iscsi_intf(self, pureid, fabric_id):
        """
        :param pureid: id of FlashArray
        :type pureid: str
        :returns: list of ethernet interfaces

        """

        loginfo("comes into get_fa_iscsi_intf with pureid :{}".format(pureid))
        interface_list = []
        res = result()
        if pureid is None:
            res.setResult(interface_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        cred = get_device_credentials(
            key="mac", value=pureid)
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FA_LOGIN_FAILURE"))
            return res
        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])
        fi_model = get_device_model(key="mac", value=fabric_id)
        intf_list = obj.get_fa_ports(fi_model)
        new_intf_list = []
        for intf in intf_list:
            new_intf_list.append('CT0.' + intf)
            new_intf_list.append('CT1.' + intf)
        obj.release_pure_handle()
        loginfo("get iscsi interface list going is :{}".format(new_intf_list))
        return new_intf_list

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

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type logfile: str
        :param inputs: input from global variables
        :type logfile: dict

        """
        loginfo("enters into iscsi interface prepare function")
        res = result()
        pure_id = getGlobalArg(inputs, 'pure_id')
        fabric_id = getGlobalArg(inputs, 'ucs_switch_a')
        interfaces = self.get_fa_iscsi_intf(pure_id, fabric_id)
        loginfo("interfaces in prepare :{}".format(interfaces))
        if texecid == 't300':
            job_input_save(jobid, texecid, 'name', interfaces[0])
        elif texecid == 't301':
            job_input_save(jobid, texecid, 'name', interfaces[1])
        elif texecid == 't302':
            job_input_save(jobid, texecid, 'name', interfaces[2])
        elif texecid == 't303':
            job_input_save(jobid, texecid, 'name', interfaces[3])

        loginfo("final mdata in network interface going is :{}".format(interfaces))
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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

    def rollback(self, inputs, outputs, logfile):
        """
        :param inputs: task input for FlashArrayConfigureNI
        :type inputs: dict
        :param outputs: task output for FlashArrayConfigureNI
        :type outputs: dict
        :param logfile: for printing logs
        :type logfile: function

        """

        loginfo("pure host delete, input is : {} ".format(inputs))
        cred = get_device_credentials(
            key="mac", value=inputs['pure_id'])
        if not cred:
            res = result()
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FA_LOGIN_FAILURE"))

            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result = obj.remove_iscsi_network_interface(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

    def get_iscsi_intf_list(self, keys):
        res = result()
        pureid = getArg(keys, 'pure_id')
        if pureid is None:
            res.setResult([], PTK_OKAY, "success")
            return res
        res.setResult(self.get_iscsi_interfaces(pureid), PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class FlashArrayConfigureNIInputs:
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
        mandatory="0",
        static_values="",
        order=1)
    # name = Textbox(validation_criteria='', hidden='False', isbasic='True', helptext='', dt_type="string", static="False", api="", name="name", label="Name",
    #               svalue="", static_values="", mandatory="0", mapval="", order=2, recommended="1")
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

    name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='iSCSI interface name',
        dt_type="string",
        static="False",
        api="get_iscsi_intf_list()|[pure_id:1:pure_id.value]",
        name="name",
        label="Name",
        svalue="",
        static_values="",
        mandatory="0",
        mapval="",
        order=2,
        recommended="1")
    enabled = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='Enable or Disable Interface',
        dt_type="boolean",
        static="True",
        api="",
        name="enabled",
        label="Enabled",
        svalue="True",
        static_values="True@False:1:enabled",
        mandatory="0",
        mapval="",
        order=3,
        allow_multiple_values="0",
        recommended="1")
    address = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='IP Address',
        dt_type="string",
        static="False",
        api="",
        name="address",
        label="Address",
        svalue="",
        static_values="",
        mandatory="0",
        mapval="",
        order=4)
    netmask = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Netmask',
        dt_type="string",
        static="False",
        api="",
        name="netmask",
        label="Netmask",
        svalue="",
        static_values="",
        mandatory="0",
        mapval="",
        order=5)
    mtu = Textbox(
        validation_criteria='int|min:1|max:9000',
        hidden='False',
        isbasic='True',
        helptext='MTU',
        dt_type="integer",
        static="False",
        api="",
        name="mtu",
        label="MTU",
        svalue="9000",
        static_values="",
        mandatory="0",
        mapval="",
        order=8,
        recommended="1")


class FlashArrayConfigureNIOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
