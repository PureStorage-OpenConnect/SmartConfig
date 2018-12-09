from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSSetiSCSIBootParameters",
    task_name="Set iSCSI Boot parameters for iSCSI",
    task_desc="Set iSCSI Boot parameters for iSCSI",
    task_type="UCSM"
)


class UCSSetiSCSIBootParameters:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_iSCSI_boot_parameters_for_iSCSI")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsSetiSCSIBootParameters(
            taskinfo['inputs'], fp)
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("set iSCSI boot parameters for iSCSI rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteiSCSIBootParams(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

        return 0

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        print ucs_list, res
        return res

    def getiSCSIvNIC(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        iSCSI_vNIC_list = handle.query_classid("lsbootIScsiImagePath")
        selected = "1"
        for iSCSI_vNIC in iSCSI_vNIC_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": iSCSI_vNIC.i_scsi_vnic_name, "selected": selected, "label": iSCSI_vNIC.i_scsi_vnic_name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getiSCSIippools(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        ippool_list = handle.query_classid("ippoolPool")
        selected = "1"
        for ippool in ippool_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": ippool.name, "selected": selected, "label": ippool.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res


# Map iSCSI_target_name from pure tasks
class UCSSetiSCSIBootParametersInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    template_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Template name', dt_type="string", api="", static="False", static_values="", name="template_name",
                            label="template name", svalue="VM-Host-iSCSI-A", mandatory='1', mapval="0", order=2)
    iSCSI_vNIC_name = Dropdown(hidden='False', isbasic='True', helptext='iSCSI vNIC Name', dt_type="string", api="getiSCSIvNIC()|[fabric_id:1:fabric_id.value]", static="False",
                               static_values="", name="iSCSI_vNIC_name", label="iSCSI_vNIC_A", svalue="iSCSI-A-vNIC", mapval="0", mandatory='1', order=3)
    iSCSI_Boot = Radiobutton(hidden='False', isbasic='True', helptext='iSCSI Boot', dt_type="string", static="True", api="", name="iSCSI_Boot", label="iSCSI vNIC",
                             static_values="A:1:A|B:0:B", svalue="A", mapval="", mandatory='1', order=4)
    init_ipaddr_policy = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getiSCSIippools()|[fabric_id:1:fabric_id.value]", static="False",
                                  static_values="", name="init_ipaddr_policy", label="Initiator IP Address Policy A", svalue="iSCSI-IP-Pool-A", mapval="0", mandatory='1', order=5)
    iSCSI_Target_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='', dt_type="string", static="False", api="", name="iSCSI_Target_name",
                                label="iSCSI Target Name", static_values="", svalue="", mapval="1", mandatory="1", order=6)
    iSCSI_ip_address_eth8 = Textbox(validation_criteria='ip',  hidden='False', isbasic='True', helptext='', dt_type="string", static="False", api="", name="iSCSI_ip_address_eth8", label="iSCSI IPv4 Address for ct0 iSCSI Interface",
                                    static_values="", svalue="", mapval="3", mandatory="1", order=7)
    iSCSI_ip_address_eth9 = Textbox(validation_criteria='ip',  hidden='False', isbasic='True', helptext='', dt_type="string", static="False", api="", name="iSCSI_ip_address_eth9", label="iSCSI IPv4 Address for ct1 iSCSI Interface",
                                    static_values="", svalue="", mapval="3", mandatory="1", order=8)
    lunid = Textbox(validation_criteria='int|min:1|max:100',  hidden='False', isbasic='True', helptext='', dt_type="string", static="False", api="", name="lunid", label="LUN ID",
                    static_values="", svalue="1", mapval="", mandatory="1", order=9)


class UCSSetiSCSIBootParametersOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
