from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_UCSEnableServerandUplinkPorts:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print("Enable Server and Uplink Ports rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def ucsmethports(self, keys):
        res = result()
        val = [
            {
                "id": "39", "label": "Port 39", "selected": "1"}, {
                "id": "29", "label": "Port 29", "selected": "0"}, {
                "id": "19", "label": "Port 19", "selected": "0"}, {
                    "id": "38", "label": "Port 38", "selected": "0"}, {
                        "id": "28", "label": "Port 28", "selected": "0"}, {
                            "id": "18", "label": "Port 18", "selected": "0"}, {
                                "id": "37", "label": "Port 37", "selected": "0"}, {
                                    "id": "27", "label": "Port 27", "selected": "0"}, {
                                        "id": "17", "label": "Port 17", "selected": "0"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
