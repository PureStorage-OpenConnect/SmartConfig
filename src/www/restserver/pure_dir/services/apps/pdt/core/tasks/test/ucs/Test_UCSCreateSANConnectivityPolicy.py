from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreateSANConnectivityPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Test create_SAN_connectivity_policy")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "create san connectivity policy rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getwwnn(self, keys):
        res = result()
        val = [{"id": "WWNN_Pool", "selected": "1", "label": "WWNN_Pool"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
