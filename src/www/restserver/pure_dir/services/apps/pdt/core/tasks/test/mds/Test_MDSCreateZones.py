from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_MDSCreateZones:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("Test MDS Create Zones")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        loginfo("Test MDS Create Zones rollback")
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def get_mds_list(self, keys):
        res = result()
        mds_list = [{'label': 'mds-a', 'id': 'AB:CD:EF:GH:IJ:KL', 'selected': '0'},
                    {'label': 'mds-b', 'id': 'MN:OP:QR:ST:UV:WX', 'selected': '0'}]
        res.setResult(mds_list, PTK_OKAY, "success")
        return res

    def get_vsan_list(self, keys):
        res = result()
        vsan_list = ['101']
        res.setResult(vsan_list, PTK_OKAY, "success")
        return res

    def get_device_aliases(self, keys):
        res = result()
        devalias_list = ['FlashArray-CT0FC0', 'FlashArray-CT0FC2', 'FlashArray-CT1FC0',
                         'FlashArray-CT1FC2', 'VM-Host-Infra-01', 'VM-Host-Infra-02']
        res.setResult(devalias_list, PTK_OKAY, "success")
        return res
