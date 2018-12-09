from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.components.common import *
from pure_dir.components.compute.ucs.ucs_upgrade import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'

metadata = dict(
    task_id="UCSBladeFirmwareUpgrade",
    task_name="Blade firmware upgrade",
    task_desc="Blade firmware upgrade",
    task_type="UCSM"
)


class UCSBladeFirmwareUpgrade:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("blade_firmware_upgrade")

        status, details = get_xml_element(
            file_name=static_discovery_store, attribute_key="mac", attribute_value=taskinfo['inputs']['fabric_id'])
	obj = UCSTasks()
        res = obj.bladeFirmwareUpgrade(taskinfo['inputs'], logfile, details[0]['vipaddress'], "admin", decrypt(details[0]['password']))

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Blade firmware upgrade rollback")
	customlogs("Skipping rollback for Blade firmware upgrade", logfile)
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def bladeimages(self, keys):
        images_list = []
        res = result()
	images_list = ucsbladeimages()
        res.setResult(images_list, PTK_OKAY, "success")
        return res

    def validate(self, item):
        member = eval(item)
	stacktype = get_xml_element("/mnt/system/pure_dir/pdt/settings.xml", "stacktype")[1][0]['stacktype']
	if member['upgrade']['ismapped'] == "3":
	    member['upgrade']['value'] = get_global_val(stacktype, "upgrade")
	if member['firmware']['ismapped'] == "3":
	    member['firmware']['value'] = get_global_val(stacktype, "firmware")
	if member['upgrade']['value'] == "Yes" and member['firmware']['value'] == "":
	    return False, "firmware", "Select any image"

	return True, "firmware", member['firmware']['ismapped']


class UCSBladeFirmwareUpgradeInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    upgrade = Dropdown(hidden='', isbasic='True',
                        helptext='Upgrade blade firmware',
                        dt_type="string", static="True", api="", name="upgrade", label="Upgrade Blade Server Firmware",
                        static_values="Yes:1:Yes|No:0:No", svalue="Yes", mapval="",
                        mandatory="1", recommended="1", group_member="1")
    firmware = Dropdown(hidden='False', isbasic='True', helptext='Select the package', dt_type="string", static="False", api="bladeimages()", 
			name="firmware", label="Blade Server Bundle", static_values="", svalue="", mapval="", mandatory="1", group_member="1")
    blade_upg = Group(validation_criteria='function', hidden='', isbasic='True', helptext='Select whether blade firmware needs to be upgraded and the appropriate bundle', 
			dt_type="string", static="False", api="", name="blade_upg", label="Blade firmware upgrade", static_values="", svalue="", mapval="", mandatory="1", 
			members=["upgrade", "firmware"], add="False", order=2)


class UCSBladeFirmwareUpgradeOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")

