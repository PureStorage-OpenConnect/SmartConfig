from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import get_device_list
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult, getArg
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *


class UCSCreateServiceProfileFromTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_service_profile_from_template")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateServiceProfileFromTemplate(
            taskinfo['inputs'], fp)
        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        print "create service profile from template rollback"
        res = result()
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        print ucs_list, res
        return res

    def gettemplate(self, keys):
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
        s = handle.query_classid("lsServer")
        selected = "1"
        for w in s:
            if w.type == 'initial-template':
                if temp_list:
                    selected = "0"
                temp_list.append(
                    {"id": w.name, "selected": selected, "label": w.name})
        ucsm_logout(handle)
        res.setResult(temp_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
