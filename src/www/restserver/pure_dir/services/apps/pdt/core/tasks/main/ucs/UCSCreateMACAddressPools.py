from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg, job_input_save
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_file
import xmltodict
import random
import re

metadata = dict(
    task_id="UCSCreateMACAddressPools",
    task_name="Create MAC Address Pools",
    task_desc="Create MAC Address pools in UCS",
    task_type="UCSM"
)


class UCSCreateMACAddressPools:
    def __init__(self):
        pass
    
    def execute(self, taskinfo, logfile):
        loginfo("Create MAC Address Pools")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateMACAddressPools(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("RollBack: Create MAC Address Pools")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteMACAddressPools(
            inputs, outputs, logfile)

        obj.release_ucs_handle()
        return res

    def prepare(self, jobid, texecid, inputs):
        res = result()

        job_xml = get_job_file(jobid)
        fd = None
        try:
            fd = open(job_xml, 'r')
        except IOError:
            loginfo("Could not read file: %s" % job_xml)

        doc = xmltodict.parse(fd.read())

        mac_id = [[switch['@value'] for switch in task['args']['arg'] if switch['@name'] == "mac_name"][0]
                  for task in doc['workflow']['tasks']['task'] if task['@texecid'] == texecid][0]

        mac_address = self.random_mac(mac_id)
        loginfo("Random mac number:%s" % mac_address)
        job_input_save(jobid, texecid, 'mac_start', mac_address)

        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def gen_hex(self, length):
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(length))

    def random_mac(self, mac_name):
        if 'MAC_Pool_A' in mac_name:
            mac_A = (
                '00',
                self.gen_hex(2),
                self.gen_hex(2),
                self.gen_hex(2),
                self.gen_hex(1) + 'A',
                self.gen_hex(2))
            macA = ':'.join(mac_A)
            return macA
        elif 'MAC_Pool_B' in mac_name:
            mac_B = (
                '00',
                self.gen_hex(2),
                self.gen_hex(2),
                self.gen_hex(2),
                self.gen_hex(1) + 'B',
                self.gen_hex(2))
            macB = ':'.join(mac_B)
            return macB

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def validate(self, item, mac_name):
        if re.match("[0-9a-f]{2}([:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", 
                    item.lower()) and item[-4] == mac_name and item[:2] == "00":
            pass
        else:
            return False, "Invalid MAC Address format Eg: 00:xx:xx:xx:x"+mac_name+":xx"
        return True, ""


class UCSCreateMACAddressPoolsInputs:
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
    mac_name = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='MAC Address Pool Name',
        api="",
        dt_type="string",
        label="Name",
        mapval="0",
        name="mac_name",
        static="False",
        svalue="MAC_Pool_A",
        mandatory='1',
        static_values="",
        order=2)
    descr = Textbox(
        validation_criteria='str|min:1|max:128',
        hidden='False',
        isbasic='True',
        helptext='Description',
        api="",
        dt_type="string",
        label="Description",
        mapval="0",
        name="descr",
        static="False",
        svalue="mac pool A",
        mandatory='1',
        static_values="",
        order=3)
    mac_order = Radiobutton(
        hidden='False',
        isbasic='True',
        helptext='Assignment order',
        api="",
        dt_type="string",
        label="Assignment order",
        mapval="0",
        name="mac_order",
        static="True",
        static_values="default:1:Default|sequential:0:Sequential",
        svalue="sequential",
        mandatory='1',
        order=4)
    mac_start = Textbox(
        validation_criteria='function_rand',
        hidden='False',
        isbasic='True',
        helptext='MAC Start Address',
        api="",
        dt_type="string",
        label="First MAC Address",
        mapval="0",
        name="mac_start",
        static="False",
        svalue="00:25:B5:91:1A:00",
        mandatory='1',
        static_values="",
        order=5,
        recommended="1")
    size = Textbox(
        validation_criteria='int|min:1|max:1000',
        hidden='False',
        isbasic='True',
        helptext='Size',
        api="",
        dt_type="string",
        label="Size(1-1000)",
        mapval="0",
        name="size",
        static="False",
        svalue="32",
        mandatory='1',
        static_values="",
        order=6,
        recommended="1")


class UCSCreateMACAddressPoolsOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    name = Output(dt_type="string", name="mac_name", tvalue="MAC_Pool_A")
