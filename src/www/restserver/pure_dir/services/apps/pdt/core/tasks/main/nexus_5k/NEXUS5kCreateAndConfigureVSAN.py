from pure_dir.infra.logging.logmanager import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *

metadata = dict(
    task_id="NEXUS5kCreateAndConfigureVSAN",
    task_name="Create and Configure VSAN",
    task_desc="Create VSAN and apply to the interfaces in the NEXUS switch",
    task_type="NEXUS"
)


class NEXUS5kCreateAndConfigureVSAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Configuring vsan for NEXUS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                # Create VSAN
                res = obj.create_vsan(taskinfo['inputs'], logfile)
                if res.getStatus() == PTK_OKAY:
                    # Configure VSAN
                    res = obj.configure_vsan(taskinfo['inputs'], logfile)
                    if res.getStatus() != PTK_OKAY:
                        loginfo("Failed to configure VSAN")
                        obj.delete_vsan(taskinfo['inputs'], logfile)
                        res.setResult(False, PTK_INTERNALERROR,
                                      "VSAN Configuration failed")
                    else:
                        loginfo(
                            "NEXUSCreateAndConfigureVSAN executed successfully")
                        res.setResult(
                            parseResult(res)['data'], PTK_OKAY,
                            "NEXUSCreateAndConfigureVSAN task executed successfully")
                else:
                    loginfo("Failed to create VSAN")
                    res.setResult(False, PTK_INTERNALERROR,
                                  "VSAN Creation failed")
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
        loginfo("Rollback - CreateAndConfigureVSAN for NEXUS")
        cred = get_device_credentials(
            key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(cred['ipaddress'],
                             cred['username'], cred['password'])
            if obj:
                # Delete VSAN
                res = obj.delete_vsan(inputs, logfile)
                if res.getStatus() != PTK_OKAY:
                    loginfo("Failed to delete VSAN")
                    res.setResult(False, PTK_INTERNALERROR,
                                  "VSAN deletion failed")
                else:
                    loginfo(
                        "NEXUSCreateAndConfigureVSAN rollback executed successfully")
                    res.setResult(
                        parseResult(res)['data'], PTK_OKAY,
                        "NEXUSCreateAndConfigureVSAN rollback task executed successfully")
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
                res.setResult(fc_list, PTK_OKAY, "success")
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
                res.setResult(fc_list, PTK_OKAY, "success")
                return res

            obj = Nexus()
            tmp_fc_list = obj.getfc_list(slot, ports).getResult()
            for index, fc in enumerate(tmp_fc_list):
                fc_list.append(
                    {"id": fc['iface_id'], "selected": "0", "label": fc['iface_id']})

        except Exception as e:
            loginfo(str(e))
            loginfo("Exception occured in get_fc_list")

        res.setResult(fc_list, PTK_OKAY, "success")
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
                              "Unable to login to the NEXUS")
        else:
            loginfo("Unable to get the device credentials of the NEXUS")
            res.setResult(pc_list, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the NEXUS")

        res.setResult(pc_list, PTK_OKAY, "success")
        return res


class NEXUS5kCreateAndConfigureVSANInputs:
    nexus_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", static_values="",
                        api="get_nexus_list()",
                        name="nexus_id", label="Nexus switch", svalue="", mapval="", mandatory="1", order="1")
    vsan_id = Textbox(validation_criteria='int|min:1|max:4094', hidden='False', isbasic='True', helptext='VSAN ID', dt_type="string",
                      static="False", api="", name="vsan_id",
                      static_values="", label="VSAN", svalue="101", mapval="", mandatory="1", order="2",
                      recommended="1")
    fc_list = Multiselect(hidden='False', isbasic='True', helptext='Interfaces to be configured in VSAN',
                          dt_type="string", static="False", api="get_fc_list()", name="fc_list", label="Interfaces",
                          static_values="", svalue="fc1/1|fc1/2|fc1/3|fc1/4",
                          mapval="", mandatory="1", order="3", recommended="1")
    pc_list = Multiselect(hidden='False', isbasic='True', helptext='Port Channel to be configured in VSAN',
                          dt_type="string", static="False", api="get_portchannel_list()|[nexus_id:1:nexus_id.value]",
                          name="pc_list", static_values="1", label="Port Channels", svalue="1",
                          mapval="", mandatory="1", order="4", recommended="1")


class NEXUS5kCreateAndConfigureVSANOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
