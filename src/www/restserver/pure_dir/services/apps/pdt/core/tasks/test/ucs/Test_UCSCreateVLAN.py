from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreateVLAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("create_VLAN")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "VLAN creation rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def multicastpolicies(self, keys):
        ret = result()
        mcast_pol_list = [{"id": "default", "label": "default", "selected": "0"}, {
            "id": "", "label": "not-set", "selected": "1"}]
        ret.setResult(mcast_pol_list, PTK_OKAY, "success")
        return ret

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
