from pure_dir.components.storage.flashblade.flashblade_tasks import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_global_wf_config_file
from pure_dir.components.common import get_device_credentials
from pure_dir.services.utils.miscellaneous import *
import xmltodict
import copy
import urllib.error
from threading import Lock
from pure_dir.global_config import get_settings_file

g_hw_details = {}
g_fb_task_obj = None
lock = Lock()


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
                        'pure_id',
                        'fb_id']:
                    g_hw_details[input_val['@name']] = input_val['@value']
        for key, val in g_hw_details.items():
            if key != hw_type:
                continue
            cred = get_device_credentials(
                key="mac", value=val)
            return cred

    except urllib.error.URLError as e:
        loginfo("Failed during FlashBlade Report Generation" + str(e))

    return None


def _fb_handler():
    """ To get FlashBlade Handle to access the REST APIs."""
    pure_creden = {}
    global g_fb_task_obj
    pure_creden = get_device_details('fb_id')
    if g_fb_task_obj is not None:
        return g_fb_task_obj
    try:
        fb_task_obj = FlashBladeTasks(ipaddress=pure_creden['ipaddress'],
                                      username=pure_creden['username'],
                                      password=pure_creden['password'])
        g_fb_task_obj = fb_task_obj
        if fb_task_obj is not None:
            if fb_task_obj.handle is not None and fb_task_obj.fb is not None:
                return fb_task_obj
            else:
                loginfo("Failed to get FlashBlade handler")
                return None
        else:
            return None
    except Exception as e:
        loginfo("Failed to get FlashBlade handler" + str(e))
        return None


def release_fb_handler():
    """To release FlashBlade Handle."""
    global g_fb_task_obj
    res = result()
    if g_fb_task_obj is not None and g_fb_task_obj.fb is not None:
        g_fb_task_obj.fb.logout()
        res.setResult(True, PTK_OKAY, "Released FlashBlade Handle")
        loginfo("Released FlashBlade handle")
        g_fb_task_obj = None
        return res
    g_fb_task_obj = None
    res.setResult(False, PTK_NOTEXIST, "FlashBlade Handle doesn't exist")
    return res


def get_fb_system_info(args={}):
    """
    Function to obtain FlashBlade System Information.

    Parameters:
        args (dict): None.

    Returns:
        List of FlashBlade Info.

    """
    fb_info_list = []
    fb_tmp_dict = {}
    fb = None
    fb_ini = {
        'fb_name': "",
        'fb_ip': "",
        'fb_id': "",
        'fb_version': "",
        'fb_revision': "",
        'fb_capacity': "",
        'fb_serial': "",
        'fb_model': ""}
    fb_info = copy.deepcopy(fb_ini)
    method = "FlashBlade System Info"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb = fb_task_obj.fb
            fb_info['fb_ip'] = get_device_details('fb_id')['ipaddress']
            fb_info['fb_serial'] = fb_task_obj.fb.hardware.list_hardware(
                filter='type=\'ch\'').items[0].serial
            fb_info['fb_model'] = fb_task_obj.fb.hardware.list_hardware(
                filter='type=\'fb\'').items[0].model
            fb_info['fb_capacity'] = str(fb.arrays.list_arrays_space().items[0].capacity)
            fb_tmp_dict = fb.arrays.list_arrays()
            fb_info['fb_name'] = fb_tmp_dict.items[0].name
            fb_info['fb_id'] = fb_tmp_dict.items[0].id
            fb_info['fb_version'] = fb_tmp_dict.items[0].version
            fb_info['fb_revision'] = fb_tmp_dict.items[0].revision
            fb_info_list.append(fb_info.copy())
            if [fb_dict for fb_dict in fb_info_list if not fb_dict == fb_ini] != []:
                return PTK_OKAY, fb_info_list, _("PDT_SUCCESS_MSG")
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, fb_info_list, "Unable to get " + method
        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_info_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_info_list, str(e)

    finally:
        '''if fb_task_obj is not None:
            fb.logout()'''
        lock.release()


