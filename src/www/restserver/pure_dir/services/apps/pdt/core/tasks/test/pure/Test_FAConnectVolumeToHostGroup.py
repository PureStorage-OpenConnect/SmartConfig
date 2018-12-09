from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.storage.mds.mds_tasks import *


class Test_FAConnectVolumeToHostGroup:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Test_FAConnectVolumeToHostGroup")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("rollback Test_FAConnectVolumeToHostGroup")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
