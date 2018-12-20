from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from distutils.version import LooseVersion


class UCSCreateHostFirmwarePackage:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Create Host Firmware Package")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateHostFirmwarePackage(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Reset Host Firmware Package")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsResetHostFirmwarePackage(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def prepare(self, jobid, texecid, inputs):
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        blade_res = self.get_firmware_bundles(
            keys, bundle_type="b-series-bundle")
        rack_res = self.get_firmware_bundles(
            keys, bundle_type="c-series-bundle")

        blade_version_list = blade_res.getResult()
        rack_version_list = rack_res.getResult()
        blade_val = ''
        rack_val = ''

        for blade_version in blade_version_list:
            blade_val = blade_version['id']
        for rack_version in rack_version_list:
            #rack_val = rack_version['id']
            rack_val = ''  # Done because latest rack package is not uploaded

        blade_firmware = getGlobalArg(inputs, 'firmware')
        if blade_firmware:
            ver = blade_firmware[-12:].split('.')
            version = ver[0] + "." + ver[1] + "(" + ver[2] + ")" + ver[3]
            blade_val = version

        job_input_save(jobid, texecid, 'blade_pkg', blade_val)
        job_input_save(jobid, texecid, 'rack_pkg', rack_val)

        if blade_res.getStatus() != PTK_OKAY:
            return blade_res
        if rack_res.getStatus() != PTK_OKAY:
            return rack_res

        res.setResult(None, PTK_OKAY, "success")
        return res

    def get_b_series_firmware_bundle(self, keys):
        bundle_type = 'b-series-bundle'
        temp_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            res.setResult(temp_list, PTK_OKAY, "success")
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()

        filter_str = None
        if bundle_type is not None:
            filter_str = '(type, %s, type="eq")' % bundle_type
        bundles = handle.query_classid(
            class_id="FirmwareDistributable", filter_str=filter_str)
        bundle_result = []

        for bundle in bundles:
            bundle_result.append(
                {'id': bundle.version, "selected": "1", "label": bundle.version})

        bundle_result.extend(ucsbladeimages(version=True))
        bundle_result = [dict(t)
                         for t in {tuple(d.items()) for d in bundle_result}]

        ucsm_logout(handle)
        res.setResult(bundle_result, PTK_OKAY, "success")
        return res

    def get_c_series_firmware_bundle(self, keys):
        bundle_type = 'c-series-bundle'
        temp_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            res.setResult(temp_list, PTK_OKAY, "success")
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()

        filter_str = None
        if bundle_type is not None:
            filter_str = '(type, %s, type="eq")' % bundle_type
        bundles = handle.query_classid(
            class_id="FirmwareDistributable", filter_str=filter_str)
        bundle_result = []

        for bundle in bundles:
            bundle_result.append(
                {'id': bundle.version, "selected": "1", "label": bundle.version})
        ucsm_logout(handle)
        res.setResult(bundle_result, PTK_OKAY, "success")
        return res

    def get_firmware_bundles(self, keys, bundle_type=None):
        temp_list = []
        bundle_dict = {}
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            res.setResult(temp_list, PTK_OKAY, "success")
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()

        filter_str = None
        if bundle_type is not None:
            filter_str = '(type, %s, type="eq")' % bundle_type
        bundles = handle.query_classid(
            class_id="FirmwareDistributable", filter_str=filter_str)
        bundle_list = []
        bundle_result = []
        for bundle in bundles:
            bundle_list += [bundle.version]
        if bundle_list:
            bundle_list.sort(key=LooseVersion)
            bundle_pkg_version = bundle_list[-1]
            bundle_dict = {'id': bundle_pkg_version,
                           'selected': '1', "label": "bundle_version"}
            bundle_result.append(bundle_dict)
        ucsm_logout(handle)
        res.setResult(bundle_result, PTK_OKAY, "success")
        return res

    def getrackpackage(self, keys):
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
        fm_versions = handle.query_classid("firmwareRunning")
        selected = "1"
        for fm_version in fm_versions:
            if fm_version.type == 'system':
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": fm_version.version + "C", "selected": selected, "label": fm_version.version + "C"})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getbladepackage(self, keys):
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
        fm_versions = handle.query_classid("firmwareRunning")
        selected = "1"
        for fm_version in fm_versions:
            if fm_version.type == 'system':
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": fm_version.version + "B", "selected": selected, "label": fm_version.version + "B"})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, "success")
        return res

    def getexcludedcomp(self, keys):
        res = result()
        val = [{"id": "local-disk", "selected": "1", "label": "Local Disk"},
               {"id": "adaptor", "selected": "0", "label": "Adaptor"},
               {"id": "host-nic-optionrom", "selected": "0",
                   "label": "Host NIC Option ROM"},
               {"id": "blade-controller", "selected": "0", "label": "CIMC"},
               {"id": "board-controller", "selected": "0",
                   "label": "Board Controller"},
               {"id": "flexflash-controller", "selected": "0",
                   "label": "Flex Flash Controller"},
               {"id": "blade-bios", "selected": "0", "label": "BIOS"},
               {"id": "psu", "selected": "0", "label": "PSU"},
               {"id": "sas-expander", "selected": "0", "label": "SAS Expander"},
               {"id": "storage-controller-onboard-device", "selected": "0",
                "label": "Storage Controller Onboard Device"},
               {"id": "storage-dev-bridge", "selected": "0",
                   "label": "Storage Device Bridge"},
               {"id": "graphics-card", "selected": "0", "label": "GPU"},
               {"id": "host-hba-optionrom", "selected": "0",
                   "label": "HBA Option ROM"},
               {"id": "sas-exp-reg-fw", "selected": "0",
                   "label": "SAS Expander Regular Firmware"},
               {"id": "host-nic", "selected": "0", "label": "Host NIC"},
               {"id": "storage-controller", "selected": "0",
                   "label": "Storage Controller"},
               {"id": "storage-controller-onboard-device-cpld", "selected": "0",
                "label": "Storage Controller Onboard Device Cpld"}
               ]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res


class UCSCreateHostFirmwarePackageInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", svalue="", mapval="", static_values="", mandatory="1", order=1)
    name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Firmware Package', api="", dt_type="string", label="Name", mapval="0", name="name",
                   static_values="", static="False", mandatory='1', svalue="default", order=2)
    desc = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='Description', api="", dt_type="string", label="Description", mapval="0", name="desc",
                   static_values="", static="False", mandatory='1', svalue="default firmware package", order=3)
    blade_pkg = Dropdown(hidden='False', isbasic='True', helptext='Blade Package', api="get_b_series_firmware_bundle()|[fabric_id:1:fabric_id.value]",
                         dt_type="string", label="Blade Package", mapval="0", mandatory="1", name="blade_pkg", static="False", static_values="", svalue="", order=4)
    rack_pkg = Dropdown(hidden='False', isbasic='True', helptext='Rack Package', api="get_c_series_firmware_bundle()|[fabric_id:1:fabric_id.value]", dt_type="string", label="Rack Package", mapval="0", name="rack_pkg",
                        static="False", mandatory='0', static_values="", svalue="", order=5, validation_criteria="None")
    excluded_comp = Checkbox(hidden='False', isbasic='True', helptext='Excluded package', api="getexcludedcomp()", dt_type="string", label="Excluded Components", mapval="0", mandatory='1',
                             name="excluded_comp", static="False", allow_multiple_values="0", static_values="", svalue="local-disk", order=6)


class UCSCreateHostFirmwarePackageOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
