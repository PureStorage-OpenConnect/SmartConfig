from pure_dir.infra.logging.logmanager import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.components.storage.mds.mds_tasks import *


class Test_FACreateMultipleHosts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Test_FACreateMultipleHosts")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Test_FACreateMultipleHosts rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
