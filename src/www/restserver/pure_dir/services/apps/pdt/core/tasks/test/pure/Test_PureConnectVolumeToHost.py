from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo


class Test_PureConnectVolumeToHost:

    def execute(self, taskinfo, fp):
        obj = result()
        loginfo("Connect volume to Host")
        data = {"status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        return obj.getResult()

    def get_host_list(self, keys):
        obj = result()
        data = [{"id": "0000111122223333", "selected": "1", "label": "Host1"},
                {"id": "0000111122222231", "selected": "0", "label": "Host2"}]
        obj.setResult(data, PTK_OKAY, "success")
        return obj

    def get_volume_list(self, keys):
        obj = result()
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
        return 0
