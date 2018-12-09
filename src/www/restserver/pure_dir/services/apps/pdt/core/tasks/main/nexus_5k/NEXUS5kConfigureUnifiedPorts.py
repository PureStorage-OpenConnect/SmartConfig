from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.components.network.nexus.nexus_tasks import *
from pure_dir.components.common import *
from pure_dir.services.utils.miscellaneous import *

static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'

metadata = dict(
        task_id="NEXUS5kConfigureUnifiedPorts",
        task_name="Add NTP Distribution Interface",
        task_desc="Add NTP Distribution Interface for Nexus switch",
        task_type="NEXUS"
)


class NEXUS5kConfigureUnifiedPorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("NEXUS Configure Unified ports")
        cred = get_device_credentials(
                key="mac", value=taskinfo['inputs']['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                    ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusConfigureUnifiedPorts(taskinfo['inputs'],
                                                     logfile, cred['ipaddress'], cred['username'], cred['password'])
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
        loginfo("NEXUS Configure Unified ports rollback")
        cred = get_device_credentials(
                key="mac", value=inputs['nexus_id'])
        if cred:
            obj = NEXUSTasks(
                    ipaddress=cred['ipaddress'], username=cred['username'], password=cred['password'])
            if obj:
                res = obj.nexusUnconfigureUnifiedPorts(inputs,
                                                       logfile, cred['ipaddress'], cred['username'], cred['password'])
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

    def get_slot_list(self, keys):
        res = result()
        slot_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "nexus_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(slot_list, PTK_OKAY, "success")
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                slot_list = obj.get_slot_list()
            else:
                loginfo("Unable to login to the Nexus")
                res.setResult(slot_list, PTK_INTERNALERROR,
                              "Unable to login to the Nexus")
        else:
            loginfo("Unable to get the device credentials of the Nexus")
            res.setResult(slot_list, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the Nexus")

        res.setResult(slot_list, PTK_OKAY, "success")
        return res

    def get_interfaces_in_slot(self, keys):
        res = result()
        intf_list = []

        nexus_id = getArg(keys, 'nexus_id')
        if nexus_id == None:
            res.setResult(intf_list, PTK_OKAY, "success")
            return res

        slot = getArg(keys, 'slot')
        if slot == None:
            res.setResult(intf_list, PTK_OKAY, "success")
            return res

        cred = get_device_credentials(key="mac", value=nexus_id)
        if cred:
            obj = Nexus(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                intf_list = obj.get_interfaces_in_slot(slot)
            else:
                loginfo("Unable to login to the Nexus")
                res.setResult(intf_list, PTK_INTERNALERROR,
                              "Unable to login to the Nexus")
        else:
            loginfo("Unable to get the device credentials of the Nexus")
            res.setResult(intf_list, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the Nexus")

        res.setResult(intf_list, PTK_OKAY, "success")
        return res


class NEXUS5kConfigureUnifiedPortsInputs:
    nexus_id = Dropdown(hidden='True', isbasic='', helptext='', dt_type="string", static="False", static_values="",
                        api="getnexuslist()",
                        name="nexus_id", label="Nexus switch", svalue="", mapval="", mandatory="1", order=1)
    slot = Dropdown(hidden='', isbasic='True', helptext='Slot', dt_type="string",
                    static="False", api="get_slot_list()|[nexus_id:1:nexus_id.value]", name="slot", label="Slot",
                    static_values="", svalue="", mapval="", mandatory="1", order=2, recommended="1")
    ports = Rangepicker(hidden='', isbasic='True', helptext='Enter the respective ports', dt_type="string",
                        static="False", api="get_interfaces_in_slot()|[nexus_id:1:nexus_id.value|slot:1:slot.value]",
                        name="ports", label="Ports",
                        static_values="", svalue="", mapval="", mandatory="1", order=3, recommended="1", min_range=0,
                        max_range=0, max_fixed=True, min_interval=8)
    port_type = Dropdown(hidden='', isbasic='True', helptext='Port type', dt_type="string", static="True", api="",
                         name="port_type", label="Type",
                         static_values="fc:1:FC|Eth:0:Eth", svalue="", mapval="", mandatory="1", order=4,
                         recommended="1")


class NEXUS5kConfigureUnifiedPortsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    slot = Output(dt_type="string", name="slot", tvalue="1")
    ports = Output(dt_type="string", name="ports", tvalue="1-32")
    port_type = Output(dt_type="string", name="port_type", tvalue="fc")
