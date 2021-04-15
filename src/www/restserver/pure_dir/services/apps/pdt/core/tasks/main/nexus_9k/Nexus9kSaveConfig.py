from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.common import get_device_list, get_device_credentials
from pure_dir.infra.apiresults import *
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_devices_wf_config_file
from pure_dir.services.utils.miscellaneous import get_xml_childelements
from pure_dir.components.common import decrypt

metadata = dict(
    task_id="Nexus9kCopyrunningconfigFB",
    task_name="Copy running config to switch",
    task_desc="Copy running config to startup config",
    task_type="NEXUS"
)

class Nexus9kSaveConfig:
    def __init__(self):
        pass
    
    def execute(self, taskinfo, logfile):
        res = result()
        dicts={}
        loginfo("Copy running config")
        for switch in taskinfo['inputs']:
            cred = get_device_credentials(
                key="mac", value=taskinfo['inputs'][switch])
            if cred:
                nexus_res = Nexus(ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
                if nexus_res:
                   loginfo("Copying running config to startup config in nexus switch {}". format(switch[-1].upper()))
                   res = nexus_res.save_config()
                   if res.getStatus() != PTK_OKAY:
                       msg = "Unable to copy running config to startup config in nexus switch {}\n".format(switch[-1].upper())
                       customlogs(msg, logfile)
                       return parseTaskResult(res)
            else:
                loginfo("Unable to get device credentials")
                customlogs("Failed to get device credentials\n", logfile)
                res.setResult(False, PTK_INTERNALERROR, _("PDT_NEXUS_LOGIN_FAILURE"))

        res.setResult({}, PTK_OKAY,  _("PDT_SUCCESS_MSG"))
        customlogs("Nexus configuration saved to startup successfully\n", logfile)
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Nexus Copy running config rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 9k")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

class Nexus9kSaveConfigInputs:
    nexus_id_a = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        static_values="",
        api="getnexuslist()",
        name="nexus_id",
        label="Nexus switch",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)

    nexus_id_b = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        static_values="",
        api="getnexuslist()",
        name="nexus_id",
        label="Nexus switch",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)


class Nexus9kSaveConfigOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
