from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg, getGlobalArg, job_input_save, get_field_value_from_jobid
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
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        print(ucs_list, res)
        return res

    def list_server_disks(self, handle):
        blades = handle.query_classid(class_id="ComputeBlade")
        all_disks = []
        for serv in blades:
            chassis = serv.chassis_id
            slot_id = serv.slot_id
            cquery = "(dn, \"sys/chassis-{0}/blade-{1}/board.*\", type=\"re\")".format(chassis, slot_id)
            controllers = handle.query_classid("StorageController", cquery)
        # Get the disks of each controller.
            for c in controllers:
                dquery = "(dn, \"{0}\", type=\"re\")".format(c.dn)
                disks = handle.query_classid("StorageLocalDisk", dquery)
                for d in disks:
                    all_disks.append(d)
        return all_disks

    def prepare(self, jobid, texecid, inputs):
        loginfo(
            "preparing to save values for creating service profile template input params")
        res = result()
        # TODO for safer side. Please ensure map val set for desired fields
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}

        fabricid = getArg(keys, 'fabric_id')
        if fabricid is None:
            res.setResult([], PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()

        res = self.getuuidpool(keys)
        uuid_list = [uuid for uuid in res.getResult() if uuid.get('id')
                     != 'default']
        self.sp_template_save_inputs(
            jobid, texecid, "ident_pool_name", uuid_list)

        san_conn_policy = self.getsanconnectivity(keys)
        self.sp_template_save_inputs(
            jobid, texecid, "san_conn_policy_name", san_conn_policy.getResult())

        lan_conn_policy = self.getlanconnectivity(keys)
        self.sp_template_save_inputs(
            jobid, texecid, "lan_conn_policy_name", lan_conn_policy.getResult())

        boot_policy = self.getbootpolicy(keys)
        boot_pol_list = [boot for boot in boot_policy.getResult() if boot.get(
            'id') not in ['utility', 'diag', 'default', 'default-UEFI']]
        self.sp_template_save_inputs(
            jobid, texecid, "boot_policy_name", boot_pol_list)

        power_policy = self.getpowerpolicy(keys)
        power_pol_list = [power_pol for power_pol in power_policy.getResult(
        ) if power_pol.get('id') != 'default']
        self.sp_template_save_inputs(
            jobid, texecid, "power_policy_name", power_pol_list)

        local_disk_policy = self.getlocaldiskpolicy(keys)

        disks = self.list_server_disks(handle)
        loginfo("Local disk policy is default when there are local disks in server")
        if disks:
            job_input_save(jobid, texecid, "local_disk_policy_name", "default")
        else:
            localdisk_pol_list = [localdisk_pol for localdisk_pol in local_disk_policy.getResult(
            ) if localdisk_pol.get('id') != 'default']
            self.sp_template_save_inputs(
                jobid, texecid, "local_disk_policy_name", localdisk_pol_list)

        bios_policy = self.getbiospolicy(keys)
        bios_pol_list = [bios_pol for bios_pol in bios_policy.getResult(
        ) if bios_pol.get('id') not in ['SRIOV', 'usNIC']]
        self.sp_template_save_inputs(
            jobid, texecid, "biospolicy", bios_pol_list)

        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def sp_template_save_inputs(self, jobid, texecid, input_field_name, input_list):
        field_val_from_xml = get_field_value_from_jobid(
            jobid, "UCSCreateServiceProfileTemplate", input_field_name)
        for input_val in input_list:
            input_value = input_val['id']
            if field_val_from_xml != input_value:
                job_input_save(jobid, texecid, input_field_name, input_value)

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

    def getsanconnectivity(self, keys):
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
        san_list = handle.query_classid("vnicsanConnPolicy")
        selected = "1"
        for san in san_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": san.name, "selected": selected, "label": san.name})
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

    def getvmediapolicy(self, keys):
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
        vmedia_list = handle.query_classid("cimcvmediaMountConfigPolicy")
        selected = "1"
        for vmedia in vmedia_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": vmedia.name, "selected": selected, "label": vmedia.name})
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

    def getqualifier(self, keys):
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
        qual_list = handle.query_classid("computeQual")
        selected = "1"
        for qual in qual_list:
            if temp_list:
                selected = "0"
            temp_list.append(
                {"id": qual.name, "selected": selected, "label": qual.name})
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


class UCSCreateServiceProfileTemplateInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='Enter Name For UCS Fabric',
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
        helptext='Enter Name For The Template',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="template_name",
        label="Name",
        svalue="VM-Host-Infra-A",
        mandatory='1',
        mapval="0",
        order=2,
        recommended="1")
    template_desc = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='',
        dt_type="string",
        api="",
        static="False",
        static_values="",
        name="template_desc",
        label="Description",
        svalue="Service Profile template",
        mandatory='1',
        mapval="0",
        order=3)
    type = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Template type',
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
        helptext='UUID Pool',
        dt_type="string",
        api="getuuidpool()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="ident_pool_name",
        label="UUID Assignment",
        svalue="UUID_Pool",
        mandatory='1',
        mapval="0",
        order=5)
    lan_conn_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='LAN Connectivity',
        dt_type="string",
        api="getlanconnectivity()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="lan_conn_policy_name",
        label="LAN Connectivity policy",
        svalue="",
        mandatory='1',
        mapval="0",
        order=6)
    san_conn_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='SAN Connectivity',
        dt_type="string",
        api="getsanconnectivity()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="san_conn_policy_name",
        label="SAN Connectivity policy",
        svalue="",
        mapval="0",
        mandatory='1',
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
        svalue="Boot-FC-A",
        mapval="0",
        mandatory='1',
        order=8)
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
        order=9)
    local_disk_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Local disk policy',
        dt_type="string",
        api="getlocaldiskpolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="local_disk_policy_name",
        label="Local Disk Configuration Policy",
        svalue="SAN-Boot",
        mandatory='1',
        mapval="0",
        order=10)
    pool_assignment = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='Pool assignment',
        dt_type="string",
        api="getpoolassignment()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        mapval="1",
        name="pool_assignment",
        label="Pool Assignment",
        svalue="__t200.CreateServerPool.name",
        mandatory='1',
        order=11)
    biospolicy = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='BIOS policy',
        dt_type="string",
        api="getbiospolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="biospolicy",
        label="BIOS Policy",
        svalue="",
        mandatory='1',
        mapval="0",
        order=12)
    maint_policy_name = Dropdown(
        hidden='False',
        isbasic='True',
        helptext='maintenance policy',
        dt_type="string",
        api="getmaintenancepolicy()|[fabric_id:1:fabric_id.value]",
        static="False",
        static_values="",
        name="maint_policy_name",
        label="Maintenance Policy",
        svalue="",
        mandatory='1',
        mapval="0",
        order=13)


class UCSCreateServiceProfileTemplateOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    serviceprofilename = Output(
        dt_type="string", name="serviceprofilename", tvalue="VM-Host-Infra-A")
    ident_pool_name = Output(
        dt_type="string", name="ident_pool_name", tvalue="UUID_Pool")
    boot_policy_name = Output(
        dt_type="string", name="boot_policy_name", tvalue="Boot-FC-X-A")
    power_policy_name = Output(
        dt_type="string", name="power_policy_name", tvalue="No-Power-Cap")
    local_disk_policy_name = Output(
        dt_type="string", name="local_disk_policy_name", tvalue="SAN-Boot")
    biospolicy = Output(
        dt_type="string", name="biospolicy", tvalue="VM-Host")
