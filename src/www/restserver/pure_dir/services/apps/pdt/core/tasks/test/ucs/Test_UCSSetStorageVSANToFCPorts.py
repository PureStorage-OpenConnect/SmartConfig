from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_UCSSetStorageVSANToFCPorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Test_UCSSetStorageVSANToFCPorts")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Test_UCSSetStorageVSANToFCPorts rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def ucs_get_fc_ports(self, keys):
        res = result()
        val=[{"id": "A", "selected": "0", "label": "Port " + "A"},{"id": "B", "selected": "0", "label": "Port " + "B"}]
        res.setResult(val, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    
    def getstoragevsan(self, keys):
    	res = result()
	val=[{"id": "VSAN Fabric A", "selected": "0", "label":"VSAN Fabric A"},
	     {"id": "VSAN Fabric B", "selected": "1", "label": "VSAN Fabric A"}]
	res.setResult(val, PTK_OKAY, "success")
        return res
                                                                                                                                                                                                                                  	