def get_fb_hardware_info(args={}):
    """
    Function to obtain FlashBlade Hardware Information.

    Parameters:
        args (dict): None.

    Returns:
        List of Hardware Components in FlashBlade.

    """
    fb_hw_info_list = []
    fb_tmp_dict = {}
    fb_ini = {
        'hw_type': "",
        'hw_name': "",
        'hw_serial': "",
        'hw_model': "",
        'hw_status': "",
        'hw_speed': "",
        'hw_capacity': ""}
    fb_hw_info = copy.deepcopy(fb_ini)
    method = "FlashBlade Hardware Info"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb_tmp_dict = fb_task_obj.fb.hardware.list_hardware(filter='type=\'ch\'').items
            for item in fb_tmp_dict:
                fb_hw_info['hw_type'] = "Chassis - " + str(item.index)
                fb_hw_info['hw_name'] = item.name
                fb_hw_info['hw_serial'] = item.serial if item.serial else "--"
                fb_hw_info['hw_model'] = item.model if item.model else "--"
                fb_hw_info['hw_status'] = item.status
                fb_hw_info['hw_speed'] = str(item.speed) if item.speed else "--"
                fb_hw_info['hw_capacity'] = "N/A"
                fb_hw_info_list.append(fb_hw_info.copy())
            fb_tmp_dict = list(zip(fb_task_obj.fb.hardware.list_hardware(
                filter='type=\'fb\'').items, fb_task_obj.fb.blade.list_blades().items))
            for item in fb_tmp_dict:
                fb_hw_info['hw_type'] = "FlashBlade - " + str(item[0].slot)
                fb_hw_info['hw_name'] = item[0].name
                fb_hw_info['hw_serial'] = item[0].serial if item[0].serial else "--"
                fb_hw_info['hw_model'] = item[0].model if item[0].model else "--"
                fb_hw_info['hw_status'] = item[0].status
                fb_hw_info['hw_speed'] = str(item[0].speed) if item[0].speed else "--"
                fb_hw_info['hw_capacity'] = str(item[1].raw_capacity)
                fb_hw_info_list.append(fb_hw_info.copy())
            if [fb_dict for fb_dict in fb_hw_info_list if not fb_dict == fb_ini] != []:
                return PTK_OKAY, fb_hw_info_list, _("PDT_SUCCESS_MSG")
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, fb_hw_info_list, "Unable to get " + method
        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_hw_info_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_hw_info_list, str(e)

    finally:
        lock.release()


def get_fb_global_settings_info(args={}):
    """
    Function to obtain FlashBlade Global Settings Information.

    Parameters:
        args (dict): None.

    Returns:
        List of global settings in FlashBlade.

    """
    fb_glob_settings_info_list = []
    fb_tmp_dict = {}
    fb_ini = {
        'domain': "",
        'dns_servers': [],
        'ntp_servers': [],
        'time_zone': "",
        'relay_host': "",
        'sender_domain': "",
        'alert_email': ""}
    fb_glob_settings_info = copy.deepcopy(fb_ini)
    method = "FlashBlade Global Settings Info"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb_tmp_dict = fb_task_obj.fb.dns.list_dns().items[0]
            fb_glob_settings_info['domain'] = fb_tmp_dict.domain
            fb_glob_settings_info['dns_servers'] = fb_tmp_dict.nameservers
            fb_tmp_dict = fb_task_obj.fb.arrays.list_arrays().items[0]
            fb_glob_settings_info['time_zone'] = fb_tmp_dict.time_zone
            fb_glob_settings_info['ntp_servers'] = fb_tmp_dict.ntp_servers
            fb_tmp_dict = fb_task_obj.fb.smtp.list_smtp().items[0]
            fb_glob_settings_info['relay_host'] = fb_tmp_dict.relay_host
            fb_glob_settings_info['sender_domain'] = fb_tmp_dict.sender_domain
            fb_glob_settings_info['alert_email'] = fb_task_obj.fb.alert_watchers.list_alert_watchers(
            ).items[0].name
            fb_glob_settings_info_list.append(fb_glob_settings_info.copy())
            if [fb_dict for fb_dict in fb_glob_settings_info_list if not fb_dict == fb_ini] != []:
                return PTK_OKAY, fb_glob_settings_info_list, _("PDT_SUCCESS_MSG")
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, fb_glob_settings_info_list, "Unable to get " + method
        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_glob_settings_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_glob_settings_info_list, str(e)

    finally:
        lock.release()


