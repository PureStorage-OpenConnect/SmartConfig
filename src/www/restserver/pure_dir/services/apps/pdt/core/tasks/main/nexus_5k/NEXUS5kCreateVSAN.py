from pure_dir.infra.logging.logmanager import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *

metadata = dict(
        task_id="NEXUS5kCreateVSAN",
        task_name="Create VSAN",
        task_desc="Create VSAN in the NEXUS switch",
        task_type="NEXUS"
)


class NEXUS5kCreateVSAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Creating vsan for NEXUS")
        cred = get_device_credentials(
                key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                res = obj.create_vsan(taskinfo['inputs'], logfile)
            else:
                loginfo("Unable to login to the NEXUS")
                res.setResult(False, PTK_INTERNALERROR,
                              "Unable to login to the NEXUS")
        else:
            loginfo("Unable to get the device credentials of the NEXUS")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the NEXUS")

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("Rollback - CreateVSAN for NEXUS")
        cred = get_device_credentials(
                key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                res = obj.delete_vsan(inputs, logfile)
            else:
                loginfo("Unable to login to the NEXUS")
                res.setResult(False, PTK_INTERNALERROR,
                              "Unable to login to the NEXUS")
        else:
            loginfo("Unable to get the device credentials of the NEXUS")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the NEXUS")

        return parseTaskResult(res)

    def get_nexus_list(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 5k")
        res.setResult(nexus_list, PTK_OKAY, "success")
        return res


class NEXUS5kCreateVSANInputs:
    nexus_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", static_values="",
                        api="get_nexus_list()",
                        name="nexus_id", label="NEXUS switch", svalue="", mapval="", mandatory="1", order="1")
    vsan_id = Textbox(validation_criteria='', hidden='True', isbasic='True', helptext='', dt_type="string",
                      static="False", api="", name="vsan_id",
                      static_values="", label="VSAN", svalue="101", mapval="", mandatory="1", order="2")


class NEXUS5kCreateVSANOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vsan_id = Output(dt_type="string", name="vsan_id", tvalue="101")
