from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.storage.mds.mds_tasks import *
from pure_dir.components.common import get_device_credentials, get_device_list
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="MDSEnableFeatures",
    task_name="Enable Features",
    task_desc="Enable the features in the MDS switch",
    task_type="MDS"
)


class MDSEnableFeatures:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = result()
        loginfo("Enabling features for MDS")
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                res = obj.enable_features(taskinfo['inputs'], logfile)
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
        loginfo("Rollback - EnableFeatures for MDS")
        cred = get_device_credentials(
            key="mac", value=inputs['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                res = obj.disable_features(inputs, logfile)
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

    def get_feature_list(self, keys):
        res = result()
        loginfo("Getting MDS feature list...")
        flist = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "mds_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(flist, PTK_OKAY, _("PDT_SUCCESS_MSG"))
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = MDS(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                feat_list = obj.get_feature_list()
                for index, feature in enumerate(feat_list):
                    flist.append(
                        {"id": feature, "selected": "0", "label": feature})

            else:
                loginfo("Unable to login to the MDS")
                res.setResult(flist, PTK_INTERNALERROR,
                              _("PDT_MDS_LOGIN_FAILURE"))
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(flist, PTK_INTERNALERROR,
                          _("PDT_MDS_LOGIN_FAILURE"))

        res.setResult(flist, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res


class MDSEnableFeaturesInputs:
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
    feature_list = Multiselect(
        hidden='False',
        isbasic='True',
        helptext='List of available features',
        dt_type="string",
        static="False",
        api="get_feature_list()|[mds_id:1:mds_id.value]",
        name="feature_list",
        label="Features",
        static_values="",
        svalue="npiv|fport-channel-trunk",
        mapval="",
        mandatory="1",
        order="2",
        recommended="1")


class MDSEnableFeaturesOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
