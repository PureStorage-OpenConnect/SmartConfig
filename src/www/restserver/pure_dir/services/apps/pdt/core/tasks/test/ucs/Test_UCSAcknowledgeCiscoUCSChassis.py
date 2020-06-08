from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSAcknowledgeCiscoUCSChassis:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test acknowledge_cisco_ucs_chassis")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "acknowledge cisco ucs chassis"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def ucsmchassis(self, keys):
        res = result()
        val = [
            {
                "id": "3", "label": "Chassis 3", "selected": "1"}, {
                "id": "4", "label": "Chassis 4", "selected": "0"}, {
                "id": "5", "label": "Chassis 5", "selected": "0"}, {
                    "id": "6", "label": "Chassis 6", "selected": "0"}, {
                        "id": "7", "label": "Chassis 7", "selected": "0"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
