from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_UCSCreateServiceProfileTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_service_profile_from_template")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("create service profile from template rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getuuidpool(self, keys):
        res = result()
        val = [{"id": "UUID_Pool", "selected": "1", "label": "UUID_Pool"}, {
            "id": "default", "selected": "0", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getsanconnectivity(self, keys):
        res = result()
        val = [{"id": "Infra-SAN-Policy",
                "selected": "1", "label": "Infra-SAN-Policy"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getlanconnectivity(self, keys):
        res = result()
        val = [{"id": "Infra-LAN-Policy",
                "selected": "1", "label": "Infra-LAN-Policy"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getpowerpolicy(self, keys):
        res = result()
        val = [{"id": "default", "selected": "1", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getlocaldiskpolicy(self, keys):
        res = result()
        val = [{"id": "default", "selected": "1", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getbootpolicy(self, keys):
        res = result()
        val = [{"id": "BOOT-FC-A", "selected": "1", "label": "BOOT-FC-A"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getvmediapolicy(self, keys):
        res = result()
        val = [{"id": "ESXi-6.0U2-HTTP",
                "selected": "1", "label": "ESXi-6.0U2-HTTP"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getbiospolicy(self, keys):
        res = result()
        val = [{"id": "default", "selected": "1", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getmaintenancepolicy(self, keys):
        res = result()
        val = [{"id": "default", "selected": "1", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getqualifier(self, keys):
        res = result()
        val = [{"id": "default", "selected": "1", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getpoolassignment(self, keys):
        res = result()
        val = [{"id": "default", "selected": "1", "label": "default"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
