from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSAddCimcMountedDisk",
    task_name="Add CIMC Mounted disk",
    task_desc="Add CIMC Mounted disk in UCS",
    task_type="UCSM"
)


class UCSAddCimcMountedDisk:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("add_cimc_mounted_disk")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.addCimcMountedDisk(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("remove_cimc_mounted_disk")

        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.deleteCimcMountedDisk(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        print ucs_list, res
        return res


class UCSAddCimcMountedDiskInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    bootpolicyname = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Boot policy name', dt_type="string", api="", static="False", static_values="", name="bootpolicyname",
                             label="Boot Policy Name", mapval="1", svalue="__t201.UCSCreateBootPolicy.bootpolicyname", mandatory="1", order=2)


class UCSAddCimcMountedDiskOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
