from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.components.storage.flashblade.flashblade_tasks import FlashBladeTasks


metadata = dict(
    task_id="FBCreateNFS",
    task_name="Create NFS",
    task_desc="Creates NFS",
    task_type="FlashBlade"
)


class FBCreateNFS:
    
    def __init__(self):
        pass

    
    def execute(self, taskinfo, logfile):
        """
         :param taskinfo: task input for FBCreateNFS
         :type taskinfo: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing the NFS created.
         :rtype: dict

        """
        loginfo("Creating NFS for FlashBlade...")
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
            result = obj.create_file_system(taskinfo['inputs'], logfile)
            return parseTaskResult(result)

        res.setResult(False, PTK_INTERNALERROR, _("PDT_FB_LOGIN_FAILURE"))
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        """
         :param inputs: task input for FBCreateNFS
         :type inputs: dict
         :param logfile: for printing logs
         :type logfile: function

         """

        loginfo("Rollback - Create NFS for FlashBlade with the inputs: {} ".format(inputs))
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
            result = obj.delete_file_system(inputs, logfile)
            return parseTaskResult(result)

        res.setResult(False, PTK_INTERNALERROR, _("PDT_FB_LOGIN_FAILURE"))
        return parseTaskResult(res)

    def volumesize_unit(self, keys):
        loginfo("volumesize unit keys is :{}".format(keys))
        res = result()
        K = 2**10  # 1024
        M = 2**20  # 1048576
        G = 2**30  # 1073741824
        T = 2**40  # 1099511627776
        P = 2**50  # 1125899906842624
        val = [{"id": str(K), "selected": "0", "label": "K"},
               {"id": str(M), "selected": "0", "label": "M"},
               {"id": str(G), "selected": "1", "label": "G"},
               {"id": str(T), "selected": "0", "label": "T"},
               {"id": str(P), "selected": "0", "label": "P"}
               ]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


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


class FBCreateNFSInputs:
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
        mapval="0",
        order=2,
        recommended="1")
    provisioned_size = Textbox(
        validation_criteria='int',
        hidden='False',
        isbasic='True',
        helptext="Provisioned size in specified units",
        dt_type="integer",
        static="False",
        api="",
        name="provisioned_size",
        label="Provisioned Size",
        svalue="1",
        group_member="1",
        static_values="",
        mandatory="1",
        mapval="",
        order=3,
        recommended="1")
    provisioned_size_unit = Dropdown(
        hidden='False',
        isbasic='True',
        helptext="Unit of Provisioned Size",
        dt_type="string",
        static="False",
        api="volumesize_unit()",
        name="provisioned_size_unit",
        label="Provisioned Size Unit",
        svalue="",
        group_member="1",
        static_values="",
        mapval="0",
        mandatory="1",
        order=4,
        recommended="1")
    provisioned_set = Group(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='Provisioned Size of the File System in bytes',
        dt_type="string",
        static="False",
        api="",
        name="provisioned_set",
        label="Provisioned Size(Bytes)",
        svalue="",
        mapval="0",
        mandatory="0",
        members=[
            "provisioned_size",
            "provisioned_size_unit"],
        add="False",
        static_values="",
        order=5,
        recommended="1")
    nfs_version = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='NFS Protocol Version',
        dt_type="string",
        static="True",
        static_values="v3_enabled:1:NFSv3|v4_1_enabled:0:NFSv4.1",
        api="",
        name="nfs_version",
        label="NFS Protocol",
        svalue="NFSv3",
        mandatory='1',
        mapval="0",
        order=6)
    snapshot = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='Enable or Disable Snapshots',
        dt_type="boolean",
        static="True",
        api="",
        name="snapshot",
        label="Snapshot",
        svalue="True",
        static_values="True@False:1:Snapshot",
        mandatory="0",
        mapval="0",
        order=7,
        allow_multiple_values="0",
        recommended="1")
    fast_remove = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='Enable or Disable Fast Removal',
        dt_type="boolean",
        static="True",
        api="",
        name="fast_remove",
        label="Fast Remove",
        svalue="True",
        static_values="True@False:1:Fast Removal",
        mandatory="0",
        mapval="0",
        order=8,
        allow_multiple_values="0",
        recommended="1")
    export_rule = Textbox(
        validation_criteria='str|min:1|max:64',
        hidden='False',
        isbasic='True',
        helptext="NFS Protocol Export Rules",
        dt_type="string",
        static="False",
        api="",
        name="export_rule",
        label="Export Rule",
        #svalue="E.g., 1.0.0.0/8(rw,no_root_squash) 
        #        fd01:abcd::/64(ro,secure,root_squash,anongid=16000) 
        #        @netgrp(rw,all_squash,anonuid=99,no_fileid_32bit) 
        #        1.41.8.32(rw,no_all_squash,fileid_32bit)",
        svalue="__t300.FBCreateSubnet.prefix",
        static_values="",
        mandatory="0",
        mapval="1",
        order=9,
        recommended="1")


class FBCreateNFSOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")

