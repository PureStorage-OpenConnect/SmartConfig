from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo


class Test_PureAddHostToHostGroup:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("taskinfo in add host to hgroup")
        obj = result()
        data = {"status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        return obj.getResult()

    def get_hgroup_list(self, keys):
        obj = result()
        data = [{"id": "hg1", "selected": "1", "label": "HostGroup1"},
                {"id": "hg2", "selected": "0", "label": "HostGroup2"}]
        obj.setResult(data, PTK_OKAY, "success")
        return obj

    def get_host_list(self, keys):
        obj = result()
        data = [{"id": "0000111122223333", "selected": "1", "label": "Host1"},
                {"id": "0000111122222231", "selected": "0", "label": "Host2"}]
        obj.setResult(data, PTK_OKAY, "success")
        return obj

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("get volume rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
