from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.components.storage.flashblade.flashblade_tasks import FlashBladeTasks


metadata = dict(
    task_id="FBCreateSubnet",
    task_name="Create Subnet",
    task_desc="Creates Subnet",
    task_type="FlashBlade"
)


class FBCreateSubnet:

    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        """
         :param taskinfo: task input for FBCreateSubnet
         :type taskinfo: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing the Subnet created.
         :rtype: dict

        """
        loginfo("Creating Subnet for FlashBlade...")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['fb_id'])
        if not cred:
            res = result()
            loginfo("Unable to get the device credentials of the FlashBlade")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FB_LOGIN_FAILURE"))

            return parseTaskResult(res)

        obj = FlashBladeTasks(cred['ipaddress'],
                              cred['username'], cred['password'])
        if obj:
            result = obj.create_subnet(taskinfo['inputs'], logfile)
            return parseTaskResult(result)

        res.setResult(False, PTK_INTERNALERROR, _("PDT_FB_LOGIN_FAILURE"))
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        """
         :param inputs: task input for FBCreateSubnet
         :type inputs: dict
         :param logfile: for printing logs
         :type logfile: function

         """

        loginfo("Rollback - Create Subnet for FlashBlade with the inputs: {} ".format(inputs))
        cred = get_device_credentials(
            key="mac", value=inputs['fb_id'])
        if not cred:
            res = result()
            loginfo("Unable to get the device credentials of the FlashBlade")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_FB_LOGIN_FAILURE"))

            return parseTaskResult(res)

        obj = FlashBladeTasks(cred['ipaddress'],
                              cred['username'], cred['password'])

        if obj:
            result = obj.delete_subnet(inputs, logfile)
            return parseTaskResult(result)

        res.setResult(False, PTK_INTERNALERROR, _("PDT_FB_LOGIN_FAILURE"))
        return parseTaskResult(res)

    def fblist(self, keys):
        """
        :param keys: task input describing flashblade type e.g. PURE
        :type keys: dict
        :returns: list of FlashBlades

        """
        res = result()
        fb_list = get_device_list(device_type="FlashBlade")
        res.setResult(fb_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class FBCreateSubnetInputs:
    fb_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='Name of FlashBlade',
        dt_type="string",
        static="False",
        api="fblist()",
        name="fb_id",
        label="FlashBlade",
        svalue="",
        mapval="",
        static_values="",
        mandatory="0",
        order=1)
    name = Textbox(
        validation_criteria='str|min:1|max:64',
        hidden='False',
        isbasic='True',
        helptext='Subnet Name',
        dt_type="string",
        static="False",
        api="",
        name="name",
        label="Name",
        svalue="",
        static_values="",
        mandatory="1",
        mapval="",
        order=2,
        recommended="1")
    prefix = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Subnet Prefix',
        dt_type="string",
        static="False",
        api="",
        name="prefix",
        label="Prefix",
        svalue="",
        static_values="",
        mandatory="1",
        mapval="",
        order=3,
        recommended="1")
    vlan = Textbox(
        validation_criteria='int|min:1|max:4094',
        hidden='False',
        isbasic='True',
        helptext='Subnet VLAN ID',
        dt_type="string",
        static="False",
        api="",
        name="vlan",
        label="VLAN",
        svalue="0",
        static_values="",
        mandatory="0",
        mapval="",
        order=4,
        recommended="1")
    gateway = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Subnet Gateway Address',
        dt_type="string",
        static="False",
        api="",
        name="gateway",
        label="Gateway",
        svalue="",
        static_values="",
        mandatory="1",
        mapval="",
        order=5,
        recommended="1")
    mtu = Textbox(
        validation_criteria='int|min:1280|max:9216',
        hidden='False',
        isbasic='True',
        helptext='Subnet MTU',
        dt_type="string",
        static="False",
        api="",
        name="mtu",
        label="MTU",
        svalue="9000",
        static_values="",
        mandatory="0",
        mapval="",
        order=6,
        recommended="1")


class FBCreateSubnetOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="prefix", tvalue="192.168.52.0/24")