def get_fb_subnet_interfaces(args={}):
    """
    Function to obtain FlashBlade Subnets & Network Interfaces.

    Parameters:
        args (dict): None.

    Returns:
        List of Subnets and their corresponding interfaces in FlashBlade.

    """
    fb_subnet_interf_list = []
    fb_tmp_dict = {}
    fb_ini = {
        'subnet_name': "",
        'subnet_prefix': "",
        'vlan': "",
        'mtu': "",
        'netmask': "",
        'gateway': "",
        'interf_name': [],
        'interf_ip_addr': [],
        'services': []}
    fb_subnet_interf = copy.deepcopy(fb_ini)
    method = "FlashBlade Subnets and Network Interfaces"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb_tmp_dict = fb_task_obj.fb.subnets.list_subnets().items
            for item in fb_tmp_dict:
                fb_subnet_interf['subnet_name'] = item.name
                fb_subnet_interf['subnet_prefix'] = item.prefix
                fb_subnet_interf['vlan'] = str(item.vlan)
                fb_subnet_interf['mtu'] = str(item.mtu)
                fb_subnet_interf['gateway'] = item.gateway
                fb_subnet_interf['interf_name'] = [interf.name for interf in item.interfaces]
                nw_interf = fb_task_obj.fb.network_interfaces.list_network_interfaces(
                    names=fb_subnet_interf['interf_name']).items
                fb_subnet_interf['interf_ip_addr'] = [''.join(intf.address) for intf in nw_interf]
                fb_subnet_interf['services'] = [''.join(intf.services) for intf in nw_interf]
                fb_subnet_interf['netmask'] = nw_interf[0].netmask
                fb_subnet_interf_list.append(fb_subnet_interf.copy())
            if [fb_dict for fb_dict in fb_subnet_interf_list if not fb_dict == fb_ini] != []:
                return PTK_OKAY, fb_subnet_interf_list, _("PDT_SUCCESS_MSG")
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, fb_subnet_interf_list, "Unable to get " + method
        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_subnet_interf_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_subnet_interf_list, str(e)

    finally:
        lock.release()


def get_fb_eth_ports(args={}):
    """
    Function to obtain FlashBlade Ethernet Ports.

    Parameters:
        args (dict): None.

    Returns:
        List of FlashBlade Ethernet Ports.

    """
    fb_eth_ports_list = []
    fb_tmp_dict = {}
    fb_ini = {
        'port_name': "",
        'slot': "",
        'serial': "",
        'model': "",
        'speed': "",
        'status': ""}
    fb_eth_ports = copy.deepcopy(fb_ini)
    method = "FlashBlade Ethernet Ports"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb_tmp_dict = fb_task_obj.fb.hardware.list_hardware(filter='type=\'eth\'').items
            for item in fb_tmp_dict:
                fb_eth_ports['port_name'] = item.name
                fb_eth_ports['slot'] = str(item.slot)
                fb_eth_ports['serial'] = item.serial if item.serial else "--"
                fb_eth_ports['model'] = item.model if item.model else "--"
                fb_eth_ports['speed'] = str(item.speed)
                fb_eth_ports['status'] = item.status
                fb_eth_ports_list.append(fb_eth_ports.copy())
            if [fb_dict for fb_dict in fb_eth_ports_list if not fb_dict == fb_ini] != []:
                return PTK_OKAY, fb_eth_ports_list, _("PDT_SUCCESS_MSG")
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, fb_eth_ports_list, "Unable to get " + method
        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_eth_ports_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_eth_ports_list, str(e)

    finally:
        lock.release()


