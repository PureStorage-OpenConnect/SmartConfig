from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSbindoATemplate",
    task_name="UCS bind to a  template",
    task_desc="UCS bind to a  template",
    task_type="UCSM"
)


class UCSBindToATemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("UCSbindToATemplate")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsbindtoatemplate(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        print "create boot policy rollback"
        return 0

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

    def getserviceprofiletemplate(self, keys):
        loginfo("get service profile template")
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
        serviceprofile_list = handle.query_classid("lsServer")
        selected = "1"
        for serviceprofile in serviceprofile_list:
            if serviceprofile.type == "updating-template":
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": serviceprofile.name, "selected": selected, "label": serviceprofile.name})
        print "temp_list", temp_list
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getserviceprofile(self, keys):
        loginfo("get service profile ")
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
        serviceprofile_list = handle.query_classid("lsServer")
        selected = "1"
        for serviceprofile in serviceprofile_list:
            if serviceprofile.type == "instance":
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": serviceprofile.name, "selected": selected, "label": serviceprofile.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res


class UCSBindToATemplateInputs:
    service_profile_name = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getserviceprofile()|[fabric_id:1:fabric_id.value]", static="False",
                                    static_values="", name="service_profile_name", label="Service Profile", svalue="", mandatory='1', mapval="0", order=1)
    vmedia_policy_name = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getvmediapolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                  static_values="", name="vmedia_policy_name", label="Vmedia Policy", svalue="", mapval="0", mandatory='1', order=2)
    biospolicy = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getbiospolicy()|[fabric_id:1:fabric_id.value]", static="False",
                          static_values="", name="biospolicy", label="Bios Policy", svalue="", mandatory='1', mapval="0", order=3)
    boot_policy_name = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getbootpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                static_values="", name="boot_policy_name", label="Boot Policy", svalue="Boot-FC-A", mapval="0", mandatory='1', order=4)
    power_policy_name = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getpowerpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                 static_values="", name="power_policy_name", label="Power Policy", svalue="No-Power-Cap", mandatory='1', mapval="", order=5)
    local_disk_policy_name = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getlocaldiskpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                      static_values="", name="local_disk_policy_name", label="Local Disk Policy", svalue="SAN-Boot", mandatory='1', mapval="0", order=6)
    service_profile_template = Dropdown(hidden='False', isbasic='True', helptext='', dt_type="string", api="getserviceprofiletemplate()|[fabric_id:1:fabric_id.value]", static="False",
                                        static_values="", name="service_profile_template", label="Service Profile Template", svalue="", mandatory='1', mapval="0", order=7)


class UCSBindToATemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
