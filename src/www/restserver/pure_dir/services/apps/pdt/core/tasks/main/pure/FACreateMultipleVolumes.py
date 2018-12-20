from pure_dir.components.storage.purestorage.pure_tasks import PureTasks
from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.common import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *


metadata = dict(
    task_id="FACreateMultipleVolumes",
    task_name="Create volume",
    task_desc="Creates multiple volumes",
    task_type="PURE"
)


class FACreateMultipleVolumes:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        """
         :param inputs: task input for FACreateMultipleVolumes, name, volumsize
         :type inputs: dict
         :param logfile: for printing logs
         :type logfile: function

         :returns: A dictionary describing the list of volumes created.
         :rtype: dict

         """
        cred = get_device_credentials(
            key="mac", value=inputs['inputs']['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.create_multiple_volumes(inputs['inputs'], logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)

    def purelist(self, keys):
        """
        :param keys: task input describing array type e.g. PURE
        :type keys: dict
        :returns: list of FlashArrays

        """
        res = result()
        pure_list = get_device_list(device_type="PURE")
        res.setResult(pure_list, PTK_OKAY, "success")
        return res

    def volumesize_unit(self, keys):
        loginfo("volumesize unit keys is :{}".format(keys))
        res = result()
        K = 2**10  # 1024
        M = 2**20  # 1048576
        G = 2**30  # 1073741824
        T = 2**40  # 1099511627776
        P = 2**50  # 1125899906842624
        val = [{"id": str(K), "selected": "0", "label": "K"},
               {"id": str(M), "selected": "0", "label": "M"},
               {"id": str(G), "selected": "1", "label": "G"},
               {"id": str(T), "selected": "0", "label": "T"},
               {"id": str(P), "selected": "0", "label": "P"}
               ]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        """
         :param inputs: task input for FACreateMultipleVolumes
         :type inputs: dict
         :param outputs: task output for FACreateMultipleVolumes
         :type outputs: dict
         :param logfile: for printing logs
         :type logfile: function

         """

        cred = get_device_credentials(
            key="mac", value=inputs['pure_id'])
        res = result()
        if not cred:
            loginfo("Unable to get the device credentials of the FlashArray")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the FlashArray")
            return parseTaskResult(res)

        obj = PureTasks(cred['ipaddress'],
                        cred['username'], cred['password'])

        result_data = obj.delete_multiple_volumes(inputs, logfile)
        obj.release_pure_handle()
        return parseTaskResult(result_data)

    def prepare(self, jobid, texecid, inputs):
        """
        :param jobid: executed job id
        :type jobid: str
        :param texecid: task execution id
        :type texecid: str
        :param inputs: input from global variables
        :type inputs: dict

        """
        res = result()
        val = getGlobalArg(inputs, 'ucs_switch_a')
        keys = {"keyvalues": [
            {"key": "fabric_id", "ismapped": "3", "value": val}]}
        res = self.ucsm_get_associated_sp_cnt(
            keys)  # self.ucsmbladeservers(keys)
        blade_list = res.getResult()
        val = ''

        if len(blade_list) > 0:
            blade_len = int(blade_list[0]['id'])
        loginfo("vol count create vol going is : {}".format(str(blade_len)))
        job_input_save(jobid, texecid, 'count', str(blade_len))

        if res.getStatus() != PTK_OKAY:
            return res

        res.setResult(None, PTK_OKAY, "success")
        return res

    def ucsm_get_associated_sp_cnt(self, keys):
        """
        :param keys: key for fabric id value
        :type taskinfo: str
        :returns: list of blade servers
        :rtype: list

        """
        servers_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            res.setResult(servers_list, PTK_OKAY, "success")
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        handle = res.getResult()
        service_profiles = handle.query_classid("lsServer")
        sp_cnt = []
        for sp in service_profiles:
            if sp.type != "updating-template" and sp.pn_dn != '':
                sp_cnt.append(sp.name)

        server_dict = {
            'id': str(len(sp_cnt)),
            "selected": "1",
            "label": str(len(sp_cnt))}
        servers_list.append(server_dict)
        print "server list from ucs", servers_list
        ucsm_logout(handle)
        res.setResult(servers_list, PTK_OKAY, "success")
        return res


class FACreateMultipleVolumesInputs:
    pure_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="purelist()", name="pure_id",
                       label="FlashArray", svalue="", mapval="", mandatory="0", static_values="", order=1)
    name = Textbox(validation_criteria='str|min:1|max:64', hidden='False', isbasic='True', helptext='Volume Name', dt_type="string", static="False", api="", name="name", label="Name",
                   svalue="VM-Vol-FC-#", static_values="", mandatory="0", mapval="", order=2, recommended="1")
    size = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext="Volume's Size", dt_type="integer", static="False", api="", name="size", label="Size",
                   svalue="10", group_member="1", static_values="", mandatory="0", mapval="", order=3, recommended="1")
    size_unit = Dropdown(hidden='False', isbasic='True', helptext="Unit of volume's size", dt_type="string", static="False", api="volumesize_unit()", name="size_unit", label="Size Unit",
                         svalue="", group_member="1", static_values="", mapval="", mandatory="0", order=3, recommended="1")
    vol_set = Group(validation_criteria='', hidden='False', isbasic='True', helptext='Provisioning Size', dt_type="string", static="False", api="", name="vol_set", label="Provisioned size", svalue="", mapval="",
                    mandatory="0", members=["size", "size_unit"], add="False", static_values="", order=4, recommended="1")
    st_no = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext="Volume Name's starting number", dt_type="string", static="False", api="", name="st_no", label="Start number",
                    svalue="1", mandatory="0", static_values="", mapval="", order=5, recommended="1")
    count = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext='Number of Volumes', dt_type="string", static="False", api="", name="count", label="Count",
                    svalue="2", mandatory="0", static_values="", mapval="", order=6)
    num_digits = Textbox(validation_criteria='int', hidden='False', isbasic='True', helptext='Number of digits appending for Host Name', dt_type="string",
                         static="False", api="", name="num_digits", label="Number of Digits", svalue="2", mandatory="0", static_values="", mapval="", order=7, recommended="1")


class FACreateMultipleVolumesOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
