from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreateFCPortChannels:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Test Create_FC_Port_Channel")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def ucsgetfcports(self, keys):
        ports_list = []
        res = result()
        # TODO:returning first 16 ports that can be configured as Unified Ports Change later
        for i in range(1, 17):
            ports_entity = {
                "id": str(i), "selected": "0", "label": "Port " + str(i)}
            ports_list.append(ports_entity)
        res.setResult(ports_list, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        print "Create FC Port Channels rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
