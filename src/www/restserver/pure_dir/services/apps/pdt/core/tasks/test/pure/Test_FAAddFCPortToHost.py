from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_FAAddFCPortToHost:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Test_Add Port to Host")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Test_AddPorttoHost rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
