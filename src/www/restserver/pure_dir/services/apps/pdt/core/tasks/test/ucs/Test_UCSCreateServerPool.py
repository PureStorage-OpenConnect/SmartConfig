from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_UCSCreateServerPool:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Create Server Pool")
        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print("Create Server Pool rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def ucsmservers(self, keys):
        res = result()
        val = [{"id": "sys/chassis-3/blade-3",
                "label": "blade_server",
                "selected": "1"},
               {"id": "sys/chassis-3/blade-1",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-3/blade-7",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-4/blade-1",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-4/blade-2",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-5/blade-1",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-5/blade-2",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-5/blade-3",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-5/blade-4",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-5/blade-5",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-6/blade-1",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-7/blade-3",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-7/blade-1",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-7/blade-5",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/chassis-7/blade-7",
                "label": "blade_server",
                "selected": "0"},
               {"id": "sys/rack-unit-1",
                "label": "rack",
                "selected": "0"},
               {"id": "sys/rack-unit-2",
                "label": "rack",
                "selected": "0"},
               {"id": "sys/rack-unit-3",
                "label": "rack",
                "selected": "0"},
               {"id": "sys/rack-unit-4",
                "label": "rack",
                "selected": "0"},
               {"id": "sys/rack-unit-5",
                "label": "rack",
                "selected": "0"},
               {"id": "sys/rack-unit-6",
                "label": "rack",
                "selected": "0"},
               {"id": "sys/rack-unit-7",
                "label": "rack",
                "selected": "0"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
