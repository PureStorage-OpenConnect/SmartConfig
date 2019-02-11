from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import NEXUSTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.infra.apiresults import *


metadata = dict(
    task_id="NEXUS5kSetGlobalConfigurations",
    task_name="Set global configurations",
    task_desc="Set global configurations in the Nexus switch",
    task_type="NEXUS"
)


class NEXUS5kSetGlobalConfigurations:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Set Global Configurations")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusSetGlobalConfigurations(
                    taskinfo['inputs'], logfile, "n5k")
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("NEXUS Set Global Configurations rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusRemoveGlobalConfigurations(
                    inputs, logfile, "n5k")
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 5k")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class NEXUS5kSetGlobalConfigurationsInputs:
    nexus_id = Dropdown(
        hidden='True',
        isbasic='',
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
    route = Textbox(
        validation_criteria='ip',
        hidden='',
        isbasic='True',
        helptext='Route address',
        dt_type="string",
        static="False",
        api="",
        name="route",
        label="Route",
        static_values="",
        svalue="0.0.0.0/0",
        mapval="",
        mandatory="1",
        order=2,
        recommended="1")
    gateway = Textbox(
        validation_criteria='ip',
        hidden='',
        isbasic='True',
        helptext='Gateway address',
        dt_type="string",
        static="False",
        api="",
        name="gateway",
        label="Gateway",
        static_values="",
        svalue="192.168.10.28",
        mapval="",
        mandatory="1",
        order=3,
        recommended="1")
    ntp = Textbox(
        validation_criteria='ip',
        hidden='',
        isbasic='True',
        helptext='NTP address',
        dt_type="string",
        static="False",
        api="",
        name="ntp",
        label="NTP",
        static_values="",
        svalue="192.168.10.29",
        mapval="",
        mandatory="1",
        order=4,
        recommended="1")
    mtu_value = Textbox(
        validation_criteria='int|min:1500|max:9216',
        hidden='',
        isbasic='',
        helptext='Maximum transfer unit',
        dt_type="string",
        static="False",
        api="",
        name="mtu_value",
        static_values="",
        label="MTU value (1500-9216)",
        svalue="9216",
        mapval="",
        mandatory="1",
        order=6)


class NEXUS5kSetGlobalConfigurationsOutputs:
    route = Output(dt_type="string", name="route", tvalue="0.0.0.0/0")
    gateway = Output(dt_type="string", name="gateway", tvalue="192.168.10.28")
    ntp = Output(dt_type="string", name="ntp", tvalue="192.168.10.29")
    mtu_value = Output(dt_type="string", name="mtu_value", tvalue="9216")
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
