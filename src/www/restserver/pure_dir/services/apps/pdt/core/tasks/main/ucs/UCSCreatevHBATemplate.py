from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreatevHBATemplate",
    task_name="Create vHBA template in UCS",
    task_desc="Create vHBA template in UCS",
    task_type="UCSM"
)


class UCSCreatevHBATemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_vHBA Template")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreatevHBATemplate(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS rollback _vHBA Template")

        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsDeletevHBATemplate(inputs, logfile)

        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        print(ucs_list, res)
        return res

    def getvhbatemplate(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        ucs_fabricid = getArg(keys, 'ucs_fabric_id')
        if ucs_fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
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
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getvsan(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        ucs_fabricid = getArg(keys, 'ucs_fabric_id')
        if ucs_fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        handle = res.getResult()
        res = result()
        vsan_list = handle.query_classid("fabricVsan")
        selected = "1"
        for vsan in vsan_list:
            if temp_list:
                selected = "0"
            if vsan.switch_id == ucs_fabricid:
                temp_list.append(
                    {"id": vsan.name, "selected": selected, "label": vsan.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getwwpn(self, keys):
        temp_list = []
        ret = result()
        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret
        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        s = handle.query_classid("fcpoolInitiators")
        selected = "1"
        for w in s:
            if temp_list:
                selected = "0"
            if w.purpose == "port-wwn-assignment":
                temp_list.append(
                    {"id": w.name, "selected": selected, "label": w.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreatevHBATemplateInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        api="getfilist()",
        dt_type="string",
        label="UC Fabric Name",
        mandatory="1",
        mapval="0",
        name="fabric_id",
        static="False",
        svalue="",
        static_values="None",
        order=1)
    vhba_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='vHBA Name',
        dt_type="string",
        static="False",
        static_values="None",
        api="",
        name="vhba_name",
        label="Name",
        svalue="",
        mandatory='1',
        mapval="0",
        order=2)
    vhba_description = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        static_values="None",
        api="",
        name="vhba_description",
        label="Description",
        svalue="",
        mandatory='1',
        mapval="0",
        order=3)
    ident_pool_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        static_values="None",
        api="getwwpn()|[fabric_id:1:fabric_id.value]",
        mapval="1",
        name="ident_pool_name",
        label="WWPN Pool ",
        svalue="",
        mandatory='1',
        order=4)
    ucs_fabric_id = Radiobutton(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="True",
        static_values="A:1:Fabric Interconnect A(primary)|B:0:Fabric Interconnect B(subordinate)",
        api="",
        name="ucs_fabric_id",
        label="Fabric ID",
        svalue="",
        mandatory='1',
        mapval="0",
        order=5)
    redundancy_type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="",
        static="True",
        static_values="none:1:No Redundancy|pimary:0:Primary Template|secondary:0:Secondary Template",
        name="redundancy_type",
        label="Redundancy Type",
        svalue="",
        mandatory='1',
        mapval="0",
        order=6)
    max_data_field_size = Textbox(
        validation_criteria='int|min:256|max:2048',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="integer",
        api="",
        static="False",
        static_values="None",
        name="max_data_field_size",
        label="Max Data Field Size",
        svalue="",
        mandatory='1',
        mapval="0",
        order=7)
    template_type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="",
        static="True",
        static_values="initial-template:1:Initial Template|updating-template:0:Updating Template",
        label="Template Type",
        name="template_type",
        svalue="",
        mandatory='1',
        mapval="0",
        order=8)
    vsan_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getvsan()|[fabric_id:1:fabric_id.value|ucs_fabric_id:1:ucs_fabric_id.value]",
        mapval="1",
        name="vsan_name",
        static_values="None",
        label="Select VSAN",
        svalue="",
        mandatory='1',
        order=9)


class UCSCreatevHBATemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vhba_name = Output(dt_type="string", name="vhba_name",
                       tvalue="vHBA_template_A")
