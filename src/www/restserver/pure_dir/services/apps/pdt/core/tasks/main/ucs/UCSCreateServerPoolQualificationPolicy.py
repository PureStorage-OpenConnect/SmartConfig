from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateServerPoolQualificationPolicy",
    task_name="Create Server pool qualification policy",
    task_desc="Create Server pool qualification policy in UCS",
    task_type="UCSM"
)


class UCSCreateServerPoolQualificationPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create_Server_Pool_Qualification_Policy")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateServerPoolQualificationPolicy(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        print "Create Server Pool Qualification Policy rollback"
        return 0

    def getprocessorarch(self, keys):
        res = result()
        val = [
            {
                "id": "Opteron", "selected": "0", "label": "Opteron"}, {
                "id": "Turion_64", "selected": "0", "label": "Turion 64"}, {
                "id": "Dual-Core_Opteron", "selected": "0", "label": "Dual Core Opteron"}, {
                    "id": "Pentium_4", "selected": "0", "label": "Pentium 4"}, {
                        "id": "Xeon", "selected": "1", "label": "Xeon"}, {
                            "id": "Xeon_MP", "selected": "0", "label": "Xeon MP"}, {
                                "id": "any", "selected": "0", "label": "Any"}, {
                                    "id": "Intel_P4_C", "selected": "0", "label": "Intel P4 C"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res


class UCSCreateServerPoolQualificationPolicyInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", svalue="", mapval="", mandatory="1", static_values="", order=1)
    name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="Name", mapval="0", name="name",
                   static_values="", mandatory='1', static="False", svalue="UCS-Broadwell", order=2)
    descr = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="Description", mapval="0", name="descr",
                    static_values="", mandatory='1', static="False", svalue="server pool qual", order=3)
    arch = Dropdown(hidden='False', isbasic='True', helptext='Processor Architecture', api="getprocessorarch()", dt_type="string", label="Processor Architecture",
                    static_values="", mandatory='1', mapval="0", name="arch", static="False", svalue="Xeon", order=4)
    pid = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='', api="", dt_type="string", label="PID Regex", mapval="0", name="pid",
                  static="False", static_values="", mandatory='1', svalue="UCS-CPU-E52660E", order=5)
    min_cores = Radiobutton(hidden='False', isbasic='True', helptext='Min number of cores', api="", dt_type="string", label="Min number of cores", mapval="0", name="min_cores", static="True",
                            mandatory='1', static_values="unspecified:1:Unspecified|select:0:select", svalue="unspecified", order=6)
    max_cores = Radiobutton(hidden='False', isbasic='True', helptext='Max number of cores', api="", dt_type="string", label="Max number of cores", mapval="0", name="max_cores", static="True",
                            mandatory='1', static_values="unspecified:1:Unspecified|select:0:select", svalue="unspecified", order=7)
    min_threads = Radiobutton(hidden='False', isbasic='True', helptext='Min number of threads', api="", dt_type="string", label="Min number of threads", mapval="0", name="min_threads",
                              mandatory='1', static="True", static_values="unspecified:1:Unspecified|select:0:select", svalue="unspecified", order=8)
    max_threads = Radiobutton(hidden='False', isbasic='True', helptext='Max number of threads', api="", dt_type="string", label="Max number of threads", mapval="0", name="max_threads",
                              mandatory='1', static="True", static_values="unspecified:1:Unspecified|select:0:select", svalue="unspecified", order=9)
    speed = Radiobutton(hidden='False', isbasic='True', helptext='CPU Speed', api="", dt_type="string", label="CPU Speed", mapval="0", name="speed", mandatory='1',
                        static="True", static_values="unspecified:1:Unspecified|select:0:select", svalue="unspecified", order=10)
    stepping = Radiobutton(hidden='False', isbasic='True', helptext='Stepping', api="", dt_type="string", label="CPU Stepping", mapval="0", name="stepping", static="True",
                           mandatory='1', static_values="unspecified:1:Unspecified|select:1:select", svalue="unspecified", order=11)


class UCSCreateServerPoolQualificationPolicyOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="UCS-Broadwell")
