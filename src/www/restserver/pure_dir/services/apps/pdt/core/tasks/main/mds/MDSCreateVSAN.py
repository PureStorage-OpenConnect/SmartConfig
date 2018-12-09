from pure_dir.infra.logging.logmanager import *
from pure_dir.components.storage.mds.mds_tasks import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *

metadata = dict(
    task_id="MDSCreateVSAN",
    task_name="Create VSAN",
    task_desc="Create VSAN in the MDS switch",
    task_type="MDS"
)


class MDSCreateVSAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Creating vsan for MDS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                res = obj.create_vsan(taskinfo['inputs'], logfile)
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(False, PTK_INTERNALERROR,
                              "Unable to login to the MDS")
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("Rollback - CreateVSAN for MDS")
        cred = get_device_credentials(
            key="mac", value=inputs['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                res = obj.delete_vsan(inputs, logfile)
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(False, PTK_INTERNALERROR,
                              "Unable to login to the MDS")
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

        return parseTaskResult(res)

    def get_mds_list(self, keys):
        res = result()
        mds_list = get_device_list(device_type="MDS")
        res.setResult(mds_list, PTK_OKAY, "success")
        return res


class MDSCreateVSANInputs:
    mds_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", static_values="", api="get_mds_list()",
                      name="mds_id", label="MDS switch", svalue="", mapval="", mandatory="1", order="1")
    vsan_id = Textbox(validation_criteria='',  hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="", name="vsan_id",
                      static_values="", label="VSAN", svalue="101", mapval="", mandatory="1", order="2")


class MDSCreateVSANOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vsan_id = Output(dt_type="string", name="vsan_id", tvalue="101")
