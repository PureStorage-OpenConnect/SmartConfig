import ast
import xmltodict
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, job_input_save, getGlobalArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import NEXUSTasks
from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.common import get_device_list, get_device_credentials
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_file
from pure_dir.services.utils.miscellaneous import get_xml_element

metadata = dict(
    task_id="NEXUS9kAddIndividualPortDescription",
    task_name="Add Individual Port Description",
    task_desc="Add Individual Port Description for Nexus switch",
    task_type="NEXUS"
)

settings = '/mnt/system/pure_dir/pdt/settings.xml'

class NEXUS9kAddIndividualPortDescription:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Add Individual Port Description")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusAddIndividualPortDescription(
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
        loginfo("NEXUS Add Individual Port Description rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusRemoveIndividualPortDescription(inputs, logfile)
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

    def validate(self, item):
        member = eval(item)
        obj = Nexus()
        if member['interface']['value'] == "Vlan":
            if member['id']['ismapped'] == "0":
                if obj.fieldvalidation(member['id']['value'])[0] == False:
                    return False, "id", "Invalid Value"
                if int(member['id']['value']) < 1 or int(member['id']['value']) > 3967:
                    return False, "id", "Enter the Value inbetween " + "1" + " - " + "3967"
            return True, "id", member['id']['ismapped']
        elif member['interface']['value'] == "port-channel":
            if member['id']['ismapped'] == "0":
                if obj.fieldvalidation(member['id']['value'])[0] == False:
                    return False, "id", "Invalid Value"
                if int(member['id']['value']) < 1 or int(member['id']['value']) > 4096:
                    return False, "id", "Enter the Value inbetween " + "1" + " - " + "4096"
            return True, "id", member['id']['ismapped']
        elif member['interface']['value'] == "Eth":
            eth = member['id']['value'].split('/')
            if member['id']['ismapped'] == "0":
                if eth[0] not in ["1", "2"] or int(eth[1]) < 1 or int(eth[1]) > 54:
                    return False, "id", "Enter proper interface value"
            return True, "id", member['id']['ismapped']
        else:
            return True, "id", member['id']['ismapped']

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type texecid: str
        :param inputs: input from global variables
        :type inputs: dict

        """
        loginfo("Enters into prepare function for {}".format(metadata['task_name']))
        res = result()
        status, data = get_xml_element(settings, 'subtype')
        if status:
            subtype = data[0]['subtype']
            if not (('6454' in subtype) and ('iscsi' in subtype)):
                res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                return res
        pureid = getGlobalArg(inputs, 'pure_id')
        if pureid is None:
            res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res
        job_xml = get_job_file(jobid)
        try:
            with open(job_xml, 'r') as fd:
                doc = xmltodict.parse(fd.read())
                port_set = [[arg for arg in task['args']['arg'] if arg['@name'] == "port_set"][0]
                          for task in doc['workflow']['tasks']['task'] if task['@texecid'] == texecid][0]['@value']
        except IOError:
            loginfo("Could not read file: %s" % job_xml)
            res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res
        nexus_intf, is_job_save = self.get_fa_iscsi_intf(pureid, port_set)
        if is_job_save:
            intf_desc = "|".join(map(str,nexus_intf))
            loginfo("Interfaces in prepare for {} :{}".format(metadata['task_name'], intf_desc))
            job_input_save(jobid, texecid, 'port_set', intf_desc)
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


    def get_fa_iscsi_intf(self, pureid, inputs):
        """
        :param inputs: mac of FlashArray
        :type: str
        :param inputs: inputs from global variables
        :type: dict
        :returns: list of ethernet interfaces

        """

        loginfo("Fetching the Nexus Interfaces based on FA interfaces..")
        res = result()
        fi_model = ""
        is_job_save = False
        port_list = list(map(lambda intf:ast.literal_eval(intf),inputs.split("|")))

        cred = get_device_credentials(
            key="mac", value=pureid)
        if not cred:
            loginfo("Unable to get the FA credentials")
            return port_list, is_job_save

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])
        intf_list = obj.get_fa_ports(fi_model)
        obj.release_pure_handle()
        if [intf for intf in intf_list if intf in ["ETH4", "ETH5", "ETH18", "ETH19"]]:
            is_job_save = True
            for port in port_list:
                for key, val in port.items():
                    if '1/49' in val['value']:
                        val['value'] = '1/37'
                    elif '1/50' in val['value']:
                        val['value'] = '1/38'
            return port_list, is_job_save
        return port_list, is_job_save

class NEXUS9kAddIndividualPortDescriptionInputs:
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
    interface = Dropdown(
        hidden='',
        isbasic='True',
        helptext='Select the interface to be configured',
        dt_type="string",
        static="True",
        api="",
        name="interface",
        label="Interface",
        static_values="Vlan:1:Vlan|port-channel:0:Port-channel|Eth:0:Eth",
        svalue="",
        mapval="",
        mandatory="1",
        group_member="1")
    id = Textbox(
        validation_criteria='',
        hidden='',
        isbasic='True',
        helptext='Provide the required id',
        dt_type="string",
        static="False",
        api="",
        name="id",
        label="ID",
        static_values="",
        svalue="115",
        mapval="",
        mandatory="",
        group_member="1")
    desc = Textbox(
        validation_criteria='',
        hidden='Description to be added to the interface',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="",
        name="desc",
        label="Description",
        static_values="",
        svalue="In-Band NTP Redistribution Interface VLAN 115",
        mapval="",
        mandatory="",
        group_member="1")
    port_set = Group(
        validation_criteria='function',
        hidden='',
        isbasic='True',
        helptext='Provide interface type, id and description',
        dt_type="string",
        static="False",
        api="",
        name="port_set",
        label="Add Individual Port Description",
        static_values="",
        svalue="{'interface': {'ismapped': '0', 'value': 'Vlan'}, 'id': {'ismapped': '0', 'value': '115'}, 'desc': {'ismapped': '0', 'value': 'In-Band NTP Redistribution Interface VLAN 115'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '11'}, 'desc': {'ismapped': '0', 'value': 'vPC peer-link'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '151'}, 'desc': {'ismapped': '0', 'value': 'vPC UCS 6332-16UP-1 FI'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '152'}, 'desc': {'ismapped': '0', 'value': 'vPC UCS 6332-16UP-2 FI'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '153'}, 'desc': {'ismapped': '0', 'value': 'vPC Upstream Network Switch A'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '154'}, 'desc': {'ismapped': '0', 'value': 'vPC Upstream Network Switch B'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/1'}, 'desc': {'ismapped': '0', 'value': 'vPC peer-link connection to b19-93180-2'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/2'}, 'desc': {'ismapped': '0', 'value': 'vPC peer-link connection to b19-93180-2'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/51'}, 'desc': {'ismapped': '0', 'value': 'vPC 151 connection to UCS 6332-16UP-1 FI'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/52'}, 'desc': {'ismapped': '0', 'value': 'vPC 152 connection to UCS 6332-16UP-2 FI'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/53'}, 'desc': {'ismapped': '0', 'value': ' vPC 153 connection to Upstream Network Switch A'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/54'}, 'desc': {'ismapped': '0', 'value': ' vPC 153 connection to Upstream Network Switch B'}}",
        mapval="",
        mandatory="1",
        members=[
            "interface",
            "id",
            "desc"],
        add="True",
        order=2)


class NEXUS9kAddIndividualPortDescriptionOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    port_set = Output(dt_type="string", name="port_set", tvalue="")
