from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import NEXUSTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.infra.apiresults import *


metadata = dict(
    task_id="NEXUS5kEnableFeaturesAndSettings",
    task_name="Enable Features",
    task_desc="Enable the features in the Nexus switch",
    task_type="NEXUS"
)


class NEXUS5kEnableFeaturesAndSettings:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Enable Features And Settings")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusEnableFeaturesAndSettings(
                    taskinfo['inputs'], logfile)
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
        loginfo("NEXUS Enable Features And Settings rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusDisableFeaturesAndSettings(inputs, logfile)
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

    def get_feature_list_n5k(self, keys):
        res = result()
        loginfo("Getting NEXUS feature list...")
        flist = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(flist, PTK_OKAY,  _("PDT_SUCCESS_MSG"))
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                flist = obj.get_feature_list_n5k()
            else:
                loginfo("Unable to login to the Nexus")
                res.setResult(flist, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the Nexus")
            res.setResult(flist, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        res.setResult(flist, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class NEXUS5kEnableFeaturesAndSettingsInputs:
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
    spanning = Checkbox(
        hidden='',
        isbasic='True',
        helptext='Actual commands:<br/> spanning-tree port type network default <br/> spanning-tree port type edge bpduguard default<br/> spanning-tree port type edge bpdufilter default',
        dt_type="string",
        static="True",
        api="",
        name="spanning",
        label="Configure spanning tree",
        static_values="Yes@No:1:spanning",
        svalue="Yes",
        mapval="",
        mandatory="1",
        allow_multiple_values="0",
        order=2,
        recommended="1")
    feature = Multiselect(
        hidden='',
        isbasic='True',
        helptext='List of available features',
        dt_type="string",
        static="False",
        api="get_feature_list_n5k()|[nexus_id:1:nexus_id.value]",
        name="feature",
        label="Features",
        static_values="",
        svalue="lacp|vpc|interface-vlan",
        mapval="",
        mandatory="1",
        order=3,
        recommended="1")


class NEXUS5kEnableFeaturesAndSettingsOutputs:
    features = Output(dt_type="string", name="features",
                      tvalue="lacp|vpc|interface-vlan")
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    spanning = Output(dt_type="string", name="spanning", tvalue="Yes")
