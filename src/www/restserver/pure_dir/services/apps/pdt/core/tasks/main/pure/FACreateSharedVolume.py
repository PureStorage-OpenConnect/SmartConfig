from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *

metadata = dict(
    task_id="FACreateSharedVolume",
    task_name="Create shared volume",
    task_desc="Creating shared volume for host group",
    task_type="PURE"
)


class FACreateSharedVolume:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
        :param inputs: task input for FACreateSharedVolume, volname, volsize
        :type inputs: dict
        :param logfile: for printing logs
        :type logfile: function
        :returns: A dictionary describing the public volume created
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

        result_data = obj.create_shared_volume(inputs['inputs'], logfile)
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

    def volumesize_unit(self, keys):
        res = result()
        K = 2**10  # 1024
        M = 2**20  # 1048576
        G = 2**30  # 1073741824
        T = 2**40  # 1099511627776
        P = 2**50  # 1125899906842624
        val = [{"id": str(K), "selected": "0", "label": "K"},
               {"id": str(M), "selected": "0", "label": "M"},
               {"id": str(G), "selected": "0", "label": "G"},
               {"id": str(T), "selected": "1", "label": "T"},
               {"id": str(P), "selected": "0", "label": "P"}
               ]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def rollback(self, inputs, outputs, logfile):
        """
        :param inputs: task input for FACreateSharedVolume
        :type inputs: dict
        :param outputs: task output for FACreateSharedVolume
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

        result_data = obj.delete_shared_volume(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)


class FACreateSharedVolumeInputs:
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
    name = Textbox(
        validation_criteria='str|min:1|max:64',
        hidden='False',
        isbasic='True',
        helptext="Shared Volume's Name",
        dt_type="string",
        static="False",
        api="",
        name="name",
        label="Name",
        svalue="",
        static_values="",
        mandatory="0",
        mapval="",
        order=2,
        recommended="1")
    size = Textbox(
        validation_criteria='int',
        hidden='False',
        isbasic='True',
        helptext="Shared Volume's Size",
        dt_type="integer",
        static="False",
        api="",
        name="size",
        label="Size",
        svalue="1",
        group_member="1",
        static_values="",
        mandatory="0",
        mapval="",
        order=3,
        recommended="1")
    size_unit = Dropdown(
        hidden='False',
        isbasic='True',
        helptext="Shared Volume's Size Unit",
        dt_type="string",
        static="False",
        api="volumesize_unit()",
        name="size_unit",
        label="Size Unit",
        svalue="",
        group_member="1",
        static_values="",
        mapval="",
        mandatory="0",
        order=3,
        recommended="1")
    vol_set = Group(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext="Shared Volume's Provisioning Size",
        dt_type="string",
        static="False",
        api="",
        name="vol_set",
        label="Provisioned size",
        svalue="",
        mapval="",
        mandatory="0",
        members=[
            "size",
            "size_unit"],
        add="False",
        static_values="",
        order=4,
        recommended="1")


class FACreateSharedVolumeOutputs:
    name = Output(dt_type="string", name="name", tvalue="SUCCESS")
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
