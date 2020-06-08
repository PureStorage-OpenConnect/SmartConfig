from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
import os
import glob
from pure_dir.services.utils.miscellaneous import network_info
metadata = dict(
    task_id="UCSCreatevMediaPolicy",
    task_name="Create vMedia policy",
    task_desc="Create vMedia policy in UCS",
    task_type="UCSM"
)


class UCSCreatevMediaPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create vMedia Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatevMediaPolicy(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete vMedia Policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeletevMediaPolicy(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def esxiimages(self, keys):
        res = result()
        img_list = []
        images = [os.path.basename(fn) for fn in glob.glob(
            '/mnt/system/uploads/Vmware*.iso')]
        if len(images) > 0:
            selected = "1"
            for img in images:
                if img_list:
                    selected = "0"
                img_list.append(
                    {"id": img, "selected": selected, "label": img})
            res.setResult(img_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res
        res.setResult(img_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getnetworkip(self, keys):
        ntwk = network_info()
        res = result()
        ntwkip_dict = [{"id": ntwk['ip'], "selected":"1", "label":ntwk['ip']}]
        res.setResult(ntwkip_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreatevMediaPolicyInputs:

    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        static_values="",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)
    name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="ESXi-6.5U1-HTTP",
        static_values="",
        mandatory='1',
        order=2,
        recommended="1")
    descr = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="descr",
        static="False",
        svalue="Mount Cisco Custom ISO for ESXI 6.0 U2",
        static_values="",
        mandatory='1',
        order=3)
    mount = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Retry on mount failure",
        mapval="0",
        name="mount",
        static="True",
        static_values="no:0:No|yes:1:Yes",
        svalue="yes",
        mandatory='1',
        order=4)
    mount_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="mount_name",
        static="False",
        static_values="",
        svalue="ESXi-6.0U2-HTTP",
        mandatory='1',
        order=5)
    mount_desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="mount_desc",
        static="False",
        static_values="",
        svalue="ESXI ISO mount via HTTP",
        mandatory='1',
        order=6)
    type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Device Type",
        mapval="0",
        name="type",
        static="True",
        static_values="cdd:0:CDD|hdd:0:HDD",
        svalue="cdd",
        mandatory='1',
        order=7)
    protocol = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Protocol",
        mapval="0",
        name="protocol",
        static="True",
        static_values="http:1:HTTP|https:0:HTTPS",
        svalue="http",
        mandatory='1',
        order=8)
    image_name = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Image Name Variable",
        mapval="0",
        name="image_name",
        static="True",
        static_values="none:1:None|service_profile_name:0:Service Profile Name",
        svalue="none",
        mandatory='1',
        order=9)
    remote_file = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        api="esxiimages()",
        dt_type="string",
        label="Remote File",
        mapval="0",
        name="remote_file",
        static="False",
        static_values="",
        svalue="Vmware-ESXi-6.5.0-5969303-Custom-Cisco-6.5.1.1.iso",
        mandatory="1",
        order=10)
    image_path = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Remote Path",
        mapval="0",
        name="image_path",
        static_values="",
        static="False",
        mandatory='1',
        svalue="/images",
        order=11)


class UCSCreatevMediaPolicyOutputs:

    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="ESXi-6.5U1-HTTP")
