import os
import threading
import requests
import time
import re
import json
from requests_toolbelt import MultipartEncoder
from ucsmsdk.ucshandle import UcsHandle
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.common import decrypt
from pure_dir.global_config import get_discovery_store
from pure_dir.components.compute.ucs.ucs_upgrade import ucsm_upgrade

from isc_dhcp_leases import IscDhcpLeases
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

#ucsm_credentials_store = "/mnt/system/pure_dir/pdt/ucsmlogin.xml"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UCSManager:
    dhcp_lease_file = '/var/lib/dhcpd/dhcpd.leases'

    def __init__(self):
        pass

    def _dhcpdiscovery(self):
        """
        DHCP Discovery of Fabric Interconnect
        :return: Returns the mac address,ip address and hostname of FI
        """
        discovery_list = []
        res = result()
        if os.path.exists(self.dhcp_lease_file) is False:
            res.setResult(
                discovery_list,
                PTK_INTERNALERROR,
                "DHCP leases file not present")
            return res

        leases = IscDhcpLeases(self.dhcp_lease_file)
        active_leases = leases.get_current()

        if len(active_leases) == 0:
            res.setResult(discovery_list, PTK_OKAY, "No active leases")
            return res

        for key, value in active_leases.items():
            discovery_list.append({"mac_address": key,
                                   "ip_address": active_leases[key].ip,
                                   "hostname": active_leases[key].hostname})
        res.setResult(discovery_list, PTK_OKAY, "success")
        return res

    def ucsmlist(self):
        """
        Get the UCS FI details
        :return: Returns the name and mac address of FI
        """

        res = result()
        ucsm_list = []
        if os.path.exists(get_discovery_store()) is True:
            doc = parse_xml(get_discovery_store())
            for subelement in doc.getElementsByTagName("device"):
                if subelement.getAttribute("device_type") == "UCSM" and subelement.getAttribute(
                        "leadership") != "subordinate":
                    details = {}
                    details['name'] = subelement.getAttribute("name")
                    details['mac'] = subelement.getAttribute("mac")
                    ucsm_list.append(details)

        res.setResult(ucsm_list, PTK_OKAY, "success")
        return res

    def is_passwd_strong(self, passwd):
        pattern = '^.*(?=.{6,80})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!"%&\'()*+,-./:;<>@[\]^_`{|}~]).*$'
        if not re.search(pattern, passwd):
            return False
        else:
            password = passwd.lower()
            if (re.findall(r'(([a-zA-Z0-9_])\2{1,})', password) or
                           re.findall(r'((\d)\2{1,})', password)):
                return False
            else:
                numlst = [int(num) for num in [i for i in
                            re.split(r'[!"%&\'()*+,-./:;<>@[\]^_`{|}~]', password)
                            if i.isdigit()][0]]
                if sorted(numlst) == list(range(min(numlst), max(numlst)+1)):
                    return False

    def requests_retry_session(self,
                               retries=100,
                               backoff_factor=0.3,
                               status_forcelist=(500, 502, 504),
                               session=None,
                               ):
        """
        Create a requests session that handles errors by retrying
        :param retries: Number of retries to attempt
        :param backoff_factor: backoff factor
        :param status_forcelist: status codes that must be retried
        :param session: Existing request session to configure
        :return: session
        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        return session

    def is_ucsm_up(self, ip):
        """
        Verify whether UCS go down for reboot after Unified ports configuration
        :param ip: UCSM FI IP Address
        """
        url = "http://" + ip
        for attempts in range(100):
            try:
                r = requests.get(url, timeout=5, verify=False)
                time.sleep(2)
                if r.status_code == 200:
                    loginfo("UCS is UP attempt %d" % attempts)
                    continue
                else:
                    loginfo("Fabric module " + ip + " is down")
                    break
            except BaseException:
                loginfo("Fabric module " + ip + " is down")
                return "ucs down"
            else:
                break

    def verify_ucsm_accessible(self, ip):
        """
        Verify if UCSM is accessible
        :param ip: UCSM FI IP Address
        """
        t0 = time.time()
        try:
            self.requests_retry_session().get(
                'http://' + ip, verify=False
            )
        except Exception as x:
            loginfo('Checking if UCS is accessible failed %s' %
                    x.__class__.__name__)
            loginfo("exception result %s" % x)
        else:
            loginfo("UCS is up")
        finally:
            t1 = time.time()
            loginfo('Took' + str(t1 - t0) + 'seconds')

    def fabric_info(self, ip, username, password):

        fabrics = self.fabric_list(ip, username, password).getResult()
        for fabric in fabrics:
            if fabric['leadership'] == "subordinate":
                fabric['name'] = fabric['name'] + "-B"
                fabric['vipaddress'] = fabric['vip']
            elif fabric['leadership'] == "primary":
                fabric['name'] = fabric['name'] + "-A"
                fabric['vipaddress'] = fabric['vip']
            else:
                fabric['name'] = fabric['name'] + "-A"
                fabric['vipaddress'] = ""
        return fabrics

    def fabric_list(self, ip, username, password):
        res = result()
        handle = self._ucsm_handler(
            ip, username, password)
        if handle is None:
            res.setResult(None, PTK_RESOURCENOTAVAILABLE,
                          "failed to get handler")
            return res

        switch_list = []
        if handle is not None:
            fabrics = handle.query_classid("networkelement")
            mo = handle.query_dn("sys")

            for fabric in fabrics:
                switch = {}
                switch['mac_addr'] = fabric.oob_if_mac
                switch['model'] = fabric.model
                switch['serial_no'] = fabric.serial
                switch['ip'] = fabric.oob_if_ip
                switch['name'] = mo.name
                switch['vip'] = mo.address
                version_info = handle.query_dn("sys/mgmt/fw-system")
                switch['version'] = version_info.version

                mgmtentities = handle.query_classid("MgmtEntity")
                for mgmtentity in mgmtentities:
                    if fabric.id == mgmtentity.id:
                        leadership = mgmtentity.leadership
                        switch['leadership'] = leadership

                switch_list.append(switch)
            res.setResult(switch_list, PTK_OKAY, "success")
            self._release_ucsm_handler(handle)
            return res

        res.setResult(None, PTK_RESOURCENOTAVAILABLE, "failed to get handler")
        return res


    def ucsm_sp_wwpn(self, ipaddress, username, password):
        wwpn_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress, username, password)
        if handle is not None:
            sp_list = handle.query_classid("LsServer")
            for sp in sp_list:
                if sp.type != "updating-template" and sp.dn != '' and sp.pn_dn != '':
                    mo = handle.query_dn(sp.dn)
                    vnic_data = handle.query_children(
                        in_mo=mo, class_id='VnicFc')
                    for fc_vnic in vnic_data:
                        wwpn_list.append(fc_vnic.addr)
            res.setResult(wwpn_list, PTK_OKAY, "success")
        else:
            res.setResult(
                wwpn_list,
                PTK_NOTEXIST,
                "Unable to retrieve wwpn list")
        self._release_ucsm_handler(handle)
        return res

    def _save_ucsm_primary_details(
            self,
            ipaddress,
            username,
            password,
            serial_no,
            mac,
            model,
            device_type,
            configured,
            name,
            tag,
            vipaddress,
            leadership,
            reachability,
            dns,
            domain_name,
            gateway,
            ntp_server,
            ipformat,
            netmask,
            pri_cluster,
            pri_id,
            pri_orig_ip,
            pri_setup_mode,
            validated,
            esxi_file,
            esxi_kickstart,
            os_install,
            infra_image,
            blade_image,
            ucs_upgrade,
            server_type):
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(get_discovery_store(), data)
        return

    def _save_ucsm_subordinate_details(
            self,
            ipaddress,
            username,
            password,
            pri_ip,
            serial_no,
            mac,
            model,
            device_type,
            configured,
            name,
            tag,
            vipaddress,
            leadership,
            reachability,
            sec_cluster,
            sec_id,
            sec_orig_ip,
            netmask,
            gateway,
            ntp_server,
            validated,
            infra_image,
            blade_image,
            ucs_upgrade,
            server_type):
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(get_discovery_store(), data)
        return

    def ucsmficonfigure(self, mode, config):
        res = result()

        if mode == "cluster":
            update_xml_element(
                get_discovery_store(),
                matching_key="mac",
                matching_value=config['pri_switch_mac'],
                data={
                    "configured": "In-progress",
                    "timestamp": str(
                        time.time())})
            update_xml_element(
                get_discovery_store(),
                matching_key="mac",
                matching_value=config['sec_switch_mac'],
                data={
                    "configured": "In-progress",
                    "timestamp": str(
                        time.time())})

            threading.Thread(target=self.ucsmclusterficonfigure,
                             args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        elif mode == "primary":
            update_xml_element(
                get_discovery_store(),
                matching_key="mac",
                matching_value=config['pri_switch_mac'],
                data={
                    "configured": "In-progress",
                    "timestamp": str(
                        time.time())})

            threading.Thread(target=self.ucsmprimaryficonfigure,
                             args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        elif mode == "subordinate":
            update_xml_element(
                get_discovery_store(),
                matching_key="mac",
                matching_value=config['sec_switch_mac'],
                data={
                    "configured": "In-progress",
                    "timestamp": str(
                        time.time())})

            threading.Thread(
                target=self.ucsmsubordinateficonfigure, args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        elif mode == "standalone":
            update_xml_element(
                get_discovery_store(),
                matching_key="mac",
                matching_value=config['pri_switch_mac'],
                data={
                    "configured": "In-progress",
                    "timestamp": str(
                        time.time())})

            threading.Thread(
                target=self.ucsmstandaloneficonfigure, args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        else:
            res.setResult(
                '',
                PTK_NOTEXIST,
                "Invalid mode")
            return res

    def ucsmfireconfig(self, data, force):
        if force == 0:
            populate_lst = []
            for dt in data:
                fi_dict = {}
                fi_dict['mode'] = dt['leadership']
                fi_dict['switch_netmask'] = dt['netmask']
                fi_dict['switch_gateway'] = dt['gateway']
                fi_dict['ntp_server'] = dt['ntp_server']
                fi_dict['switch_ip'] = dt['ipaddress']
                fi_dict['virtual_ip'] = dt['vipaddress']
                fi_dict['switch_name'] = dt['name'].rsplit('-', 1)[0]
                fi_dict['switch_tag'] = dt['tag']
                fi_dict['switch_mac'] = dt['mac']
                fi_dict['ucs_upgrade'] = dt['ucs_upgrade']
                fi_dict['infra_image'] = dt['infra_image']
                fi_dict['blade_image'] = dt['blade_image']
                fi_dict['server_type'] = dt['server_type']
                if dt['leadership'] == "primary":
                    fi_dict['dns'] = dt['dns']
                    fi_dict['domain_name'] = dt['domain_name']
                    fi_dict['esxi_file'] = dt['esxi_file']
                    fi_dict['esxi_kickstart'] = dt['esxi_kickstart']
                elif dt['leadership'] == "subordinate":
                    fi_dict['pri_ip'] = dt['pri_ip']
                populate_lst.append(fi_dict)
            return True, json.dumps(populate_lst)
        else:
            return self.ucsmfireconfigure(data)

    def ucsmfireconfigure(self, data):
        input_dict = {}
        if len(data) == 2:
            loginfo("FI Reconfigure: Gathering inputs for cluster mode")
            mode = "cluster"
            for dt in data:
                if dt['leadership'] == "primary":
                    primary_data = dt
                elif dt['leadership'] == "subordinate":
                    subordinate_data = dt
            input_dict = {"pri_switch_mac": primary_data["mac"],
                          "pri_switch_serial_no": primary_data["serial_no"],
                          "pri_switch_vendor": primary_data["model"],
                          "pri_setup_mode": primary_data["pri_setup_mode"],
                          "pri_cluster": primary_data["pri_cluster"],
                          "pri_id": primary_data["pri_id"],
                          "ipformat": primary_data["ipformat"],
                          "pri_name": primary_data["name"],
                          "pri_passwd": decrypt(primary_data["password"]),
                          "pri_ip": primary_data["ipaddress"],
                          "pri_orig_ip": primary_data["pri_orig_ip"],
                          "netmask": primary_data["netmask"],
                          "gateway": primary_data["gateway"],
                          "ntp_server": primary_data["ntp_server"],
                          "virtual_ip": primary_data["vipaddress"],
                          "dns": primary_data["dns"],
                          "domain_name": primary_data["domain_name"],
                          "ucs_upgrade": primary_data["ucs_upgrade"],
                          "infra_image": primary_data["infra_image"],
                          "blade_image": primary_data["blade_image"],
                          "server_type": primary_data["server_type"],
                          "sec_switch_mac": subordinate_data["mac"],
                          "sec_switch_serial_no": subordinate_data["serial_no"],
                          "sec_switch_vendor": subordinate_data["model"],
                          "sec_cluster": subordinate_data["sec_cluster"],
                          "esxi_file": primary_data["esxi_file"],
                          "esxi_kickstart": primary_data["esxi_kickstart"],
                          "sec_orig_ip": subordinate_data["sec_orig_ip"],
                          "sec_ip": subordinate_data["ipaddress"],
                          "sec_id": subordinate_data["sec_id"],
                          "conf_passwd": decrypt(primary_data["password"])}

        elif len(data) == 1:
            data = data[0]
            mode = data['leadership']
            input_dict['pri_name'] = data['name']
            input_dict['pri_passwd'] = decrypt(data['password'])
            input_dict['virtual_ip'] = data['vipaddress']
            input_dict['ucs_upgrade'] = data['ucs_upgrade'],
            input_dict['infra_image'] = data['infra_image'],
            input_dict['blade_image'] = data['blade_image'],
            input_dict['server_type'] = data['server_type']
            if data['leadership'] == "primary":
                loginfo("FI Reconfigure: Gathering inputs for primary mode")
                input_dict['dns'] = data['dns']
                input_dict['domain_name'] = data['domain_name']
                input_dict['netmask'] = data['netmask']
                input_dict['gateway'] = data['gateway']
                input_dict['ntp_server'] = data['ntp_server'],
                input_dict['ipformat'] = data['ipformat']
                input_dict['pri_cluster'] = data['pri_cluster']
                input_dict['pri_id'] = data['pri_id']
                input_dict['pri_ip'] = data['ipaddress']
                input_dict['pri_orig_ip'] = data['pri_orig_ip']
                input_dict['pri_setup_mode'] = data['pri_setup_mode']
                input_dict['pri_switch_mac'] = data['mac']
                input_dict['pri_switch_serial_no'] = data['serial_no']
                input_dict['pri_switch_vendor'] = data['model']
                input_dict['esxi_file'] = data['esxi_file']
                input_dict['esxi_kickstart'] = data["esxi_kickstart"]
            elif data['leadership'] == "subordinate":
                loginfo("FI Reconfigure: Gathering inputs for subordinate mode")
                input_dict['sec_cluster'] = data['sec_cluster']
                input_dict['pri_ip'] = data['pri_ip']
                input_dict['sec_id'] = data['sec_id']
                input_dict['sec_ip'] = data['ipaddress']
                input_dict['sec_orig_ip'] = data['sec_orig_ip']
                input_dict['sec_switch_mac'] = data['mac']
                input_dict['sec_switch_serial_no'] = data['serial_no']
                input_dict['sec_switch_vendor'] = data['model']
                input_dict['server_type'] = data['server_type']

        loginfo("FI Reconfigure: Validating FI configuration params")
        validation_status = self.ucsmfivalidate(mode, input_dict).getStatus()
        if validation_status == PTK_OKAY:
            loginfo("FI Reconfigure: FI Validation success. Configuring FI")
            conf_status = self.ucsmficonfigure(mode, input_dict).getStatus()
            if conf_status == PTK_OKAY:
                loginfo("FI Reconfigure: FI Configuration success")
                return True, 0
            else:
                loginfo("FI Reconfigure: FI Configuration failure")
                return False, -1
        else:
            loginfo("FI Reconfigure: FI Validation failure")
            return False, -1

    def ucsm_validate_ip(self, ip_list, netmask, gateway):
        res = result()
        err = []
        ipv = IpValidator()
        valid = True
        if len(ip_list) == len(set(ip_list)):
            for ip in ip_list:
 		ip_val = False
                if ip != 'dns':
                       ip_val = ipvalidation(ip_list[ip])
                else:
                       ip_val = True
                if not ip_val:
                    err.append({"field": ip, "msg": "Please Enter Valid IP"})
                if ip != 'dns':
                    network_reach, ip_reach = ipv.validate_ip(
                        ip_list[ip], netmask, gateway)
                    if network_reach:
                        if ip_reach:
                            err.append(
                                {"field": ip, "msg": "IP Address is already occupied"})
                    else:
                        err.append(
                            {"field": ip, "msg": "Please check the network settings"})
                        valid = False

            if not valid:
                err.append(
                    {"field": "gateway", "msg": "Please check the network settings"})
                err.append(
                    {"field": "netmask", "msg": "Please check the network settings"})

            if len(err) == 0:
                res.setResult(err, PTK_OKAY, "Success")
                return res
            else:
                res.setResult(err, PTK_INTERNALERROR,
                              "Please check the IP address.")
                return res
        else:
            res.setResult(err, PTK_INTERNALERROR,
                          "IP addresses should be unique")
            return res

    def ucsmfivalidate(self, mode, config):
        res = result()
        ret = []

        if mode == "cluster":
            ret = validate_input_data({'pri_ip': 'Mgmt IP for primary FI',
                                       'pri_passwd': 'Password',
                                       'conf_passwd': 'Confirm password',
                                       'pri_switch_serial_no': 'Serial number of primary FI',
                                       'pri_switch_mac': 'MAC of primary FI',
                                       'pri_switch_vendor': 'Vendor of primary FI',
                                       'pri_name': 'Name for primary FI',
                                       'pri_orig_ip': 'DHCP IP of primary FI',
                                       'pri_setup_mode': 'Set up mode for primary FI',
                                       'pri_cluster': 'Cluster mode for primary FI',
                                       'pri_id': 'ID for primary FI',
                                       'ipformat': 'IP format',
                                       'netmask': 'Netmask',
                                       'gateway': 'Gateway',
                                       'ntp_server': 'NTP Server ip',
                                       'virtual_ip': 'Virtual IP',
                                       'sec_ip': 'IP for subordiate FI',
                                       'sec_switch_serial_no': 'Serial number of subordiate FI',
                                       'sec_switch_mac': 'MAC of subordiate FI',
                                       'sec_switch_vendor': 'Vendor of subordiate FI',
                                       'sec_orig_ip': 'DHCP IP of subordiate FI',
                                       'sec_cluster': 'Cluster mode for subordiate FI',
                                       'sec_id': 'ID for subordinate FI',
                                      #'esxi_file': 'Remote ESX file',
                                       'dns': 'DNS IP',
                                       'server_type': 'Server type may be Rack or Blade'},
                                      config)
            if len(ret) > 0:
                res.setResult(ret, PTK_INTERNALERROR,
                              "Please fill all mandatory fields")
                return res
            else:
                if config['pri_passwd'] != config['conf_passwd']:
                    ret.append({'field': 'conf_passwd',
                                'msg': 'Password does not match'})
                    res.setResult(ret, PTK_INTERNALERROR,
                                  "Make sure details are correct")
                    return res

                if 'pri_passwd' in config and config['pri_passwd']:
                    if self.is_passwd_strong(config['pri_passwd']) == False:
                        ret.append({'field': 'pri_passwd',
                                    'msg': 'Password is incorrect. please refer the HelpText'})
                        ret.append({'field': 'conf_passwd',
                                    'msg': 'Password is incorrect. please refer the HelpText'})
                        res.setResult(ret, PTK_INTERNALERROR,
                                      "Make sure details are correct")
                        return res
                                
                if 'os_install' in config and config['os_install'] == "Yes":
                    if config['esxi_file'] == "":
                        ret.append({'field': 'esxi_file',
                                    'msg': 'Remote ESX file cannot be empty'})
                        res.setResult(ret, PTK_INTERNALERROR, 
                                      "Remote ESX file cannot be empty")
                        return res

                if 'ucs_upgrade' in config and config['ucs_upgrade'] == "Yes":
                    if config['infra_image'] == "" and config['blade_image'] == "":
                        ret.append({'field': 'infra_image',
                                    'msg': 'Select any image'})
                        ret.append({'field': 'blade_image',
                                    'msg': 'Select any image'})
                        res.setResult(ret, PTK_INTERNALERROR,
                                      "Select any image")
                        return res
                    if "FI-62" in config['pri_switch_vendor'] and config['infra_image'] != "":
                        if "ucs-k9" not in config['infra_image']:
                            ret.append({'field': 'infra_image',
                                        'msg': 'Select an Image supported for Gen2 FI'})
                            res.setResult(ret, PTK_INTERNALERROR,
                                          "Select correct image")
                            return res
                    if "FI-63" in config['pri_switch_vendor'] and config['infra_image'] != "":
                        if "ucs-6300" not in config['infra_image']:
                            ret.append({'field': 'infra_image',
                                        'msg': 'Select an Image supported for Gen3 FI'})
                            res.setResult(ret, PTK_INTERNALERROR,
                                          "Select correct image")
                            return res
                    if "FI-64" in config['pri_switch_vendor'] and config['infra_image'] != "":
                        if "ucs-6400" not in config['infra_image']:
                            ret.append({'field': 'infra_image',
                                        'msg': 'Select an Image supported for Gen4 FI'})
                            res.setResult(ret, PTK_INTERNALERROR,
                                          "Select correct image")
                            return res
                    if "FI-632" in config['pri_switch_vendor'] and config['infra_image'] != "":
                        if "ucs-mini-k9" not in config['infra_image']:
                            ret.append({'field': 'infra_image',
                                        'msg': 'Select an Image supported for Gen3 mini FI'})
                            res.setResult(ret, PTK_INTERNALERROR,
                                          "Select correct image")
                            return res
                ip_list = {
                    'pri_ip': config['pri_ip'],
                    'sec_ip': config['sec_ip'],
                    'virtual_ip': config['virtual_ip'],
                    'dns': config['dns']}
                # ip_list = [config['pri_ip'],
                #         config['sec_ip'], config['virtual_ip']]
                res = self.ucsm_validate_ip(
                    ip_list, config['netmask'], config['gateway'])
                return res

        elif mode == "primary":
            ret = validate_input_data({'pri_ip': 'Mgmt IP for primary FI',
                                       'pri_passwd': 'Password for primary FI',
                                       'pri_switch_serial_no': 'Serial number of primary FI',
                                       'pri_switch_mac': 'MAC of primary FI',
                                       'pri_switch_vendor': 'Vendor of primary FI',
                                       'pri_name': 'Name for primary FI',
                                       'pri_orig_ip': 'DHCP IP of primary FI',
                                       'pri_setup_mode': 'Set up mode for primary FI',
                                       'pri_cluster': 'Cluster mode for primary FI',
                                       'pri_id': 'ID for primary FI',
                                       'ipformat': 'IP format',
                                       'netmask': 'Netmask',
                                       'gateway': 'Gateway',
                                       'ntp_server': 'NTP Server ip',
                                       'virtual_ip': 'Virtual IP'},
                                      config)
            if len(ret) > 0:
                res.setResult(ret, PTK_INTERNALERROR,
                              "Please fill all mandatory fields")
                return res
            else:
                ip_list = {'pri_ip': config['pri_ip'], 'pri_orig_ip': config['pri_orig_ip'],
                           'virtual_ip': config['virtual_ip']}
                # ip_list = [config['pri_ip'], config['virtual_ip']]
                res = self.ucsm_validate_ip(
                    ip_list, config['netmask'], config['gateway'])
                return res

        elif mode == "subordinate":
            ret = validate_input_data({'pri_ip': 'Mgmt IP for standalone FI',
                                       'sec_ip': 'IP for subordiate FI',
                                       'sec_switch_serial_no': 'Serial number of subordiate FI',
                                       'sec_switch_mac': 'MAC of subordiate FI',
                                       'sec_switch_vendor': 'Vendor of subordiate FI',
                                       'sec_orig_ip': 'DHCP IP of subordiate FI',
                                       'sec_cluster': 'Cluster mode for subordiate FI',
                                       'sec_id': 'ID for subordinate FI'},
                                      config)
            if len(ret) > 0:
                res.setResult(ret, PTK_INTERNALERROR,
                              "Please fill all mandatory fields")
                return res
            else:
                ipv = IpValidator()
                if ipv.is_ip_up(config['pri_ip']) == False:
                    res.setResult(ret, PTK_INTERNALERROR,
                                  "Primary IP Address is not reachable")
                    return res
                if ipv.is_ip_up(config['sec_ip']):
                    res.setResult(
                        ret,
                        PTK_INTERNALERROR,
                        "Mgmt IP Address provided is already active, provide a free IP")
                    return res
                res.setResult(ret, PTK_OKAY, "Success")
                return res

        elif mode == "standalone":
            ret = validate_input_data({'pri_ip': 'Mgmt IP for standalone FI',
                                       'pri_passwd': 'Password for standalone FI',
                                       'pri_switch_serial_no': 'Serial number of standalone FI',
                                       'pri_switch_mac': 'MAC of standalone FI',
                                       'pri_switch_vendor': 'Vendor of standalone FI',
                                       'pri_name': 'Name for standalone FI',
                                       'pri_orig_ip': 'DHCP IP of standalone FI',
                                       'pri_setup_mode': 'Set up mode for standalone FI',
                                       'pri_cluster': 'Cluster mode for standalone FI',
                                       'pri_id': 'ID for standalone FI',
                                       'ntp_server': 'NTP Server ip',
                                       'ipformat': 'IP format',
                                       'netmask': 'Netmask',
                                       'gateway': 'Gateway'},
                                      config)
            if len(ret) > 0:
                res.setResult(ret, PTK_INTERNALERROR,
                              "Please fill all mandatory fields")
                return res
            else:
                ip_list = {'pri_ip': config['pri_ip'],
                           'pri_orig_ip': config['pri_orig_ip']}
                ip_list = [config['pri_ip']]
                res = self.ucsm_validate_ip(
                    ip_list, config['netmask'], config['gateway'])
                return res

        else:
            res.setResult(
                ret,
                PTK_NOTEXIST,
                "Invalid mode")
            return res

    def ucsmprimaryficonfigure(self, config):
        loginfo("Configuring the primary FI %s" % config['pri_name'])
        url = "https://" + config['pri_orig_ip'] + \
              "/cgi-bin/initial_setup_new.cgi"
        data = {}
        data = self._form_data(
            setup_mode=config['pri_setup_mode'],
            cluster=config['pri_cluster'],
            switchFabric=config['pri_id'],
            ipformat=config['ipformat'],
            systemName=config['pri_name'],
            adminPasswd=config['pri_passwd'],
            oobIP=config['pri_ip'],
            oobNM=config['netmask'],
            oobGW=config['gateway'],
            virtualIP=config['virtual_ip'],
            dns1=config['dns'].split(',')[0],
            domainName=config['domain_name'],
            pasadena="",
            pasadenasecret="")
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the primary FI %s. Maximum attempts reached" %
                        config['pri_name'])
                    return
                loginfo("Failed to configure the primary FI %s. Retrying once more" %
                        config['pri_name'])
                retry += 1
                time.sleep(2)

        loginfo("Successfully configure the primary FI %s" %
                config['pri_name'])
        return

    def ucsmsubordinateficonfigure(self, config):
        loginfo("Configuring the subordinate FI")

        url = "https://" + config['sec_orig_ip'] + \
              "/cgi-bin/initial_setup_clusteradd.cgi"
        data = {
            "hidden_forcePeerA": "",
            "cluster": config['sec_cluster'],
            "switchFabric": config['sec_id'],
            "adminPasswd": config['pri_passwd']}
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" %
                        config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" %
                    config['sec_ip'])
                retry += 1
                time.sleep(2)

        url = "https://" + config['sec_orig_ip'] + \
              "/cgi-bin/initial_setup_oob.cgi"
        sub_ip = config['sec_ip'].split('.')
        data = {
            "hidden_init": "hidden_init",
            "oobIP1": sub_ip[0],
            "oobIP2": sub_ip[1],
            "oobIP3": sub_ip[2],
            "oobIP4": sub_ip[3]}
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" %
                        config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" %
                    config['sec_ip'])
                retry += 1
                time.sleep(2)

        loginfo(
            "Successfully configured subordinate FI %s" % config['sec_ip'])

        if 'ucs_upgrade' in config and config['ucs_upgrade'] == "Yes":
            loginfo("Waiting for UCS vip to be up")
            retry = 0
            while retry < 20:
                (error, status) = execute_remote_command(
                    config['virtual_ip'], "admin", config['pri_passwd'], "show version")
                if status is False:
                    time.sleep(20)
                    retry += 1
                else:
                    break
 
            time.sleep(300)

            loginfo("Triggering UCS upgrade")
            staus, msg = ucsm_upgrade(
                ip=config['virtual_ip'], username="admin", password=config['pri_passwd'], infra=config['infra_image'])
            if not status:
                loginfo("UCS upgrade failed. Updating device status")
                update_xml_element(
                    get_discovery_store(),
                    matching_key="mac",
                    matching_value=config['sec_switch_mac'],
                    data={
                        "configured": "Re-validate",
                        "reval_msg": msg})
            else:
                loginfo("UCS upgrade done. Updating device status")
                update_xml_element(
                    get_discovery_store(),
                    matching_key="mac",
                    matching_value=config['sec_switch_mac'],
                    data={
                        "configured": "Configured"})

        return

    def ucsmstandaloneficonfigure(self, config):
        loginfo("Configuring the standalone FI %s" % config['pri_name'])
        url = "https://" + config['pri_orig_ip'] + \
              "/cgi-bin/initial_setup_new.cgi"
        data = {}
        data = self._form_data(
            setup_mode=config['pri_setup_mode'],
            cluster=config['pri_cluster'],
            switchFabric=config['pri_id'],
            ipformat=config['ipformat'],
            systemName=config['pri_name'],
            adminPasswd=config['pri_passwd'],
            oobIP=config['pri_ip'],
            oobNM=config['netmask'],
            oobGW=config['gateway'],
            virtualIP=config['virtual_ip'],
            dns1=config['dns'].split(',')[0],
            domainName=config['domain_name'],
            pasadena="",
            pasadenasecret="")
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the standalone FI %s. Maximum attempts reached" %
                        config['pri_name'])
                    return
                loginfo("Failed to configure the standalone FI %s. Retrying once more" %
                        config['pri_name'])
                retry += 1
                time.sleep(2)

        loginfo("Successfully configure the standalone FI %s" %
                config['pri_name'])
        return

    def ucsmclusterficonfigure(self, config):
        loginfo("Configuring the primary FI %s" % config['pri_name'])
        url = "https://" + config['pri_orig_ip'] + \
              "/cgi-bin/initial_setup_new.cgi"
        data = {}
        data = self._form_data(
            setup_mode=config['pri_setup_mode'],
            cluster=config['pri_cluster'],
            switchFabric=config['pri_id'],
            ipformat=config['ipformat'],
            systemName=config['pri_name'],
            adminPasswd=config['pri_passwd'],
            oobIP=config['pri_ip'],
            oobNM=config['netmask'],
            oobGW=config['gateway'],
            virtualIP=config['virtual_ip'],
            dns1=config['dns'].split(',')[0],
            domainName=config['domain_name'],
            pasadena="",
            pasadenasecret="")
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the primary FI %s. Maximum attempts reached" %
                        config['pri_name'])
                    return
                loginfo("Failed to configure the primary FI %s. Retrying once more" %
                        config['pri_name'])
                retry += 1
                time.sleep(2)

        retry = 0
        while retry < 15:
            '''status = False
            try:
                #Bad fix, needs to upgrade paramiko
                handle = UcsHandle(config['pri_ip'],
                           'admin', config['pri_passwd'])
                handle_status = handle.login()
                if handle_status:
                        handle.logout()
                        break
            except Exception as e:
                if 'ERR-secondary-node' in str(e):
                    loginfo(str(e))
                    status = True
                    break'''

            (error, status) = execute_remote_command(
                config['pri_ip'], "admin", config['pri_passwd'], "show version")
            if status is False:
                loginfo("Waiting for primary FI to be reachable...")
                time.sleep(10)
                retry += 1
            else:
                break

        if status is False:
            loginfo("Failed to configure the primary FI %s" %
                    config['pri_name'])
            return

        '''self._save_ucsm_login_details(
            ipaddress=config['pri_ip'],
            username="admin",
            password=config['pri_passwd'])'''

        loginfo("Successfully configured primary FI %s" % config['pri_name'])

        loginfo("Configuring the subordinate FI %s" % config['sec_ip'])

        url = "https://" + config['sec_orig_ip'] + \
              "/cgi-bin/initial_setup_clusteradd.cgi"
        data = {
            "hidden_forcePeerA": "",
            "cluster": config['sec_cluster'],
            "switchFabric": config['sec_id'],
            "adminPasswd": config['pri_passwd']}
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" %
                        config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" %
                    config['sec_ip'])
                retry += 1
                time.sleep(2)

        url = "https://" + config['sec_orig_ip'] + \
              "/cgi-bin/initial_setup_oob.cgi"
        sub_ip = config['sec_ip'].split('.')
        data = {
            "hidden_init": "hidden_init",
            "oobIP1": sub_ip[0],
            "oobIP2": sub_ip[1],
            "oobIP3": sub_ip[2],
            "oobIP4": sub_ip[3]}
        payload = MultipartEncoder(data)
        loginfo(payload)

        retry = 0
        while retry < 5:
            try:
                requests.post(
                    url,
                    payload,
                    headers={
                        'Content-Type': payload.content_type},
                    verify=False)
                break
            except Exception as e:
                loginfo(str(e))
                if retry == 4:
                    loginfo(
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" %
                        config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" %
                    config['sec_ip'])
                retry += 1
                time.sleep(2)

        loginfo(
            "Successfully configured subordinate FI %s. Cluster configuration done" %
            config['sec_ip'])

        if 'ucs_upgrade' in config and config['ucs_upgrade'] == "Yes" and config['infra_image'] != "":
            loginfo("Waiting for UCS vip to be up")
            retry = 0
            while retry < 20:
                (error, status) = execute_remote_command(
                    config['virtual_ip'], "admin", config['pri_passwd'], "show version")
                if status is False:
                    time.sleep(20)
                    retry += 1
                else:
                    break

            time.sleep(300)

            loginfo("Triggering UCS upgrade")
            staus, msg = ucsm_upgrade(
                ip=config['virtual_ip'], username="admin", password=config['pri_passwd'], infra=config['infra_image'])
            if not status:
                loginfo("UCS upgrade failed. Updating device status")
                update_xml_element(
                    get_discovery_store(),
                    matching_key="mac",
                    matching_value=config['pri_switch_mac'],
                    data={
                        "configured": "Re-validate",
                        "reval_msg": msg})
                update_xml_element(
                    get_discovery_store(),
                    matching_key="mac",
                    matching_value=config['sec_switch_mac'],
                    data={
                        "configured": "Re-validate",
                        "reval_msg": msg})
            else:
                loginfo("UCS upgrade done. Updating device status")
                update_xml_element(
                    get_discovery_store(),
                    matching_key="mac",
                    matching_value=config['pri_switch_mac'],
                    data={
                        "configured": "Configured"})
                update_xml_element(
                    get_discovery_store(),
                    matching_key="mac",
                    matching_value=config['sec_switch_mac'],
                    data={
                        "configured": "Configured"})

        return

    def ucsmsetip(
            self,
            clusterip='',
            primaryip='',
            secondaryip='',
            gateway='',
            netmask=''):
        res = result()
        result = ""
        """
        if clusterip:
                handle = self._ucsm_handler(ipaddress="", username="", password="")
                if handle != None:
            ob = handle.query_dn("sys")
            mo = NetworkElement(parent_mo_or_dn=ob, oob_if_ip=secondaryip, admin_evac_state="fill", oob_if_gw=gateway, force_evac="no", oob_if_mask=netmask, id="B")
            handle.add_mo(mo, True)
            try:
                handle.commit()
            except UcsException as e:
                loginfo("error" + str(e))
                res.setResult(result, PTK_INTERNALERROR, "Failed to set ip for FI")
                return res

            ob = handle.query_dn("sys")
            mo = NetworkElement(parent_mo_or_dn=ob, oob_if_ip=primaryip, admin_evac_state="fill", oob_if_gw=gateway, force_evac="no", oob_if_mask=netmask, id="A")
            handle.add_mo(mo, True)
            try:
                handle.commit()
                    except UcsException as e:
                        loginfo("error" + str(e))
                        res.setResult(result,PTK_INTERNALERROR, "Failed to set ip for FI")
                        return res

                mo = handle.query_dn("sys")
            mo.ipv6_addr = "::"
            #mo.name = "FI-A"
            mo.descr = ""
            mo.site = ""
            mo.address = clusterip
            mo.owner = ""
            handle.set_mo(mo)
            try:
                handle.commit()
                    except UcsException as e:
                        loginfo("error" + str(e))
                        res.setResult(result, PTK_INTERNALERROR, "Failed to set VIP")
                        return res
        elif primaryip:
            handle = self._ucsm_handler(ipaddress="", username="", password="")
            if handle != None:
                ob = handle.query_dn("sys")
            fabric = handle.query_classid("networkelement")
            mo = NetworkElement(parent_mo_or_dn=ob, oob_if_ip=primaryip, admin_evac_state="fill", oob_if_gw=gateway, force_evac="no", oob_if_mask=netmask, id=fabric.id)
            handle.add_mo(mo, True)
            try:
                handle.commit()
                    except UcsException as e:
                        loginfo("error" + str(e))
                        res.setResult(result, PTK_INTERNALERROR, "Failed to set ip for FI")
                        return res
        """
        res.setResult(result, PTK_OKAY, "Configured successfully")
        return res

    def _release_ucsm_handler(self, handle):
        handle.logout()

    ############################# Helper functions ###########################

    def _ucsm_handler(self, ipaddress="", username="", password=""):
        try:
            handle = UcsHandle(ipaddress, username, password)
            login_state = handle.login()
            if login_state:
                return handle
            else:
                return None
        except BaseException:
            return None

    ############################# UCSSafe functions ##########################

    def _form_data(
            self,
            setup_mode='',
            cluster='',
            switchFabric='',
            ipformat='',
            virtualIP='',
            systemName='',
            adminPasswd='',
            oobIP='',
            oobNM='',
            oobGW='',
            dns1='',
            domainName='',
            pasadena='',
            pasadenasecret=''):
        data = {}
        vir_ip = []
        pri_ip = []
        pri_mask = []
        pri_gw = []
        pas = []
        dns_1 = []

        if dns1:
            dns_1 = dns1.split('.')
        else:
            for i in range(0, 4):
                dns_1.append("")

        if virtualIP:
            vir_ip = virtualIP.split('.')
        else:
            for i in range(0, 4):
                vir_ip.append("")
        if pasadena:
            pas = pasadena.split('.')
        else:
            for i in range(0, 4):
                pas.append("")
        pri_ip = oobIP.split('.')
        pri_mask = oobNM.split('.')
        pri_gw = oobGW.split('.')

        data['setup_mode'] = setup_mode
        data['hidden_init'] = "hidden_init"
        data['cluster'] = cluster
        data['ooblocalFIIP1'] = ""
        data['ooblocalFIIP2'] = ""
        data['ooblocalFIIP3'] = ""
        data['ooblocalFIIP4'] = ""
        data['ooblocalFIIPv6'] = ""
        data['switchFabric'] = switchFabric
        data['ipformat'] = ipformat
        data['virtualIP1'] = vir_ip[0]
        data['virtualIP2'] = vir_ip[1]
        data['virtualIP3'] = vir_ip[2]
        data['virtualIP4'] = vir_ip[3]
        data['yes_or_no_passwd'] = "2"
        data['systemName'] = re.sub('\-A$', '', systemName)
        data['adminPasswd'] = adminPasswd
        data['adminPasswd1'] = adminPasswd
        data['oobIP1'] = pri_ip[0]
        data['oobIP2'] = pri_ip[1]
        data['oobIP3'] = pri_ip[2]
        data['oobIP4'] = pri_ip[3]
        data['oobNM1'] = pri_mask[0]
        data['oobNM2'] = pri_mask[1]
        data['oobNM3'] = pri_mask[2]
        data['oobNM4'] = pri_mask[3]
        data['oobGW1'] = pri_gw[0]
        data['oobGW2'] = pri_gw[1]
        data['oobGW3'] = pri_gw[2]
        data['oobGW4'] = pri_gw[3]
        data['dns1'] = dns_1[0]
        data['dns2'] = dns_1[1]
        data['dns3'] = dns_1[2]
        data['dns4'] = dns_1[3]
        data['domainName'] = domainName
        data['pasadena1'] = pas[0]
        data['pasadena2'] = pas[0]
        data['pasadena3'] = pas[0]
        data['pasadena4'] = pas[0]
        data['pasadenaSecret'] = pasadenasecret
        data['virtualIPv6'] = ""
        data['yes_or_no_passwd_ipv6'] = "1"
        data['systemNameipv6'] = ""
        data['adminPasswdipv6'] = ""
        data['oobIPv6'] = ""
        data['oobPrefix'] = ""
        data['oobIPv6GW'] = ""
        data['IPv6dns'] = ""
        data['domainNameipv6'] = ""
        data['IPv6pasadena'] = ""
        data['IPv6pasadenasecret'] = ""
        data['submit'] = "Submit"
        return data
