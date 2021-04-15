from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_devices_wf_config_file
from pure_dir.services.utils.miscellaneous import get_xml_childelements
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.storage.mds.mds import MDS
from pure_dir.components.common import decrypt

metadata = dict(
    task_id="UCSResetServer",
    task_name="Reset UCS server",
    task_desc="Reset UCS Server",
    task_type="UCSM"
)


class UCSResetServer:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("reset_ucs_server")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])


        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsServerReset(taskinfo['inputs'], logfile)
        
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)

        status, devices_details = get_xml_childelements(get_devices_wf_config_file(), 'devices', 'device',
                                                ['device_type', 'ipaddress', 'username', 'password', 'vipaddress', 'tag'])
        for hw in devices_details:
            if hw['device_type'] in ['Nexus 9k', 'Nexus 5k']:
                nexus_res = Nexus(ipaddress=hw['ipaddress'], username=hw['username'], password=decrypt(hw['password']))

                loginfo("Copying running config to startup config in {} switch {}". format(hw['device_type'], hw['tag']))
                res = nexus_res.save_config()
                if res.getStatus() != PTK_OKAY:
                    msg = "Unable to copy running config to startup config in {} switch {}\n".format(hw['device_type'], hw['tag'])
                    customlogs(msg, logfile)
                    return parseTaskResult(res)

            if hw['device_type'] in ['MDS']:
                mds_res = MDS(ipaddr=hw['ipaddress'], uname=hw['username'], passwd=decrypt(hw['password']))

                loginfo("Copying running config to startup config in {} switch {}". format(hw['device_type'], hw['tag']))
                res = mds_res.save_config()
                if res.getStatus() != PTK_OKAY:
                    msg = "Unable to copy running config to startup config in {} switch {}\n".format(hw['device_type'], hw['tag'])
                    customlogs(msg, logfile)
                    return parseTaskResult(res)

        obj.release_ucs_handle()
        res.setResult({}, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS Reset Server rollback")
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class UCSResetServerInputs:
    fabric_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        api="getfilist()",
        name="fabric_id",
        label="UCS Fabric Name",
        svalue="",
        mapval="",
        static_values="",
        mandatory="1",
        order=1)


class UCSResetServerOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
