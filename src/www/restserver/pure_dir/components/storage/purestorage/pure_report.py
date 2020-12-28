from pure_dir.components.storage.purestorage.pure_tasks import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import getAsList
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_global_wf_config_file
from pure_dir.components.common import get_device_credentials
from pure_dir.services.utils.miscellaneous import *
from purestorage import FlashArray
import xmltodict
import copy
import urllib.error
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
        for key, val in g_hw_details.items():
            if key != hw_type:
                continue
            cred = get_device_credentials(
                key="mac", value=val)
            return cred

    except urllib.error.URLError as e:
        loginfo("Failed during FlashArray Report Generation" + str(e))

    return None


def _pure_handler():
    """ To get FlashArray Handle to access the REST APIs."""
    pure_creden = {}
    pure_creden = get_device_details('pure_id')
    try:
        pure_obj = PureTasks(ipaddress=pure_creden['ipaddress'],
                             username=pure_creden['username'],
                             password=pure_creden['password'])
        handle = pure_obj.pure_handler(ipaddress=pure_creden['ipaddress'],
                                       username=pure_creden['username'],
                                       password=pure_creden['password'])
        return handle, pure_obj
    except Exception as e:
        loginfo("Failed to get Pure handler")
        return None, None


def get_fa_system_info(args={}):
    """
    Function to obtain FlashArray System Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Info.

    """
    fa_info_list = []
    array_tmp_dict = {}
    fa_ini = {
        'array_name': "",
        'array_ip': "",
        'array_id': "",
        'array_version': "",
        'array_revision': "",
        'array_capacity': "",
        'serial_no': ""}
    fa_info = copy.deepcopy(fa_ini)
    method = "FlashArray System Info"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            array_tmp_dict = handle.get()
            fa_info['array_name'] = array_tmp_dict['array_name']
            fa_info['array_ip'] = get_device_details('pure_id')['ipaddress']
            fa_info['array_id'] = array_tmp_dict['id']
            fa_info['array_version'] = array_tmp_dict['version']
            fa_info['array_revision'] = array_tmp_dict['revision']
            fa_info['array_capacity'] = str(handle.get(space=True)[0]['capacity'])
            fa_info['serial_no'] = pure_obj.getSerial_no(fa_info['array_ip'])
            fa_info_list.append(fa_info.copy())
            if [fa_dict for fa_dict in fa_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_controller_info(args={}):
    """
    Function to obtain FlashArray Controller Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Controller Info.

    """
    fa_controller_info_list = []
    array_tmp_list = []
    fa_ini = {
        'fa_controller_name': "",
        'fa_controller_mode': "",
        'fa_controller_status': "",
        'fa_controller_model': ""}
    fa_controller_info = copy.deepcopy(fa_ini)
    method = "FlashArray Controllers Info"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            array_tmp_list = handle.get(controllers=True)
            for controller in array_tmp_list:
                fa_controller_info['fa_controller_name'] = controller['name']
                fa_controller_info['fa_controller_mode'] = controller['mode']
                fa_controller_info['fa_controller_status'] = controller['status']
                fa_controller_info['fa_controller_model'] = controller['model']
                fa_controller_info_list.append(fa_controller_info.copy())
            if [fa_dict for fa_dict in fa_controller_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_controller_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_controller_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_controller_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_controller_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_global_settings_info(args={}):
    """
    Function to obtain FlashArray Global Settings Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Global Settings Info.

    """
    fa_global_info_list = []
    array_tmp_dict = {}
    fa_ini = {'domain': "", 'dns_servers': "", 'ntp_servers': "", 'phone_home': ""}
    fa_global_info = copy.deepcopy(fa_ini)
    method = "FlashArray Global Settings Info"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            array_tmp_dict = handle.get_dns()
            fa_global_info['domain'] = array_tmp_dict['domain']
            fa_global_info['dns_servers'] = array_tmp_dict['nameservers']
            fa_global_info['ntp_servers'] = handle.get(ntpserver=True)['ntpserver']
            fa_global_info['phone_home'] = handle.get(phonehome=True)['phonehome']
            fa_global_info_list.append(fa_global_info.copy())
            if [fa_dict for fa_dict in fa_global_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_global_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_global_info_list, "Unable to get " + method
        else:
            #loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_global_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_global_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_nw_interfaces(args={}):
    """
    Function to obtain FlashArray Network Interfaces.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Network Interfaces.

    """
    fa_nw_interf_info_list = []
    array_tmp_list = []
    fa_ini = {
        'interf_name': "",
        'subnet': "",
        'ip_addr': "",
        'netmask': "",
        'gateway': "",
        'mtu': "",
        'speed': "",
        'status': "",
        'services': "",
        'hw_addr': ""}
    fa_nw_interf_info = copy.deepcopy(fa_ini)
    method = "FlashArray Network Interfaces"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            array_tmp_list = handle.list_network_interfaces()
            for nw_interf in array_tmp_list:
                fa_nw_interf_info['interf_name'] = nw_interf['name']
                fa_nw_interf_info['subnet'] = nw_interf['subnet']
                fa_nw_interf_info['ip_addr'] = nw_interf['address']
                fa_nw_interf_info['netmask'] = nw_interf['netmask']
                fa_nw_interf_info['gateway'] = nw_interf['gateway']
                fa_nw_interf_info['mtu'] = str(nw_interf['mtu'])
                fa_nw_interf_info['speed'] = str(nw_interf['speed'])
                fa_nw_interf_info['status'] = nw_interf['enabled']
                fa_nw_interf_info['services'] = nw_interf['services']
                fa_nw_interf_info['hw_addr'] = nw_interf['hwaddr']
                fa_nw_interf_info_list.append(fa_nw_interf_info.copy())
            if [fa_dict for fa_dict in fa_nw_interf_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_nw_interf_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_nw_interf_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_nw_interf_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_nw_interf_info, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_host_group(args={}):
    """
    Function to obtain FlashArray Host Group.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Host Group.

    """
    fa_hgroup_info_list = []
    fa_hgroup_list = []
    fa_hgroup_vol = []
    fa_hgroup_size = []
    fa_ini = {'hgroup_name': "", 'hosts': "", 'shared_vol': "", 'size': ""}
    fa_hgroup_info = copy.deepcopy(fa_ini)
    method = "FlashArray Host Group"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            fa_hgroup_list = handle.list_hgroups()
            fa_hgroup_vol = handle.list_hgroups(connect=True)
            fa_hgroup_size = handle.list_hgroups(space=True)
            for hgroup in fa_hgroup_list:
                fa_hgroup_info['hgroup_name'] = hgroup['name']
                fa_hgroup_info['hosts'] = hgroup['hosts']
                for hg_vol in fa_hgroup_vol:
                    if fa_hgroup_info['hgroup_name'] == hg_vol['name']:
                        fa_hgroup_info['shared_vol'] = hg_vol['vol']
                        break
                for hg_size in fa_hgroup_size:
                    if fa_hgroup_info['hgroup_name'] == hg_size['name']:
                        fa_hgroup_info['size'] = str(hg_size['size'])
                        break
                fa_hgroup_info_list.append(fa_hgroup_info.copy())
            if [fa_dict for fa_dict in fa_hgroup_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_hgroup_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_hgroup_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_hgroup_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_hgroup_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_volumes(args={}):
    """
    Function to obtain FlashArray Volumes.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Volumes.

    """
    fa_volumes_info_list = []
    array_tmp_list = []
    vol_serial_list = []
    shared_vol_list = []
    fa_ini = {'vol_name': "", 'serial': "", 'lun_id': "", 'size': "", 'vol_type': ""}
    fa_volumes_info = copy.deepcopy(fa_ini)
    method = "FlashArray Volumes"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            array_tmp_list = handle.list_volumes(connect=True, private=True)
            shared_vol_list = handle.list_volumes(connect=True, shared=True)
            vol_serial_list = handle.list_volumes()
            for volume in array_tmp_list:
                fa_volumes_info['vol_name'] = volume['name']
                fa_volumes_info['lun_id'] = str(volume['lun'])
                fa_volumes_info['size'] = str(volume['size'])
                fa_volumes_info['vol_type'] = "Private Volume"
                for vol_serial in vol_serial_list:
                    if fa_volumes_info['vol_name'] == vol_serial['name']:
                        fa_volumes_info['serial'] = vol_serial['serial']
                        break
                fa_volumes_info_list.append(fa_volumes_info.copy())
            for shared_vol in shared_vol_list:
                if [fa_vol['vol_name']
                        for fa_vol in fa_volumes_info_list if shared_vol['name'] == fa_vol['vol_name']] == []:
                    fa_volumes_info['vol_name'] = shared_vol['name']
                    fa_volumes_info['lun_id'] = str(shared_vol['lun'])
                    fa_volumes_info['size'] = str(shared_vol['size'])
                    fa_volumes_info['vol_type'] = "Shared Volume"
                    for vol_serial in vol_serial_list:
                        if fa_volumes_info['vol_name'] == vol_serial['name']:
                            fa_volumes_info['serial'] = vol_serial['serial']
                            break
                    fa_volumes_info_list.append(fa_volumes_info.copy())
            if [fa_dict for fa_dict in fa_volumes_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_volumes_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_volumes_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_volumes_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_volumes_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_ports(args={}):
    """
    Function to obtain FlashArray Ports.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Ports.

    """
    fa_ports_info_list = []
    array_tmp_list = []
    fa_ini = {
        'interf_name': "",
        'initiator_wwn': "",
        'target_wwn': "",
        'initiator_iqn': "",
        'target_iqn': ""}
    fa_ports_info = copy.deepcopy(fa_ini)
    method = "FlashArray Ports"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            array_tmp_list = handle.list_ports(initiators=True)
            for port in array_tmp_list:
                if port['target'] is not None:
                    fa_ports_info['interf_name'] = port['target']
                    fa_ports_info['initiator_wwn'] = port['wwn']
                    fa_ports_info['target_wwn'] = port['target_wwn']
                    fa_ports_info['initiator_iqn'] = port['iqn']
                    fa_ports_info['target_iqn'] = port['target_iqn']
                    if fa_ports_info != fa_ini:
                        fa_ports_info_list.append(fa_ports_info.copy())
            if [fa_dict for fa_dict in fa_ports_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_ports_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_ports_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_ports_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_ports_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()


def get_fa_hosts(args={}):
    """
    Function to obtain FlashArray Hosts.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of FlashArray Hosts.

    """
    fa_hosts_info_list = []
    method = "FlashArray Hosts"
    try:
        handle, pure_obj = _pure_handler()
        if handle and pure_obj is not None:
            host_list = handle.list_hosts()
            vol_list = handle.list_hosts(connect=True)
            vol_size_list = handle.list_hosts(space=True)
            for host in host_list:
                fa_ini = {
                    'host_name': "",
                    'connected_volumes': [],
                    'iqn': [],
                    'wwn': [],
                    'lun_id': [],
                    'size': ""}
                fa_hosts_info = copy.deepcopy(fa_ini)
                fa_hosts_info['host_name'] = host['name']
                if host['wwn'] != []:
                    fa_hosts_info['wwn'] = host['wwn']
                if host['iqn'] != []:
                    fa_hosts_info['iqn'] = host['iqn']
                for volume in vol_list:
                    if volume['name'] == host['name']:
                        fa_hosts_info['connected_volumes'].append(volume['vol'])
                        fa_hosts_info['lun_id'].append(str(volume['lun']))
                for vol_space in vol_size_list:
                    if vol_space['name'] == host['name']:
                        fa_hosts_info['size'] = str(vol_space['size'])
                fa_hosts_info_list.append(copy.deepcopy(fa_hosts_info))
            if [fa_dict for fa_dict in fa_hosts_info_list if not fa_dict == fa_ini] != []:
                return PTK_OKAY, fa_hosts_info_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, fa_hosts_info_list, "Unable to get " + method
        else:
            loginfo("failed to get Pure Handler for FlashArray Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fa_hosts_info_list, "failed to get Pure Handler for FlashArray Report Generation"

    except Exception as e:
        loginfo("Exception has occured while fetching " + method + str(e))
        return PTK_INTERNALERROR, fa_hosts_info_list, str(e)

    finally:
        #loginfo("Released the Pure Handle after fetching " + method)
        pure_obj.release_pure_handle()
