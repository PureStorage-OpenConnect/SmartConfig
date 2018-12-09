from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.common import *

metadata = dict(
        task_id="NEXUS5kCreateVLAN",
        task_name="Create VLAN",
        task_desc="Create VLAN in the Nexus switch",
        task_type="NEXUS"
)


class NEXUS5kCreateVLAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Create VLAN")
        cred = get_device_credentials(
                key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                    ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusCreateVLAN(taskinfo['inputs'], logfile)
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
        loginfo("NEXUS Create VLAN rollback")
        cred = get_device_credentials(
                key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                    ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusDeleteVLAN(inputs, logfile)
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
        nexus_list = get_device_list(device_type="Nexus 5k")
        res.setResult(nexus_list, PTK_OKAY, "success")
        return res


class NEXUS5kCreateVLANInputs:
    nexus_id = Dropdown(hidden='True', isbasic='', helptext='', dt_type="string", static="False", static_values="",
                        api="getnexuslist()",
                        name="nexus_id", label="Nexus switch", svalue="", mapval="", mandatory="1", order=1)
    vlan_id = Textbox(validation_criteria='int|min:1|max:3967', hidden='', isbasic='True', helptext='Virtual LAN id',
                      dt_type="string", static="False", api="", name="vlan_id", static_values="",
                      label="VLAN id", svalue="115", mapval="", mandatory="1", group_member="1", recommended="1")
    vlan_name = Textbox(validation_criteria='str|min:1|max:128', hidden='', isbasic='True', helptext='Virtual LAN name',
                        dt_type="string", static="False", api="", name="vlan_name", static_values="",
                        label="VLAN name", svalue="IB-MGMT-VLAN", mapval="", mandatory="1", group_member="1",
                        recommended="1")
    vlan_set = Group(validation_criteria='', hidden='', isbasic='True', helptext='Enter VLAN id and VLAN name',
                     dt_type="string", static="False", api="", name="vlan_set", label="Create VLAN", static_values="",
                     svalue="{'vlan_id': {'ismapped': '0', 'value': '115'}, 'vlan_name': {'ismapped': '0', 'value': 'IB-MGMT-VLAN'}}|{'vlan_id': {'ismapped': '0', 'value': '2'}, 'vlan_name': {'ismapped': '0', 'value': 'Native-VLAN'}}|{'vlan_id': {'ismapped':'0', 'value': '200'}, 'vlan_name': {'ismapped': '0', 'value': 'vMotion-VLAN'}}|{'vlan_id': {'ismapped': '0', 'value': '201'}, 'vlan_name': {'ismapped': '0', 'value': 'VM-App1-VLAN'}}|{'vlan_id': {'ismapped': '0', 'value': '202'}, 'vlan_name': {'ismapped': '0', 'value': 'VM-App2-VLAN'}}|{'vlan_id': {'ismapped': '0', 'value': '203'}, 'vlan_name': {'ismapped': '0', 'value': 'VM-App3-VLAN'}}",
                     mapval="", mandatory="1", members=["vlan_id", "vlan_name"], add="True", order=2, recommended="1")


class NEXUS5kCreateVLANOutputs:
    vlan_set = Output(dt_type="integer", name="vlan_set", tvalue="")
    status = Output(dt_type="string", name="status", tvalue="SUCCESS")
