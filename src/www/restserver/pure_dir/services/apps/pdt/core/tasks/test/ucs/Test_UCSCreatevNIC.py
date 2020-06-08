from pure_dir.infra.logging.logmanager import loginfo 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import getMappedOutputs
from pure_dir.infra.apiresults import PTK_OKAY, result

class Test_UCSCreatevNIC:
    def __init__(self):
        pass

    def execute(self, taskinfo, fp):
        loginfo("Test create_vNIC")

        res = getMappedOutputs(taskinfo['jid'], taskinfo['texecid'])
        return res.getResult()

    def rollback(self, inputs, outputs, logfile):
        print "create vNIC rollback"
        res = result()
        res.setResult(None, PTK_OKAY, "success")
        return res

    def getfilist(self, keys):
        res = result()
        val = [{"id": "A", "selected": "1", "label": "Fabric Interconnect A(primary)"}, {
            "id": "B", "selected": "0", "label": "Fabric Interconnect B (subordinate)"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getlanconpolicylist(self, keys):
        res = result()
        val = [{"id": "testlanpolicy", "selected": "0", "label": 'testlanpolicy'},
               {"id": "", "selected": "1", "label": "not-set"}]
        res.setResult(val, PTK_OKAY, "success")
        return res

    def getadapterpolicy(self, keys):
        res = result()
        adapter_pol = [
            {
                "id": "linux", "selected": "0", "label": "Linux"}, {
                "id": "smbclient", "selected": "0", "label": "SMBCLient"}, {
                "id": "smbserver", "selected": "0", "label": "SMBServer"}, {
                    "id": "sriov", "selected": "0", "label": "SRIOV"}, {
                        "id": "solaris", "selected": "0", "label": "Solaris"}, {
                            "id": "VMWare", "selected": "0", "label": "VMWare"}, {
                                "id": "VMWarePassThrough", "selected": "0", "label": "VMWarePassThrough"}, {
                                    "id": "Windows", "selected": "0", "label": "Windows"}, {
                                        "id": "default", "selected": "0", "label": "default"}, {
                                            "id": "usNIC", "selected": "0", "label": "usNIC"}, {
                                                "id": "usNICOracleRAC", "selected": "0", "label": "usNICOracleRAC"}]
        res.setResult(adapter_pol, PTK_OKAY, "success")
        return res

    def getvnictemplate(self, keys):
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
