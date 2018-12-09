from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreatevHBA",
    task_name="Create vHBA in UCS",
    task_desc="Create vHBA from vHBA template in UCS",
    task_type="UCSM"
)


class UCSCreatevHBA:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_vHBA")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatevHBA(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS vHBA rollback")

        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeletevHBA(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getsanconnectivity(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        san_list = handle.query_classid("vnicSanConnPolicy")
        selected = "1"
        for san in san_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": san.name, "selected": selected, "label": san.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getvhbatemplate(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret
        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        ucs_fabricid = getArg(keys, 'ucs_fabric_id')
        if ucs_fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret
        handle = res.getResult()
        san_conn_list = handle.query_classid("vnicSanConnTempl")
        selected = "1"
        for san_conn in san_conn_list:
            if temp_list:
                selected = "0"
            if ucs_fabricid == san_conn.switch_id:
                temp_list.append(
                    {"id": san_conn.name, "selected": selected, "label": san_conn.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res


class UCSCreatevHBAInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', api="getfilist()", dt_type="string", label="UCS Fabric Name", mandatory="1",
                         mapval="0", name="fabric_id", static="False", svalue="", static_values="None", order=1)
    vhba_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='vhba name', dt_type="string", api="", static="False", static_values="None",
                        name="vhba_name", label="Name", svalue="", mandatory='1', mapval="0", order=2, recommended="1")
    ucs_fabric_id = Radiobutton(hidden='False', isbasic='True', helptext='Primary Or Secondary FI', dt_type="string", api="", static="True", static_values="A:0:Fabric Interconnect A(primary)|B:1:Fabric Interconnect B(subordinate)",
                                name="ucs_fabric_id", label="Fabric ID", svalue="", mandatory='1', mapval="0", order=3)
    vhba_template = Dropdown(hidden='False', isbasic='True', helptext='vHBA template name', dt_type="string", api="getvhbatemplate()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
                             static="False", static_values="None", mapval="1", name="vhba_template", label="vHBA Template", svalue="", mandatory='1', order=4)
    vsan_con_policy = Dropdown(hidden='False', isbasic='True', helptext='VSAN Connectivity Policy', dt_type="string", name="vsan_con_policy", static="False",
                               api="getsanconnectivity()|[fabric_id:1:fabric_id.value]", static_values="None", mapval="1", label="vSAN Connectivity Policy Name", svalue="", mandatory='1', order=5)


class UCSCreatevHBAOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vhba_name = Output(dt_type="string", name="vhba_name", tvalue="Fabric-B")
