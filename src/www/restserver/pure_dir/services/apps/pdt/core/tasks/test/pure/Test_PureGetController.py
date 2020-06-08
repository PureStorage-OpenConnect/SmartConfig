from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo


class Test_PureGetController:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        obj = result()
        loginfo(" Test_PureGetController::")
        data = {"name": "CT0.FC1", "status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        loginfo("pure get controller data is : {}".format(data))
        return obj.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Get controller rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
