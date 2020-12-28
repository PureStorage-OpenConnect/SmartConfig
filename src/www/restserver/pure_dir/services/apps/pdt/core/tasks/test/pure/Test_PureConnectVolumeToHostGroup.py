from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.infra.apiresults import PTK_OKAY, result


class Test_PureConnectVolumeToHostGroup:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        print("taskinfo in connect vol to hgroup ", taskinfo)
        obj = result()
        data = {"status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        return obj.getResult()

    def get_hgroup_list(self, keys):
        obj = result()
        print("comes in get hgroup list")
        data = [{"id": "hg1", "selected": "1", "label": "HostGroup3"},
                {"id": "hg2", "selected": "0", "label": "HostGroup4"}]
        obj.setResult(data, PTK_OKAY, "success")
        return obj

    def get_volume_list(self, keys):
        obj = result()
        print("comes in get volume list")
        data = [{"id": "2057EC093C094AEE00011010", "selected": "1", "label": "vol1"},
                {"id": "2057EC093C094AEE00011011", "selected": "0", "label": "vol2"}]
        obj.setResult(data, PTK_OKAY, "success")
        return obj

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def rollback(self, inputs, outputs, logfile):
        loginfo("connect host with volume rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
