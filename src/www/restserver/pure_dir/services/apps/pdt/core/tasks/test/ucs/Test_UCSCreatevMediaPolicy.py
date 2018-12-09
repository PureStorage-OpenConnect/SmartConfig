from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_UCSCreatevMediaPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Create vMedia Policy")
        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "Create vMedia Policy rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def esxiimages(self, keys):
        print "inside esxiimages"
        res = result()

        val = [{"id": "ESX5.0", "selected": "1", "label": "ESX 5.0"}, {
            "id": "ESX6.0", "selected": "0", "label": "ESX 6.0"}]

        res.setResult(val, PTK_OKAY, "success")
        return res
