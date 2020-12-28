from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_NEXUS9kSetGlobalConfigurations:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("NEXUS Set Global Configurations")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print("NEXUS Set Global Configurations rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getnexuslist(self, keys):
        res = result()
        nexus_list = [{'label': 'nexus-a', 'id': 'AB:CD', 'selected': '0'},
                      {'label': 'nexus-b', 'id': 'EF:GH', 'selected': '0'}]
        res.setResult(nexus_list, PTK_OKAY, "success")
        return res
