import xmltodict
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg, job_input_save, getGlobalArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_file
from pure_dir.services.utils.miscellaneous import get_xml_element

metadata = dict(
    task_id="UCSConfigureAppliancePorts",
    task_name="Configure Ports connected to Storage Array",
    task_desc="Configure Ports connected to Storage Array as Appliance Ports",
    task_type="UCSM"
)
settings = '/mnt/system/pure_dir/pdt/settings.xml'


class UCSConfigureAppliancePorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Configure Appliance Ports")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsConfigureAppliancePorts(
            taskinfo['inputs'], logfile)
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Configure Appliance Ports rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsUnconfigureAppliancePorts(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def ucsmethports(self, keys):
        ports_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')
        ucs_fabric_name = getArg(keys, 'ucs_fabric_id')

        if fabricid is None:
            res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return res
        handle = res.getResult()
        switch_id = 'sys/switch-' + ucs_fabric_name
        ports_dn = switch_id + "/slot-1/switch-ether"
        ports = handle.query_dn(ports_dn)
        ports_list_obj = handle.query_children(in_mo=ports)
        for port in ports_list_obj:
            if 'aggr' in port.rn:
                continue
            ports_list.append({"id": port.port_id,
                               "selected": "0",
                               "label": "Port " + port.port_id})
        ucsm_logout(handle)
        res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
        subtype = data[0]['subtype']
        if status:
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
                appliance_ports = [[arg for arg in task['args']['arg'] if arg['@name'] == "ports"][0]
                          for task in doc['workflow']['tasks']['task'] if task['@texecid'] == texecid][0]['@value']

        except IOError:
            loginfo("Could not read file: %s" % job_xml)

        appl_ports_list , is_job_save = self.get_fa_iscsi_intf(pureid, appliance_ports)
        if is_job_save:
            appl_ports = "|".join(appl_ports_list)
            loginfo("Ports in prepare of {} : {}".format(metadata['task_name'], appl_ports))
            job_input_save(jobid, texecid, 'ports', appl_ports)
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

        loginfo("Fetching Appliance ports based on FA interfaces..")
        res = result()
        fi_model = ""
        is_job_save = False
        appl_port_list = inputs.split("|")


        cred = get_device_credentials(
            key="mac", value=pureid)
        if not cred:
            loginfo("Unable to get the FA credentials")
            return appl_port_list, is_job_save

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])
        intf_list = obj.get_fa_ports(fi_model)
        obj.release_pure_handle()
        if [intf for intf in intf_list if intf in ["ETH4", "ETH5", "ETH18", "ETH19"]]:
            is_job_save = True
            for port in range(len(appl_port_list)):
                if '49' in appl_port_list[port]:
                    appl_port_list[port] = '37'
                else:
                    appl_port_list[port] = '38'
            return appl_port_list, is_job_save
        return appl_port_list, is_job_save


class UCSConfigufreAppliancePortsInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        static_values="",
        mandatory="1",
        order=1)
    ucs_fabric_id = Radiobutton(
        hidden='True',
        isbasic='True',
        helptext='UCS Fabric ID',
        api="getfis()",
        dt_type="string",
        label="Fabric ID",
        mandatory="1",
        mapval="0",
        name="ucs_fabric_id",
        static="False",
        svalue="A",
        static_values="",
        order=2)
    ports = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Ethernet ports to configure as appliance port',
        api="ucsmethports()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
        dt_type="list",
        mandatory="1",
        label="Ethernet Ports",
        mapval="0",
        name="ports",
        static="False",
        svalue="1|2",
        static_values="",
        order=3,
        recommended="1")


class UCSConfigureAppliancePortsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
