from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *


class UCSCreateLocalDiskConfigurationPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Local Disk Configuration Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateLocalDiskConfigurationPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Local Disk Configuration Policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteLocalDiskConfigurationPolicy(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getdiskconfigmodes(self, keys):
        res = result()
        val = [{"id": "no-local-storage",
                "selected": "1",
                "label": "No Local Storage"},
               {"id": "any-configuration",
                "selected": "0",
                "label": "Any Configuration"},
               {"id": "raid-mirrored",
                "selected": "0",
                "label": "RAID 1 Mirrored"},
               {"id": "raid-striped",
                "selected": "0",
                "label": "RAID 0 Striped"},
               {"id": "no-raid",
                "selected": "0",
                "label": "No RAID"},
               {"id": "raid-striped-parity",
                "selected": "0",
                "label": "RAID 5 Striped Parity"},
               {"id": "raid-striped-dual-parity",
                "selected": "0",
                "label": "RAID 6 Striped Dual Parity"},
               {"id": "raid-mirrored-striped",
                "selected": "0",
                "label": "RAID 10 Mirrored and Striped"},
               {"id": "raid-striped-parity-striped",
                "selected": "0",
                "label": "RAID 50 Striped Parity and Striped"},
               {"id": "raid-striped-dual-parity-striped",
                "selected": "0",
                "label": "RAID 60 Striped Dual Parity and Striped"}]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateLocalDiskConfigurationPolicyInputs:
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
    name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Local disk policy name',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="SAN-Boot",
        mandatory='1',
        static_values="",
        order=2)
    descr = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='description',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="descr",
        static="False",
        svalue="Local disk config policy",
        mandatory='1',
        static_values="",
        order=3)
    mode = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Disk config modes',
        api="getdiskconfigmodes()",
        dt_type="string",
        label="Mode",
        mapval="0",
        name="mode",
        static="False",
        svalue="no-local-storage",
        mandatory='1',
        static_values="",
        order=4)
    flash_state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Flexflash State',
        api="",
        dt_type="string",
        label="FlexFlash State",
        mapval="0",
        name="flash_state",
        static="True",
        static_values="disable:1:Disable|enable:0:Enable",
        svalue="disable",
        mandatory='1',
        order=5)
    raid_state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='RAID reporting state',
        api="",
        dt_type="string",
        label="RAID Reporting State",
        mapval="0",
        name="raid_state",
        static="True",
        static_values="disable:1:Disable|enable:0:Enable",
        svalue="disable",
        mandatory='1',
        order=6)


class UCSCreateLocalDiskConfigurationPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
