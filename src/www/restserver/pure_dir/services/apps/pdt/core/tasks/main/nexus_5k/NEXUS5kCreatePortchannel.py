from pure_dir.infra.logging.logmanager import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *

metadata = dict(
        task_id="NEXUS5kCreatePortchannel",
        task_name="Create PortChannel",
        task_desc="Create Port Channel in the NEXUS switch",
        task_type="NEXUS"
)


class NEXUS5kCreatePortchannel:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Creating port channel for NEXUS")
        cred = get_device_credentials(
                key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                res = obj.create_portchannel(taskinfo['inputs'], logfile)
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
        loginfo("Rollback - CreatePortChannel for NEXUS")
        cred = get_device_credentials(
                key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                res = obj.delete_portchannel(inputs, logfile)
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


class NEXUS5kCreatePortchannelInputs:
    nexus_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", static_values="",
                        api="get_nexus_list()",
                        name="nexus_id", label="Nexus switch", svalue="", mapval="", mandatory="1", order="1")
    portchannel_id = Textbox(validation_criteria='int|min:1|max:256', hidden='False', isbasic='True', helptext='Port channel ID',
                             dt_type="string", static="False", api="", name="portchannel_id",
                             static_values="", label="Port Channel (1-256)", svalue="1", mapval="", mandatory="1",
                             order="2", recommended="1")


class NEXUS5kCreatePortchannelOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    portchannel_id = Output(
            dt_type="string", name="portchannel_id", tvalue="1")
