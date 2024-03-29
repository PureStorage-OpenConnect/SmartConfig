from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateServiceProfileTemplateFB",
    task_name="Create Service Profile Template For FlashBlade",
    task_desc="Create Service Profile Template For FlashBlade",
    task_type="UCSM"
)


class UCSCreateServiceProfileTemplateFB:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_service_profile_for_fb")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateServiceProfileTemplateForiSCSI(
            taskinfo['inputs'], fp, flashBlade=True)
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("create service profile for FlashBlade rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteServiceProfileTemplate(
            inputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getuuidpool(self, keys):
        loginfo("get uuid pool")
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
        uuid_list = handle.query_classid("uuidpoolPool")
        selected = "1"
        for uuid in uuid_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": uuid.name, "selected": selected, "label": uuid.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getlanconnectivity(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        lan_list = handle.query_classid("vnicLanConnPolicy")
        selected = "1"
        for lan in lan_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": lan.name, "selected": selected, "label": lan.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getpowerpolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()

        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        pp_list = handle.query_classid("powerPolicy")
        selected = "1"
        for pp in pp_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": pp.name, "selected": selected, "label": pp.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getlocaldiskpolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        storage_list = handle.query_classid("storageLocalDiskConfigPolicy")
        selected = "1"
        for storage in storage_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": storage.name, "selected": selected, "label": storage.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getbootpolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        boot_list = handle.query_classid("lsbootPolicy")
        selected = "1"
        for boot in boot_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": boot.name, "selected": selected, "label": boot.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getpoolassignment(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        pool_list = handle.query_classid("computePool")
        selected = "1"
        for pool in pool_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": pool.name, "selected": selected, "label": pool.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getbiospolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        bios_list = handle.query_classid("biosVProfile")
        selected = "1"
        for bios in bios_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": bios.name, "selected": selected, "label": bios.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getiqnpool(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        iqn_list = handle.query_classid("iqnpoolPool")
        selected = "1"
        for iqn in iqn_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": iqn.name, "selected": selected, "label": iqn.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getmaintenancepolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid is None:
            ret.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        maintenance_list = handle.query_classid("lsmaintMaintPolicy")
        selected = "1"
        for maintenance in maintenance_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": maintenance.name, "selected": selected, "label": maintenance.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSCreateServiceProfileTemplateFBInputs:
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
    template_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="template_name",
        label="Template Name",
        svalue="BM-Storage-Fabric-A",
        mandatory='1',
        mapval="0",
        order=2,
        recommended="1")
    template_desc = Textbox(
        validation_criteria='',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="template_desc",
        label="template description",
        svalue="Service Profile template",
        mandatory='1',
        mapval="0",
        order=3)
    type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="",
        static="True",
        static_values="initial-template:0:Initial Template|updating-template:1:Updating Template",
        label="Type",
        name="type",
        svalue="updating-template",
        mandatory='1',
        mapval="0",
        order=4)
    ident_pool_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="getuuidpool()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="ident_pool_name",
        label="Pool name",
        svalue="UUID_Pool",
        mandatory='1',
        mapval="0",
        order=5)
    local_disk_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="getlocaldiskpolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="local_disk_policy_name",
        label="Local Disk Policy",
        svalue="Disk-Raid1",
        mandatory='1',
        mapval="0",
        order=6)
    lan_conn_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='LAN Connectivity policy',
        dt_type="string",
        api="getlanconnectivity()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="lan_conn_policy_name",
        label="LAN Connectivity policy",
        svalue="Disk-Raid1",
        mandatory='1',
        mapval="0",
        order=7)
    boot_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Boot policy',
        dt_type="string",
        api="getbootpolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="boot_policy_name",
        label="Boot Policy",
        svalue="Local-Boot",
        mapval="0",
        mandatory='1',
        order=8)
    pool_assignment = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Pool Assignment',
        dt_type="string",
        api="getpoolassignment()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        mapval="1",
        name="pool_assignment",
        label="Pool Assignment",
        svalue="__t200.CreateServerPool.name",
        mandatory='1',
        order=9)
    power_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Power control policy',
        dt_type="string",
        api="getpowerpolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="power_policy_name",
        label="Power Policy",
        svalue="No-Power-Cap",
        mandatory='1',
        mapval="",
        order=10)
    biospolicy = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Server BIOS policy',
        dt_type="string",
        api="getbiospolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="biospolicy",
        label="BIOS Policy",
        svalue="AI-ML-Hosts",
        mandatory='1',
        mapval="0",
        order=11)


class UCSCreateServiceProfileTemplateFBOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    template_name = Output(
        dt_type="string", name="template_name", tvalue="BM-Storage-Fabric-A")
