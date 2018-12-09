from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FAConnectVolumeToHostGroup",
    task_name="Connect volume to host group",
    task_desc="Connect volume to host group",
    task_type="PURE"
)


class FAConnectVolumeToHostGroup:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FAConnectVolumeToHostGroup like volname, hgname
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the public volume connected with hostgroup
        :rtype: dict

        """
        loginfo("pure connect hostgroup with inputs :{} ".format(inputs))
        cred = get_device_credentials(
            key="mac", value=inputs['inputs']['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.connect_host_group(inputs['inputs'], logfile)
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
        :param inputs: task input for FAConnectVolumeToHostGroup
        :type inputs: dict
        :param outputs: task output for FAConnectVolumeToHostGroup
        :type outputs: dict
        :param logfile: for printing logs
        :type logfile: function

        """

        loginfo("pure connect hostgroup with inputs :{} ".format(inputs))
        cred = get_device_credentials(
            key="mac", value=inputs['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.disconnect_host_group(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)

    def get_volume_list(self, keys):
        loginfo("FlashArray  get volumelist")
        vol_list = []
        res = result()
        data = result()
        pureid = getArg(keys, 'pure_id')
        if pureid == None:
            res.setResult(vol_list, PTK_OKAY, "success")
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

        result_data = obj.get_volume_list()
        if result_data.getStatus() != PTK_OKAY:
            return result_data

        for volDict in result_data.getResult():
            vol_list.append(
                {"id": volDict['name'], "selected": "0", "label": volDict['name']})
        obj.release_pure_handle()
        data.setResult(vol_list, PTK_OKAY, "Success")
        return data



class FAConnectVolumeToHostGroupInputs:
    pure_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", mandatory="0", static_values="", order=1)

    hgname = Textbox(validation_criteria='str|min:1|max:64', hidden='False', isbasic='True', helptext='Host Group Name', dt_type="string", static="False", api="", name="hgname", label="Host Group Name",
                     svalue="", static_values="", mandatory="0", mapval="", order=2, recommended="1")

    volumename = Dropdown(hidden='False', isbasic='True', helptext="Shared Volume's Name", dt_type="string", static="False", api="get_volume_list()|[pure_id:1:pure_id.value]", name="volumename", label="Volume Name",
                         svalue="", static_values="", mandatory="0", mapval="", order=3, recommended="1")


class FAConnectVolumeToHostGroupOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
