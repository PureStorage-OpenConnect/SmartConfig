from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreatevHBA:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Test create_vHBA")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "vHBA Template creation rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getsanconnectivity(self, keys):
        res = result()
        val = [{"id": "Infra-SAN-Policy",
                "selected": "1", "label": "Infra-SAN-Policy"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getvhbatemplate(self, keys):
        res = result()
        val = [{"id": "vHBA_template_A",
                "selected": "1", "label": "vHBA_template_A"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
