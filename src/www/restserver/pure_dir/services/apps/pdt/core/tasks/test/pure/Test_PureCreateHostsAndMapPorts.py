from pure_dir.infra.apiresults import PTK_OKAY
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import result


class Test_PureCreateHostsAndMapPorts:

    def __init__(self):
        pass

    def execute(self, inputs, logfile):
        loginfo("pure host create, input is : {} ".format(input))
        obj = result()
        name = "h1"
        data = {"name": name, "status": "SUCCESS"}
        obj.setResult(data, PTK_OKAY, "success")
        loginfo("pure host create and Map name : {}".format(name))
        return obj.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("host create rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def purelist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "TestArray1"}, {
            "id": "B", "selected": "0", "label": "TestArray2"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def get_ports(self, keys):
        obj = result()
        data = [{"id": "5001500150015080", "selected": "1", "label": "CT0.FC0"},
                {"id": "5001500150015081", "selected": "0", "label": "CT0.FC1"}]
        obj.setResult(data, PTK_OKAY, "success")
        return obj
