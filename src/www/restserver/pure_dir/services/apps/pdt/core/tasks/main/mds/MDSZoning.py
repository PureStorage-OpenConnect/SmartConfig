from pure_dir.infra.logging.logmanager import *
from pure_dir.components.storage.mds.mds_tasks import *
from pure_dir.components.storage.mds.mds import *
from pure_dir.components.compute.ucs.ucs import UCSManager
from pure_dir.components.common import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_data_structures import *
import time


class MDSZoning:
    def __init__(self):
        pass

    def prepare(self, jobid, texecid, inputs):
        res = result()
        job_xml = get_job_file(jobid)
        fd = None
        try:
            fd = open(job_xml, 'r')
        except IOError:
            loginfo("Could not read file: %s" % job_xml)

        fa_alias_template = "FlashArray-CT%sFC%s-fabric%s"
        bs_alias_template = "VM-Host-FC-0%s-%s"

        # Getting the required params
        doc = xmltodict.parse(fd.read())
        mds_id = [[switch['@value'] for switch in task['args']['arg'] if switch['@name'] == "mds_id"][0]
                  for task in doc['workflow']['tasks']['task'] if task['@texecid'] == texecid][0]
        switch_tag = mds_id.split('_')[-1].upper()

        mds_mac_addr = [mac['value'] for mac in inputs if mac['name'] == mds_id][0]
	ucs_mac_addr = [mac['value'] for mac in inputs if mac['name'] == 'ucs_switch_a'][0]

        inp_dict = {"keyvalues": [
            {"key": "mds_id", "value": mds_mac_addr}, {"key": "group", "value": "1"}]}

        # Task1 - Creating device alias names

        flogi_sess_list = self.get_flogi_sessions(inp_dict).getResult()
	ucsm_sp_pwwn_list = self.get_ucsm_sp_pwwn(ucs_mac_addr)
	if ucsm_sp_pwwn_list == []:
	    loginfo("Failed to get pwwn of blade servers from UCSM for MDS Zoning")

        alias_list = []
        zone_list = []
        for flogi in flogi_sess_list:
            if flogi['pwwn'].lower() in ucsm_sp_pwwn_list:
	        # Alias for blade servers. UCSM itself accepts WWN even without OUI - 00:25:B5 eventhough it is recommended
                alias_name = bs_alias_template % (
                    str(int(flogi['pwwn'][-1])+1), switch_tag.upper())
                zone_list.append(alias_name.encode('utf-8'))
            elif get_oui(flogi['pwwn']) == oui_pure:
	        # Alias for flash array ports. FlashArray ports' WWN comes with OUI from vendor itself.
                alias_name = fa_alias_template % (
                    flogi['pwwn'][-2], flogi['pwwn'][-1], switch_tag.upper())
            else:
                # This is done mainly to skip the UCS entry from flogi database
                continue
            if alias_name:
                alias_dict = {}
                alias_dict['iface_id'] = {
                    "ismapped": "0", "value": flogi['iface_id']}
                alias_dict['pwwn'] = {"ismapped": "0", "value": flogi['pwwn']}
                alias_dict['alias_name'] = {
                    "ismapped": "0", "value": alias_name.encode("utf-8")}
                alias_list.append(alias_dict)

        loginfo("Alias_list: %s" % str(alias_list))
        val = "|".join([str(k) for k in alias_list])
        job_input_save(jobid, texecid, 'flogi_list', val)

        # Task2 - Creating zones
        loginfo("Zone_list: %s" % str(zone_list))
        zone_lst = []
        for idx, zone in enumerate(zone_list):
            zone_dict = {}
            zone_dict['zone_name'] = {"ismapped": "0", "value": zone}
            zone_dict['zone_members'] = {"ismapped": "2", "value": (
                [alias['alias_name']['value'] for alias in alias_list if alias['alias_name']['value'] not in zone_list] + [zone])}
            zone_lst.append(zone_dict)

        val = "|".join([str(k) for k in zone_lst])
        job_input_save(jobid, texecid, 'zones', val)

        # Task3 - Creating zoneset
        zoneset_dict = {}
        vsan_id = getGlobalArg(inputs, 'vsan_%s' % switch_tag.lower())
        zoneset_name = "flashstack-zoneset-vsan-%s" % vsan_id
        zoneset_dict['zoneset_name'] = {
            "ismapped": "0", "value": zoneset_name.encode("utf-8")}
        zoneset_dict['zoneset_members'] = {"ismapped": "2", "value": zone_list}
        job_input_save(jobid, texecid, 'zoneset', str(zoneset_dict))

        res.setResult(None, PTK_OKAY, "success")
        return res

    def execute(self, taskinfo, logfile):
        res = result()
        cred = get_device_credentials(
            key="mac", value=taskinfo['inputs']['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                # Creating device aliases
                loginfo("Creating device aliases for MDS")
                res = obj.create_device_aliases(taskinfo['inputs'], logfile)
                if res.getStatus() == PTK_OKAY:
                    # Creating zones
                    loginfo("Creating zones in MDS")
                    res = obj.create_zones(taskinfo['inputs'], logfile)
                    if res.getStatus() == PTK_OKAY:
                        # Creating zoneset
                        loginfo("Creating zoneset in MDS")
                        res = obj.create_zonesets(taskinfo['inputs'], logfile)
                        if res.getStatus() != PTK_OKAY:
                            obj.delete_zones(self.get_zones(
                                taskinfo['inputs']), logfile)
                            obj.delete_device_aliases(
                                self.get_zoneset(taskinfo['inputs']), logfile)
                            loginfo("Failed to create zoneset")
                            res.setResult(False, PTK_INTERNALERROR,
                                          "Zoneset Creation failed")
                        else:
                            loginfo("MDSZoning task executed successfully")
                            customlogs(
                                "MDSZoning task executed successfully", logfile)
                            # Waiting for FlashArray to discover host pwwn
                            time.sleep(30)
                            res.setResult(
                                parseResult(res)['data'], PTK_OKAY, "MDSZoning task executed successfully")
                    else:
                        loginfo("Failed to create zones")
                        obj.delete_device_aliases(
                            self.get_alias(taskinfo['inputs']), logfile)
                        res.setResult(False, PTK_INTERNALERROR,
                                      "Zone Creation failed")
                else:
                    loginfo("Failed to create device aliases for the interfaces")
                    res.setResult(False, PTK_INTERNALERROR,
                                  "Device Alias Creation failed")
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(False, PTK_INTERNALERROR,
                              "Unable to login to the MDS")
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

        return parseTaskResult(res)

    def rollback(self, inputs, outputs, logfile):
        loginfo("Rollback - Zoning for MDS")
        inp_dict = {}

        inp_dict.update(self.get_alias(inputs))
        inp_dict.update(self.get_zones(inputs))
        inp_dict.update(self.get_zoneset(inputs))

        cred = get_device_credentials(
            key="mac", value=inputs['mds_id'])
        if cred:
            obj = MDSTasks(cred['ipaddress'],
                           cred['username'], cred['password'])
            if obj:
                # Deleting zonesets
                loginfo("Deleting zonesets in MDS")
                res = obj.delete_zonesets(inp_dict, logfile)
                if res.getStatus() == PTK_OKAY:
                    # Deleting zones
                    loginfo("Deleting zones in MDS")
                    res = obj.delete_zones(inp_dict, logfile)
                    if res.getStatus() == PTK_OKAY:
                        # Deleting device aliases
                        loginfo("Deleting device aliases in MDS")
                        res = obj.delete_device_aliases(inp_dict, logfile)
                        if res.getStatus() != PTK_OKAY:
                            loginfo("Failed to delete device aliases")
                            res.setResult(False, PTK_INTERNALERROR,
                                          "Deleting device aliases failed")
                        else:
                            loginfo("MDSZoning rollback done")
                            customlogs(
                                "MDSZoning rollback executed successfully", logfile)
                            res.setResult(
                                parseResult(res)['data'], PTK_OKAY, "MDSZoning task rollback executed successfully")
                    else:
                        loginfo("Failed to delete zones")
                        res.setResult(False, PTK_INTERNALERROR,
                                      "Zone deletion failed")
                else:
                    loginfo("Failed to delete zonesets")
                    res.setResult(False, PTK_INTERNALERROR,
                                  "Zoneset deletion failed")
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(False, PTK_INTERNALERROR,
                              "Unable to login to the MDS")
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(False, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

        return parseTaskResult(res)

    def get_mds_list(self, keys):
        res = result()
        mds_list = get_device_list(device_type="MDS")
        res.setResult(mds_list, PTK_OKAY, "success")
        return res

    def get_flogi_sessions(self, keys):
        res = result()
        loginfo("Getting MDS flogi sessions...")
        flogi_sess_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "mds_id":
                    if arg['value']:
                        mac_addr = arg['value']
                    else:
                        res.setResult(flogi_sess_list, PTK_OKAY, "success")
                        return res
                if arg['key'] == "group":
                    if arg['value'] and arg['value'] == "1":
                        group = 1
                    else:
                        group = 0

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = MDS(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                tmp_flogi_sess_list = obj.get_flogi_sessions().getResult()
                for index, flogi in enumerate(tmp_flogi_sess_list):
                    if group == 1:
                        flogi_sess_list.append(
                            {"pwwn": flogi['pwwn'], "iface_id": flogi['iface_id']})
                    else:
                        flogi_sess_list.append(
                            {"id": flogi['pwwn'], "selected": "0", "label": flogi['iface_id']})
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(flogi_sess_list, PTK_INTERNALERROR,
                              "Unable to login to the MDS")
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(flogi_sess_list, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

        res.setResult(flogi_sess_list, PTK_OKAY, "success")
        return res

    def get_vsan_list(self, keys):
        res = result()
        loginfo("Getting MDS vsan list...")
        vsan_list = []

        for args in keys.values():
            for arg in args:
                if arg['key'] == "mds_id":
                    if arg['value']:
                        mac_addr = arg['value']
                        break
                    else:
                        res.setResult(vsan_list, PTK_OKAY, "success")
                        return res

        cred = get_device_credentials(key="mac", value=mac_addr)
        if cred:
            obj = MDS(cred['ipaddress'], cred['username'], cred['password'])
            if obj:
                tmp_vsan_list = obj.get_vsan_list().getResult()
                for index, vsan in enumerate(tmp_vsan_list):
                    vsan_list.append(
                        {"id": vsan, "selected": "0", "label": vsan})
            else:
                loginfo("Unable to login to the MDS")
                res.setResult(vsan_list, PTK_INTERNALERROR,
                              "Unable to login to the MDS")
        else:
            loginfo("Unable to get the device credentials of the MDS")
            res.setResult(vsan_list, PTK_INTERNALERROR,
                          "Unable to get the device credentials of the MDS")

        res.setResult(vsan_list, PTK_OKAY, "success")
        return res

    def get_ucsm_sp_pwwn(self, fi_mac_addr):
	pwwn_list = []
        if fi_mac_addr == None:
	    return pwwn_list
        cred = get_device_credentials(key="mac", value=fi_mac_addr)
	if cred:
	    obj = UCSManager()
	    if obj:
	        res = obj.ucsm_sp_wwpn(cred['vipaddress'], cred['username'], cred['password'])
		if res.getStatus() == PTK_OKAY:
		    pwwn_list = map(str.lower, res.getResult())
                else:
                    loginfo("Unable to get pwwn of service profiles from UCS from MDS zoning")
            else:
                loginfo("Unable to get access to UCS helper functions from MDS zoning")
        else:
            loginfo("Unable to get device credentials of UCS from MDS zoning")
	return pwwn_list
	
    def get_alias(self, inputs):
        inp_dict = {}
        alias_list = []
        flogi_list = inputs['flogi_list'].split('|')
        for fl_sess in flogi_list:
            fl_sess = eval(fl_sess)
            alias_list.append(fl_sess['alias_name']['value'])
        inp_dict['aliases'] = '|'.join(alias_list)
        return inp_dict

    def get_zones(self, inputs):
        inp_dict = {}
        zone_list = []
        zones_lst = inputs['zones'].split('|')
        for zone in zones_lst:
            zone = eval(zone)
            zone_list.append(zone['zone_name']['value'])
        inp_dict['zones'] = '|'.join(zone_list)
        inp_dict['vsan_id'] = inputs['vsan_id']
        return inp_dict

    def get_zoneset(self, inputs):
        inp_dict = {}
        zoneset_list = []
        zonesets_lst = inputs['zoneset'].split('|')
        for zoneset in zonesets_lst:
            zoneset = eval(zoneset)
            zoneset_list.append(zoneset['zoneset_name']['value'])
        inp_dict['zonesets'] = '|'.join(zoneset_list)
        inp_dict['vsan_id'] = inputs['vsan_id']
        return inp_dict


class MDSZoningInputs:
    mds_id = Dropdown(hidden='True', isbasic='True', helptext='', dt_type="string", static="False", static_values="", api="get_mds_list()",
                      name="mds_id", label="MDS switch", svalue="", mapval="", mandatory="1", order="1")

    iface_id = Label(hidden='0', isbasic='True', helptext='', dt_type="string", static="False", api="", name="iface_id", static_values="",
                     label="Interface", svalue="", mapval="", mandatory="1", group_member="1")
    pwwn = Label(hidden='0', isbasic='True', helptext='', dt_type="string", static="False", api="", name="pwwn", static_values="",
                 label="PWWN", svalue="", mapval="", mandatory="1", group_member="1")
    alias_name = Textbox(validation_criteria='str|min:1|max:64', hidden='0', isbasic='True', helptext='', dt_type="string", static="False", api="", name="alias_name",
                         static_values="", label="Alias", svalue="", mapval="", mandatory="1", group_member="1")
    flogi_list = Group(validation_criteria='', hidden='0', isbasic='True', helptext='Fabric login sessions', dt_type="string", static="False", api="get_flogi_sessions()|[mds_id:1:mds_id.value]", name="flogi_list", label="FLOGI List",
                       static_values="", svalue="{'alias_name': {'ismapped': '0', 'value': 'FlashArray-CT0FC0-fabricA'}, 'pwwn': {'ismapped': '0', 'value': '52:4a:93:7c:da:be:5c:03'}, 'iface_id': {'ismapped': '0', 'value': 'fc1/1'}}|{'alias_name': {'ismapped': '0', 'value': 'FlashArray-CT0FC2-fabricA'}, 'pwwn': {'ismapped': '0', 'value': '52:4a:93:7c:da:be:5c:13'}, 'iface_id': {'ismapped': '0', 'value': 'fc1/2'}}|{'alias_name': {'ismapped': '0', 'value': 'FlashArray-CT1FC0-fabricA'}, 'pwwn': {'ismapped': '0', 'value': '52:4a:93:7c:da:be:5c:00'}, 'iface_id': {'ismapped': '0', 'value': 'fc1/3'}}|{'alias_name': {'ismapped': '0', 'value': 'FlashArray-CT1FC2-fabricA'}, 'pwwn': {'ismapped': '0', 'value': '52:4a:93:7c:da:be:5c:10'}, 'iface_id': {'ismapped': '0', 'value': 'fc1/4'}}|{'alias_name': {'ismapped': '0', 'value': 'VM-Host-FC-02-A'}, 'pwwn': {'ismapped': '0', 'value': '20:00:00:25:b5:01:0a:01'}, 'iface_id': {'ismapped': '0', 'value': 'port-channel1'}}|{'alias_name': {'ismapped': '0', 'value': 'VM-Host-FC-01-A'}, 'pwwn': {'ismapped': '0', 'value': '20:00:00:25:b5:01:0a:00'}, 'iface_id': {'ismapped': '0', 'value': 'port-channel1'}}", mapval="", mandatory="1", members=["iface_id", "pwwn", "alias_name"], add="True", order="2")

    vsan_id = Dropdown(hidden='0', isbasic='True', helptext='VSAN ID', dt_type="string", static="False", api="get_vsan_list()|[mds_id:1:mds_id.value]",
                       name="vsan_id", static_values="", label="VSAN", svalue="101", mapval="", mandatory="1", order="3", recommended="1")

    zone_name = Textbox(validation_criteria='str|min:1|max:64', hidden='0', isbasic='True', helptext='', dt_type="string", static="False", api="", name="zone_name", static_values="",
                        label="Zone Name", svalue="", mapval="", mandatory="1", group_member="1")
    zone_members = Multiselectdropdown(hidden='0', isbasic='True', helptext='', dt_type="string", static="True", api="", name="zone_members",
                                       static_values="field:0:alias_name", label="Zone Members", svalue="", mapval="2", mandatory="1", group_member="1")
    zones = Group(validation_criteria='', hidden='0', isbasic='True', helptext='Create Zones and add members to the Zone', dt_type="string", static="False", api="", name="zones", label="Create Zones", static_values="",
                  svalue="{'zone_name': {'ismapped': '0', 'value': 'VM-Host-FC-02-A'}, 'zone_members': {'ismapped': '0', 'value': ['FlashArray-CT0FC0-fabricA', 'FlashArray-CT0FC2-fabricA', 'FlashArray-CT1FC0-fabricA', 'FlashArray-CT1FC2-fabricA', 'VM-Host-FC-02-A']}}|{'zone_name': {'ismapped': '0', 'value': 'VM-Host-FC-01-A'}, 'zone_members': {'ismapped': '0', 'value': ['FlashArray-CT0FC0-fabricA', 'FlashArray-CT0FC2-fabricA', 'FlashArray-CT1FC0-fabricA', 'FlashArray-CT1FC2-fabricA', 'VM-Host-FC-01-A']}}", mapval="", mandatory="1", members=["zone_name", "zone_members"], add="True", order="4")

    zoneset_name = Textbox(validation_criteria='str|min:1|max:64', hidden='0', isbasic='True', helptext='', dt_type="string", static="False", api="", name="zoneset_name", static_values="",
                           label="Zoneset Name", svalue="", mapval="", mandatory="1", group_member="1")
    zoneset_members = Multiselectdropdown(hidden='0', isbasic='True', helptext='', dt_type="string", static="True", api="", name="zoneset_members",
                                          static_values="field:0:zone_name", label="Zoneset Members", svalue="", mapval="2", mandatory="1", group_member="1")
    zoneset = Group(validation_criteria='', hidden='0', isbasic='True', helptext='Create Zoneset and add Zones to the Zoneset', dt_type="string", static="False", api="", name="zoneset", label="Create Zonesets", static_values="",
                    svalue="{'zoneset_name': {'ismapped': '0', 'value': 'flashstack-zoneset-vsan-101'}, 'zoneset_members': {'ismapped': '0', 'value': ['VM-Host-FC-01-A', 'VM-Host-FC-02-A']}}", mapval="", mandatory="1", members=["zoneset_name", "zoneset_members"], add="True", order="5")


class MDSZoningOutputs:
    status = Output(dt_type="integer", name="status", tvalue="SUCCESS")
