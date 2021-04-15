from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.global_config import get_settings_file
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.ucsexception import UcsException
from pure_dir.services.utils.miscellaneous import *
import xmltodict
import copy
import urllib.error
from threading import Lock
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_global_wf_config_file
from pure_dir.components.common import get_device_credentials

g_hw_details = {}
g_ucs_handle = None
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
                        'pure_id']:
                    g_hw_details[input_val['@name']] = input_val['@value']
        for key, val in g_hw_details.items():
            if key != hw_type:
                continue
            cred = get_device_credentials(
                key="mac", value=val)
            return cred

    except urllib.error.URLError as e:
        loginfo("Failed during UCS Report Generation" + str(e))

    return None


def _ucs_handler():
    """ To get UCS Handle to access the REST APIs."""
    ucs_creden = {}
    global g_ucs_handle
    ucs_creden = get_device_details('ucs_switch_a')
    if g_ucs_handle is not None:
        "Check if handle.show version returns a value.if not do  relogin"
        return g_ucs_handle

    try:
        handle = UcsHandle(ucs_creden['vipaddress'],
                           ucs_creden['username'],
                           ucs_creden['password'])
        g_ucs_handle = handle
        if handle is not None:
            login_state = handle.login()
            if login_state:
                loginfo("Taken UCSHandle")
                return handle
            else:
                return None
        else:
            return None
    except BaseException as be:
        loginfo("Failed to get ucs handler " + str(be))
        return None
    except UcsException as ue:
        loginfo("Failed to get ucs handler " + str(ue))
        return None
    except Excepton as e:
        loginfo("Failed to get ucs handler " + str(e))
        return None


def release_ucsm_handler():
    """To release UCS Handle."""
    global g_ucs_handle
    res = result()
    if g_ucs_handle is not None:
        g_ucs_handle.logout()
        res.setResult(True, PTK_OKAY, "Released UCS Handle")
        loginfo("Released UCS handle")
        g_ucs_handle = None
        return res
    g_ucs_handle = None
    res.setResult(False, PTK_NOTEXIST, "UCS Handle doesn't exist")
    return res

# UCS : Compute Infra


