from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_UCSCreateHostFirmwarePackage:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("test Create Host Firmware Package")
        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print("Create Host Firmware Package rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getexcludedcomp(self, keys):
        res = result()
        val = [{"id": "local-disk", "selected": "1", "label": "Local Disk"},
               {"id": "adaptor", "selected": "0", "label": "Adaptor"},
               {"id": "host-nic-optionrom", "selected": "0",
                   "label": "Host NIC Option ROM"},
               {"id": "blade-controller", "selected": "0", "label": "CIMC"},
               {"id": "board-controller", "selected": "0",
                   "label": "Board Controller"},
               {"id": "flexflash-controller", "selected": "0",
                   "label": "Flex Flash Controller"},
               {"id": "blade-bios", "selected": "0", "label": "BIOS"},
               {"id": "psu", "selected": "0", "label": "PSU"},
               {"id": "sas-expander", "selected": "0", "label": "SAS Expander"},
               {"id": "storage-controller-onboard-device", "selected": "0",
                "label": "Storage Controller Onboard Device"},
               {"id": "storage-dev-bridge", "selected": "0",
                   "label": "Storage Device Bridge"},
               {"id": "graphics-card", "selected": "0", "label": "GPU"},
               {"id": "host-hba-optionrom", "selected": "0",
                   "label": "HBA Option ROM"},
               {"id": "sas-exp-reg-fw", "selected": "0",
                   "label": "SAS Expander Regular Firmware"},
               {"id": "host-nic", "selected": "0", "label": "Host NIC"},
               {"id": "storage-controller", "selected": "0",
                   "label": "Storage Controller"},
               {"id": "storage-controller-onboard-device-cpld", "selected": "0",
                "label": "Storage Controller Onboard Device Cpld"}
               ]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
