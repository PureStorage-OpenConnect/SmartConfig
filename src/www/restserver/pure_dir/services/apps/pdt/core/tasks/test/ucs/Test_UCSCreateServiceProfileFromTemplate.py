from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreateServiceProfileFromTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("simulated create_service_profile_from_template")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def gettemplate(self, keys):
        res = result()
        val = [{"id": "Templateeaxample",
                "selected": "1", "label": "Example template"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        print "create service profile from template rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
