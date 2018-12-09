from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_PureCreateMultipleHosts:

    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        obj = result()
        loginfo(" Test_Pure Create Multiple Hosts:")
        name = "h1"
        data = {"name": name, "status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        loginfo("pure host create, name : {}".format(name))
        return obj.getResult()

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def rollback(self, name, inputs):
        loginfo("host create rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res
