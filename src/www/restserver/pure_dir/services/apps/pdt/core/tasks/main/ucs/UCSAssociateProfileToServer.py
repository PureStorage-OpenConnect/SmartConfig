from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *


class UCSAssociateProfileToServer:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("associate_profile_to_server")
        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsAssociateProfileToServer(taskinfo['inputs'], fp)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("associate_profile_to_server_rollback")
        return 0
