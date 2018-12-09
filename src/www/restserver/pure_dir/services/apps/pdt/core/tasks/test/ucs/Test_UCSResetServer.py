from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_UCSResetServer:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Test_UCSResetServer")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Test_UCSResetServer rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
