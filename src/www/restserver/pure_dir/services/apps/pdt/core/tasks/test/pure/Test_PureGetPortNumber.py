
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_PureGetPortNumber:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        obj = result()
        loginfo(" Test_PureGetPortNumber:")
        data = {"pwwn": "524A937CDABE5C00", "status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        loginfo("pure get port number data is : {}".format(data))
        return obj.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Get port number rollback")
        obj = result()
        obj.setResult(None, PTK_OKAY, "success")
        return obj

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
