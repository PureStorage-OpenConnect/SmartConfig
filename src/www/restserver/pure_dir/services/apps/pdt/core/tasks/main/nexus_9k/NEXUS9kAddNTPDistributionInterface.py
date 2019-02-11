from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import NEXUSTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.common import get_device_list, get_device_credentials
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import get_xml_element

static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'

metadata = dict(
    task_id="NEXUS9kAddNTPDistributionInterface",
    task_name="Add NTP Distribution Interface",
    task_desc="Add NTP Distribution Interface for Nexus switch",
    task_type="NEXUS"
)


class NEXUS9kAddNTPDistributionInterface:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Add NTP Distribution Interface")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusAddNTPDistributionInterface(
                    taskinfo['inputs'], logfile, cred['ipaddress'])
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              "Connection to NEXUS failed")
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("NEXUS Add NTP Distribution Interface rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusRemoveNTPDistributionInterface(
                    inputs, logfile, cred['ipaddress'])
            else:
                customlogs("Failed to login to NEXUS switch", logfile)
                loginfo("Failed to login to NEXUS switch")
                res.setResult(False, PTK_INTERNALERROR,
                              "Connection to NEXUS failed")
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 9k")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_ip(self, keys):
        res = result()
        nexus_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(nexus_list, PTK_OKAY,  _("PDT_SUCCESS_MSG"))
                        return res

        nexus_list = self.get_detail(mac=mac_addr, src="1", dst="0")
        res.setResult(nexus_list, PTK_OKAY,  _("PDT_SUCCESS_MSG"))
        return res

    def get_detail(self, mac, src, dst):
        nexus_list = []
        status, details = get_xml_element(
            file_name=static_discovery_store, attribute_key="device_type", attribute_value="Nexus 9k")

        if status:
            for detail in details:
                nexus = {}
                if detail['mac'] == mac:
                    nexus['selected'] = src
                else:
                    nexus['selected'] = dst
                nexus['label'] = detail['ipaddress']
                nexus['id'] = detail['ipaddress']
                nexus_list.append(nexus)

        return nexus_list


class NEXUS9kAddNTPDistributionInterfaceInputs:
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
    gateway = Textbox(
        validation_criteria='ip',
        hidden='',
        isbasic='True',
        helptext='Gateway address',
        dt_type="string",
        static="False",
        api="",
        name="gateway",
        static_values="",
        label="Gateway",
        svalue="",
        mapval="",
        mandatory="1",
        order=2)
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
        order=3)
    mask_length = Textbox(
        validation_criteria='int|min:1|max:31',
        hidden='',
        isbasic='True',
        helptext='Netmask length',
        dt_type="string",
        static="False",
        api="",
        name="mask_length",
        static_values="",
        label="Mask length",
        svalue="24",
        mapval="",
        mandatory="1",
        order=4)
    stratum_no = Textbox(
        validation_criteria='int|min:1|max:15',
        hidden='',
        isbasic='True',
        helptext='Stratum number for NTP',
        dt_type="string",
        static="False",
        api="",
        name="stratum_no",
        static_values="",
        label="Stratum number",
        svalue="3",
        mapval="",
        mandatory="1",
        order=5)
    vlan_id = Textbox(
        validation_criteria='int|min:1|max:3967',
        hidden='',
        isbasic='True',
        helptext='Virtual LAN id',
        dt_type="string",
        static="False",
        api="",
        name="vlan_id",
        static_values="",
        label="VLAN id",
        svalue="115",
        mapval="",
        mandatory="1",
        order=6,
        recommended="1")


class NEXUS9kAddNTPDistributionInterfaceOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    ip = Output(dt_type="string", name="ip", tvalue="192.168.10.70")
    gateway = Output(dt_type="string", name="gateway", tvalue="192.168.10.71")
    mask_length = Output(dt_type="string", name="mask_length", tvalue="24")
    vlan_id = Output(dt_type="string", name="vlan_id", tvalue="115")
    stratum_no = Output(dt_type="string", name="stratum_no", tvalue="3")