def get_fb_file_systems(args={}):
    """
    Function to obtain FlashBlade NFS FileSystems.

    Parameters:
        args (dict): None.

    Returns:
        List of FlashBlade NFS FileSystems.

    """
    fb_nfs_list = []
    fb_tmp_dict = {}
    fb_ini = {
        'name': "",
        'created_size': "",
        'provisioned_size': "",
        'fast_remove': "",
        'nfs': "",
        'nfs_rule': ""}
    fb_nfs = copy.deepcopy(fb_ini)
    method = "FlashBlade NFS FileSystems"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb_tmp_dict = fb_task_obj.fb.file_systems.list_file_systems(
                filter='destroyed=\'False\'' and 'nfs.v3_enabled or nfs.v4_1_enabled').items
            for item in fb_tmp_dict:
                fb_nfs['name'] = item.name
                fb_nfs['created_size'] = str(item.created)
                fb_nfs['provisioned_size'] = str(item.provisioned)
                fb_nfs['fast_remove'] = item.fast_remove_directory_enabled
                fb_nfs['nfs'] = "NFSv3 Enabled" if item.nfs.v3_enabled else "NFSv4.1 Enabled"
                fb_nfs['nfs_rule'] = item.nfs.rules
                fb_nfs_list.append(fb_nfs.copy())
            if [fb_dict for fb_dict in fb_nfs_list if not fb_dict == fb_ini] != []:
                return PTK_OKAY, fb_nfs_list, _("PDT_SUCCESS_MSG")
            loginfo("Unable to get " + method)
            return PTK_NOTEXIST, fb_nfs_list, "Unable to get " + method
        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_nfs_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_nfs_list, str(e)

    finally:
        lock.release()


def get_fb_lag_list(args={}):
    """
    Function to obtain LAGs in FlashBlade

    Parameters:
        args (dict): None.

    Returns:
        List of LAGs created in FlashBlade.

    """
    fb_lag_list = []
    fb_ini = {
        'name': "",
        'id': "",
        'lag_speed': "",
        'port_speed': "",
        'mac_address': "",
        'state': "",
        'ports': ""}
    #fb_lag =copy.deepcopy(fb_ini)
    method = "FlashBlade LAG List"
    try:
        lock.acquire()
        fb_task_obj = _fb_handler()
        if fb_task_obj is not None:
            fb_hw_list = fb_task_obj.fb.hardware.list_hardware().to_dict().get('items')
            fb_eth_list = [hw for hw in fb_hw_list if hw['type'] == 'eth']
            fb_lag_list = fb_task_obj.fb.link_aggregation_groups.list_link_aggregation_groups().to_dict().get('items')
            [fb_lag.update({'state': 'up' if fb_lag['status'] == 'healthy' else 'down'})
             for fb_lag in fb_lag_list]
            [port.update({'state': 'up' if iface['status'] == 'healthy' else 'unused' if iface['status'] == 'unused' else 'down'})
             for lag in fb_lag_list for port in lag['ports'] for iface in fb_eth_list if port['name'] == iface['name']]

            # TODO: MAC address of lag is None in list_link_aggregation_groups()
            # output. So taking it from cli.
            fb_cred = get_device_details('fb_id')
            error, output = execute_remote_command(
                fb_cred['ipaddress'], fb_cred['username'], fb_cred['password'], "purelag list --csv")
            if error == 0:
                output = list(filter(None, [op.rstrip() for op in output.split('\n')[1:]]))
                lag_cli_list = [{'name': lag.split(',')[0],
                                 'mac': lag.split(',')[-1]} for lag in output]
                [lag_sdk.update({'mac_address': lag_cli.get(
                    'mac')}) for lag_sdk in fb_lag_list for lag_cli in lag_cli_list if lag_sdk['name'] == lag_cli['name']]

            [lag.update({'lag_speed': str(int(lag['lag_speed'] / (1000 * 1000 * 1000))) + ' Gb/s',
                         'port_speed':str(int(lag['port_speed'] / (1000 * 1000 * 1000))) + ' Gb/s'}) for lag in fb_lag_list]
            return PTK_OKAY, fb_lag_list, _("PDT_SUCCESS_MSG")

        loginfo("Failed to get Handler for FlashBlade Report Generation " + method)
        return PTK_RESOURCENOTAVAILABLE, fb_lag_list, "Failed to get Handler for FlashBlade Report Generation"

    except Exception as e:
        loginfo("An Exception occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fb_lag_list, str(e)

    finally:
        lock.release()
