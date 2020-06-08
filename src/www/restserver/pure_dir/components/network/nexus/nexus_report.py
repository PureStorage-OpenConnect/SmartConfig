import time

from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import getAsList
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.components.network.nexus.nexus import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_global_wf_config_file
from pure_dir.components.common import get_device_credentials
from pure_dir.services.utils.miscellaneous import *
import xmltodict
import copy
import urllib2
from pure_dir.global_config import get_settings_file

g_hw_details = {}

def get_device_details(hw_type):
    """
    Function to get the device IP and Credentials based on MAC Address. 
    
    Parameters:
        hw_type (str): Hardware type for which details are to be obtained.
    
    Returns:
        cred (dict): Dict of IP Address and Credentials for the hardware type argument. 
    """
    try:
        stacktype = get_xml_element(
            get_settings_file(), "stacktype")[1][0]['subtype']
        fd = open(get_global_wf_config_file(), 'r')
        doc = xmltodict.parse(fd.read())

        for htype in doc['globals']['htype']:
            if htype['@stacktype'] != stacktype:
                continue
            for input_val in htype['input']:
                if input_val['@name'] in [
                    'nexus_switch_a',
                    'nexus_switch_b',
                    'mds_switch_a',
                    'mds_switch_b',
                    'ucs_switch_a',
                    'ucs_switch_b',
                        'pure_id']:
                    g_hw_details[input_val['@name']] = input_val['@value']
        for key, val in g_hw_details.iteritems():
            if key != hw_type:
                continue
            cred = get_device_credentials(
                key="mac", value=val)
            return cred

    except urllib2.URLError as e:
        loginfo("Failed during Nexus Report Generation" + str(e))

    return None

def _nexus_handler(switch_name):
    """To get Nexus Handle"""
    obj = result()
    nexus_creden = {}
    nexus_creden = get_device_details(switch_name)
    try:
        handle = Nexus(ipaddress=nexus_creden['ipaddress'],
                        username=nexus_creden['username'],
                        password=nexus_creden['password'])
        return handle
    except BaseException:
        loginfo("Failed to get nexus handler")
        return None

def get_nexus_switch_info(args={}):
    """
    fetches nexus switch info includes: switchname, hardware name, version,time
    """
    nexus_sys_info = []
    method = "Nexus Switch System Information"
    switch_name = ['nexus_switch_a' , 'nexus_switch_b']
    for switch in switch_name:
        helper = _nexus_handler(switch)
        if helper is not None:
            nexus_info = {}
            nexus_version = {}
            nexus_init= {'name' : "", 'ip_address' : "", 'model' : "", 'serial_no' : "", 'system_version' : "", 'kickstart_version' : "", 'uptime' : ""}
            nexus_sys = copy.deepcopy(nexus_init)
            nexus_info = helper.nexus_switch_info()
            nexus_sys['name'] = nexus_info['name']
            nexus_sys['ip_address'] = get_device_details(switch)['ipaddress']
            nexus_sys['model'] = nexus_info['model']
            nexus_sys['serial_no'] = nexus_info['serial_no'] 
            nexus_version = helper.get_nexus_sys_ks_version()
            nexus_sys['system_version'] = nexus_version['system_version'] 
            nexus_sys['kickstart_version'] = nexus_version['kickstart_version'] 
            nexus_sys['uptime'] = helper.nexus_uptime()['uptime']
            nexus_sys_info.append(nexus_sys.copy())
        else:
            return PTK_RESOURCENOTAVAILABLE, nexus_sys_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])
    if [nexus_dict for nexus_dict in nexus_sys_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
        #loginfo("Successfully fetched " + method)
        return PTK_OKAY, nexus_sys_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, nexus_sys_info, "Unable to get " + method

def get_nexus_global_info(args={}):
    """
    fetches domain, dns, ntp, lacp, vpc, interface-vlan
    """
    nex_glob_info = []
    method = "Nexus Global Switch Information"
    nex_sys = {}
    switch_name = ['nexus_switch_a' , 'nexus_switch_b']
    for switch in switch_name:
        nex_init = {'name' : '', 'domain': '', 'dns': '', 'ntp': '', 'lacp': '', 'vpc': '', 'interface-vlan': ''}
        nex_sys = copy.deepcopy(nex_init)
        helper = _nexus_handler(switch)
        if helper is not None:
            try:
                nex_show_dns = helper.nexus_command('show hosts', ['TABLE_vrf'])
                nex_sys['domain'] = nex_show_dns['TABLE_vrf'][0]['ROW_vrf']['defaultdomains']
                nex_sys['dns'] = nex_show_dns['TABLE_vrf'][0]['ROW_vrf']['nameservice']
            except IndexError:
                nex_show_dns = helper.nexus_command('show hosts', ['dnsnameservice'])
                nex_sys['dns'] = nex_show_dns['dnsnameservice'][0]
                nex_sys['domain'] = ""
            finally:
                nex_show_ntp = helper.nexus_command('show ntp peers',['PeerIPAddress'])
	        nex_show_feature = helper.nexus_command('show feature', ['ROW_cfcFeatureCtrlTable'], cfcFeatureCtrlName2=['lacp','vpc','interface-vlan'])
                nex_sys['ntp'] = nex_show_ntp['PeerIPAddress'][0].strip()
                nex_sys['lacp'] = nex_show_feature[0]['cfcFeatureCtrlOpStatus2']
	        nex_sys['vpc'] = nex_show_feature[1]['cfcFeatureCtrlOpStatus2']
	        nex_sys['interface-vlan']=nex_show_feature[2]['cfcFeatureCtrlOpStatus2']
                nex_sys['name'] = helper.nexus_switch_info()['name']
                nex_glob_info.append(nex_sys)
        else:
            return PTK_RESOURCENOTAVAILABLE, nex_glob_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])
    if [nexus_dict for nexus_dict in nex_glob_info if (cmp(nexus_dict, nex_init)) != 0] != []:
        #loginfo("Successfully fetched " + method)
        return PTK_OKAY, nex_glob_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, nex_glob_info, "Unable to get " + method

