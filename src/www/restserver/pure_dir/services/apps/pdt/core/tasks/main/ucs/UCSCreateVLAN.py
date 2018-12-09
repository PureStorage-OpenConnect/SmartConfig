from pure_dir.infra.logging.logmanager import *
from pure_dir.components.compute.ucs.ucs_tasks import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs.common import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *

metadata = dict(
    task_id="UCSCreateVLAN",
    task_name="Create VLAN",
    task_desc="Create VLAN in UCS",
    task_type="UCSM"
)


class UCSCreateVLAN:
    def __init__(self):
        pass

    def execute(self, taskinfo, logfile):
        loginfo("create_VLAN")

        res = get_ucs_handle(taskinfo['inputs']['fabric_id'])

        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        obj = res.getResult()

        res = obj.ucsCreateVLAN(taskinfo['inputs'], logfile)

        obj.release_ucs_handle()
        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("UCS VLAN creation rollback")
        res = get_ucs_handle(inputs['fabric_id'])
        if res.getStatus() != PTK_OKAY:
            return res
        obj = res.getResult()

        res = obj.ucsDeleteVLAN(
            inputs, outputs, logfile)
        obj.release_ucs_handle()
        return res

    def getfilist(self, keys):
        res = result()
        ucs_list = get_device_list(device_type="UCSM")
        res.setResult(ucs_list, PTK_OKAY, "success")
        return res

    def multicastpolicies(self, keys):
        mcast_pol_list = []
        res = result()
        fabricid = getArg(keys, 'fabric_id')

        if fabricid == None:
            res.setResult(mcast_pol_list, PTK_OKAY, "success")
            return res

        res = get_ucs_login(fabricid)
        if res.getStatus() != PTK_OKAY:
            return parseTaskResult(res)
        handle = res.getResult()

        ret = result()
        mcast_pol = handle.query_classid("fabricMulticastPolicy")
        for mcast in mcast_pol:
            mcast_pol_list.append(
                {"id": mcast.name, "selected": "0", "label": mcast.name})
        mcast_pol_list.append({"id": "", "selected": "1", "label": "not-set"})
        ucsm_logout(handle)
        ret.setResult(mcast_pol_list, PTK_OKAY, "success")
        return ret


class UCSCreateVLANInputs:
    fabric_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", api="getfilist()", name="fabric_id",
                         label="UCS Fabric Name", static_values="", svalue="", mapval="", mandatory="1", order=1)
    vlan_name = Textbox(validation_criteria='str|min:1|max:128',  hidden='False', isbasic='True', helptext='VLAN Name', api="", dt_type="string", label="VLAN Name", mapval="0", name="vlan_name",
                        static="False", svalue="Native-VLAN", mandatory='1', static_values="", order=2, recommended="1")
    vlan_id = Textbox(validation_criteria='int|min:100|max:2067',  hidden='False', isbasic='True', helptext='VLAN ID', api="", dt_type="string", label="VLAN IDs", mapval="0", name="vlan_id",
                      static="False", svalue="2", mandatory='1', static_values="", order=3, recommended="1")
    vlan_type = Radiobutton(hidden='False', isbasic='True', helptext='Scope of VLAN', api="", dt_type="string", label="VLAN Scope", mapval="0", name="vlan_type", static="True",
                            static_values="fabric/lan:1:Common/Global|fabric/lan/A:0:Fabric A|fabric/lan/B:0:Fabric B", svalue="fabric/lan", mandatory='1', order=4)
    sharing = Radiobutton(hidden='False', isbasic='True', helptext='Sharing type', api="", dt_type="string", label="Sharing Type", mapval="0", name="sharing", static="True",
                          static_values="none:1:None|pri:0:Primary|isolated:0:Isolated|community:0:Community", svalue="none", mandatory='1', order=5)


class UCSCreateVLANOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
    vlan_name = Output(dt_type="string", name="vlan_name",
                       tvalue="Native-VLAN")
