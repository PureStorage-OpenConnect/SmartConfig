from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.storage.mds.mds_tasks import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult

metadata = dict(
    task_id="MDSCreatePortchannel",
    task_name="Create PortChannel",
    task_desc="Create Port Channel in the MDS switch",
    task_type="MDS"
)


class MDSCreatePortchannel:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Creating port channel for MDS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                res = obj.create_portchannel(taskinfo['inputs'], logfile)
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_MDS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_MDS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        res = result()
        loginfo("Rollback - CreatePortChannel for MDS")
        cred = get_device_credentials(
            key="mac", value=inputs['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                res = obj.delete_portchannel(inputs, logfile)
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(False, PTK_INTERNALERROR,
                              _("PDT_MDS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(False, PTK_INTERNALERROR,
                          _("PDT_MDS_LOGIN_FAILURE"))

        return parseTaskResult(res)

    def get_mds_list(self, keys):
        res = result()
        mds_list = get_device_list(device_type="MDS")
        res.setResult(mds_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class MDSCreatePortchannelInputs:
    mds_id = Dropdown(
        hidden='True',
        isbasic='True',
        helptext='',
        dt_type="string",
        static="False",
        static_values="",
        api="get_mds_list()",
        name="mds_id",
        label="MDS switch",
        svalue="",
        mapval="",
        mandatory="1",
        order="1")
    portchannel_id = Textbox(
        validation_criteria='int|min:1|max:256',
        hidden='False',
        isbasic='True',
        helptext='Port channel ID',
        dt_type="string",
        static="False",
        api="",
        name="portchannel_id",
        static_values="",
        label="Port-Channel (1-256)",
        svalue="1",
        mapval="",
        mandatory="1",
        order="2",
        recommended="1")


class MDSCreatePortchannelOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    portchannel_id = Output(
        dt_type="string", name="portchannel_id", tvalue="1")
