from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSAddBlockofIPAddressesforKVMAccess",
    task_name="Add block of IP Address for KVM access",
    task_desc="Add block of IP Address for KVM access in UCS",
    task_type="UCSM"
)


class UCSAddBlockofIPAddressesforKVMAccess:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("add_block_of_ipaddress_for_kvmaccess")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.addBlockIPAddForKVMAccess(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Block of KVM IP Addresses")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteKVMIPAddresses(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSAddBlockofIPAddressesforKVMAccessInputs:
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
    kvm_console_ip = Textbox(
        validation_criteria='ip-range',
        hidden='False',
        isbasic='True',
        helptext='KVM Starting IP Address',
        api="",
        dt_type="string",
        mandatory="1",
        static_values="",
        label="From",
        mapval="0",
        name="kvm_console_ip",
        static="False",
        svalue="120-132",
        order=2)
    size = Textbox(
        validation_criteria='int|min:1|max:1000',
        hidden='False',
        isbasic='True',
        helptext='Size',
        api="",
        dt_type="string",
        mandatory="1",
        static_values="",
        label="Size(1-1000)",
        mapval="0",
        name="size",
        static="False",
        svalue="12",
        order=3)
    mask = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Netmask',
        api="",
        dt_type="string",
        mandatory="1",
        static_values="",
        label="Subnet Mask",
        mapval="0",
        name="mask",
        static="False",
        svalue="255.255.255.0",
        order=4)
    gateway = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Gateway',
        api="",
        dt_type="string",
        mandatory="1",
        static_values="",
        label="Default Gateway",
        mapval="0",
        name="gateway",
        static="False",
        svalue="192.168.10.1",
        order=5)
    pri_dns = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Primary DNS',
        api="",
        dt_type="string",
        mandatory="1",
        static_values="",
        label="Primary DNS",
        mapval="0",
        name="pri_dns",
        static="False",
        svalue="0.0.0.0",
        order=6)
    sec_dns = Textbox(
        validation_criteria='ip',
        hidden='False',
        isbasic='True',
        helptext='Secondary DNS',
        api="",
        dt_type="string",
        mandatory="1",
        static_values="",
        label="Secondary DNS",
        mapval="0",
        name="sec_dns",
        static="False",
        svalue="0.0.0.0",
        order=7)


class UCSAddBlockofIPAddressesforKVMAccessOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
