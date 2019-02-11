from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.storage.mds.mds_tasks import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult

metadata = dict(
    task_id="MDSCreateAndConfigureVSAN",
    task_name="Create and Configure VSAN",
    task_desc="Create VSAN and apply to the interfaces in the MDS switch",
    task_type="MDS"
)


class MDSCreateAndConfigureVSAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Configuring vsan for MDS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                # Create VSAN
                res = obj.create_vsan(taskinfo['inputs'], logfile)
                if res.getStatus() == PTK_OKAY:
                    # Configure VSAN
                    res = obj.configure_vsan(taskinfo['inputs'], logfile)
                    if res.getStatus() != PTK_OKAY:
                        loginfo("Failed to configure VSAN")
                        obj.delete_vsan(taskinfo['inputs'], logfile)
                        res.setResult(False, PTK_INTERNALERROR,
                                      _("PDT_FAILED_MSG"))
                    else:
                        loginfo("MDSCreateAndConfigureVSAN executed successfully")
                        res.setResult(
                            parseResult(res)['data'],
                            PTK_OKAY,
                            _("PDT_SUCCESS_MSG"))
                else:
                    loginfo("Failed to create VSAN")
                    res.setResult(False, PTK_INTERNALERROR,
                                  _("PDT_FAILED_MSG"))
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
        loginfo("Rollback - CreateAndConfigureVSAN for MDS")
        cred = get_device_credentials(
            key="mac", value=inputs['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                # Delete VSAN
                res = obj.delete_vsan(inputs, logfile)
                if res.getStatus() != PTK_OKAY:
                    loginfo("Failed to delete VSAN")
                    res.setResult(False, PTK_INTERNALERROR,
                                  _("PDT_FAILED_MSG"))
                else:
                    loginfo(
                        "MDSCreateAndConfigureVSAN rollback executed successfully")
                    res.setResult(
                        parseResult(res)['data'],
                        PTK_OKAY,
                        "MDSCreateAndConfigureVSAN rollback task executed successfully")
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

    def get_fc_list(self, keys):
        res = result()
        loginfo("Getting MDS fc list...")
        fc_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "mds_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(fc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = MDS(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                tmp_fc_list = obj.get_fc_list().getResult()
                for index, fc in enumerate(tmp_fc_list):
                    fc_list.append(
                        {"id": fc['iface_id'], "selected": "0", "label": fc['iface_id']})
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(fc_list, PTK_INTERNALERROR,
                              _("PDT_MDS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(fc_list, PTK_INTERNALERROR,
                          _("PDT_MDS_LOGIN_FAILURE"))

        res.setResult(fc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def get_portchannel_list(self, keys):
        res = result()
        loginfo("Getting MDS port channel list...")
        pc_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "mds_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(pc_list, PTK_OKAY, "success")
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = MDS(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                tmp_pc_list = obj.get_portchannel_list().getResult()
                for index, pc in enumerate(tmp_pc_list):
                    pc_list.append(
                        {"id": pc['iface_id'], "selected": "0", "label": pc['iface_id']})
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(pc_list, PTK_INTERNALERROR,
                              _("PDT_MDS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(pc_list, PTK_INTERNALERROR,
                          _("PDT_MDS_LOGIN_FAILURE"))

        res.setResult(pc_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class MDSCreateAndConfigureVSANInputs:
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
    vsan_id = Textbox(
        validation_criteria='int|min:1|max:4094',
        hidden='False',
        isbasic='True',
        helptext='VSAN ID',
        dt_type="string",
        static="False",
        api="",
        name="vsan_id",
        static_values="",
        label="VSAN",
        svalue="101",
        mapval="",
        mandatory="1",
        order="2",
        recommended="1")
    fc_list = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Interfaces to be configured in VSAN',
        dt_type="string",
        static="False",
        api="get_fc_list()|[mds_id:1:mds_id.value]",
        name="fc_list",
        label="Interfaces",
        static_values="",
        svalue="fc1/1|fc1/2|fc1/3|fc1/4",
        mapval="",
        mandatory="1",
        order="3",
        recommended="1")
    pc_list = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='Port Channel to be configured in VSAN',
        dt_type="string",
        static="False",
        api="get_portchannel_list()|[mds_id:1:mds_id.value]",
        name="pc_list",
        static_values="1",
        label="Port-Channels",
        svalue="1",
        mapval="",
        mandatory="1",
        order="4",
        recommended="1")


class MDSCreateAndConfigureVSANOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
