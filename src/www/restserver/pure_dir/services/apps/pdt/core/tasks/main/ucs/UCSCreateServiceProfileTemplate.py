from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateServiceProfileTemplate",
    task_name="Create Service Profile template",
    task_desc="Create Service Profile Template in UCS",
    task_type="UCSM"
)


class UCSCreateServiceProfileTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_service_profile_template")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()
        loginfo("------------")

        res = obj.ucsCreateServiceProfileTemplate(
            taskinfo['inputs'], fp)
        loginfo("-----------")
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS service profile template rollback")
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
        res.setResult(ucs_list, PTK_OKAY, "success")
        print ucs_list, res
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

    def getsanconnectivity(self, keys):
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
        san_list = handle.query_classid("vnicsanConnPolicy")
        selected = "1"
        for san in san_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": san.name, "selected": selected, "label": san.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getlanconnectivity(self, keys):
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
        lan_list = handle.query_classid("vnicLanConnPolicy")
        selected = "1"
        for lan in lan_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": lan.name, "selected": selected, "label": lan.name})
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

    def getmaintenancepolicy(self, keys):
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
        maintenance_list = handle.query_classid("lsmaintMaintPolicy")
        selected = "1"
        for maintenance in maintenance_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": maintenance.name, "selected": selected, "label": maintenance.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getqualifier(self, keys):
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
        qual_list = handle.query_classid("computeQual")
        selected = "1"
        for qual in qual_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": qual.name, "selected": selected, "label": qual.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getpoolassignment(self, keys):
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
        pool_list = handle.query_classid("computePool")
        selected = "1"
        for pool in pool_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": pool.name, "selected": selected, "label": pool.name})
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


class UCSCreateServiceProfileTemplateInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='Enter Name For UCS Fabric', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    template_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Enter Name For The Template', dt_type="string", api="", static="False", static_values="", name="template_name",
                            label="Name", svalue="VM-Host-Infra-A", mandatory='1', mapval="0", order=2, recommended="1")
    template_desc = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='', dt_type="string", api="", static="False", static_values="", name="template_desc",
                            label="Description", svalue="Service Profile template", mandatory='1', mapval="0", order=3)
    type = Radiobutton(hidden='False', isbasic='True', helptext='Template type', dt_type="string", api="", static="True", static_values="initial-template:0:Initial Template|updating-template:1:Updating Template",
                   label="Type", name="type", svalue="updating-template", mandatory='1', mapval="0", order=4)
    ident_pool_name = Dropdown(hidden='False', isbasic='True', helptext='UUID Pool', dt_type="string", api="getuuidpool()|[fabric_id:1:fabric_id.value]", static="False",
                               static_values="", name="ident_pool_name", label="UUID Assignment", svalue="UUID_Pool", mandatory='1', mapval="0", order=5)
    lan_conn_policy_name = Dropdown(hidden='False', isbasic='True', helptext='LAN Connectivity', dt_type="string", api="getlanconnectivity()|[fabric_id:1:fabric_id.value]", static="False",
                                    static_values="", name="lan_conn_policy_name", label="LAN Connectivity policy", svalue="", mandatory='1', mapval="0", order=6)
    san_conn_policy_name = Dropdown(hidden='False', isbasic='True', helptext='SAN Connectivity', dt_type="string", api="getsanconnectivity()|[fabric_id:1:fabric_id.value]", static="False",
                                    static_values="", name="san_conn_policy_name", label="SAN Connectivity policy", svalue="", mapval="0", mandatory='1', order=7)
    boot_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Boot policy', dt_type="string", api="getbootpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                static_values="", name="boot_policy_name", label="Boot Policy", svalue="Boot-FC-A", mapval="0", mandatory='1', order=8)
    power_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Power control policy', dt_type="string", api="getpowerpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                 static_values="", name="power_policy_name", label="Power Policy", svalue="No-Power-Cap", mandatory='1', mapval="", order=9)
    local_disk_policy_name = Dropdown(hidden='False', isbasic='True', helptext='Local disk policy', dt_type="string", api="getlocaldiskpolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                      static_values="", name="local_disk_policy_name", label="Local Disk Configuration Policy", svalue="SAN-Boot", mandatory='1', mapval="0", order=10)
    pool_assignment = Dropdown(hidden='False', isbasic='True', helptext='Pool assignment', dt_type="string", api="getpoolassignment()|[fabric_id:1:fabric_id.value]", static="False", static_values="",
                               mapval="1", name="pool_assignment", label="Pool Assignment", svalue="__t200.CreateServerPool.name", mandatory='1', order=11)
    biospolicy = Dropdown(hidden='False', isbasic='True', helptext='BIOS policy', dt_type="string", api="getbiospolicy()|[fabric_id:1:fabric_id.value]", static="False",
                          static_values="", name="biospolicy", label="BIOS Policy", svalue="", mandatory='1', mapval="0", order=12)
    maint_policy_name = Dropdown(hidden='False', isbasic='True', helptext='maintenance policy', dt_type="string", api="getmaintenancepolicy()|[fabric_id:1:fabric_id.value]", static="False",
                                 static_values="", name="maint_policy_name", label="Maintenance Policy", svalue="", mandatory='1', mapval="0", order=13)


class UCSCreateServiceProfileTemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    serviceprofilename = Output(
        dt_type="string", name="serviceprofilename", tvalue="VM-Host-Infra-A")
