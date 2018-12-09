from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *


class UCSGlobalPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("setting ucs global policy")
        res = get_ucs_handle()
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsGlobalPolicy(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        print "synchronize ucs to ntp rollback"
        return 0
