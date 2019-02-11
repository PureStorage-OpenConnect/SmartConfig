import xmltodict
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.network.nexus.nexus_tasks import NEXUSTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_file
from pure_dir.infra.apiresults import *

metadata = dict(
    task_id="NEXUS5kConfigurePortchannel",
    task_name="Configure PortChannel",
    task_desc="Configure Port Channel in the NEXUS switch",
    task_type="NEXUS"
)


class NEXUS5kConfigurePortchannel:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Configuring port channel for NEXUS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                res = obj.configure_portchannel(taskinfo['inputs'], logfile)
            else:
                loginfo("Unable to login to the NEXUS")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the NEXUS")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("Rollback - Configure PortChannel for NEXUS")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                res = obj.unconfigure_portchannel(inputs, logfile)
            else:
                loginfo("Unable to login to the NEXUS")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the NEXUS")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_NEXUS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def get_nexus_list(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 5k")
        res.setResult(nexus_list, PTK_OKAY, "success")
        return res

    def get_portchannel_list(self, keys):
        res = result()
        loginfo("Getting NEXUS port channel list...")
        pc_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(pc_list, PTK_OKAY, "success")
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                tmp_pc_list = obj.get_portchannel_list().getResult()
                for index, pc in enumerate(tmp_pc_list):
                    pc_list.append(
                        {"id": pc['iface_id'], "selected": "0", "label": pc['iface_id']})
            else:
                loginfo("Unable to login to the NEXUS")
                res.setResult(pc_list, PTK_INTERNALERROR,
                               _("PDT_NEXUS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the NEXUS")
            res.setResult(pc_list, PTK_INTERNALERROR,
                           _("PDT_NEXUS_LOGIN_FAILURE"))

        res.setResult(pc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_fc_list(self, keys):
        res = result()
        loginfo("Getting NEXUS fc list...")
        fc_list = []

        try:
            jobid = str([arg['value'] for args in keys.values()
                         for arg in args if arg['key'] == "jobid"][0])
            texecid = str([arg['value'] for args in keys.values()
                           for arg in args if arg['key'] == "texecid"][0])
            if jobid == "" or texecid == "":
                res.setResult(fc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                return res

            job_xml = get_job_file(jobid)
            fd = open(job_xml, 'r')
            doc = xmltodict.parse(fd.read())

            tag = [task['@desc'][-1] for task in doc['workflow']
                   ['tasks']['task'] if task['@texecid'] == texecid][0]
            slot = [[switch['@value'] for switch in task['args']['arg'] if switch['@name'] == "slot"][0]
                    for task in doc['workflow']['tasks']['task'] if
                    task['@id'] == "NEXUS5kConfigureUnifiedPorts" and task['@desc'][-1] == tag][0]
            ports = [[switch['@value'] for switch in task['args']['arg'] if switch['@name'] == "ports"][0]
                     for task in doc['workflow']['tasks']['task'] if
                     task['@id'] == "NEXUS5kConfigureUnifiedPorts" and task['@desc'][-1] == tag][0]

            if slot == "" or ports == "":
                res.setResult(fc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                return res

            obj = Nexus()
            tmp_fc_list = obj.getfc_list(slot, ports).getResult()
            for index, fc in enumerate(tmp_fc_list):
                fc_list.append(
                    {"id": fc['iface_id'], "selected": "0", "label": fc['iface_id']})

        except Exception as e:
            loginfo(str(e))
            loginfo("Exception occured in get_fc_list")

        res.setResult(fc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class NEXUS5kConfigurePortchannelInputs:
    nexus_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        static_values="",
        api="get_nexus_list()",
        name="nexus_id",
        label="Nexus switch",
        svalue="",
        mapval="",
        mandatory="1",
        order="1")
    portchannel_id = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Port channel ID',
        dt_type="string",
        static="False",
        api="get_portchannel_list()|[nexus_id:1:nexus_id.value]",
        name="portchannel_id",
        static_values="",
        label="Port Channel",
        svalue="1",
        mapval="",
        mandatory="1",
        order="2",
        recommended="1")
    fc_list = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Interfaces to be configured in Port Channel',
        dt_type="string",
        static="False",
        api="get_fc_list()",
        name="fc_list",
        label="Interfaces",
        static_values="",
        svalue="fc1/5|fc1/6|fc1/7|fc1/8",
        mapval="",
        mandatory="1",
        order="3",
        recommended="1")


class NEXUS5kConfigurePortchannelOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
