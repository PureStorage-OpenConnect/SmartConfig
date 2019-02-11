from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *


class Test_UCSCreateMgmtvNiCTemplate:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Test create_Management_vNIC_Template")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "create Management vNIC Template rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getfis(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getpeerredundancytempl(self, keys):
        ret = result()
        vnic_templ_list = [
            {
                "id": "vNIC_Mgmt_A", "label": "vNIC_Mgmt_A", "selected": "0"}, {
                "id": "vNIC_Mgmt_B", "label": "vNIC_Mgmt_B", "selected": "0"}, {
                "id": "vNIC_vMotion_A", "label": "vNIC_vMotion_A", "selected": "0"}, {
                    "id": "vNIC_vMotion_B", "label": "vNIC_vMotion_B", "selected": "0"}, {
                        "id": "vNIC_App_A", "label": "vNIC_App_A", "selected": "0"}, {
                            "id": "vNIC_App_B", "label": "vNIC_App_B", "selected": "0"}, {
                                "id": "", "label": "not-set", "selected": "1"}]
        ret.setResult(vnic_templ_list, PTK_OKAY, "success")
        return ret

    def getVLANs(self, keys):
        ret = result()
        vlans_list = [{"id": "default",
                       "label": "default",
                       "selected": "0"},
                      {"id": "default",
                       "label": "default",
                       "selected": "0"},
                      {"id": "Native-VLAN",
                       "label": "Native-VLAN",
                       "selected": "0"},
                      {"id": "IB-Mgmt",
                       "label": "IB-Mgmt",
                       "selected": "0"},
                      {"id": "vMotion",
                       "label": "vMotion",
                       "selected": "0"},
                      {"id": "VM-App-1",
                       "label": "VM-App-1",
                       "selected": "0"}]
        ret.setResult(vlans_list, PTK_OKAY, "success")
        return ret

    def setNativeVLANs(self, keys):
        ret = result()
        native_vlans = [{"id": "IB-Mgmt", "label": "IB-Mgmt", "selected": "0"},
                        {"id": "Native-VLAN", "label": "Native-VLAN", "selected": "0"}]
        ret.setResult(native_vlans, PTK_OKAY, "success")
        return ret

    def getmacpools(self, keys):
        ret = result()
        mac_list = [{"id": "default",
                     "label": "default(0/0)",
                     "selected": "0"},
                    {"id": "MAC_Pool_B",
                     "label": "MAC_Pool_B(32/32)",
                     "selected": "0"},
                    {"id": "MAC_Pool_A",
                     "label": "MAC_Pool_A(32/32)",
                     "selected": "0"}]
        ret.setResult(mac_list, PTK_OKAY, "success")
        return ret

    def getnwctrlpolicy(self, keys):
        ret = result()
        nw_ctrl_list = [{"id": "default", "label": "default", "selected": "0"},
                        {"id": "Enable-CDP", "label": "Enable-CDP", "selected": "0"}]
        ret.setResult(nw_ctrl_list, PTK_OKAY, "success")
        return ret

    def getstatsthresholdpolicy(self, keys):
        ret = result()
        stats_list = [{"id": "default", "label": "default", "selected": "1"},
                      {"id": "", "label": "not-set", "selected": "0"}]
        ret.setResult(stats_list, PTK_OKAY, "success")
        return ret
