from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreateServerPoolQualificationPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Create_Server_Pool_Qualification_Policy")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "Create Server Pool Qualification Policy rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getprocessorarch(self, keys):
        res = result()
        val = [
            {
                "id": "Opteron", "selected": "0", "label": "Opteron"}, {
                "id": "Turion_64", "selected": "0", "label": "Turion 64"}, {
                "id": "Dual-Core_Opteron", "selected": "0", "label": "Dual Core Opteron"}, {
                    "id": "Pentium_4", "selected": "0", "label": "Pentium 4"}, {
                        "id": "Xeon", "selected": "0", "label": "Xeon"}, {
                            "id": "Xeon_MP", "selected": "0", "label": "Xeon MP"}, {
                                "id": "Any", "selected": "1", "label": "Any"}, {
                                    "id": "Intel_P4_C", "selected": "0", "label": "Intel P4 C"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
