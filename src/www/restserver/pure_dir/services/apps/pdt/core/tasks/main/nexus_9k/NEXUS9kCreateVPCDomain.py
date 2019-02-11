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
    task_id="NEXUS9kCreateVPCDomain",
    task_name="Create VPC Domain",
    task_desc="Create VPC Domain for Nexus switch",
    task_type="NEXUS"
)


class NEXUS9kCreateVPCDomain:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Create VPC Domain")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusCreateVPCDomain(taskinfo['inputs'], logfile)
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
        loginfo("NEXUS Create VPC Domain rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusDeleteVPCDomain(inputs, logfile)
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
        nexus_list = get_device_list(device_type="Nexus 9k")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_src_ip(self, keys):
        res = result()
        nexus_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                        return res

        nexus_list = self.get_detail(mac=mac_addr, src="1", dst="0")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_dst_ip(self, keys):
        res = result()
        nexus_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                        return res

        nexus_list = self.get_detail(mac=mac_addr, src="0", dst="1")
        res.setResult(nexus_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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


class NEXUS9kCreateVPCDomainInputs:
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
    vpc_id = Textbox(
        validation_criteria='int|min:1|max:1000',
        hidden='',
        isbasic='True',
        helptext='Virtual Port channel domain id',
        dt_type="string",
        static="False",
        api="",
        name="vpc_id",
        static_values="",
        label="VPC domain (1-1000)",
        svalue="10",
        mapval="",
        mandatory="1",
        order=2,
        recommended="1")
    vpc_role = Textbox(
        validation_criteria='int|min:1|max:65535',
        hidden='',
        isbasic='',
        helptext='Virtual Port channel role priority',
        dt_type="string",
        static="False",
        api="",
        name="vpc_role",
        static_values="",
        label="VPC role priority (1-65535)",
        svalue="10",
        mapval="",
        mandatory="1",
        order=3)
    ip_b = Textbox(
        validation_criteria='ip',
        hidden='',
        isbasic='',
        helptext='Destination IP address',
        dt_type="string",
        static="False",
        static_values="",
        api="",
        name="ip_b",
        label="Destination",
        svalue="",
        mapval="",
        mandatory="1",
        order=4)
    ip_a = Textbox(
        validation_criteria='ip',
        hidden='',
        isbasic='',
        helptext='Source IP address',
        dt_type="string",
        static="False",
        static_values="",
        api="",
        name="ip_a",
        label="Source",
        svalue="",
        mapval="",
        mandatory="1",
        order=5)
    delay = Textbox(
        validation_criteria='int|min:1|max:3600',
        hidden='',
        isbasic='',
        helptext='Delay interval',
        dt_type="string",
        static="False",
        api="",
        name="delay",
        static_values="",
        label="Delay (1-3600)",
        svalue="150",
        mapval="",
        mandatory="1",
        order=6)


class NEXUS9kCreateVPCDomainOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vpc_id = Output(dt_type="string", name="vpc_id", tvalue="10")
    vpc_role = Output(dt_type="string", name="vpc_role", tvalue="10")
    ip_b = Output(dt_type="string", name="ip_b", tvalue="192.168.10.67")
    ip_a = Output(dt_type="string", name="ip_a", tvalue="192.168.10.66")
    delay = Output(dt_type="string", name="delay", tvalue="150")
