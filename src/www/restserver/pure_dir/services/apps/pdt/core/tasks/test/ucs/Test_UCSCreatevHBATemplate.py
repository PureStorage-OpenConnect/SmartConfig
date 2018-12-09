from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_UCSCreatevHBATemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Test create_vHBA Template")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "vHBA Template creation rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getwwpn(self, keys):
        res = result()
        val = [
            {"id": "WWWPN_Pool_B(24/32)", "selected": "1", "label": "WWWPN_Pool_B(24/32)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getvsan(self, keys):
        res = result()
        val = [{"id": "VSAN_A", "selected": "1", "label": "VSAN_A"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