def get_ucs_system_cluster_info(args={}):
    """
    Function to obtain UCS Cluster Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Cluster Info.

    """
    ucs_cluster_list = []
    method = "UCS System Cluster Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_cluster_list, "failed to get handler for UCS Report Generation"
        ucs_ini = {
            'name': "",
            'ip': "",
            'ucsm_version': "",
            'chassis_discovery': "",
            'power_redundancy': "",
            'mgmt_interface_monitoring': "",
            'eth_switchmode': ""}
        ucs_cluster = copy.deepcopy(ucs_ini)
        if args['san_type'] == "FC":
            ucs_ini['fc_switchmode'] = ""
            ucs_cluster['fc_switchmode'] = ""
        mo = handle.query_dn("sys")
        version_info = handle.query_dn("sys/mgmt/fw-system")
        ucs_cluster['name'] = mo.name
        ucs_cluster['ip'] = mo.address
        ucs_cluster['ucsm_version'] = version_info.version
        ucs_cluster['chassis_discovery'] = handle.query_dn("org-root/chassis-discovery").action
        ucs_cluster['power_redundancy'] = handle.query_dn("org-root/psu-policy").redundancy
        ucs_cluster['mgmt_interface_monitoring'] = handle.query_dn(
            "sys/extmgmt-intf-monitor-policy").admin_state
        ucs_cluster['eth_switchmode'] = handle.query_dn("fabric/lan").mode
        if args['san_type'] == "FC":
            ucs_cluster['fc_switchmode'] = handle.query_dn("fabric/san").mode
        ucs_cluster_list.append(ucs_cluster.copy())
        if [ucs_dict for ucs_dict in ucs_cluster_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_cluster_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_cluster_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_cluster_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_fi_info(args={}):
    """
    Function to obtain UCS Fabric Interconnect Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS FI Info.

    """
    ucs_fiinfo_list = []
    method = "UCS System Fabric Interconnect Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_fiinfo_list, "failed to get handler for UCS Report Generation"
        for ucs_info in handle.query_classid(class_id="NetworkElement"):
            ucs_ini = {
                'fabric_name': "",
                'fabric_ip': "",
                'fabric_subnetmask': "",
                'fabric_gateway': "",
                'model': "",
                'serial': "",
                'leadership': "",
                'nxos_system': "",
                'nxos_kickstart': ""}
            ucs_fiinfo = copy.deepcopy(ucs_ini)
            ucs_fiinfo['fabric_name'] = handle.query_dn(
                "sys").name + "-" + ucs_info.id
            ucs_fiinfo['fabric_ip'] = ucs_info.oob_if_ip
            ucs_fiinfo['fabric_subnetmask'] = ucs_info.oob_if_mask
            ucs_fiinfo['fabric_gateway'] = ucs_info.oob_if_gw
            ucs_fiinfo['model'] = ucs_info.model
            ucs_fiinfo['serial'] = ucs_info.serial
            dn_str = "sys/mgmt-entity-" + ucs_info.id
            ucs_fiinfo['leadership'] = handle.query_dn(dn_str).leadership
            dn_str_system = "sys/switch-" + ucs_info.id + "/mgmt/fw-boot-def/bootunit-system"
            dn_str_kernel = "sys/switch-" + ucs_info.id + "/mgmt/fw-boot-def/bootunit-kernel"
            ucs_fiinfo['nxos_system'] = handle.query_dn(dn_str_system).version
            ucs_fiinfo['nxos_kickstart'] = handle.query_dn(dn_str_kernel).version
            ucs_fiinfo_list.append(ucs_fiinfo.copy())
        if [ucs_dict for ucs_dict in ucs_fiinfo_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_fiinfo_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_fiinfo_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_fiinfo_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_fi_inventory(args={}):
    """
    Function to obtain UCS Fabric Interconnect Inventory Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS FI Inventory Info.

    """
    ucs_fiinventory_list = []
    method = "UCS System Fabric Interconnect Inventory"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_fiinventory_list, "failed to get handler for UCS Report Generation"
        for ucs_fiinv in handle.query_classid(class_id="NetworkElement"):
            ucs_ini = {
                'fabric_name': "",
                'dn': "",
                'model': "",
                'description': "",
                'operability': "",
                'state': "",
                'serial': ""}
            ucs_fiinventory = copy.deepcopy(ucs_ini)
            mo_inv = handle.query_dn(ucs_fiinv.dn + "/slot-1")
            ucs_fiinventory['fabric_name'] = handle.query_dn(
                "sys").name + "-" + ucs_fiinv.id
            ucs_fiinventory['dn'] = mo_inv.dn
            ucs_fiinventory['model'] = mo_inv.model
            ucs_fiinventory['description'] = mo_inv.descr
            ucs_fiinventory['operability'] = mo_inv.operability
            ucs_fiinventory['state'] = mo_inv.state
            ucs_fiinventory['serial'] = mo_inv.serial
            ucs_fiinventory_list.append(ucs_fiinventory.copy())
        if [ucs_dict for ucs_dict in ucs_fiinventory_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_fiinventory_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_fiinventory_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_fiinventory_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_fi_globalsettings(args={}):
    """
    Function to obtain UCS Fabric Interconnect Global Settings Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS FI Global Settings Info.

    """
    ucs_figlobalset_list = []
    method = "UCSM Cluster Global settings area"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_figlobalset_list, "failed to get handler for UCS Report Generation"
        for fi_global in handle.query_classid(class_id="CommSvcEp"):
            ucs_ini = {
                'domain': "",
                'timezone': "",
                'snmp_community': "",
                'dns': [],
                'ntp_server': [],
                'syslog_server': [],
                'snmp_trapreceiver': []}
            ucs_figlobalset = copy.deepcopy(ucs_ini)
            if len(handle.query_children(in_mo=fi_global)) != 0:
                mo_global_dns = handle.query_children(in_mo=fi_global, class_id="CommDns")
                mo_global_time = handle.query_children(in_mo=fi_global, class_id="CommDateTime")
                mo_global_syslog = handle.query_children(in_mo=fi_global, class_id="CommSyslog")
                mo_global_snmp = handle.query_children(in_mo=fi_global, class_id="CommSnmp")
                for fi_globchild in mo_global_dns:
                    if fi_globchild.get_class_id() == "CommDns":
                        ucs_figlobalset['domain'] = fi_globchild.domain
                        if len(handle.query_children(in_mo=fi_globchild)) != 0:
                            mo_global_child = handle.query_children(
                                in_mo=fi_globchild, class_id="CommDnsProvider")
                            for fi_dnschild in mo_global_child:
                                if fi_dnschild.get_class_id() == "CommDnsProvider":
                                    ucs_figlobalset['dns'].append(fi_dnschild.name)
                for fi_globchild in mo_global_time:
                    if fi_globchild.get_class_id() == "CommDateTime":
                        ucs_figlobalset['timezone'] = fi_globchild.oper_timezone
                        if len(handle.query_children(in_mo=fi_globchild)) != 0:
                            mo_global_child = handle.query_children(
                                in_mo=fi_globchild, class_id="CommNtpProvider")
                            for fi_ntpchild in mo_global_child:
                                if fi_ntpchild.get_class_id() == "CommNtpProvider":
                                    ucs_figlobalset['ntp_server'].append(fi_ntpchild.name)
                for fi_globchild in mo_global_syslog:
                    if fi_globchild.get_class_id() == "CommSyslog":
                        if len(handle.query_children(in_mo=fi_globchild)) != 0:
                            mo_global_child = handle.query_children(
                                in_mo=fi_globchild, class_id="CommSyslogClient")
                            for fi_syschild in mo_global_child:
                                if fi_syschild.get_class_id() == "CommSyslogClient":
                                    ucs_figlobalset['syslog_server'].append(
                                        fi_syschild.hostname + "/" + fi_syschild.forwarding_facility + "/" + fi_syschild.severity)
                for fi_globchild in mo_global_snmp:
                    if fi_globchild.get_class_id() == "CommSnmp":
                        ucs_figlobalset['snmp_community'] = fi_globchild.community
                        if len(handle.query_children(in_mo=fi_globchild)) != 0:
                            mo_global_child = handle.query_children(
                                in_mo=fi_globchild, class_id="CommSnmpTrap")
                        for fi_snmpchild in mo_global_child:
                            if fi_snmpchild.get_class_id() == "CommSnmpTrap":
                                ucs_figlobalset['snmp_trapreceiver'].append(
                                    fi_snmpchild.hostname + "/" + fi_snmpchild.community)
            ucs_figlobalset_list.append(copy.deepcopy(ucs_figlobalset))
        if [ucs_dict for ucs_dict in ucs_figlobalset_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_figlobalset_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_figlobalset_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_figlobalset_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_organizations(args={}):
    """
    Function to obtain UCS Organizations.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Oganizations.

    """
    ucs_sysorg_list = []
    method = "Organizations"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_sysorg_list, "failed to get handler for UCS Report Generation"
        for ucs_org in handle.query_classid(class_id="OrgOrg"):
            ucs_ini = {'name': "", 'dn': ""}
            ucs_sysorg = copy.deepcopy(ucs_ini)
            ucs_sysorg['name'] = ucs_org.name
            ucs_sysorg['dn'] = ucs_org.dn
            ucs_sysorg_list.append(ucs_sysorg)
        if [ucs_dict for ucs_dict in ucs_sysorg_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_sysorg_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_sysorg_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_sysorg_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_callhomebase(args={}):
    """
    Function to obtain UCS Call Home Base.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Call Home Base Info.

    """
    ucs_callhome_list = []
    method = "UCS System Call home base area"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_callhome_list, "failed to get handler for UCS Report Generation"
        for ucs_syscall in handle.query_classid(class_id="CallhomeEp"):
            ucs_ini = {
                'admin_state': "", 'inventory': "", 'contact_details': {
                    'contactname': {
                        "label": "Contact Name", "value": ""}, 'contactphone': {
                        "label": "Contact Phone", "value": ""}, 'contactemail': {
                        "label": "Contact Email", "value": ""}, 'contactaddress': {
                        "label": "Contact Address", "value": ""}, 'contractno': {
                            "label": "Contract No", "value": ""}, 'customerno': {
                                "label": "Customer No", "value": ""}, 'siteno': {
                                    "label": "Site No", "value": ""}}, 'mail_details': {
                                        'emailfrom': {
                                            "label": "Email From", "value": ""}, 'emailto': {
                                                "label": "Email To", "value": ""}}}
            ucs_callhome = copy.deepcopy(ucs_ini)
            mo_homebase = handle.query_children(in_mo=ucs_syscall)
            if len(mo_homebase) != 0:
                for ucs_syscall_child in mo_homebase:
                    if ucs_syscall_child.get_class_id() == "CallhomePeriodicSystemInventory":
                        ucs_callhome['admin_state'] = ucs_syscall_child.admin_state
                        ucs_callhome['inventory'] = ucs_syscall_child.admin_state + \
                            "/every " + ucs_syscall_child.interval_days + \
                            " Days(s)"
                    if ucs_syscall_child.get_class_id() == "CallhomeSource":
                        ucs_callhome['contact_details'] = {
                            'contactname': {
                                "label": "Contact Name", "value": ucs_syscall_child.contact}, 'contactphone': {
                                "label": "Contact Phone", "value": ucs_syscall_child.phone}, 'contactemail': {
                                "label": "Contact Email", "value": ucs_syscall_child.email}, 'contactaddress': {
                                "label": "Contact Address", "value": ucs_syscall_child.addr}, 'contractno': {
                                "label": "Contract No", "value": ucs_syscall_child.contract}, 'customerno': {
                                "label": "Customer No", "value": ucs_syscall_child.customer}, 'siteno': {
                                "label": "Site No", "value": ucs_syscall_child.site}}
                        ucs_callhome['mail_details'] = {
                            'emailfrom': {"label": "Email From", "value": ucs_syscall_child.r_from},
                            'emailto': {"label": "Email To", "value": ucs_syscall_child.reply_to}}
                    if ucs_syscall_child.get_class_id() == "CallhomeSmtp":
                        ucs_callhome['mail_details'].update(
                            {'mailserver': {"label": "Mail Server", "value": ucs_syscall_child.host + ":" + ucs_syscall_child.port}})
            ucs_callhome_list.append(copy.deepcopy(ucs_callhome))
        if [ucs_dict for ucs_dict in ucs_callhome_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_callhome_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_callhome_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_callhome_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_callhome_profiles(args={}):
    """
    Function to obtain UCS Call Home Profile Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Call Home Profile Info.

    """
    ucs_callhome_profiles_list = []
    method = "UCS System Call home profiles"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_callhome_profiles_list, "failed to get handler for UCS Report Generation"
        for ucs_callhome in handle.query_classid(class_id="CallhomeProfile"):
            ucs_ini = {'name': "", 'level': "", 'alert_groups': "", 'destn_email': []}
            ucs_callhome_profiles = copy.deepcopy(ucs_ini)
            ucs_callhome_profiles['name'] = ucs_callhome.name
            ucs_callhome_profiles['level'] = ucs_callhome.level
            ucs_callhome_profiles['alert_groups'] = ucs_callhome.alert_groups
            if len(handle.query_children(in_mo=ucs_callhome)) != 0:
                mo_homeprofile = handle.query_children(in_mo=ucs_callhome, class_id="CallhomeDest")
                for mo_child in mo_homeprofile:
                    if mo_child.get_class_id() == "CallhomeDest":
                        ucs_callhome_profiles['destn_email'].append(mo_child.email)
            ucs_callhome_profiles_list.append(copy.deepcopy(ucs_callhome_profiles))
        if [ucs_dict for ucs_dict in ucs_callhome_profiles_list if not ucs_dict == ucs_ini] != [
        ]:
            return PTK_OKAY, ucs_callhome_profiles_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_callhome_profiles_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_callhome_profiles_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_licenseinfo(args={}):
    """
    Function to obtain UCS License Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS License Info.

    """
    ucs_licenseinfo_list = []
    method = "UCS System License Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_licenseinfo_list, "failed to get handler for UCS Report Generation"
        for ucs_system_lic in handle.query_classid(class_id="LicenseFeature"):
            ucs_ini = {
                'fabric': "",
                'feature_type': "",
                'state': "",
                'default_qty': "",
                'total_qty': "",
                'is_present': "",
                'total_used_qty': "",
                'peer_status': "",
                'time_left': ""}
            ucs_licenseinfo = copy.deepcopy(ucs_ini)
            ucs_licenseinfo['time_left'] = ucs_system_lic.grace_period
            mo_license = handle.query_children(in_mo=ucs_system_lic)
            if len(mo_license) != 0:
                for ucs_system_lic_child in mo_license:
                    ucs_licenseinfo['fabric'] = ucs_system_lic_child.scope
                    ucs_licenseinfo['feature_type'] = ucs_system_lic_child.feature
                    ucs_licenseinfo['state'] = ucs_system_lic_child.oper_state
                    ucs_licenseinfo['default_qty'] = ucs_system_lic_child.def_quant
                    ucs_licenseinfo['total_qty'] = ucs_system_lic_child.abs_quant
                    ucs_licenseinfo['is_present'] = ucs_system_lic_child.is_present
                    ucs_licenseinfo['total_used_qty'] = ucs_system_lic_child.used_quant
                    ucs_licenseinfo['peer_status'] = ucs_system_lic_child.peer_status
                    ucs_licenseinfo_list.append(ucs_licenseinfo.copy())
        if [ucs_dict for ucs_dict in ucs_licenseinfo_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_licenseinfo_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_licenseinfo_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_licenseinfo_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_chassisinfo(args={}):
    """
    Function to obtain UCS Chassis Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Chassis Info.

    """
    ucs_chassisinfo_list = []
    method = "UCS System License Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_chassisinfo_list, "failed to get handler for UCS Report Generation"
        for ucs_system_chassis in handle.query_classid(class_id="EquipmentChassis"):
            ucs_ini = {
                'chassis_id': "",
                'model': "",
                'serial_no': "",
                'state': "",
                'iom1_model': "",
                'iom1_sn': "",
                'iom1_fw': "",
                'iom2_model': "",
                'iom2_sn': "",
                'iom2_fw': ""}
            ucs_chassisinfo = copy.deepcopy(ucs_ini)
            ucs_chassisinfo['chassis_id'] = ucs_system_chassis.id
            ucs_chassisinfo['model'] = ucs_system_chassis.model
            ucs_chassisinfo['serial_no'] = ucs_system_chassis.serial
            ucs_chassisinfo['state'] = ucs_system_chassis.oper_state
            if len(handle.query_children(in_mo=ucs_system_chassis)) != 0:
                mo_chassis = handle.query_children(
                    in_mo=ucs_system_chassis, class_id="EquipmentIOCard")
                for ucs_system_chassis_child in mo_chassis:
                    if len(handle.query_children(in_mo=ucs_system_chassis_child)) != 0:
                        chassis_child = handle.query_children(
                            in_mo=ucs_system_chassis_child, class_id="MgmtController")
                        if ucs_system_chassis_child.get_class_id() == "EquipmentIOCard":
                            if ucs_system_chassis_child.id == "1":
                                ucs_chassisinfo['iom1_model'] = ucs_system_chassis_child.model
                                ucs_chassisinfo['iom1_sn'] = ucs_system_chassis_child.serial
                                for ucs_system_iomchild in chassis_child:
                                    if len(handle.query_children(in_mo=ucs_system_iomchild)) != 0:
                                        chassis_fw_child = handle.query_children(
                                            in_mo=ucs_system_iomchild, class_id="FirmwareRunning")
                                        if ucs_system_iomchild.get_class_id() == "MgmtController":
                                            for ucs_system_fw_child in chassis_fw_child:
                                                if ucs_system_fw_child.get_class_id() == "FirmwareRunning" and "fw-system" in ucs_system_fw_child.dn:
                                                    ucs_chassisinfo['iom1_fw'] = ucs_system_fw_child.version
                                                    break
                            elif ucs_system_chassis_child.id == "2":
                                ucs_chassisinfo['iom2_model'] = ucs_system_chassis_child.model
                                ucs_chassisinfo['iom2_sn'] = ucs_system_chassis_child.serial
                                for ucs_system_iomchild in chassis_child:
                                    if len(handle.query_children(in_mo=ucs_system_iomchild)) != 0:
                                        chassis_fw_child = handle.query_children(
                                            in_mo=ucs_system_iomchild, class_id="FirmwareRunning")
                                        if ucs_system_iomchild.get_class_id() == "MgmtController":
                                            if len(chassis_fw_child) != 0:
                                                for ucs_system_fw_child in chassis_fw_child:
                                                    if ucs_system_fw_child.get_class_id() == "FirmwareRunning" and "fw-system" in ucs_system_fw_child.dn:
                                                        ucs_chassisinfo['iom2_fw'] = ucs_system_fw_child.version
                                                        break
            ucs_chassisinfo_list.append(ucs_chassisinfo.copy())
        if [ucs_dict for ucs_dict in ucs_chassisinfo_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_chassisinfo_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_chassisinfo_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_chassisinfo_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_serverinfo(args={}):
    """
    Function to obtain UCS Server Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server Info.

    """
    ucs_serverinfo_list = []
    method = "UCS System Blade & Rack Server Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        server_types = ["ComputeBlade", "ComputeRackUnit"]
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_serverinfo_list, "failed to get handler for UCS Report Generation"
        for server_type in server_types:
            for ucs_sys_server in handle.query_classid(class_id=server_type):
                ucs_ini = {
                    'location': "",
                    'part_no': "",
                    'model': "",
                    'serial_no': "",
                    'cpu_cores': "",
                    'memory': "",
                    'mgmt_ip': "",
                    'bios': ""}
                ucs_serverinfo = copy.deepcopy(ucs_ini)
                if server_type == "ComputeBlade":
                    ucs_serverinfo['location'] = ucs_sys_server.chassis_id + \
                        "/" + ucs_sys_server.slot_id
                else:
                    ucs_serverinfo['location'] = "RackUnit-" + ucs_sys_server.id
                ucs_serverinfo['part_no'] = ucs_sys_server.part_number
                ucs_serverinfo['model'] = ucs_sys_server.model
                ucs_serverinfo['serial_no'] = ucs_sys_server.serial
                ucs_serverinfo['cpu_cores'] = ucs_sys_server.num_of_cpus + \
                    "/" + ucs_sys_server.num_of_cores
                ucs_serverinfo['memory'] = ucs_sys_server.total_memory
                if len(handle.query_children(in_mo=ucs_sys_server)) != 0:
                    mo_server_mgmt = handle.query_children(
                        in_mo=ucs_sys_server, class_id="MgmtController")
                    mo_server_bios = handle.query_children(
                        in_mo=ucs_sys_server, class_id="BiosUnit")
                    for ucs_sys_server_child in mo_server_mgmt:
                        if len(handle.query_children(in_mo=ucs_sys_server_child)) != 0:
                            server_child = handle.query_children(
                                in_mo=ucs_sys_server_child, class_id="VnicIpV4PooledAddr")
                            if ucs_sys_server_child.get_class_id() == "MgmtController":
                                for ucs_mgmt_child in server_child:
                                    if ucs_mgmt_child.get_class_id() == "VnicIpV4PooledAddr":
                                        ucs_serverinfo['mgmt_ip'] = ucs_mgmt_child.addr
                                        break
                    for ucs_sys_server_child in mo_server_bios:
                        if ucs_sys_server_child.get_class_id() == "BiosUnit":
                            if len(handle.query_children(in_mo=ucs_sys_server_child)) != 0:
                                server_child = handle.query_children(
                                    in_mo=ucs_sys_server_child, class_id="FirmwareRunning")
                                for ucs_sys_bios_child in server_child:
                                    if ucs_sys_bios_child.get_class_id() == "FirmwareRunning":
                                        ucs_serverinfo['bios'] = ucs_sys_bios_child.version
                                        break
                ucs_serverinfo_list.append(copy.deepcopy(ucs_serverinfo))
        if [ucs_dict for ucs_dict in ucs_serverinfo_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_serverinfo_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_serverinfo_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_serverinfo_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_config_info(args={}):
    """
    Function to obtain UCS Server Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server Info.

    """
    ucs_serverinfo_list = []
    method = "UCS System Server Configuration Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        server_types = ["ComputeBlade", "ComputeRackUnit"]
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_serverinfo_list, "failed to get handler for UCS Report Generation"
        for server_type in server_types:
            for ucs_sys_server in handle.query_classid(class_id=server_type):
                ucs_ini = {'location': "", 'cimc': "", 'uuid': "", 'adapters': [], 'cpu_type': [],
                           'service_profile_state': ""}
                ucs_serverinfo = copy.deepcopy(ucs_ini)
                if server_type == "ComputeBlade":
                    ucs_serverinfo['location'] = ucs_sys_server.chassis_id + \
                        "/" + ucs_sys_server.slot_id
                else:
                    ucs_serverinfo['location'] = "RackUnit-" + ucs_sys_server.id
                ucs_serverinfo['uuid'] = ucs_sys_server.uuid
                if ucs_sys_server.assigned_to_dn != "":
                    ucs_serverinfo['service_profile_state'] = ucs_sys_server.assigned_to_dn.split(
                        "/")[1][3:] + "(" + ucs_sys_server.association + ")"
                if len(handle.query_children(in_mo=ucs_sys_server)) != 0:
                    mo_server_fw = handle.query_children(
                        in_mo=ucs_sys_server, class_id="FirmwareStatus")
                    mo_server_adaptor = handle.query_children(
                        in_mo=ucs_sys_server, class_id="AdaptorUnit")
                    mo_server_compboard = handle.query_children(
                        in_mo=ucs_sys_server, class_id="ComputeBoard")

                    for ucs_sys_server_child in mo_server_fw:
                        if ucs_sys_server_child.get_class_id() == "FirmwareStatus":
                            ucs_serverinfo['cimc'] = ucs_sys_server_child.cimc_version
                            break
                    for ucs_sys_server_child in mo_server_adaptor:
                        fw_version = None
                        if ucs_sys_server_child.get_class_id() == "AdaptorUnit":
                            fw_version = handle.query_dn(
                                ucs_sys_server.dn +
                                "/mgmt/fw-system")
                            ucs_serverinfo['adapters'].append(
                                ucs_sys_server_child.id +
                                ":" +
                                ucs_sys_server_child.model +
                                "," +
                                ucs_sys_server_child.serial +
                                "," +
                                fw_version.version if fw_version else "")
                    for ucs_sys_server_child in mo_server_compboard:
                        if ucs_sys_server_child.get_class_id() == "ComputeBoard":
                            if len(handle.query_children(in_mo=ucs_sys_server_child)) != 0:
                                server_child = handle.query_children(
                                    in_mo=ucs_sys_server_child, class_id="ProcessorUnit")
                                for ucs_cpu_child in server_child:
                                    if ucs_cpu_child.get_class_id() == "ProcessorUnit":
                                        ucs_serverinfo['cpu_type'].append(
                                            ucs_cpu_child.id + " , " + ucs_cpu_child.model)
                ucs_serverinfo_list.append(copy.deepcopy(ucs_serverinfo))
        if [ucs_dict for ucs_dict in ucs_serverinfo_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_serverinfo_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_serverinfo_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_serverinfo_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_faultinfo(args={}):
    """
    Function to obtain UCS Fault Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Fault Info.

    """
    ucs_faultinfo_list = []
    method = "UCS System Fault Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_faultinfo_list, "failed to get handler for UCS Report Generation"
        for ucs_sys_fault in handle.query_classid(class_id="FaultInst"):
            ucs_ini = {'severity': "", 'created': "", 'type': "", 'description': ""}
            ucs_faultinfo = copy.deepcopy(ucs_ini)
            ucs_faultinfo['severity'] = ucs_sys_fault.orig_severity
            ucs_faultinfo['created'] = ucs_sys_fault.created
            ucs_faultinfo['type'] = ucs_sys_fault.type
            ucs_faultinfo['description'] = ucs_sys_fault.descr
            ucs_faultinfo_list.append(ucs_faultinfo.copy())
        if [ucs_dict for ucs_dict in ucs_faultinfo_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_faultinfo_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_faultinfo_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_faultinfo_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_syslog(args={}):
    """
    Function to obtain UCS Syslog Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Syslog Info.

    """
    ucs_syslog_list = []
    method = "Syslog"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is not None:
            syslog_dn = handle.query_dn("sys/svc-ext/syslog")
            mo_syslog = handle.query_children(in_mo=syslog_dn)
            if len(mo_syslog) != 0:
                for ucs_sys_fault_child in mo_syslog:
                    ucs_ini = {'relative_name': "", 'admin_state': "", 'name': "", 'severity': ""}
                    ucs_syslog = copy.deepcopy(ucs_ini)
                    ucs_syslog['ucs'] = handle.query_dn("sys").name
                    if (ucs_sys_fault_child.get_class_id() == "CommSyslogConsole" or
                        ucs_sys_fault_child.get_class_id() == "CommSyslogMonitor" or
                            ucs_sys_fault_child.get_class_id() == "CommSyslogFile"):
                        if ucs_sys_fault_child.dn != "":
                            ucs_syslog['relative_name'] = ucs_sys_fault_child.dn[19:]
                        ucs_syslog['admin_state'] = ucs_sys_fault_child.admin_state
                        ucs_syslog['name'] = ucs_sys_fault_child.name
                        ucs_syslog['severity'] = ucs_sys_fault_child.severity
                    ucs_syslog_list.append(ucs_syslog.copy())
            if [ucs_dict for ucs_dict in ucs_syslog_list if not ucs_dict == ucs_ini] != []:
                return PTK_OKAY, ucs_syslog_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, ucs_syslog_list, "Unable to get " + method
        else:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_syslog_list, "failed to get handler for UCS Report Generation"

    except UcsException as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_syslog_list, str(ue)
    finally:
        lock.release()

# UCS : Compute Networking


def get_ucsm_cluster(args={}):
    """
    Function to obtain UCS Cluster Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Cluster Info.

    """
    ucs_cluster_list = []
    method = "UCS System Cluster"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_cluster_list, "failed to get handler for UCS Report Generation"
        ucs_ini = {'name': "", 'ip_addr': "", 'ucsm_verison': ""}
        ucs_cluster = copy.deepcopy(ucs_ini)
        mo = handle.query_dn("sys")
        ucs_cluster['name'] = mo.name
        ucs_cluster['ip_addr'] = mo.address
        version_info = handle.query_dn("sys/mgmt/fw-system")
        ucs_cluster['ucsm_verison'] = version_info.version
        ucs_cluster_list.append(ucs_cluster.copy())
        if [ucs_dict.values for ucs_dict in ucs_cluster_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_cluster_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_cluster_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_cluster_list, str(ue)
    finally:
        lock.release()


def get_ucsm_systemclass(args={}):
    """
    Function to obtain UCS System Class Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS System Class Info.

    """
    ucs_sysclass_list = []
    method = "UCS System System Class"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_sysclass_list, "failed to get handler for UCS Report Generation"
        for smclasses in handle.query_classid(class_id="QosclassDefinition"):
            ucs_ini = {'priority': "", 'admin_state': "", 'cos': "", 'weight': "", 'drop': "",
                       'mtu': "", 'bwpct': ""}
            ucs_sysclass = copy.deepcopy(ucs_ini)
            mo_smclasses = handle.query_children(in_mo=smclasses)
            if len(mo_smclasses) != 0:
                for smclasses_child in mo_smclasses:
                    if (smclasses_child.get_class_id() == 'QosclassEthClassified' or
                        smclasses_child.get_class_id() == 'QosclassFc' or
                            smclasses_child.get_class_id() == 'QosclassEthBE'):
                        ucs_sysclass['priority'] = smclasses_child.priority
                        ucs_sysclass['admin_state'] = smclasses_child.admin_state
                        ucs_sysclass['cos'] = smclasses_child.cos
                        ucs_sysclass['weight'] = smclasses_child.weight
                        ucs_sysclass['drop'] = smclasses_child.drop
                        ucs_sysclass['mtu'] = smclasses_child.mtu
                        ucs_sysclass['bwpct'] = smclasses_child.bw_percent
                        ucs_sysclass_list.append(ucs_sysclass.copy())
        if [ucs_dict for ucs_dict in ucs_sysclass_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_sysclass_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_sysclass_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_sysclass_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_qospol(args={}):
    """
    Function to obtain UCS QoS Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS QoS Policy Info.

    """
    ucs_qospol_list = []
    method = "UCS System QoS Policies"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is not None:
            for qos_policies in handle.query_classid(class_id="Epqosdefinition"):
                ucs_ini = {'name': "", 'priority': "", 'burst': "", 'host_control': "", 'rate': ""}
                ucs_qospol = copy.deepcopy(ucs_ini)
                ucs_qospol['name'] = qos_policies.name
                mo_qos = handle.query_children(in_mo=qos_policies)
                if len(mo_qos) != 0:
                    for qospolicies_child in mo_qos:
                        if qospolicies_child.get_class_id() == 'EpqosEgress':
                            ucs_qospol['priority'] = qospolicies_child.prio
                            ucs_qospol['burst'] = qospolicies_child.burst
                            ucs_qospol['host_control'] = qospolicies_child.host_control
                            ucs_qospol['rate'] = qospolicies_child.rate
                ucs_qospol_list.append(ucs_qospol.copy())
            if [ucs_dict for ucs_dict in ucs_qospol_list if not ucs_dict == ucs_ini] != []:
                return PTK_OKAY, ucs_qospol_list, _("PDT_SUCCESS_MSG")
            else:
                loginfo("Unable to get " + method)
                return PTK_NOTEXIST, ucs_qospol_list, "Unable to get " + method
        else:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_qospol_list, "failed to get handler for UCS Report Generation"

    except UcsException as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_qospol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_nwctlpol(args={}):
    """
    Function to obtain UCS Network control Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Network control Policy Info.

    """
    ucs_nwctlpol_list = []
    method = "UCS System Network Control Policy"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_nwctlpol_list, "failed to get handler for UCS Report Generation"
        for ucs_nwctrlpolicies in handle.query_classid(class_id="NwctrlDefinition"):
            ucs_ini = {
                'dn': "",
                'name': "",
                'cdp': "",
                'mac_register': "",
                'uplink_fail_policy': ""}
            ucs_nwctlpol = copy.deepcopy(ucs_ini)
            ucs_nwctlpol['dn'] = ucs_nwctrlpolicies.dn
            ucs_nwctlpol['name'] = ucs_nwctrlpolicies.name
            ucs_nwctlpol['cdp'] = ucs_nwctrlpolicies.cdp
            ucs_nwctlpol['mac_register'] = ucs_nwctrlpolicies.mac_register_mode
            ucs_nwctlpol['uplink_fail_policy'] = ucs_nwctrlpolicies.uplink_fail_action
            ucs_nwctlpol_list.append(ucs_nwctlpol.copy())
        if [ucs_dict for ucs_dict in ucs_nwctlpol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_nwctlpol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_nwctlpol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_nwctlpol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_vlaninfo(args={}):
    """
    Function to obtain UCS VLAN Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS VLAN Info.

    """
    ucs_vlan_list = []
    method = "UCS System VLAN Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_vlan_list, "failed to get handler for UCS Report Generation"
        for ucs_vlans in handle.query_classid(class_id="FabricVlan"):
            ucs_ini = {'vlan_id': "", 'vlan_name': "", 'fabric_member': "", 'vlan_role': ""}
            ucs_vlan = copy.deepcopy(ucs_ini)
            ucs_vlan['vlan_id'] = ucs_vlans.id
            ucs_vlan['vlan_name'] = ucs_vlans.name
            ucs_vlan['fabric_member'] = ucs_vlans.switch_id
            ucs_vlan['vlan_role'] = ucs_vlans.if_role
            ucs_vlan_list.append(ucs_vlan.copy())
        if [ucs_dict for ucs_dict in ucs_vlan_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_vlan_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_vlan_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_vlan_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_vsaninfo(args={}):
    """
    Function to obtain UCS VSAN Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS VSAN Info.

    """
    ucs_vsan_list = []
    method = "UCS System VSAN Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_vsan_list, "failed to get handler for UCS Report Generation"
        for ucs_vsans in handle.query_classid(class_id="FabricVsan"):
            ucs_ini = {'vsan_id': "", 'vsan_name': "", 'fabric_member': "", 'vlan_role': ""}
            ucs_vsan = copy.deepcopy(ucs_ini)
            if args['san_type'] == "FC":
                ucs_ini['fcoe_vlan'] = ""
                ucs_vsan['fcoe_vlan'] = ""
            ucs_vsan['vsan_id'] = ucs_vsans.id
            ucs_vsan['vsan_name'] = ucs_vsans.name
            ucs_vsan['fabric_member'] = ucs_vsans.switch_id
            ucs_vsan['vlan_role'] = ucs_vsans.if_role
            if args['san_type'] == "FC":
                ucs_vsan['fcoe_vlan'] = ucs_vsans.fcoe_vlan
            ucs_vsan_list.append(ucs_vsan.copy())
        if [ucs_dict for ucs_dict in ucs_vsan_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_vsan_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_vsan_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_vsan_list, str(ue)
    finally:
        lock.release()


def get_fi_portchlinfo(args={}):
    """
    Function to obtain UCS Fabric Interconnect PortChannel Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS FI PortChannel Info.

    """
    fi_portchl_list = []
    method = "Fabric Interconnect PortChannel Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_portchl_list, "failed to get handler for UCS Report Generation"
        for fi_ethportchls in handle.query_classid(class_id="FabricEthLanPc"):
            ucs_ini = {'name': "", 'state': "", 'speed': "", 'role': "", 'type': "", 'port_id': "",
                       'switch_id': "", 'transport': "", 'description': ""}
            fi_portchl = copy.deepcopy(ucs_ini)
            fi_portchl['name'] = fi_ethportchls.name
            fi_portchl['state'] = fi_ethportchls.oper_state
            fi_portchl['speed'] = fi_ethportchls.oper_speed
            fi_portchl['role'] = fi_ethportchls.if_role
            fi_portchl['type'] = fi_ethportchls.if_type
            fi_portchl['port_id'] = fi_ethportchls.port_id
            fi_portchl['switch_id'] = fi_ethportchls.switch_id
            fi_portchl['transport'] = fi_ethportchls.transport
            fi_portchl['description'] = fi_ethportchls.descr
            fi_portchl_list.append(fi_portchl.copy())
            if args['san_type'] != "FC":
                continue
            for fi_sanportchls in handle.query_classid(class_id="FabricFcSanPc"):
                fi_portchl['name'] = fi_sanportchls.name
                fi_portchl['state'] = fi_sanportchls.oper_state
                fi_portchl['speed'] = fi_ethportchls.oper_speed
                fi_portchl['role'] = fi_sanportchls.if_role
                fi_portchl['type'] = fi_sanportchls.if_type
                fi_portchl['port_id'] = fi_sanportchls.port_id
                fi_portchl['switch_id'] = fi_sanportchls.switch_id
                fi_portchl['transport'] = fi_sanportchls.transport
                fi_portchl['description'] = fi_sanportchls.descr
                fi_portchl_list.append(fi_portchl.copy())
            for fi_fcoeportchls in handle.query_classid(class_id="FabricFcoeSanPc"):
                fi_portchl['name'] = fi_fcoeportchls.name
                fi_portchl['state'] = fi_fcoeportchls.oper_state
                fi_portchl['speed'] = fi_fcoeportchls.speed
                fi_portchl['role'] = fi_fcoeportchls.if_role
                fi_portchl['type'] = fi_fcoeportchls.if_type
                fi_portchl['port_id'] = fi_fcoeportchls.port_id
                fi_portchl['switch_id'] = fi_fcoeportchls.switch_id
                fi_portchl['transport'] = fi_fcoeportchls.transport
                fi_portchl['description'] = fi_fcoeportchls.descr
                fi_portchl_list.append(fi_portchl.copy())
        if [ucs_dict for ucs_dict in fi_portchl_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_portchl_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_portchl_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_portchl_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_ethinterconnectinfo(args={}):
    """
    Function to obtain UCS Eth Interconnect Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Eth Interconnect Info.

    """
    fi_etherintercon_list = []
    method = "UCS System Eth Interconnect Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_etherintercon_list, "failed to get handler for UCS Report Generation"
        for ethernet_ports in handle.query_classid(class_id="EtherPIo"):
            ucs_ini = {
                'port': "",
                'mac': "",
                'type': "",
                'lic_state': "",
                'mode': "",
                'state': "",
                'speed': "",
                'connected_device': "",
                'connected_port': ""}
            fi_etherintercon = copy.deepcopy(ucs_ini)
            fi_etherintercon['port'] = "FI-" + ethernet_ports.switch_id + \
                " " + ethernet_ports.slot_id + "/" + ethernet_ports.port_id
            fi_etherintercon['mac'] = ethernet_ports.mac
            fi_etherintercon['type'] = ethernet_ports.if_role
            fi_etherintercon['lic_state'] = ethernet_ports.lic_state
            fi_etherintercon['mode'] = ethernet_ports.mode
            fi_etherintercon['state'] = ethernet_ports.oper_state
            fi_etherintercon['speed'] = ethernet_ports.oper_speed
            if ethernet_ports.if_role == "server":
                if ethernet_ports.peer_dn != "":
                    fi_etherintercon['connected_device'] = ethernet_ports.peer_dn.split(
                        "/")[1]
                    if fi_etherintercon['connected_device'].find("chassis") != -1:
                        fi_etherintercon['connected_port'] = "IOM " + \
                            ethernet_ports.peer_slot_id + "/" + ethernet_ports.peer_port_id
                    elif fi_etherintercon['connected_device'].find("rack") != -1:
                        if (("-" in ethernet_ports.peer_dn.split("/")[1]) and
                                ("-" in ethernet_ports.peer_dn.split("/")[2])):
                            fi_etherintercon['connected_port'] = "Rack " + ethernet_ports.peer_dn.split(
                                "/")[1].split("-")[2] + ethernet_ports.peer_dn.split("/")[2].split("-")[1]
            elif ethernet_ports.if_role == "network":
                if ethernet_ports.ep_dn != "":
                    fi_etherintercon['connected_device'] = ethernet_ports.ep_dn.split(
                        "/")[3]
                    fi_etherintercon['connected_port'] = "UCSM Uplink"
            elif ethernet_ports.if_role == "storage":
                if ethernet_ports.ep_dn != "":
                    fi_etherintercon['connected_device'] = ethernet_ports.ep_dn.split(
                        "/")[3]
                    fi_etherintercon['connected_port'] = "UCSM Appliance"
            fi_etherintercon_list.append(fi_etherintercon.copy())
        if [ucs_dict for ucs_dict in fi_etherintercon_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_etherintercon_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_etherintercon_list, "Unable to get " + method

    except UcsException as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_etherintercon_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_fcinterconnectinfo(args={}):
    """
    Function to obtain UCS FC Interconnect Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS FC Interconnect Info.

    """
    fi_fcintercon_list = []
    method = "UCS System FC Interconnect Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_fcintercon_list, "failed to get handler for UCS Report Generation"
        for fc_ports in handle.query_classid(class_id="FcPIo"):
            ucs_ini = {
                'port': "",
                'wwn': "",
                'type': "",
                'lic_state': "",
                'mode': "",
                'state': "",
                'speed': "",
                'connected_device': "",
                'connected_port': ""}
            fi_fcintercon = copy.deepcopy(ucs_ini)
            fi_fcintercon['port'] = "FI-" + fc_ports.switch_id + \
                " " + fc_ports.slot_id + "/" + fc_ports.port_id
            fi_fcintercon['wwn'] = fc_ports.wwn
            fi_fcintercon['type'] = fc_ports.if_role
            fi_fcintercon['lic_state'] = fc_ports.lic_state
            fi_fcintercon['mode'] = fc_ports.mode
            fi_fcintercon['state'] = fc_ports.oper_state
            fi_fcintercon['speed'] = fc_ports.oper_speed
            if fc_ports.ep_dn != "":
                if fc_ports.if_role == "network":
                    fi_fcintercon['connected_device'] = fc_ports.ep_dn.split(
                        "/")[3]
                    fi_fcintercon['connected_port'] = "UCSM Uplink"
                elif fc_ports.if_role == "storage":
                    fi_fcintercon['connected_device'] = fc_ports.ep_dn.split(
                        "/")[3]
                    fi_fcintercon['connected_port'] = "UCSM Unified Storage"
            fi_fcintercon_list.append(fi_fcintercon.copy())
        if [ucs_dict for ucs_dict in fi_fcintercon_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_fcintercon_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_fcintercon_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_fcintercon_list, str(ue)
    finally:
        lock.release()

# UCS : Compute Policy-temp


def get_ucs_system_uuid_pool(args={}):
    """
    Function to obtain UCS UUID Pool Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS UUID Pool Info.

    """
    fi_uuidpool_list = []
    method = "UCS System UUID Pool Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_uuidpool_list, "failed to get handler for UCS Report Generation"
        for fi_uuids in handle.query_classid(class_id="UuidpoolPool"):
            ucs_ini = {'name': "", 'assignment_order': "", 'size': "", 'used': "", 'prefix': "",
                       'from': "", 'to': ""}
            fi_uuidpool = copy.deepcopy(ucs_ini)
            fi_uuidpool['name'] = fi_uuids.name
            fi_uuidpool['assignment_order'] = fi_uuids.assignment_order
            fi_uuidpool['size'] = fi_uuids.size
            fi_uuidpool['used'] = fi_uuids.assigned
            fi_uuidpool['prefix'] = fi_uuids.prefix
            mo_uid = handle.query_children(in_mo=fi_uuids)
            if len(mo_uid) != 0:
                for uuids_child in mo_uid:
                    if uuids_child.get_class_id() == "UuidpoolBlock":
                        fi_uuidpool['from'] = uuids_child.r_from
                        fi_uuidpool['to'] = uuids_child.to
                        break
            fi_uuidpool_list.append(fi_uuidpool.copy())
        if [ucs_dict for ucs_dict in fi_uuidpool_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_uuidpool_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_uuidpool_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_fcintercon_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_wwn_pool(args={}):
    """
    Function to obtain UCS WWN Pool Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS WWN Pool Info.

    """
    fi_wwnpool_list = []
    method = "UCS System WWN Pool Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_wwnpool_list, "failed to get handler for UCS Report Generation"
        for fi_wwns in handle.query_classid(class_id="FcpoolInitiators"):
            ucs_ini = {'name': "", 'assignment_order': "", 'size': "", 'used': "", 'prefix': "",
                       'from': "", 'to': ""}
            fi_wwnpool = copy.deepcopy(ucs_ini)
            fi_wwnpool['name'] = fi_wwns.name
            fi_wwnpool['assignment_order'] = fi_wwns.assignment_order
            fi_wwnpool['size'] = fi_wwns.size
            fi_wwnpool['used'] = fi_wwns.assigned
            fi_wwnpool['prefix'] = fi_wwns.purpose
            mo_wwn = handle.query_children(in_mo=fi_wwns)
            if len(mo_wwn) != 0:
                for wwns_child in mo_wwn:
                    if wwns_child.get_class_id() == "FcpoolBlock":
                        fi_wwnpool['from'] = wwns_child.r_from
                        fi_wwnpool['to'] = wwns_child.to
                        break
            fi_wwnpool_list.append(fi_wwnpool.copy())
        if [ucs_dict for ucs_dict in fi_wwnpool_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_wwnpool_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_wwnpool_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_wwnpool_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_iqn_pool(args={}):
    """
    Function to obtain UCS IQN Pool Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS IQN Pool Info.

    """
    fi_iqnpool_list = []
    method = "UCS System IQN Pool Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_iqnpool_list, "failed to get handler for UCS Report Generation"
        for fi_iqns in handle.query_classid(class_id="IqnpoolPool"):
            ucs_ini = {
                'name': "",
                'assignment_order': "",
                'size': "",
                'used': "",
                'prefix': "",
                'suffix': "",
                'from': "",
                'to': ""}
            fi_iqnpool = copy.deepcopy(ucs_ini)
            fi_iqnpool['name'] = fi_iqns.name
            fi_iqnpool['assignment_order'] = fi_iqns.assignment_order
            fi_iqnpool['size'] = fi_iqns.size
            fi_iqnpool['used'] = fi_iqns.assigned
            fi_iqnpool['prefix'] = fi_iqns.prefix
            mo_iqn = handle.query_children(in_mo=fi_iqns)
            if len(mo_iqn) != 0:
                for iqns_child in mo_iqn:
                    if iqns_child.get_class_id() == "IqnpoolBlock":
                        fi_iqnpool['suffix'] = iqns_child.suffix
                        fi_iqnpool['from'] = iqns_child.r_from
                        fi_iqnpool['to'] = iqns_child.to
                        break
            fi_iqnpool_list.append(fi_iqnpool.copy())
        if [ucs_dict for ucs_dict in fi_iqnpool_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_iqnpool_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_iqnpool_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_iqnpool_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_mac_pool(args={}):
    """
    Function to obtain UCS MAC Pool Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS MAC Pool Info.

    """
    fi_macpool_list = []
    method = "UCS System MAC Pool Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_macpool_list, "failed to get handler for UCS Report Generation"
        for fi_macs in handle.query_classid(class_id="MacpoolPool"):
            ucs_ini = {'name': "", 'assignment_order': "", 'size': "", 'used': "",
                       'from': "", 'to': ""}
            fi_macpool = copy.deepcopy(ucs_ini)
            fi_macpool['name'] = fi_macs.name
            fi_macpool['assignment_order'] = fi_macs.assignment_order
            fi_macpool['size'] = fi_macs.size
            fi_macpool['used'] = fi_macs.assigned
            mo_mac = handle.query_children(in_mo=fi_macs)
            if len(mo_mac) != 0:
                for macs_child in mo_mac:
                    if macs_child.get_class_id() == "MacpoolBlock":
                        fi_macpool['from'] = macs_child.r_from
                        fi_macpool['to'] = macs_child.to
                        break
            fi_macpool_list.append(fi_macpool.copy())
        if [ucs_dict for ucs_dict in fi_macpool_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_macpool_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_macpool_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_macpool_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_ip_pool(args={}):
    """
    Function to obtain UCS IP Pool Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS IP Pool Info.

    """
    fi_ippool_list = []
    method = "UCS System IP Pool Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_ippool_list, "failed to get handler for UCS Report Generation"
        for fi_ippools in handle.query_classid(class_id="IppoolPool"):
            ucs_ini = {
                'name': "",
                'assignment_order': "",
                'size': "",
                'used': "",
                'dns': [],
                'from': "",
                'to': "",
                'subnet': "",
                'gateway': ""}
            fi_ippool = copy.deepcopy(ucs_ini)
            fi_ippool['name'] = fi_ippools.name
            fi_ippool['assignment_order'] = fi_ippools.assignment_order
            fi_ippool['size'] = fi_ippools.size
            fi_ippool['used'] = fi_ippools.assigned
            mo_ippool = handle.query_children(in_mo=fi_ippools)
            if len(mo_ippool) != 0:
                for ippools_child in mo_ippool:
                    if ippools_child.get_class_id() == "IppoolBlock":
                        fi_ippool['from'] = ippools_child.r_from
                        fi_ippool['to'] = ippools_child.to
                        fi_ippool['subnet'] = ippools_child.subnet
                        fi_ippool['gateway'] = ippools_child.def_gw
                        fi_ippool['dns'].append(ippools_child.prim_dns)
                        fi_ippool['dns'].append(ippools_child.sec_dns)
                        break
            fi_ippool_list.append(copy.deepcopy(fi_ippool))
        if [ucs_dict for ucs_dict in fi_ippool_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_ippool_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_ippool_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_ippool_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_fault_policy(args={}):
    """
    Function to obtain UCS Fault Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Fault Policy Info.

    """
    fi_fault_pol_list = []
    method = "UCS System Fault Policy Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_fault_pol_list, "failed to get handler for UCS Report Generation"
        for fi_faultpol in handle.query_classid(class_id="FaultPolicy"):
            ucs_ini = {
                'rn': "",
                'ack_action': "",
                'clear_action': "",
                'clear_interval': "",
                'flap_interval': "",
                'retn_interval': ""}
            fi_fault_pol = copy.deepcopy(ucs_ini)
            fi_fault_pol['rn'] = fi_faultpol.rn
            fi_fault_pol['ack_action'] = fi_faultpol.ack_action
            fi_fault_pol['clear_action'] = fi_faultpol.clear_action
            fi_fault_pol['clear_interval'] = fi_faultpol.clear_interval
            fi_fault_pol['flap_interval'] = fi_faultpol.flap_interval
            fi_fault_pol['retn_interval'] = fi_faultpol.retention_interval
            fi_fault_pol_list.append(fi_fault_pol.copy())
        if [ucs_dict for ucs_dict in fi_fault_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_fault_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_fault_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_fault_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_backup_policy(args={}):
    """
    Function to obtain UCS Backup Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Backup Policy Info.

    """
    fi_bkup_pol_list = []
    method = "UCS System Backup Policy Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_bkup_pol_list, "failed to get handler for UCS Report Generation"
        for fi_bkuppol in handle.query_classid(class_id="MgmtBackupPolicy"):
            ucs_ini = {
                'descr': "",
                'host': "",
                'last_backup': "",
                'proto': "",
                'schedule': "",
                'admin_state': ""}
            fi_bkup_pol = copy.deepcopy(ucs_ini)
            fi_bkup_pol['descr'] = fi_bkuppol.descr
            fi_bkup_pol['host'] = fi_bkuppol.host
            fi_bkup_pol['last_backup'] = fi_bkuppol.last_backup
            fi_bkup_pol['proto'] = fi_bkuppol.proto
            fi_bkup_pol['schedule'] = fi_bkuppol.schedule
            fi_bkup_pol['admin_state'] = fi_bkuppol.admin_state
            fi_bkup_pol_list.append(fi_bkup_pol.copy())
        if [ucs_dict for ucs_dict in fi_bkup_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_bkup_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_bkup_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_bkup_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_ipmi_access_profiles(args={}):
    """
    Function to obtain UCS IPMI Access Profiles.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS IPMI Access Profiles.

    """
    fi_ipmi_access_pol_list = []
    method = "UCS System IPMI Access Profiles"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_ipmi_access_pol_list, "failed to get handler for UCS Report Generation"
        for fi_ipmi in handle.query_classid(class_id="AaaEpAuthProfile"):
            ucs_ini = {'ipmi_profile': "", 'users': "", 'role': ""}
            fi_ipmi_access_pol = copy.deepcopy(ucs_ini)
            fi_ipmi_access_pol['ipmi_profile'] = fi_ipmi.name
            mo_ipmi = handle.query_children(in_mo=fi_ipmi)
            if len(mo_ipmi) != 0:
                for ipmi_child in mo_ipmi:
                    fi_ipmi_access_pol['users'] = ipmi_child.name
                    fi_ipmi_access_pol['role'] = ipmi_child.priv
                    break
            fi_ipmi_access_pol_list.append(fi_ipmi_access_pol.copy())
        if [ucs_dict for ucs_dict in fi_ipmi_access_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_ipmi_access_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_ipmi_access_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_ipmi_access_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_local_disk_policy(args={}):
    """
    Function to obtain UCS Local Disk Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Local Disk Policy Info.

    """
    fi_localdisk_pol_list = []
    method = "UCS System Local Disk Policy"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_localdisk_pol_list, "failed to get handler for UCS Report Generation"
        for fi_ldpol in handle.query_classid(class_id="StorageLocalDiskConfigPolicy"):
            ucs_ini = {'name': "", 'mode': "", 'protect_cfg': ""}
            fi_localdisk_pol = copy.deepcopy(ucs_ini)
            fi_localdisk_pol['name'] = fi_ldpol.name
            fi_localdisk_pol['mode'] = fi_ldpol.mode
            fi_localdisk_pol['protect_cfg'] = fi_ldpol.protect_config
            fi_localdisk_pol_list.append(fi_localdisk_pol.copy())
        if [ucs_dict for ucs_dict in fi_localdisk_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_localdisk_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_localdisk_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_localdisk_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_bios_policy(args={}):
    """
    Function to obtain UCS BIOS Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS BIOS Policy Info.

    """
    fi_bios_pol_list = []
    method = "UCS System BIOS Policy"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_bios_pol_list, "failed to get handler for UCS Report Generation"
        for fi_biospol in handle.query_classid(class_id="BiosVProfile"):
            ucs_ini = {'name': "", 'reboot_on_update': "", 'quiet_boot': "", 'cie_setting': ""}
            fi_bios_pol = copy.deepcopy(ucs_ini)
            fi_bios_pol['name'] = fi_biospol.name
            fi_bios_pol['reboot_on_update'] = fi_biospol.reboot_on_update
            mo_bios = handle.query_children(in_mo=fi_biospol)
            if len(mo_bios) != 0:
                for bios_child in mo_bios:
                    if bios_child.get_class_id() == "BiosVfQuietBoot":
                        fi_bios_pol['quiet_boot'] = bios_child.vp_quiet_boot
                    if bios_child.get_class_id() == "BiosVfPCILOMPortsConfiguration":
                        fi_bios_pol['cie_setting'] = bios_child.vp_pc_ie10_glo_m2_link
            fi_bios_pol_list.append(fi_bios_pol.copy())
        if [ucs_dict for ucs_dict in fi_bios_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_bios_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_bios_pol_list, "Unable to get " + method

    except UcsException as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_bios_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_maint_policy(args={}):
    """
    Function to obtain UCS Maintanence Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Maintanence Policy Info.

    """
    fi_maint_pol_list = []
    method = "UCS System Maintanence Policy"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_maint_pol_list, "failed to get handler for UCS Report Generation"
        for fi_maintpol in handle.query_classid(class_id="LsmaintMaintPolicy"):
            ucs_ini = {'name': "", 'reboot_pol': ""}
            fi_maint_pol = copy.deepcopy(ucs_ini)
            fi_maint_pol['name'] = fi_maintpol.name
            fi_maint_pol['reboot_pol'] = fi_maintpol.uptime_disr
            fi_maint_pol_list.append(fi_maint_pol.copy())
        if [ucs_dict for ucs_dict in fi_maint_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_maint_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_maint_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_maint_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_boot_policy(args={}):
    """
    Function to obtain UCS Boot Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Boot Policy Info.

    """
    fi_boot_pol_list = []
    method = "UCS System Boot Policy"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_boot_pol_list, "failed to get handler for UCS Report Generation"
        for fi_bootpol in handle.query_classid(class_id="LsbootPolicy"):
            ucs_ini = {
                'name': "",
                'enforce_vnic': "",
                'reboot_on_chg': "",
                'virtual_media_order': "",
                'lan_order': ""}
            fi_boot_pol = copy.deepcopy(ucs_ini)
            if args['san_type'] == "FC":
                ucs_ini['san_order'] = ""
                fi_boot_pol['san_order'] = ""
                san_order = ""
            virtual_media = ""
            lan_order = ""
            fi_boot_pol['name'] = fi_bootpol.name
            fi_boot_pol['enforce_vnic'] = fi_bootpol.enforce_vnic_name
            fi_boot_pol['reboot_on_chg'] = fi_bootpol.reboot_on_update
            mo_boot = handle.query_children(in_mo=fi_bootpol)
            if len(mo_boot) != 0:
                for boot_child in mo_boot:
                    mo_boot_child = handle.query_children(in_mo=boot_child)
                    if boot_child.get_class_id() == "LsbootVirtualMedia":
                        virtual_media += boot_child.order + ","
                    if boot_child.get_class_id() == "LsbootLan":
                        lan_order += boot_child.order
                        if len(mo_boot_child) != 0:
                            for lan_child in mo_boot_child:
                                if lan_child.get_class_id() == "LsbootLanImagePath":
                                    lan_order += "," + lan_child.vnic_name
                    if args['san_type'] == "FC":
                        if boot_child.get_class_id() == "LsbootSan":
                            san_order += boot_child.order
                            if len(mo_boot_child) != 0:
                                for san_child in mo_boot_child:
                                    #mo_san = handle.query_children(in_mo=san_child)
                                    if san_child.get_class_id() == "LsbootSanCatSanImage":
                                        san_order += "," + san_child.vnic_name
            fi_boot_pol['virtual_media_order'] = virtual_media[:-1]
            fi_boot_pol['lan_order'] = lan_order
            if args['san_type'] == "FC":
                fi_boot_pol['san_order'] = san_order
            fi_boot_pol_list.append(fi_boot_pol.copy())
        if [ucs_dict for ucs_dict in fi_boot_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_boot_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_boot_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_boot_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_san_boot_config_policy(args={}):
    """
    Function to obtain UCS SAN Boot Configuration Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS SAN Boot Config Policy Info.

    """
    fi_boot_pol_list = []
    method = "UCS System SAN Boot Configuration for Boot Policy"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_boot_pol_list, "failed to get handler for UCS Report Generation"
        for fi_bootpol in handle.query_classid(class_id="LsbootPolicy"):
            ucs_ini = {'name': "", 'san_order': "", 'sanpri_targetpri': "", 'sanpri_targetsec': "",
                       'sansec_targetpri': "", 'sansec_targetsec': ""}
            fi_boot_pol = copy.deepcopy(ucs_ini)
            san_order = ""
            sanpri_targetpri = ""
            sanpri_targetsec = ""
            sansec_targetpri = ""
            sansec_targetsec = ""
            fi_boot_pol['name'] = fi_bootpol.name
            mo_boot = handle.query_children(in_mo=fi_bootpol)
            if len(mo_boot) != 0:
                for boot_child in mo_boot:
                    mo_boot_child = handle.query_children(in_mo=boot_child)
                    if boot_child.get_class_id() == "LsbootSan":
                        san_order += boot_child.order
                        if len(mo_boot_child) != 0:
                            for san_child in mo_boot_child:
                                mo_san = handle.query_children(in_mo=san_child)
                                if san_child.get_class_id() == "LsbootSanCatSanImage":
                                    san_order += "," + san_child.vnic_name
                                    if len(mo_san) != 0:
                                        for san_image_child in mo_san:
                                            if " ".join(san_image_child.dn.split("/")[3:]) == \
                                                    "sanimg-secondary sanimgpath-secondary":
                                                sansec_targetsec += san_image_child.lun + \
                                                    "," + san_image_child.wwn
                                            elif " ".join(san_image_child.dn.split("/")[3:]) == \
                                                    "sanimg-secondary sanimgpath-primary":
                                                sansec_targetpri += san_image_child.lun + \
                                                    "," + san_image_child.wwn
                                            elif " ".join(san_image_child.dn.split("/")[3:]) == \
                                                    "sanimg-primary sanimgpath-secondary":
                                                sanpri_targetsec += san_image_child.lun + \
                                                    "," + san_image_child.wwn
                                            else:
                                                sanpri_targetpri += san_image_child.lun + \
                                                    "," + san_image_child.wwn
            fi_boot_pol['san_order'] = san_order
            fi_boot_pol['sanpri_targetpri'] = sanpri_targetpri
            fi_boot_pol['sanpri_targetsec'] = sanpri_targetsec
            fi_boot_pol['sansec_targetpri'] = sansec_targetpri
            fi_boot_pol['sansec_targetsec'] = sansec_targetsec
            fi_boot_pol_list.append(fi_boot_pol.copy())
        if [ucs_dict for ucs_dict in fi_boot_pol_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_boot_pol_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_boot_pol_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_boot_pol_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_lan_template(args={}):
    """
    Function to obtain UCS LAN Template.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS LAN Template.

    """
    fi_lan_temp_list = []
    method = "UCS System LAN Template"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_lan_temp_list, "failed to get handler for UCS Report Generation"
        for fi_lantemp in handle.query_classid(class_id="VnicLanConnTempl"):
            ucs_ini = {
                'name': "",
                'template_type': "",
                'fabric': "",
                'qos': "",
                'mtu': "",
                'network_control': "",
                'networks_allowed': []}
            fi_lan_temp = copy.deepcopy(ucs_ini)
            vnic_etherif = []
            fi_lan_temp['name'] = fi_lantemp.name
            fi_lan_temp['template_type'] = fi_lantemp.templ_type
            fi_lan_temp['fabric'] = fi_lantemp.switch_id
            fi_lan_temp['qos'] = fi_lantemp.qos_policy_name
            fi_lan_temp['mtu'] = fi_lantemp.mtu
            fi_lan_temp['network_control'] = fi_lantemp.nw_ctrl_policy_name
            mo_lantemp = handle.query_children(in_mo=fi_lantemp)
            if len(mo_lantemp) != 0:
                for lantemp_child in mo_lantemp:
                    if lantemp_child.get_class_id() == "VnicEtherIf":
                        vnic_etherif.append(lantemp_child.dn.split("/")[2].split("if-")[1])
                for vlans in handle.query_classid(class_id="FabricVlan"):
                    for vnic_ether_index in range(len(vnic_etherif)):
                        if (vlans.dn.split("/")[-1].split("net-")
                                [1] == vnic_etherif[vnic_ether_index]):
                            if ((vnic_etherif[vnic_ether_index] == "default") and
                                (vlans.dn.split("/")[1] == "lan") and
                                    (vlans.id not in fi_lan_temp['networks_allowed'])):
                                fi_lan_temp['networks_allowed'].append(vlans.id)
                            elif (vnic_etherif[vnic_ether_index] != "default"):
                                fi_lan_temp['networks_allowed'].append(vlans.id)
            fi_lan_temp_list.append(copy.deepcopy(fi_lan_temp))
        if [ucs_dict for ucs_dict in fi_lan_temp_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_lan_temp_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_lan_temp_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_san_template(args={}):
    """
    Function to obtain UCS SAN Template.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS SAN Template.

    """
    fi_san_temp_list = []
    method = "UCS System SAN Template"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_san_temp_list, "failed to get handler for UCS Report Generation"
        for fi_santemp in handle.query_classid(class_id="VnicSanConnTempl"):
            ucs_ini = {
                'name': "",
                'template_type': "",
                'fabric': "",
                'qos': "",
                'max_data': "",
                'vsan': ""}
            fi_san_temp = copy.deepcopy(ucs_ini)
            fi_san_temp['name'] = fi_santemp.name
            fi_san_temp['template_type'] = fi_santemp.templ_type
            fi_san_temp['fabric'] = fi_santemp.switch_id
            fi_san_temp['qos'] = fi_santemp.qos_policy_name
            fi_san_temp['max_data'] = fi_santemp.max_data_field_size
            mo_santempl = handle.query_children(in_mo=fi_santemp)
            if len(mo_santempl) != 0:
                for santemp_child in mo_santempl:
                    if santemp_child.get_class_id() == "VnicFcIf":
                        fi_san_temp['vsan'] = santemp_child.name
                        break
            fi_san_temp_list.append(fi_san_temp.copy())
        if [ucs_dict for ucs_dict in fi_san_temp_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_san_temp_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_san_temp_list, "Unable to get " + method

    except UcsException as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_san_temp_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_host_fwpkg(args={}):
    """
    Function to obtain UCS Host Firmware Package.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Host Firmware Package.

    """
    fi_host_fw_list = []
    method = "UCS System Host Firmware Package"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_host_fw_list, "failed to get handler for UCS Report Generation"
        for fi_hostfw in handle.query_classid(class_id="FirmwareComputeHostPack"):
            ucs_ini = {
                'name': "",
                'ignore_compat_check': "",
                'hardware': "",
                'type': "",
                'version': ""}
            fi_host_fw = copy.deepcopy(ucs_ini)
            fi_host_fw['name'] = fi_hostfw.name
            fi_host_fw['ignore_compat_check'] = fi_hostfw.ignore_comp_check
            mo_fw = handle.query_children(in_mo=fi_hostfw)
            if len(mo_fw) != 0:
                for fw_child in mo_fw:
                    if fw_child.get_class_id() == "FirmwarePackItem":
                        fi_host_fw['hardware'] = fw_child.hw_model
                        fi_host_fw['type'] = fw_child.type
                        fi_host_fw['version'] = fw_child.version
                        fi_host_fw_list.append(copy.deepcopy(fi_host_fw))
                        fi_host_fw['name'] = ""
                        fi_host_fw['ignore_compat_check'] = ""
        if [ucs_dict for ucs_dict in fi_host_fw_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_host_fw_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_host_fw_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_host_fw_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_pol_information(args={}):
    """
    Function to obtain UCS Server Policies Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server related Policies Information.

    """
    fi_server_info_list = []
    method = "UCS System Rack & Blade Server-related Policies Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_info_list, "failed to get handler for UCS Report Generation"
        for fi_serverinfo in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'name': "",
                'oper_state': "",
                'profile_type': "",
                'location': "",
                'maint_policy_name': "",
                'maintenance_policy': "",
                'bios_profile': "",
                'boot_policy': ""}
            fi_server_info = copy.deepcopy(ucs_ini)
            fi_server_info['name'] = fi_serverinfo.name
            fi_server_info['oper_state'] = fi_serverinfo.oper_state
            fi_server_info['profile_type'] = fi_serverinfo.type
            if fi_serverinfo.pn_dn != "":
                fi_server_info['location'] = fi_serverinfo.pn_dn.split("sys/")[1]
            fi_server_info['maint_policy_name'] = handle.query_dn(
                fi_serverinfo.oper_maint_policy_name).name
            fi_server_info['maintenance_policy'] = handle.query_dn(
                fi_serverinfo.oper_maint_policy_name).uptime_disr
            fi_server_info['bios_profile'] = fi_serverinfo.bios_profile_name
            fi_server_info['boot_policy'] = fi_serverinfo.boot_policy_name
            fi_server_info_list.append(fi_server_info.copy())
        if [ucs_dict for ucs_dict in fi_server_info_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_info_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_info_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_info_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_information(args={}):
    """
    Function to obtain UCS Server Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server Information.

    """
    fi_server_info_list = []
    method = "UCS System Rack & Blade Server Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_info_list, "failed to get handler for UCS Report Generation"
        for fi_serverinfo in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'name': "",
                'location': "",
                'local_disk_policy': "",
                'host_fw_pkg': "",
                'kvm_ip_pool': "",
                'uuid_pool': "",
                'uuid': "",
                'source_template': ""}
            fi_server_info = copy.deepcopy(ucs_ini)
            fi_server_info['name'] = fi_serverinfo.name
            if fi_serverinfo.pn_dn != "":
                fi_server_info['location'] = fi_serverinfo.pn_dn.split("sys/")[1]
            fi_server_info['local_disk_policy'] = fi_serverinfo.local_disk_policy_name
            fi_server_info['host_fw_pkg'] = handle.query_dn(
                fi_serverinfo.oper_host_fw_policy_name).name
            fi_server_info['kvm_ip_pool'] = handle.query_dn(
                fi_serverinfo.oper_kvm_mgmt_policy_name).name
            fi_server_info['uuid_pool'] = fi_serverinfo.ident_pool_name
            fi_server_info['uuid'] = fi_serverinfo.uuid
            fi_server_info['source_template'] = fi_serverinfo.src_templ_name
            fi_server_info_list.append(fi_server_info.copy())
        if [ucs_dict for ucs_dict in fi_server_info_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_info_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_info_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_info_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_interface_information(args={}):
    """
    Function to obtain UCS Server Interface Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server Interface Information.

    """
    fi_server_interface_list = []
    method = "UCS System Rack & Blade Server Interfaces Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_interface_list, "failed to get handler for UCS Report Generation"
        for fi_serverinterf in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'name': "",
                'location': "",
                'veth_interf_name': [],
                'vnic_fabric': [],
                'vnic_templ_name': [],
                'mac': [],
                'mtu': [],
                'vnic_adaptor_profile': []}
            fi_server_interface = copy.deepcopy(ucs_ini)
            mo_serverinterf = handle.query_children(in_mo=fi_serverinterf, class_id="VnicEther")
            fi_server_interface['name'] = fi_serverinterf.name
            if fi_serverinterf.pn_dn != "":
                fi_server_interface['location'] = fi_serverinterf.pn_dn.split("sys/")[1]
            if len(mo_serverinterf) != 0:
                for serverinterf_child in mo_serverinterf:
                    if serverinterf_child.get_class_id() == "VnicEther":
                        fi_server_interface['veth_interf_name'].append(serverinterf_child.name)
                        fi_server_interface['vnic_fabric'].append(serverinterf_child.switch_id)
                        fi_server_interface['vnic_templ_name'].append(
                            serverinterf_child.nw_templ_name)
                        fi_server_interface['mac'].append(serverinterf_child.addr)
                        fi_server_interface['mtu'].append(serverinterf_child.mtu)
                        fi_server_interface['vnic_adaptor_profile'].append(
                            serverinterf_child.adaptor_profile_name)
            fi_server_interface_list.append(copy.deepcopy(fi_server_interface))
        if [ucs_dict for ucs_dict in fi_server_interface_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_interface_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_interface_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_interface_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_eth_adaptor_pol_information(args={}):
    """
    Function to obtain UCS Server Eth Adaptor Policy Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server Eth Adaptor Policy Information.

    """
    fi_server_interface_list = []
    method = "UCS System Rack & Blade Server Ethernet Adapter Policy Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_interface_list, "failed to get handler for UCS Report Generation"
        for fi_serverinterf in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'name': "",
                'location': "",
                'vnic_qos_pol': [],
                'virtual_ext_lan': [],
                'tcp_large_receive': [],
                'interrupt_timer': [],
                'nw_ctl_pol': [],
                'vnic_ident_pool': [],
                'vnic_order': []}
            fi_server_interface = copy.deepcopy(ucs_ini)
            mo_serverinterf = handle.query_children(in_mo=fi_serverinterf, class_id="VnicEther")
            fi_server_interface['name'] = fi_serverinterf.name
            if fi_serverinterf.pn_dn != "":
                fi_server_interface['location'] = fi_serverinterf.pn_dn.split("sys/")[1]
            if len(mo_serverinterf) != 0:
                for serverinterf_child in mo_serverinterf:
                    if serverinterf_child.get_class_id() == "VnicEther":
                        fi_server_interface['vnic_qos_pol'].append(
                            serverinterf_child.qos_policy_name)
                        fi_server_interface['nw_ctl_pol'].append(
                            serverinterf_child.nw_ctrl_policy_name)
                        fi_server_interface['vnic_ident_pool'].append(
                            serverinterf_child.ident_pool_name)
                        fi_server_interface['vnic_order'].append(serverinterf_child.order)
                        adaptor_dn = handle.query_dn(serverinterf_child.oper_adaptor_profile_name)
                        mo_adaptor_ether = handle.query_children(in_mo=adaptor_dn)
                        if len(mo_adaptor_ether) != 0:
                            for adaptor_child in mo_adaptor_ether:
                                if adaptor_child.get_class_id() == "AdaptorEthVxLANProfile":
                                    fi_server_interface['virtual_ext_lan'].append(
                                        adaptor_child.admin_state)
                                if adaptor_child.get_class_id() == "AdaptorEthOffloadProfile":
                                    fi_server_interface['tcp_large_receive'].append(
                                        adaptor_child.large_receive)
                                if adaptor_child.get_class_id() == "AdaptorEthInterruptProfile":
                                    fi_server_interface['interrupt_timer'].append(
                                        adaptor_child.coalescing_time)
            fi_server_interface_list.append(copy.deepcopy(fi_server_interface))
        if [ucs_dict for ucs_dict in fi_server_interface_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_interface_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_interface_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_interface_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_fc_interface_information(args={}):
    """
    Function to obtain UCS Server Interface Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server FC Interface Information.

    """
    fi_server_interface_list = []
    method = "UCS System Rack & Blade Server FC Interfaces Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_interface_list, "failed to get handler for UCS Report Generation"
        for fi_serverinterf in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'name': "",
                'location': "",
                'vlans': [],
                'vhba_interfaces': [],
                'vhba_fabric': [],
                'vhba_templ_name': [],
                'wwpn': [],
                'max_data': []}
            fi_server_interface = copy.deepcopy(ucs_ini)
            mo_serverinterf = handle.query_children(in_mo=fi_serverinterf)
            fi_server_interface['name'] = fi_serverinterf.name
            if fi_serverinterf.pn_dn != "":
                fi_server_interface['location'] = fi_serverinterf.pn_dn.split("sys/")[1]
            if len(mo_serverinterf) != 0:
                for serverinterf_child in mo_serverinterf:
                    if serverinterf_child.get_class_id() == "VnicEther":
                        mo_vlan = handle.query_children(in_mo=serverinterf_child)
                        if len(mo_vlan) != 0:
                            for vlan_child in mo_vlan:
                                if vlan_child.get_class_id() == "VnicEtherIf":
                                    fi_server_interface['vlans'].append(vlan_child.vnet)
                    if serverinterf_child.get_class_id() == "VnicFc":
                        fi_server_interface['vhba_interfaces'].append(serverinterf_child.name)
                        fi_server_interface['vhba_fabric'].append(serverinterf_child.switch_id)
                        fi_server_interface['vhba_templ_name'].append(
                            serverinterf_child.nw_templ_name)
                        fi_server_interface['wwpn'].append(serverinterf_child.addr)
                        fi_server_interface['max_data'].append(
                            serverinterf_child.max_data_field_size)
            fi_server_interface_list.append(copy.deepcopy(fi_server_interface))
        if [ucs_dict for ucs_dict in fi_server_interface_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_interface_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_interface_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_interface_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_fc_interface_config(args={}):
    """
    Function to obtain UCS Server Interface Configuration.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server FC Interface Configuration.

    """
    fi_server_interface_list = []
    method = "UCS System Rack & Blade Server FC Interfaces Configuration"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_interface_list, "failed to get handler for UCS Report Generation"
        for fi_serverinterf in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'name': "",
                'location': "",
                'vhba_adaptor_profile': [],
                'vhba_qos_pol': [],
                'vhba_ident_pool': [],
                'vhba_order': [],
                'io_throttle_cnt': [],
                'luns_per_target': []}
            fi_server_interface = copy.deepcopy(ucs_ini)
            mo_serverinterf = handle.query_children(in_mo=fi_serverinterf)
            fi_server_interface['name'] = fi_serverinterf.name
            if fi_serverinterf.pn_dn != "":
                fi_server_interface['location'] = fi_serverinterf.pn_dn.split("sys/")[1]
            if len(mo_serverinterf) != 0:
                for serverinterf_child in mo_serverinterf:
                    if serverinterf_child.get_class_id() == "VnicFc":
                        fi_server_interface['vhba_adaptor_profile'].append(
                            serverinterf_child.adaptor_profile_name)
                        fi_server_interface['vhba_qos_pol'].append(
                            serverinterf_child.qos_policy_name)
                        fi_server_interface['vhba_ident_pool'].append(
                            serverinterf_child.ident_pool_name)
                        fi_server_interface['vhba_order'].append(serverinterf_child.order)
                        adaptor_fc_dn = handle.query_dn(
                            serverinterf_child.oper_adaptor_profile_name)
                        mo_adaptor_fc = handle.query_children(in_mo=adaptor_fc_dn)
                        if len(mo_adaptor_fc) != 0:
                            for adaptor_fc_child in mo_adaptor_fc:
                                if adaptor_fc_child.get_class_id() == "AdaptorFcPortProfile":
                                    fi_server_interface['io_throttle_cnt'].append(
                                        adaptor_fc_child.io_throttle_count)
                                    fi_server_interface['luns_per_target'].append(
                                        adaptor_fc_child.luns_per_target)
            fi_server_interface_list.append(copy.deepcopy(fi_server_interface))
        if [ucs_dict for ucs_dict in fi_server_interface_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_interface_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_interface_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_interface_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_server_iscsi_interface_information(args={}):
    """
    Function to obtain UCS Server Interface Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS Server Interface Information.

    """
    fi_server_interface_list = []
    method = "UCS System Rack & Blade Server iSCSI Interfaces Information"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_server_interface_list, "failed to get handler for UCS Report Generation"
        for fi_serverinterf in handle.query_classid(class_id="LsServer"):
            ucs_ini = {'name': "", 'location': "", 'vlans': [], 'iqn': "", 'iqn_ident_pool': "",
                       'iscsi_interfaces': [], 'iscsi_fabric': [], 'iscsi_templ_name': [],
                       'iscsi_adaptor_profile': [], 'iscsi_order': []}
            fi_server_interface = copy.deepcopy(ucs_ini)
            mo_serverinterf = handle.query_children(in_mo=fi_serverinterf)
            fi_server_interface['name'] = fi_serverinterf.name
            if fi_serverinterf.pn_dn != "":
                fi_server_interface['location'] = fi_serverinterf.pn_dn.split("sys/")[1]
            if len(mo_serverinterf) != 0:
                for serverinterf_child in mo_serverinterf:
                    if serverinterf_child.get_class_id() == "VnicEther":
                        mo_vlan = handle.query_children(in_mo=serverinterf_child)
                        if len(mo_vlan) != 0:
                            for vlan_child in mo_vlan:
                                if vlan_child.get_class_id() == "VnicEtherIf":
                                    fi_server_interface['vlans'].append(vlan_child.vnet)
                    if serverinterf_child.get_class_id() == "VnicIScsiNode":
                        fi_server_interface['iqn'] = serverinterf_child.initiator_name
                        fi_server_interface['iqn_ident_pool'] = serverinterf_child.iqn_ident_pool_name
                    if serverinterf_child.get_class_id() == "VnicIScsi":
                        fi_server_interface['iscsi_interfaces'].append(serverinterf_child.name)
                        fi_server_interface['iscsi_fabric'].append(serverinterf_child.switch_id)
                        fi_server_interface['iscsi_templ_name'].append(
                            serverinterf_child.nw_templ_name)
                        fi_server_interface['iscsi_adaptor_profile'].append(
                            serverinterf_child.adaptor_profile_name)
                        fi_server_interface['iscsi_order'].append(serverinterf_child.order)
            fi_server_interface_list.append(copy.deepcopy(fi_server_interface))
        if [ucs_dict for ucs_dict in fi_server_interface_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, fi_server_interface_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_server_interface_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_server_interface_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_iscsi_bootparams_primary(args={}):
    """
    Function to obtain UCS iSCSI Boot Params Primary Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS iSCSI Boot Params Primary Information.

    """
    fi_iscsi_boot_params_list = []
    method = "UCS System iSCSI Boot Parameters Primary"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_iscsi_boot_params_list, "failed to get handler for UCS Report Generation"
        for fi_service_profiles in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'service_profile': "",
                'iscsi_primary': "",
                'iscsi_primary_initiator_address': "",
                'iscsi_primary_initiator_subnet': "",
                'iscsi_primary_initiator_def_gw': "",
                'iscsi_primary_initiator_ident_pool': "",
                'initiator_primary_target_primary': "",
                'initiator_primary_target_secondary': ""}
            fi_iscsi_boot_params = copy.deepcopy(ucs_ini)
            initiator_primary_target_primary = ""
            initiator_primary_target_secondary = ""
            fi_iscsi_boot_params['service_profile'] = fi_service_profiles.name
            if len(handle.query_children(in_mo=fi_service_profiles)) != 0:
                mo_servprof_child = handle.query_children(
                    in_mo=fi_service_profiles, class_id="VnicIScsiBootParams")
                for service_profile_child in mo_servprof_child:
                    mo_iscsi_bootparams_child = handle.query_children(in_mo=service_profile_child)
                    if len(mo_iscsi_bootparams_child) != 0:
                        if service_profile_child.get_class_id() == "VnicIScsiBootParams":
                            for iscsi_bootparams_child in mo_iscsi_bootparams_child:
                                mo_iscsi_bootvnic_child = handle.query_children(
                                    in_mo=iscsi_bootparams_child)
                                if iscsi_bootparams_child.get_class_id() == "VnicIScsiBootVnic":
                                    if iscsi_bootparams_child.name.find('A') != -1:
                                        fi_iscsi_boot_params['iscsi_primary'] = iscsi_bootparams_child.name
                                    if len(mo_iscsi_bootvnic_child) != 0:
                                        for iscsi_bootvnic_child in mo_iscsi_bootvnic_child:
                                            mo_ini_targ_child = handle.query_children(
                                                in_mo=iscsi_bootvnic_child)
                                            if len(mo_ini_targ_child) != 0:
                                                if iscsi_bootvnic_child.get_class_id() == "VnicIPv4If":
                                                    for ini_targ_child in mo_ini_targ_child:
                                                        if ini_targ_child.get_class_id() == "VnicIPv4PooledIscsiAddr":
                                                            if ini_targ_child.dn.find('A') != -1:
                                                                fi_iscsi_boot_params['iscsi_primary_initiator_address'] = \
                                                                    ini_targ_child.addr
                                                                fi_iscsi_boot_params['iscsi_primary_initiator_subnet'] = \
                                                                    ini_targ_child.subnet
                                                                fi_iscsi_boot_params['iscsi_primary_initiator_def_gw'] = \
                                                                    ini_targ_child.def_gw
                                                                fi_iscsi_boot_params['iscsi_primary_initiator_ident_pool'] = \
                                                                    ini_targ_child.ident_pool_name
                                                if iscsi_bootvnic_child.get_class_id() == "VnicIScsiStaticTargetIf":
                                                    if ((iscsi_bootvnic_child.priority == "1") and (
                                                            iscsi_bootvnic_child.dn.find('A') != -1)):
                                                        initiator_primary_target_primary = iscsi_bootvnic_child.ip_address + \
                                                            "," + iscsi_bootvnic_child.name
                                                        if len(mo_ini_targ_child) != 0:
                                                            for ini_targ_child in mo_ini_targ_child:
                                                                if ini_targ_child.get_class_id() == "VnicLun":
                                                                    if ((ini_targ_child.dn.find('1') != -1) and
                                                                            (ini_targ_child.dn.find('A') != -1)):
                                                                        initiator_primary_target_primary += "," + \
                                                                            ini_targ_child.id
                                                    elif ((iscsi_bootvnic_child.priority == "2") and
                                                          (iscsi_bootvnic_child.dn.find('A') != -1)):
                                                        initiator_primary_target_secondary = iscsi_bootvnic_child.ip_address + \
                                                            "," + iscsi_bootvnic_child.name
                                                        if len(mo_ini_targ_child) != 0:
                                                            for ini_targ_child in mo_ini_targ_child:
                                                                if ini_targ_child.get_class_id() == "VnicLun":
                                                                    if ((ini_targ_child.dn.find('2') != -1) and
                                                                            (ini_targ_child.dn.find('A') != -1)):
                                                                        initiator_primary_target_secondary += "," + \
                                                                            ini_targ_child.id
            fi_iscsi_boot_params['initiator_primary_target_primary'] = initiator_primary_target_primary
            fi_iscsi_boot_params['initiator_primary_target_secondary'] = initiator_primary_target_secondary
            fi_iscsi_boot_params_list.append(fi_iscsi_boot_params.copy())
        if [ucs_dict for ucs_dict in fi_iscsi_boot_params_list if not ucs_dict == ucs_ini] != [
        ]:
            return PTK_OKAY, fi_iscsi_boot_params_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_iscsi_boot_params_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_iscsi_boot_params_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_iscsi_bootparams_secondary(args={}):
    """
    Function to obtain UCS iSCSI Boot Params Secondary Information.

    Parameters:
        args (dict): Takes the SAN Type as input.

    Returns:
        List of UCS iSCSI Boot Params Secondary Information.

    """
    fi_iscsi_boot_params_list = []
    method = "UCS System iSCSI Boot Parameters Secondary"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, fi_iscsi_boot_params_list, "failed to get handler for UCS Report Generation"
        for fi_service_profiles in handle.query_classid(class_id="LsServer"):
            ucs_ini = {
                'service_profile': "",
                'iscsi_secondary': "",
                'iscsi_secondary_initiator_address': "",
                'iscsi_secondary_initiator_subnet': "",
                'iscsi_secondary_initiator_def_gw': "",
                'iscsi_secondary_initiator_ident_pool': "",
                'initiator_secondary_target_primary': "",
                'initiator_secondary_target_secondary': ""}
            fi_iscsi_boot_params = copy.deepcopy(ucs_ini)
            initiator_secondary_target_primary = ""
            initiator_secondary_target_secondary = ""
            fi_iscsi_boot_params['service_profile'] = fi_service_profiles.name
            if len(handle.query_children(in_mo=fi_service_profiles)) != 0:
                mo_servprof_child = handle.query_children(
                    in_mo=fi_service_profiles, class_id="VnicIScsiBootParams")
                for service_profile_child in mo_servprof_child:
                    mo_iscsi_bootparams_child = handle.query_children(in_mo=service_profile_child)
                    if len(mo_iscsi_bootparams_child) != 0:
                        if service_profile_child.get_class_id() == "VnicIScsiBootParams":
                            for iscsi_bootparams_child in mo_iscsi_bootparams_child:
                                mo_iscsi_bootvnic_child = handle.query_children(
                                    in_mo=iscsi_bootparams_child)
                                if iscsi_bootparams_child.get_class_id() == "VnicIScsiBootVnic":
                                    if iscsi_bootparams_child.name.find('A') != -1:
                                        pass
                                    else:
                                        fi_iscsi_boot_params['iscsi_secondary'] = iscsi_bootparams_child.name
                                    if len(mo_iscsi_bootvnic_child) != 0:
                                        for iscsi_bootvnic_child in mo_iscsi_bootvnic_child:
                                            mo_ini_targ_child = handle.query_children(
                                                in_mo=iscsi_bootvnic_child)
                                            if len(mo_ini_targ_child) != 0:
                                                if iscsi_bootvnic_child.get_class_id() == "VnicIPv4If":
                                                    for ini_targ_child in mo_ini_targ_child:
                                                        if ini_targ_child.get_class_id() == "VnicIPv4PooledIscsiAddr":
                                                            if ini_targ_child.dn.find('A') != -1:
                                                                pass
                                                            else:
                                                                fi_iscsi_boot_params['iscsi_secondary_initiator_address'] = \
                                                                    ini_targ_child.addr
                                                                fi_iscsi_boot_params['iscsi_secondary_initiator_subnet'] = \
                                                                    ini_targ_child.subnet
                                                                fi_iscsi_boot_params['iscsi_secondary_initiator_def_gw'] = \
                                                                    ini_targ_child.def_gw
                                                                fi_iscsi_boot_params['iscsi_secondary_initiator_ident_pool'] = \
                                                                    ini_targ_child.ident_pool_name
                                                if iscsi_bootvnic_child.get_class_id() == "VnicIScsiStaticTargetIf":
                                                    if ((iscsi_bootvnic_child.priority == "1") and (
                                                            iscsi_bootvnic_child.dn.find('B') != -1)):
                                                        initiator_secondary_target_primary = iscsi_bootvnic_child.ip_address + \
                                                            "," + iscsi_bootvnic_child.name
                                                        if len(mo_ini_targ_child) != 0:
                                                            for ini_targ_child in mo_ini_targ_child:
                                                                if ini_targ_child.get_class_id() == "VnicLun":
                                                                    if ((ini_targ_child.dn.find('1') != -1) and
                                                                            (ini_targ_child.dn.find('B') != -1)):
                                                                        initiator_secondary_target_primary += "," + \
                                                                            ini_targ_child.id
                                                    elif ((iscsi_bootvnic_child.priority == "2") and
                                                          (iscsi_bootvnic_child.dn.find('B') != -1)):
                                                        initiator_secondary_target_secondary = iscsi_bootvnic_child.ip_address + \
                                                            "," + iscsi_bootvnic_child.name
                                                        if len(mo_ini_targ_child) != 0:
                                                            for ini_targ_child in mo_ini_targ_child:
                                                                if ini_targ_child.get_class_id() == "VnicLun":
                                                                    if ((ini_targ_child.dn.find('2') != -1) and
                                                                            (ini_targ_child.dn.find('B') != -1)):
                                                                        initiator_secondary_target_secondary += "," + \
                                                                            ini_targ_child.id
            fi_iscsi_boot_params['initiator_secondary_target_primary'] = initiator_secondary_target_primary
            fi_iscsi_boot_params['initiator_secondary_target_secondary'] = initiator_secondary_target_secondary
            fi_iscsi_boot_params_list.append(fi_iscsi_boot_params.copy())
        if [ucs_dict for ucs_dict in fi_iscsi_boot_params_list if not ucs_dict == ucs_ini] != [
        ]:
            return PTK_OKAY, fi_iscsi_boot_params_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, fi_iscsi_boot_params_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, fi_iscsi_boot_params_list, str(ue)
    finally:
        lock.release()


def get_ucs_system_udld_portchl_config(args={}):
    """
    Function to obtain UCS System UDLD PortChannel Configuration.

    Parameters:
        args (dict): None.

    Returns:
        List of UCS System UDLD PortChannel Configuration Info.

    """
    ucs_udld_list = []
    method = "UCS System UDLD PortChannel Configuration"
    try:
        lock.acquire()
        handle = _ucs_handler()
        if handle is None:
            loginfo("failed to get handler for UCS Report Generation " + method)
            return PTK_RESOURCENOTAVAILABLE, ucs_vsan_list, "failed to get handler for UCS Report Generation"
        for ucs_portchl in handle.query_classid(class_id="FabricEthLanPc"):
            ucs_ini = {'portchl_name': "", 'oper_speed': "", 'oper_state': "", 'switch_id': "",
                       'eth_interface': [], 'link_prof_name': [], 'udld_link_policy_name': [],
                       'udld_state': [], 'udld_mode': []}
            ucs_udld = copy.deepcopy(ucs_ini)
            ucs_udld['portchl_name'] = ucs_portchl.name
            ucs_udld['oper_speed'] = ucs_portchl.oper_speed
            ucs_udld['oper_state'] = ucs_portchl.oper_state
            ucs_udld['switch_id'] = ucs_portchl.switch_id
            if len(handle.query_children(in_mo=ucs_portchl)) != 0:
                mo_eth_interf = handle.query_children(
                    in_mo=ucs_portchl, class_id="FabricEthLanPcEp")
                for ucs_interf in mo_eth_interf:
                    ucs_udld['eth_interface'].append(ucs_interf.slot_id + "/" + ucs_interf.port_id)
                    interf_dn = ucs_interf.oper_eth_link_profile_name
                    if interf_dn:
                        mo_interf = handle.query_dn(interf_dn)
                        ucs_udld['link_prof_name'].append(mo_interf.name)
                        ucs_udld['udld_link_policy_name'].append(mo_interf.udld_link_policy_name)
                        udld_dn = mo_interf.oper_udld_link_policy_name
                        if udld_dn:
                            mo_udld = handle.query_dn(udld_dn)
                            ucs_udld['udld_state'].append(mo_udld.admin_state)
                            ucs_udld['udld_mode'].append(mo_udld.mode)
            ucs_udld_list.append(ucs_udld.copy())
        if [ucs_dict for ucs_dict in ucs_udld_list if not ucs_dict == ucs_ini] != []:
            return PTK_OKAY, ucs_udld_list, _("PDT_SUCCESS_MSG")
        loginfo("Unable to get " + method)
        return PTK_NOTEXIST, ucs_udld_list, "Unable to get " + method

    except Exception as ue:
        loginfo("UcsException has occured while fetching " + method + str(ue))
        return PTK_INTERNALERROR, ucs_udld_list, str(ue)
    finally:
        lock.release()
