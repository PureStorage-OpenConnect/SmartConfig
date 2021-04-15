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
    task_id="NEXUS9kConfigureiSCSIInterface",
    task_name="Configure iSCSI Interface",
    task_desc="Configure iSCSI Interface",
    task_type="NEXUS"
)

settings = '/mnt/system/pure_dir/pdt/settings.xml'

class NEXUS9kConfigureiSCSIInterface:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Configure iSCSI Interface")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusConfigureiSCSIInterface(
                    taskinfo['inputs'], logfile, "n9k")
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
        loginfo("NEXUS Configure iSCSI Interface rollback")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusUnconfigureiSCSIInterface(
                    inputs, logfile, "n9k")
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

    def get_intf_list(self, keys):
        res = result()
        intf_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(intf_list, PTK_OKAY, "success")
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                intf_list = obj.get_interface_list()
            else:
                loginfo("Unable to login to the Nexus")
                res.setResult(intf_list, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the Nexus")
            res.setResult(intf_list, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        res.setResult(intf_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

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
            if not('6454' in subtype and 'iscsi' in subtype):
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
                intf_set = [[arg for arg in task['args']['arg'] if arg['@name'] == "intf_set"][0]
                          for task in doc['workflow']['tasks']['task'] if task['@texecid'] == texecid][0]['@value']
        except IOError:
            loginfo("Could not read file: %s" % job_xml)
            res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res
    
        nexus_intf, is_job_save = self.get_fa_iscsi_intf(pureid, intf_set)
        if is_job_save: 
            interfaces = "|".join(map(str, nexus_intf))
            loginfo("Interfaces in prepare of {} : {}".format(metadata['task_name'], interfaces))
            job_input_save(jobid, texecid, 'intf_set', interfaces)
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


    def get_fa_iscsi_intf(self, pureid, inputs):
        """
        :param inputs: inputs from global variables
        :type : dict
        :returns: list of ethernet interfaces

        """

        loginfo("Fetching Nexus Interfaces based on FA interfaces..")
        res = result()
        fi_model = ""
        is_job_save = False
        nex_intf_list = list(map(lambda intf:ast.literal_eval(intf),inputs.split("|")))

        cred = get_device_credentials(
            key="mac", value=pureid)
        if not cred:
            loginfo("Unable to get the FA credentials")
            return nex_intf_list, is_job_save

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])
        intf_list = obj.get_fa_ports(fi_model)
        obj.release_pure_handle()
        if [intf for intf in intf_list if intf in ["ETH4", "ETH5", "ETH18", "ETH19"]]:
            is_job_save = True
            for nex_intf in nex_intf_list:
                for key, val in nex_intf.items():
                    if key == 'slot_chassis':
                        if '1/49' in val['value']:
                            val['value'] = 'Eth1/37'
                        else:
                            val['value'] = 'Eth1/38'
            return nex_intf_list, is_job_save
        return nex_intf_list, is_job_save

class NEXUS9kConfigureiSCSIInterfaceInputs:
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
    slot_chassis = Multiselectdropdown(
        hidden='',
        isbasic='True',
        helptext='Select the interfaces to be configured',
        dt_type="string",
        static="False",
        api="get_intf_list()|[nexus_id:1:nexus_id.value]",
        name="slot_chassis",
        label="Interfaces",
        static_values="",
        svalue="Eth1/49",
        mapval="",
        mandatory="1",
        group_member="1",
        recommended="1")
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
        group_member="1",
        recommended="1")
    intf_set = Group(
        validation_criteria='',
        hidden='',
        isbasic='True',
        helptext='Select the interfaces to be configured and the corresponding VLAN id',
        dt_type="string",
        static="False",
        api="",
        name="intf_set",
        label="Configure Interfaces",
        static_values="",
        svalue="{'slot_chassis': {'ismapped': '0', 'value': 'Eth1/49'}, 'vlan_id': {'ismapped': '0', 'value': '901'}}|{'slot_chassis': {'ismapped': '0', 'value': 'Eth1/50'}, 'vlan_id': {'ismapped': '0', 'value': '902'}}",
        mapval="",
        mandatory="1",
        members=[
            "slot_chassis",
            "vlan_id"],
        add="True",
        order=2,
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
        order=3)


class NEXUS9kConfigureiSCSIInterfaceOutputs:
    intf_set = Output(dt_type="string", name="intf_set", tvalue="")
    mtu_value = Output(dt_type="string", name="mtu_value", tvalue="9216")
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
