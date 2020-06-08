from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateServerBIOSPolicy",
    task_name="Create Server BIOS Policy",
    task_desc="Create Server BIOS Policy",
    task_type="UCSM"
)


class UCSCreateServerBIOSPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Server BIOS Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateServerBIOSPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Server BIOS Policy")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteServerBIOSPolicy(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateServerBIOSPolicyInputs:
    fabric_id = Dropdown(
        hidden='True',
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
    name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Server BIOS Policy',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="VM-Host",
        mandatory='1',
        static_values="",
        order=2)
    descr = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="descr",
        static="False",
        svalue="Server BIOS Policy",
        mandatory='1',
        static_values="",
        order=3)
    reboot = Checkbox(
        hidden='False',
        isbasic='True',
        helptext='Reboot on BIOS setting change',
        api="",
        dt_type="string",
        label="Reboot on BIOS settings change",
        mapval="0",
        name="reboot",
        static="True",
        static_values="yes@no:0:Reboot",
        svalue="",
        mandatory='1',
        allow_multiple_values="0",
        order=4)
    boot = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Quiet Boot',
        api="",
        dt_type="string",
        label="Quiet Boot",
        mapval="0",
        name="boot",
        static="True",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="disabled",
        mandatory='1',
        order=5)
    device_naming = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Consistent device naming',
        api="",
        dt_type="string",
        label="CDN Control",
        mapval="0",
        name="device_naming",
        static="True",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        order=6)
    dram_clock = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='DRAM Clock',
        dt_type="string",
        static="True",
        api="",
        name="dram_clock",
        label="DRAM Clock Throttling",
        static_values="auto:0:auto|balanced:0:balanced|performance:0:performance|energy-efficient:0:energy-efficient|platform-default:1:Platform Default",
        svalue="performance",
        mapval="",
        mandatory='1',
        order=7)
    freq_floor = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Frequency floor override',
        dt_type="string",
        static="True",
        api="",
        name="freq_floor",
        label="Frequency Floor Override",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=8)
    proc_c_state = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Processor C State',
        dt_type="string",
        static="True",
        api="",
        name="proc_c_state",
        label="Processor C State",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="disabled",
        mandatory='1',
        mapval="",
        order=9)
    proc_c1e = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Processor C1E',
        dt_type="string",
        static="True",
        api="",
        name="proc_c1e",
        label="Processor C1E",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="disabled",
        mandatory='1',
        mapval="",
        order=10)
    proc_c3_report = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Processor C3 Report',
        dt_type="string",
        static="True",
        api="",
        name="proc_c3_report",
        label="Processor C3 Report",
        static_values="disabled:0:disabled|enabled:0:enabled|acpi-c2:0:acpi-c2|acpi-c3:0:acpi-c3|platform-default:1:Platform Default",
        svalue="disabled",
        mapval="",
        mandatory='1',
        order=11)
    proc_c7_report = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Processor C7 report',
        dt_type="string",
        static="True",
        api="",
        name="proc_c7_report",
        label="Processor C7 Report",
        static_values="disabled:0:disabled|enabled:0:enabled|c7:0:c7|c7s:0:c7s|platform-default:1:Platform Default",
        svalue="disabled",
        mapval="",
        mandatory='1',
        order=12)
    energy_perf = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Energy performance',
        dt_type="string",
        static="True",
        api="",
        name="energy_perf",
        label="Energy Performance",
        static_values="performance:0:performance|balanced-performance:0:balanced-performance|balanced-energy:0:balanced-energy|energe-efficient:0:energy-efficient|platform-default:1:Platform Default",
        svalue="performance",
        mapval="",
        mandatory='1',
        order=13)
    lv_ddr_mode = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='LV DDR Mode',
        dt_type="string",
        static="True",
        api="",
        name="lv_ddr_mode",
        label="LV DDR Mode",
        static_values="power-saving-mode:0:power-saving-mode|performance-mode:0:performance-mode|auto:0:auto|platform-default:0:Platform Default",
        svalue="performance-mode",
        mandatory='1',
        mapval="",
        order=14)
    intel_turbo = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Intel turbo technology',
        dt_type="string",
        static="True",
        api="",
        name="intel_turbo",
        label="Intel Turbo Technology",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=15)
    intel_speedstep = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Intel SpeedStep',
        dt_type="string",
        static="True",
        api="",
        name="intel_speedstep",
        label="Intel SpeedStep Technology",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=16)
    hyper_threading = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Intel hyper threading',
        dt_type="string",
        static="True",
        api="",
        name="hyper_threading",
        label="Intel Hyper-Threading Technology",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=17)
    intel_vt = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Intel Virtualization technology',
        dt_type="string",
        static="True",
        api="",
        name="intel_vt",
        label="Intel Virtualization Technology",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=18)
    intel_vtd = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Intel VT For Directed IO',
        dt_type="string",
        static="True",
        api="",
        name="intel_vtd",
        label="Intel VT for Directed I/O",
        static_values="disabled:0:Disabled|enabled:0:Enabled|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=19)
    cpu_perf = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='CPU Performance',
        dt_type="string",
        static="True",
        api="",
        name="cpu_perf",
        label="CPU Performance",
        static_values="enterprise:0:enterprise|high-throughput:0:high-throughput|hpc:0:hpc|custom:0:custom|platform-default:1:Platform Default",
        svalue="enterprise",
        mapval="",
        mandatory='1',
        order=20)
    direct_cache_access = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Direct cache access',
        dt_type="string",
        static="True",
        api="",
        name="direct_cache_access",
        label="Direct Cache Access",
        static_values="disabled:0:Disabled|enabled:0:Enabled|auto:0:auto|platform-default:0:Platform Default",
        svalue="enabled",
        mandatory='1',
        mapval="",
        order=21)
    power_tech = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Power technology',
        dt_type="string",
        static="True",
        api="",
        name="power_tech",
        label="Power Technology",
        static_values="disabled:0:Disabled|energe-efficient:0:energy-efficient|performance:0:performance|custom:0:custom|platform-default:1:Platform Default",
        svalue="performance",
        mapval="",
        mandatory='1',
        order=22)
    memory_ras = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Memory RAS Configuration',
        dt_type="string",
        static="True",
        api="",
        name="memory_ras",
        label="Memory RAS Configuration",
        static_values="maximum-performance:0:maximum-performance|mirroring:0:mirroring|lockstep:0:lockstep|sparing:0:sparing|platform-default:1:Platform Default",
        svalue="maximum-performance",
        mapval="",
        mandatory='1',
        order=23)


class UCSCreateServerBIOSPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
