from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list, get_device_model
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="FAGetISCSIPortNumber",
    task_name="Get port number in pure Array",
    task_desc="Get port number for the pure array controller",
    task_type="PURE"
)


class FAGetISCSIPortNumber:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for PureGetPortNumber like controller name
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the list of hosts created
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

        result = obj.get_port_number(inputs['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result)

    def rollback(self, inputs, outputs, logfile):
        loginfo("get pwwn rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
        job_input_save(jobid, texecid, 'name', interfaces[0])
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def purelist(self, keys):
        """
        :param keys: task input describing array type e.g. PURE
        :type keys: dict
        :returns: list of FlashArrays

        """
        res = result()
        pure_list = get_device_list(device_type="PURE")
        loginfo("pure_list : {}".format(pure_list))
        res.setResult(pure_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

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
        return new_intf_list

    def get_iscsi_controller_list(self, keys):
        """
        :param keys: id of FlashArray
        :type keys: str
        :returns: list of controllers

        """

        # self.get_hgroup_list(keys)
        res = result()
        cont_list = []
        res = result()
        pureid = getArg(keys, 'pure_id')
        if pureid is None:
            res.setResult(cont_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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

        result_data = obj.get_iscsi_port_list()
        for contDict in result_data.getResult():
            cont_list.append(
                {"id": contDict['name'], "selected": "0", "label": contDict['name']})
        obj.release_pure_handle()
        loginfo("get controller list going is :{}".format(cont_list))
        res.setResult(cont_list, PTK_OKAY, "Success")
        return res


class FAGetISCSIPortNumberInputs:
    pure_id = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Pure ID',
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
    name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='iSCSI interface Name',
        dt_type="list",
        api="get_iscsi_controller_list()|[pure_id:1:pure_id.value]",
        static="False",
        name="name",
        label="iSCSI Interface name",
        svalue="",
        mandatory="0",
        static_values="",
        mapval="0",
        order=2,
        recommended="1")


class FAGetISCSIPortNumberOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    pwwn = Output(dt_type="string", name="pwwn", tvalue="no-op")
