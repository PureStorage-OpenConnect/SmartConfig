from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSChassisDiscoveryPolicy",
    task_name="Configure Chassis Discovery policy",
    task_desc="Configure Chassis discovery policy in UCS",
    task_type="UCSM"
)


class UCSChassisDiscoveryPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Chassis discovery policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsChassisDiscoveryPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Chassis discovery policy rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSChassisDiscoveryPolicyInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        static_values="",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        mandatory="1",
        order=1)
    fex_action = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Fex Action',
        api="",
        dt_type="string",
        label="Fex Action",
        mapval="0",
        name="fex_action",
        static="True",
        mandatory='1',
        static_values="1-link:0:1 Link|2-link:1:2 Link|4-link:0:4 Link|8-link:0:8 Link|platform-max:0:Platform Max",
        svalue="2-link",
        order=2)
    agg_pref = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Link Grouping Preference',
        api="",
        dt_type="string",
        label="Link Grouping Preference",
        mapval="0",
        name="agg_pref",
        static="True",
        mandatory='1',
        static_values="none:1:None|port-channel:0:Port Channel",
        svalue="port-channel",
        order=3)
    speed_pref = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Backplane speed preference',
        api="",
        dt_type="string",
        label="Backplane Speed Preference",
        mapval="0",
        name="speed_pref",
        static="True",
        mandatory='1',
        static_values="40G:0:40G|4x10G:1:4x10G",
        svalue="40G",
        order=4)
    rack_action = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='rack server discovery policy',
        api="",
        dt_type="string",
        label="Rack Server Discovery Policy",
        mapval="0",
        name="rack_action",
        static="True",
        mandatory='1',
        static_values="immediate:1:Immediate|user-acknowledged:0:User Acknowledged",
        svalue="immediate",
        order=5)
    scrub = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='scrub policy',
        api="",
        dt_type="string",
        label="Scrub Policy",
        mapval="0",
        name="scrub",
        static="True",
        mandatory='1',
        static_values="not-set:0:not-set|default:1:default",
        svalue="default",
        order=6)
    mgmt_action = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='rack mgmt connection policy',
        api="",
        dt_type="string",
        label="Rack Management Connection Policy",
        mapval="0",
        name="mgmt_action",
        mandatory='1',
        static="True",
        static_values="auto-acknowledged:0:Auto Acknowledged|user-acknowledged:1:User Acknowledged",
        svalue="auto-acknowledged",
        order=7)
    redundancy = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='power policy',
        api="",
        dt_type="string",
        label="Power policy",
        mapval="0",
        name="redundancy",
        mandatory='1',
        static="True",
        static_values="non-redundant:1:Non Redundant|n+1:0:N+1|grid:0:Grid",
        svalue="n+1",
        order=8)
    mac_aging = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='mac table aging',
        api="",
        dt_type="string",
        label="MAC table Aging",
        mapval="0",
        name="mac_aging",
        static="True",
        mandatory='1',
        static_values="never:1:Never|mode-default:0:Mode Default|other:0:Other",
        svalue="mode-default",
        order=9)
    style = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='global power allocation policy',
        api="",
        dt_type="string",
        label="Global Power Allocation policy",
        mapval="0",
        name="style",
        static="True",
        mandatory='1',
        static_values="manual-per-blade:0:Manual Per Blade Level Cap|intelligent-policy-driven:1:Policy Driven Chassis Group Cap",
        svalue="intelligent-policy-driven",
        order=10)
    sync_state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Firmware Auto sync policy",
        mapval="0",
        name="sync_state",
        static="True",
        mandatory='1',
        static_values="No Actions:0:No Actions|User Acknowledge:1:UserAcknowledge",
        svalue="No Actions",
        order=11)
    profiling = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Global power profiling policy",
        mapval="0",
        name="profiling",
        static="True",
        mandatory='1',
        allow_multiple_values="0",
        static_values="yes@no:0:Profile Power",
        svalue="",
        order=12)
    info_enable = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Info policy",
        mapval="0",
        name="info_enable",
        mandatory='1',
        static="True",
        static_values="enabled:0:Enabled|disabled:1:Disabled",
        svalue="disabled",
        order=13)


class UCSChassisDiscoveryPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
