from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_UCSCreateLocalDiskConfigurationPolicy:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Create Local Disk Configuration Policy")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print("Create Local Disk Configuration Policy rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getdiskconfigmodes(self, keys):
        res = result()
        val = [{"id": "any-configuration",
                "selected": "1",
                "label": "Any Configuration"},
               {"id": "raid-mirrored",
                "selected": "0",
                "label": "RAID 1 Mirrored"},
               {"id": "raid-striped",
                "selected": "0",
                "label": "RAID 0 Striped"},
               {"id": "no-raid",
                "selected": "0",
                "label": "No RAID"},
               {"id": "raid-striped-parity",
                "selected": "0",
                "label": "RAID 5 Striped Parity"},
               {"id": "raid-striped-dual-parity",
                "selected": "0",
                "label": "RAID 6 Striped Dual Parity"},
               {"id": "raid-mirrored-striped",
                "selected": "0",
                "label": "RAID 10 Mirrored and Striped"},
               {"id": "raid-striped-parity-striped",
                "selected": "0",
                "label": "RAID 50 Striped Parity and Striped"},
               {"id": "raid-striped-dual-parity-striped",
                "selected": "0",
                "label": "RAID 60 Striped Dual Parity and Striped"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
