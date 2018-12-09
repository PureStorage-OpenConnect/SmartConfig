from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCloneServiceProfileTemplate",
    task_name="Clone Service Profile template",
    task_desc="Clone Service Profile Template in UCS",
    task_type="UCSM"
)


class UCSCloneServiceProfileTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("clone_service_profile_template")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCloneServiceProfileTemplate(
            taskinfo['inputs'], fp)
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("clone service profile  template rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteClonedServiceProfileTemplate(
            inputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        print ucs_list, res
        return res

    def gettemplate(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret

        res = get_ucs_login(fabricid)

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        s = handle.query_classid("lsServer")
        selected = "1"
        for w in s:
            if w.type == 'updating-template':
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": w.name, "selected": selected, "label": w.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getuuidpool(self, keys):
        loginfo("get uuid pool")
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
        uuid_list = handle.query_classid("uuidpoolPool")
        selected = "1"
        for uuid in uuid_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": uuid.name, "selected": selected, "label": uuid.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getpowerpolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()

        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
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
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getlocaldiskpolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
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
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getbootpolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
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
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getvmediapolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
            return ret

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()
        vmedia_list = handle.query_classid("cimcvmediaMountConfigPolicy")
        selected = "1"
        for vmedia in vmedia_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": vmedia.name, "selected": selected, "label": vmedia.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getbiospolicy(self, keys):
        temp_list = []
        fabricid = getArg(keys, 'fabric_id')
        ret = result()
        if fabricid == None:
            ret.setResult(temp_list, PTK_OKAY, "success")
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
        res.setResult(temp_list, PTK_OKAY, "success")
        return res


class UCSCloneServiceProfileTemplateInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    template_name = Dropdown(hidden='False', isbasic='True', helptext='Template name', dt_type="string", static="False", api="gettemplate()|[fabric_id:1:fabric_id.value]", static_values="", name="template_name",
                             label="Template Name", mapval="1", svalue="__t201.UCSCreateServiceProfileTemplate.serviceprofilename", mandatory='1', order=2)
    vmedia_template = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='vmedia template name', dt_type="string", api="", static="False", static_values="", name="vmedia_template",
                              label="Clone Template Name", svalue="VM-Host-iSCSi-A-vM", mandatory='1', mapval="0", order=3)
    vmedia_policy_name = Dropdown(hidden='False', isbasic='True', helptext='vMedia policy name', dt_type="string", api="getvmediapolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                  static_values="", name="vmedia_policy_name", label="vMedia Policy", svalue="ESXi-6.5U1-HTTP", mapval="0", mandatory='1', order=4)
    ident_pool_name = Dropdown(hidden='False', isbasic='True', helptext='UUID Pool name', dt_type="string", api="getuuidpool()|[fabric_id:1:fabric_id.value]", static="False",
                               static_values="", name="ident_pool_name", label="Pool Assignment", svalue="UUID_Pool", mandatory='1', mapval="0", order=5)
    boot_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Boot policy', dt_type="string", api="getbootpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                static_values="", name="boot_policy_name", label="Boot Policy", svalue="Boot-FC-A", mapval="0", mandatory='1', order=6)
    power_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Power policy', dt_type="string", api="getpowerpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                 static_values="", name="power_policy_name", label="Power Policy", svalue="No-Power-Cap", mandatory='1', mapval="", order=7)
    local_disk_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Local disk policy name', dt_type="string", api="getlocaldiskpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                      static_values="", name="local_disk_policy_name", label="Local Disk Policy", svalue="SAN-Boot", mandatory='1', mapval="0", order=8)
    biospolicy = Dropdown(hidden='False', isbasic='True', helptext='BIOS policy', dt_type="string", api="getbiospolicy()|[fabric_id:1:fabric_id.value]", static="False",
                          static_values="", name="biospolicy", label="BIOS Policy", svalue="", mandatory='1', mapval="0", order=9)


class UCSCloneServiceProfileTemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    clone_sp_template_name = Output(
        dt_type="string", name="clone_sp_template_name", tvalue="VM-Host-iSCSi-A-vM")
