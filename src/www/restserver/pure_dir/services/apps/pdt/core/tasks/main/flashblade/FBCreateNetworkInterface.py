from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.components.storage.flashblade.flashblade_tasks import FlashBladeTasks


metadata = dict(
    task_id="FBCreateNetworkInterface",
    task_name="Create NetworkInterface",
    task_desc="Creates NetworkInterface",
    task_type="FlashBlade"
)


class FBCreateNetworkInterface:
    
    def __init__(self):
        pass

    
    def execute(self, taskinfo, logfile):
        """
         :param taskinfo: task input for FBCreateNetworkInterface
         :type taskinfo: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing the NetworkInterface created for a subnet.
         :rtype: dict

        """
        loginfo("Creating NetworkInterface for FlashBlade...")
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
            result = obj.create_network_interface(taskinfo['inputs'], logfile)
            return parseTaskResult(result)

        res.setResult(False, PTK_INTERNALERROR, _("PDT_FB_LOGIN_FAILURE"))
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        """
         :param inputs: task input for FBCreateNetworkInterface
         :type inputs: dict
         :param logfile: for printing logs
         :type logfile: function

         """

        loginfo("Rollback - Create NetworkInterface for FlashBlade with the inputs: {} ".format(inputs))
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
            result = obj.delete_network_interface(inputs, logfile)
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



class FBCreateNetworkInterfaceInputs:
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
        helptext='Interface Name',
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
    address= Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Interface Address',
        dt_type="string",
        static="False",
        api="",
        name="address",
        label="Address",
        svalue="",
        static_values="",
        mandatory="1",
        mapval="",
        order=3,
        recommended="1")

class FBCreateNetworkInterfaceOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")

