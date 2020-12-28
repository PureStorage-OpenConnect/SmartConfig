from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_FlashArrayConfigureNI:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test Test_FAConnectVolumeToFCHost")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("rollback Test_FAConnectVolumeToFCHost")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def get_iscsi_intf_list(self, keys):
        res = result()
        res.setResult(
            [{'label': 'eth0', 'id': 'eth0', 'selected': '1'}], PTK_OKAY, "success")
        return res

    def purelist(self, keys):
        """
        :param keys: task input describing array type e.g. PURE
        :type keys: dict
        :returns: list of FlashArrays

        """
        res = result()
        pure_list = [{'label': 'pure-a', 'id': 'AB:CD', 'selected': '0'},
                     {'label': 'pure-b', 'id': 'EF:GH', 'selected': '0'}]

        res.setResult(pure_list, PTK_OKAY, "success")
        return res
