
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_PureAddPortToHost:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        obj = result()
        loginfo(" add Port to Host")
        data = {"wwn": "1111222233334444", "status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        loginfo("pure add port to host data : {}".format(data))
        return obj.getResult()

    def get_ports(self, keys):
        obj = result()
        data = [{"id": "5001500150015080", "selected": "1", "label": "CT0.FC0"},
                {"id": "5001500150015081", "selected": "0", "label": "CT0.FC1"}]
        obj.setResult(data, PTK_OKAY, "success")
        print "obj data going is ", obj.getResult()
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
        loginfo("add port to host rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
