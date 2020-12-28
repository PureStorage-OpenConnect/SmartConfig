from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateLinkProfile",
    task_name="Create Link Profile",
    task_desc="Create Link Profile in UCS",
    task_type="UCSM"
)


class UCSCreateLinkProfile:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Link Profile")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateLinkProfile(
            taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Delete Link Profile rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteLinkProfile(
            inputs, logfile)

        obj.release_ucs_handle()
        return res


    def getudldpolicies(self, keys):
        udld_pol_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid is None:
            res.setResult(ports_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()

        udld_policies = handle.query_classid("fabricUdldLinkPolicy")
        for udld_pol in udld_policies:
            udld_pol_list.append(
                {"id" : udld_pol.name,"selected" : "0", "label" : udld_pol.name})
        udld_pol_list.append(
            {"id": "not-set", "selected": "0", "label": "not-set"})
        ucsm_logout(handle)
        res.setResult(udld_pol_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateLinkProfileInputs:
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
        helptext='',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="name",
        static="False",
        svalue="Link-Profile",
        mandatory='1',
        static_values="",
        order=2)
    udld_pol = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='UDLD Link Policy Name',
        dt_type="string",
        static="False",
        static_values="",
        api="getudldpolicies()|[fabric_id:1:fabric_id.value]",
        name="udld_pol",
        label="UDLD Link Policy",
        svalue="__t201.UCSCreateUDLDLinkPolicy.name",
        mandatory='1',
        mapval="1",
        order=3)
        




class UCSCreateLinkProfileOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="name", tvalue="Link-Profile")
