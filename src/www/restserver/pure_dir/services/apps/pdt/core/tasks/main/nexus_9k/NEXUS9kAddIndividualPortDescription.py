from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.common import *

metadata = dict(
        task_id="NEXUS9kAddIndividualPortDescription",
        task_name="Add Individual Port Description",
        task_desc="Add Individual Port Description for Nexus switch",
        task_type="NEXUS"
)


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
                              "Connection to NEXUS failed")
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          "Failed to get NEXUS switch credentials")

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
                              "Connection to NEXUS failed")
        else:
            customlogs("Failed to get NEXUS switch credentials", logfile)
            loginfo("Failed to get NEXUS switch credentials")
            res.setResult(False, PTK_INTERNALERROR,
                          "Failed to get NEXUS switch credentials")

        return parseTaskResult(res)

    def getnexuslist(self, keys):
        res = result()
        nexus_list = get_device_list(device_type="Nexus 9k")
        res.setResult(nexus_list, PTK_OKAY, "success")
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


class NEXUS9kAddIndividualPortDescriptionInputs:
    nexus_id = Dropdown(hidden='True', isbasic='', helptext='', dt_type="string", static="False", static_values="",
                        api="getnexuslist()",
                        name="nexus_id", label="Nexus switch", svalue="", mapval="", mandatory="1", order=1)
    interface = Dropdown(hidden='', isbasic='True', helptext='Select the interface to be configured', dt_type="string",
                         static="True", api="", name="interface", label="Interface",
                         static_values="Vlan:1:Vlan|port-channel:0:Port-channel|Eth:0:Eth", svalue="",
                         mapval="", mandatory="1", group_member="1")
    id = Textbox(validation_criteria='', hidden='', isbasic='True', helptext='Provide the required id',
                 dt_type="string", static="False", api="", name="id", label="ID",
                 static_values="", svalue="115", mapval="", mandatory="", group_member="1")
    desc = Textbox(validation_criteria='', hidden='Description to be added to the interface', isbasic='True',
                   helptext='', dt_type="string", static="False", api="", name="desc", label="Description",
                   static_values="", svalue="In-Band NTP Redistribution Interface VLAN 115",
                   mapval="", mandatory="", group_member="1")
    port_set = Group(validation_criteria='function', hidden='', isbasic='True',
                     helptext='Provide interface type, id and description', dt_type="string", static="False", api="",
                     name="port_set", label="Add Individual Port Description", static_values="",
                     svalue="{'interface': {'ismapped': '0', 'value': 'Vlan'}, 'id': {'ismapped': '0', 'value': '115'}, 'desc': {'ismapped': '0', 'value': 'In-Band NTP Redistribution Interface VLAN 115'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '11'}, 'desc': {'ismapped': '0', 'value': 'vPC peer-link'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '151'}, 'desc': {'ismapped': '0', 'value': 'vPC UCS 6332-16UP-1 FI'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '152'}, 'desc': {'ismapped': '0', 'value': 'vPC UCS 6332-16UP-2 FI'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '153'}, 'desc': {'ismapped': '0', 'value': 'vPC Upstream Network Switch A'}}|{'interface': {'ismapped': '0', 'value': 'port-channel'}, 'id': {'ismapped': '0', 'value': '154'}, 'desc': {'ismapped': '0', 'value': 'vPC Upstream Network Switch B'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/1'}, 'desc': {'ismapped': '0', 'value': 'vPC peer-link connection to b19-93180-2'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/2'}, 'desc': {'ismapped': '0', 'value': 'vPC peer-link connection to b19-93180-2'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/51'}, 'desc': {'ismapped': '0', 'value': 'vPC 151 connection to UCS 6332-16UP-1 FI'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/52'}, 'desc': {'ismapped': '0', 'value': 'vPC 152 connection to UCS 6332-16UP-2 FI'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/53'}, 'desc': {'ismapped': '0', 'value': ' vPC 153 connection to Upstream Network Switch A'}}|{'interface': {'ismapped': '0', 'value': 'Eth'}, 'id': {'ismapped': '0', 'value': '1/54'}, 'desc': {'ismapped': '0', 'value': ' vPC 153 connection to Upstream Network Switch B'}}",
                     mapval="", mandatory="1", members=["interface", "id", "desc"], add="True", order=2)


class NEXUS9kAddIndividualPortDescriptionOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    port_set = Output(dt_type="string", name="port_set", tvalue="")
