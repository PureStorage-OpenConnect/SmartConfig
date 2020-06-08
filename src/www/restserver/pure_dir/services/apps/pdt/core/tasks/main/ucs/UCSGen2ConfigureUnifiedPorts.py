from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
import os
import json
from pure_dir.global_config import get_discovery_store

metadata = dict(
    task_id="UCSGen2ConfigureUnifiedPorts",
    task_name="Configure Unified Ports for Gen2 FI",
    task_desc="Configure Unified Ports in UCS for Gen2 FI",
    task_type="UCSM"
)


class UCSGen2ConfigureUnifiedPorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Configure_Unified_ports")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        #res = obj.get_ucs_handle()
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsConfigureUnifiedPorts(taskinfo['inputs'], logfile)

        # obj.release_ucs_handle(handle) commenting because of handle not
        # available due to reboot after ports configure
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UnConfigure_Unified_ports")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsUnConfigureUnifiedPorts(inputs, logfile)

        return res

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_all_ucs_list(self, keys):
        res = result()
        info_list = []
        if os.path.exists(get_discovery_store()) is True:
            doc = parse_xml(get_discovery_store())
            for subelement in doc.getElementsByTagName("device"):
                if subelement.getAttribute("device_type") == "UCSM":
                    details = {}
                    details['label'] = subelement.getAttribute("name")
                    details['id'] = subelement.getAttribute("mac")
                    details['selected'] = "0"
                    info_list.append(details)
        res.setResult(info_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_ucs_ports(self, keys):
        """
        Gets the list of interfaces

        :return: Returns the list of interfaces
        """
        res = result()
        intf_list = []
        details = {}
        slot_info = {"min_range": str(1), "max_range": str(
            32), "min_fixed": False, "max_fixed": True, "min_interval": "2"}
        details['label'] = ""
        details['id'] = ""
        details['selected'] = str(17) + "-" + str(32)
        details['extrafields'] = json.dumps(slot_info)
        intf_list.append(details)
        res.setResult(intf_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSGen2ConfigureUnifiedPortsInputs:
    fabric_id = Dropdown(
        hidden='',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        static_values="",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)
    ucs_fabric_id = Radiobutton(
        hidden='',
        isbasic='True',
        helptext='Primary or Subordinate FI',
        dt_type="string",
        static="True",
        api="",
        name="ucs_fabric_id",
        label="Fabric ID",
        static_values="A:1:Fabric Interconnect A(primary)|B:0:Fabric Interconnect B(subordinate)",
        svalue="",
        mapval="",
        mandatory="1",
        order=2)
    no_of_ports = Rangepicker(
        hidden='',
        isbasic='True',
        helptext='Enter the respective ports',
        dt_type="string",
        static="False",
        api="get_ucs_ports()",
        name="no_of_ports",
        label="FC Ports",
        static_values="",
        svalue="",
        mapval="",
        mandatory="1",
        order=3,
        recommended="1",
        min_range=0,
        max_range=0,
        max_fixed=True,
        min_interval=2)


class UCSGen2ConfigureUnifiedPortsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    fabric_id = Output(dt_type="string", name="fabric_id", tvalue="A")
    no_of_ports = Output(dt_type="integer", name="no_of_ports", tvalue="6")
