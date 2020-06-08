from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result
from pytz import common_timezones


class Test_UCSSynchronizeUCStoNTP:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("test synchronize ucs to ntp")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "synchronize ucs to ntp rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def gettimezones(self, keys):
        res = result()
        tzlist = []
        for tz in common_timezones:
            tz_entity = {"id": tz, "label": tz, "selected": "0"}
            tzlist.append(tz_entity)
        res.setResult(tzlist, PTK_OKAY, "success")
        return res