def get_nexus_environment_info(args={}):
    """
    fetches hostname, psuid_status, ps_model, nex_mscs, fan_name, fan_model, fandir_status
    """
    nex_env_info = []
    method = "Nexus Environment Information"
    nex_sys = {}
    switch_name = ['nexus_switch_a' , 'nexus_switch_b']
    for switch in switch_name:
        nexus_init = {'host_name': '', 'psuid_status': [], 'ps_model': [], 'nex_mscs': [], 'fan_name': [], 'fan_model':[],
                    'fandir_status': []}
        helper = _nexus_handler(switch)
        if helper is not None:
	    nex_show_hostname = helper.nexus_command('show hardware', ['host_name'])
            nex_show_psinfo = helper.nexus_command('show environment', ['psnum','psmodel','ps_status',
				 				        'tempmod','fandir',
                                                                         'sensor', 'curtemp', 'alarmstatus',
                                                                         'fanname', 'fanmodel', 'fanstatus'])
	    nex_sys['host_name'] = ''.join(nex_show_hostname['host_name'])
	    psmod = [x.encode('utf-8') for x in nex_show_psinfo['psmodel']] 
	    psnum=[str(i) for i in nex_show_psinfo['psnum']]
	    ps_status = nex_show_psinfo['ps_status'] 
	    psuid_status = zip(psnum,ps_status)
	    nex_sys['psuid_status'] = ["/".join(i) for i in psuid_status]
	    psmodel = zip(psnum,psmod)
            nex_sys['ps_model'] = ["/".join(i) for i in psmodel]
	    nex_show_psinfo['tempmod'] = [i.strip() for i in nex_show_psinfo['tempmod']]
	    nex_mod = zip(nex_show_psinfo['tempmod'], nex_show_psinfo['sensor'], nex_show_psinfo['curtemp'], nex_show_psinfo['alarmstatus'])
	    nex_mod = ["/".join(i)  for i in nex_mod]
	    nex_sys['nex_mscs'] = nex_mod
	    nex_sys['fan_name'] = nex_show_psinfo['fanname']
            nex_sys['fan_model'] = nex_show_psinfo['fanmodel']
	    fandir_status = zip(nex_show_psinfo['fanstatus'], nex_show_psinfo['fandir'])
	    nex_sys['fandir_status'] = [' '.join(i) for i in fandir_status]
	    nex_env_info.append(copy.deepcopy(nex_sys))
        else:
            return PTK_RESOURCENOTAVAILABLE, nex_env_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])
    if [nexus_dict for nexus_dict in nex_env_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
        #loginfo("Successfully fetched " + method)
        return PTK_OKAY, nex_env_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, nex_env_info, "Unable to get " + method

def get_nexus_vlan_info(args={}):
    """
    fetches vlan_name, vlan_id, vlan_status
    """
    res = result()
    nex_vlan_info = []
    nexus_init = {'vlan_name': '', 'vlan_id': '', 'vlan_status': ''}
    vlan_dict = {}
    switch_name = args['switch_name']
    method = "Nexus Switch " + switch_name[-1].upper() + " VLAN Information"
    helper = _nexus_handler(switch_name)
    if helper is not None:
        nex_show_vlan = helper.nexus_command('show vlan brief', ['ROW_vlanbriefxbrief'])
        vlan_details = nex_show_vlan['ROW_vlanbriefxbrief']
        for vlan_info in vlan_details:
            if isinstance(vlan_info,list):
   	        for vlan in vlan_info:
                    vlan_dict['vlan_name'] = vlan["vlanshowbr-vlanname"]
                    vlan_dict['vlan_id'] = vlan['vlanshowbr-vlanid']
	            vlan_dict['vlan_status'] = vlan['vlanshowbr-vlanstate']
                    nex_vlan_info.append(vlan_dict.copy())
        if [nexus_dict for nexus_dict in nex_vlan_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_vlan_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_vlan_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_vlan_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus_intf_info(args={}):
    """
    fetches interface_name, vlan, state_speed_type, description
    """
    res = result()
    nex_intf_info = []
    intf_dict = {}
    intf_desc_dict = {}
    nex_int_desc_list = []
    switch_name = args['switch_name']
    method = "Nexus Switch " + switch_name[-1].upper() + " interface information"
    nexus_init = {'interface_name': '', 'vlan': '', 'state_speed_type': '', 'description': ''}
    helper = _nexus_handler(switch_name)
    if helper is not None:
        nex_show_intf = helper.nexus_command('show interface brief', ['ROW_interface'])
        nex_show_desc = helper.nexus_command('show interface description', ['ROW_interface'])
        intf_details = nex_show_intf['ROW_interface']
        intf_desc = nex_show_desc['ROW_interface']
        intf_desc1 = intf_desc[0]
        for intf_info in intf_details:
            if isinstance(intf_info,list):
                for intf in intf_info:
                    intf_dict['description'] = intf['desc'] if 'desc' in intf else "--"
                    intf_dict['interface_name'] = intf["interface"]
                    intf_dict['vlan'] = intf['vlan'] if 'vlan' in intf else ""
                    status = intf['state']
		    intf_type = intf['type'] if 'type' in intf else "--"
		    speed = intf['speed'] if 'speed' in intf else "--"
		    intf_dict['state_speed_type'] = status+ '/' +intf_type+ '/' + speed
   		    nex_intf_info.append(intf_dict.copy())
        for intf_descr in intf_desc:
	    if isinstance(intf_descr,list):
	        for intf_d in intf_descr:
		    intf_desc_dict['interface_name'] = intf_d['interface']
		    intf_desc_dict['description'] = intf_d['desc'] if 'desc' in intf_d else "--"
		    nex_int_desc_list.append(intf_desc_dict.copy())
        for intf in nex_intf_info:
	    intflist = [x for x in nex_int_desc_list if x['interface_name'] == intf['interface_name']]
	    if intflist:
	        intf.update(intflist[0])
        if [nexus_dict for nexus_dict in nex_intf_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_intf_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_intf_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_intf_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus_vpc_info(args={}):
    """
    fetches vpc_id, port, status, active_vlans, vpc_domain_id, vpc_role
    """
    res = result()
    nex_vpc_info = []
    vpc_dict = {}
    vpc_peer_dict = {}
    switch_name = args['switch_name']
    method = "Nexus Switch " + switch_name[-1].upper() + " vPC Domain configuration"
    helper = _nexus_handler(switch_name)
    nexus_init = {'vpc_id': '', 'port': '', 'status': '', 'active_vlans': '', 'vpc_domain_id': '', 'vpc_role': ''}
    if helper is not None:
        nex_vpc_details = helper.nexus_command('show vpc brief', ['ROW_vpc','ROW_peerlink','vpc-domain-id','vpc-role'])
        nex_vpc_det = nex_vpc_details['ROW_vpc'] 
        nex_vpc_peer = nex_vpc_details['ROW_peerlink']
        for vpc in nex_vpc_det:
	    if isinstance(vpc, list):
	        for nex_vpc in vpc:
		    vpc_dict['vpc_id'] = nex_vpc['vpc-id']
		    vpc_dict['port'] = nex_vpc['vpc-ifindex']
		    vpc_dict['status'] = nex_vpc['vpc-port-state']
		    vpc_dict['active_vlans'] = nex_vpc['up-vlan-bitset']
		    nex_vpc_info.append(vpc_dict.copy())
        for vpc_peer in nex_vpc_peer:
	    vpc_peer_dict['vpc_id'] = vpc_peer['peer-link-id']
            vpc_peer_dict['port'] = vpc_peer['peerlink-ifindex']
            vpc_peer_dict['status'] = vpc_peer['peer-link-port-state']
            vpc_peer_dict['active_vlans'] = vpc_peer['peer-up-vlan-bitset']
            nex_vpc_info.append(vpc_peer_dict.copy())
        for vpc in nex_vpc_info:
	    vpc.update({'vpc_domain_id': nex_vpc_details['vpc-domain-id'][0]})
            vpc.update({'vpc_role' : nex_vpc_details['vpc-role'][0]})
        if [nexus_dict for nexus_dict in nex_vpc_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_vpc_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_vpc_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_vpc_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus_portchannel_info(args={}):
    """
    fetches group, port_channel, protocol, type, member_ports
    """
    nex_pc_info = []
    pc_dict = {}
    pc_peer_dict = {}
    ports_l = []
    switch_name = args['switch_name']
    method = "Nexus Switch " + switch_name[-1].upper() + " Port Channel Configuration"
    helper = _nexus_handler(switch_name)
    nexus_init = {'group': '', 'port_channel': '', 'protocol': '', 'type': '', 'member_ports': [] or ''}
    if helper is not None:
        nex_pc_details = helper.nexus_command('show port-channel summary', ['ROW_channel','ROW_member','port-channel','prtcl','type'])
        pc_det = nex_pc_details['ROW_channel']
        for row_c in pc_det:
	    for pc in row_c:
 	        pc_dict['group'] = pc['group']
	        pc_dict['port_channel'] = pc['port-channel']
	        pc_dict['protocol'] = pc['prtcl']
	        pc_dict['type'] = pc['type']
	        ports_list = pc['TABLE_member']['ROW_member']
	        if isinstance(ports_list, list):
		    for ports in ports_list:
		        ports_l.append(ports['port'])
		        pc_dict['member_ports'] = ports_l
	        else:
		    pc_dict['member_ports'] = ports_list['port']
	        nex_pc_info.append(pc_dict.copy())
        if [nexus_dict for nexus_dict in nex_pc_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_pc_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_pc_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_pc_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus5k_vsan_info(args={}):
    """
    fetches vsan_name, vsan_state, vsan_interop_mode, vsan_load_balancing, vsan_operational_state
    """
    switch = args['switch_name']
    method = "Nexus5k " + switch[-1].upper() + " VSANs"
    helper = _nexus_handler(switch)
    nexus_init = {'vsan_name': '', 'vsan_state': '', 'vsan_interop_mode' : '', 'vsan_load_balancing': '', 'vsan_operational_state': ''}
    if helper is not None:
        nex_sys_info = helper.nexus_vsan_details()
        if [nexus_dict for nexus_dict in nex_sys_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_sys_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus5k_flogi(args={}):
    """
    fetches interface, vsan_id, wwpn, wwnn
    """
    res = result()
    nex_sys_info = []
    nex_sys = {}
    switch = args['switch_name']
    method = "Nexus5k " + switch[-1].upper() + " Flogi"
    helper = _nexus_handler(switch)
    nexus_init = {'interface': '', 'vsan_id': '', 'wwpn': '', 'wwnn': ''}
    if helper is not None:
        nex_show_flogi = helper.get_flogi_sessions().getResult()
        for row in nex_show_flogi:
            nex_sys['interface'] = row['iface_id']
            nex_sys['vsan_id'] = row['vsan_id']
            nex_sys['wwpn'] = row['pwwn']
            nex_sys['wwnn'] = row['nwwn']
            nex_sys_info.append(nex_sys.copy())
        if [nexus_dict for nexus_dict in nex_sys_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_sys_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus5k_zoneset(args={}):
    """
    fetches zoneset_name, zoneset_vsan_id
    """
    nex_sys_info = []
    nex_sys = {}
    switch = args['switch_name']
    method = "Nexus5k Switch " +  switch[-1].upper() + " Zone Information"
    helper = _nexus_handler(switch)
    nexus_init = {'zoneset_name': '', 'zoneset_vsan_id': ''}
    if helper is not None:
        nex_zoneset_name = helper.nexus_config_command('show zoneset brief', ['body'])
        nex_sys['zoneset_name'] = nex_zoneset_name['body'][0].encode('utf-8').split('\n')[0].split(' ')[-3]
        nex_sys['zoneset_vsan_id'] = nex_zoneset_name['body'][0].encode('utf-8').split('\n')[0].split(' ')[-1]
        nex_sys_info.append(nex_sys)
        if [nexus_dict for nexus_dict in nex_sys_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nex_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nex_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nex_sys_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus5k_zone(args={}):
    """
    fetches wwn, zone_name, logged
    """
    switch = args['switch_name']
    method = "Nexus5k " + switch[-1].upper() + " Zoning"
    helper = _nexus_handler(switch)
    nexus_init = {'wwn': '', 'zone_name': '', 'logged': ''}
    if helper is not None:
        nexus_sys_info = helper.nexus_zoneset_details()
        for i in nexus_sys_info:
            i['logged'] = 'Yes' 
        if [nexus_dict for nexus_dict in nexus_sys_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
            #loginfo("Successfully fetched " + method)
            return PTK_OKAY, nexus_sys_info, _("PDT_SUCCESS_MSG")
        else:
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, nexus_sys_info, "Unable to get " + method
    else:
        return PTK_RESOURCENOTAVAILABLE, nexus_sys_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])

def get_nexus5k_switch_info(args={}):
    """
    fetches nexus switch info includes: switchname, hardware name, version,time
    """
    nexus_sys_info = []
    nexus_info = {}
    switch_name = ['nexus_switch_a', 'nexus_switch_b']
    method = "Nexus5k Switch System Information"
    nexus_init = {'name': '', 'model': '', 'serial_num': '', 'ip_address': '', 'uptime': '', 'system_version': '', 'kickstart_version': ''}
    for switch in switch_name:
        helper = _nexus_handler(switch)
        if helper is not None:
            show_model = helper.nexus_command('show inventory', ['ROW_inv'])
            show_name = helper.nexus_command('show hostname', ['hostname'])
            nexus_info['name'] = show_name['hostname'][0]
            for row in show_model['ROW_inv']:
                for i in row:
                    if i['name'] == 'Chassis':
                        nexus_info['model'] = i['productid']
                        nexus_info['serial_num'] = i['serialnum']
            nexus_uptime = helper.nexus_uptime()
            nexus_info['ip_address'] = get_device_details(switch)['ipaddress']
            nexus_info.update(nexus_uptime)
            nexus_version = helper.get_nexus_sys_ks_version()
            nexus_info.update(nexus_version)
            nexus_sys_info.append(nexus_info.copy())
        else:
            return PTK_RESOURCENOTAVAILABLE, nexus_sys_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])
    if [nexus_dict for nexus_dict in nexus_sys_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
        #loginfo("Successfully fetched " + method)
        return PTK_OKAY, nexus_sys_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, nexus_sys_info, "Unable to get " + method

def get_nexus5k_environment_info(args={}):
    """
    fetches hostname, psuid_status, ps_model, nex_mscs, fan_name, fan_model, fandir_status
    """
    nex_env_info = []
    method = "Nexus Environment Information"
    nex_sys = {}
    switch_name = ['nexus_switch_a' , 'nexus_switch_b']
    for switch in switch_name:
        nexus_init = {'host_name': '', 'psuid_status': [], 'ps_model': [], 'nex_mscs': [], 'fan_name': [], 'fan_model':[],
                    'fandir_status': []}
        helper = _nexus_handler(switch)
        if helper is not None:
            nex_show_hostname = helper.nexus_command('show hostname', ['body'])
            nex_show_psinfo = helper.nexus_command('show environment', ['psnum','psmodel','ps_status',
                                                                        'tempmod','fandir',
                                                                         'sensor', 'curtemp', 'alarmstatus',
                                                                         'fanname', 'fanmodel', 'fanstatus'])
            nex_sys['host_name'] = [i['hostname'] for i in nex_show_hostname['body']][0]
            psmod = [x.encode('utf-8') for x in nex_show_psinfo['psmodel']]
            psnum=[str(i) for i in nex_show_psinfo['psnum']]
            ps_status = nex_show_psinfo['ps_status']
            psuid_status = zip(psnum,ps_status)
            nex_sys['psuid_status'] = ["/".join(i) for i in psuid_status]
            psmodel = zip(psnum,psmod)
            nex_sys['ps_model'] = ["/".join(i) for i in psmodel]
            nex_show_psinfo['tempmod'] = [i.strip() for i in nex_show_psinfo['tempmod']]
            nex_mod = zip(nex_show_psinfo['tempmod'], nex_show_psinfo['sensor'], nex_show_psinfo['curtemp'], nex_show_psinfo['alarmstatus'])
            nex_mod = ["/".join(i)  for i in nex_mod]
            nex_sys['nex_mscs'] = nex_mod
            nex_sys['fan_name'] = nex_show_psinfo['fanname']
            nex_sys['fan_model'] = nex_show_psinfo['fanmodel']
            fandir_status = zip(nex_show_psinfo['fanstatus'], nex_show_psinfo['fandir'])
            nex_sys['fandir_status'] = [' '.join(i) for i in fandir_status]
            nex_env_info.append(copy.deepcopy(nex_sys))
        else:
            return PTK_RESOURCENOTAVAILABLE, nex_env_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])
    if [nexus_dict for nexus_dict in nex_env_info if (cmp(nexus_dict, nexus_init)) != 0] != []:
        #loginfo("Successfully fetched " + method)
        return PTK_OKAY, nex_env_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, nex_env_info, "Unable to get " + method

def get_nexus5k_global_info(args={}):
    """
    fetches domain, dns, ntp, lacp, vpc, interface-vlan
    """
    nex_glob_info = []
    method = "Nexus Global Switch Information"
    nex_sys = {}
    switch_name = ['nexus_switch_a' , 'nexus_switch_b']
    for switch in switch_name:
        nex_init = {'name' : '', 'domain': '', 'dns': '', 'ntp': '', 'lacp': '', 'vpc': '', 'interface-vlan': ''}
        nex_sys = copy.deepcopy(nex_init)
        helper = _nexus_handler(switch)
        if helper is not None:
            try:
                nex_show_dns = helper.nexus_command('show hosts', ['TABLE_vrf'])
                nex_sys['domain'] = nex_show_dns['TABLE_vrf'][0]['ROW_vrf']['defaultdomains']
                nex_sys['dns'] = nex_show_dns['TABLE_vrf'][0]['ROW_vrf']['nameservice']
            except IndexError:
                nex_show_dns = helper.nexus_command('show hosts', ['dnsnameservice'])
                nex_sys['dns'] = nex_show_dns['dnsnameservice'][0]
                nex_sys['domain'] = ""
            finally:
                nex_show_ntp = helper.nexus_command('show ntp peers',['PeerIPAddress'])
                hostname = helper.nexus_command('show hostname', ['hostname'])
                nex_show_feature = helper.feature_list()
                nex_sys['ntp'] = nex_show_ntp['PeerIPAddress'][0].strip()
                nex_sys['lacp'] = nex_show_feature['lacp']
                nex_sys['vpc'] = nex_show_feature['vpc']
                nex_sys['interface-vlan']=nex_show_feature['interface-vlan']
                nex_sys['name'] = hostname['hostname'][0]
                nex_glob_info.append(nex_sys)
        else:
            return PTK_RESOURCENOTAVAILABLE, nex_glob_info, "failed to get handler for Nexus {} : {} Report Generation".format(switch, get_device_details(switch)['ipaddress'])
    if [nexus_dict for nexus_dict in nex_glob_info if (cmp(nexus_dict, nex_init)) != 0] != []:
        #loginfo("Successfully fetched " + method)
        return PTK_OKAY, nex_glob_info, _("PDT_SUCCESS_MSG")
    else:
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, nex_glob_info, "Unable to get " + method
