from pure_dir.infra.apiresults import PTK_OKAY, result
from pure_dir.infra.logging.logmanager import loginfo


class Test_PureCreateMultipleVolumes:

    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        obj = result()
        loginfo(" Test_Pure Create Multiple Volumes")
        name = "vol1"
        data = {"name": name, "status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        loginfo("pure create volume, name : {}".format(name))
        return obj.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("volume create rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res
