#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :flashblade_setup.py
# description     :FlashBlade ZTP 
# author          :Guruprasad
# version         :1.0
###################################################################

import requests
import json
import urllib3

from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.common import *
from pure_dir.global_config import get_discovery_store
from pure_dir.services.utils.miscellaneous import get_xml_element, get_xml_childelements
from pure_dir.global_config import get_settings_file
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_global_wf_config_file

settings = get_settings_file()
api_version = '1.8.1'
sc_subnet_name = 'sc-subnet'

class FBSetup:
    def __init__(self, ipaddress=''):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.base_url = 'https://%s/api' % ipaddress
        self.resource_url = self.base_url + '/' + api_version
        self.headers = {}
        pass


    def fbvalidate(self, data):
        """
        Validates the details provided for FlashBlade configuration

        :param data: Dictionary (model, mac, blade_name, orig_ip, serial_number, fm1_ip, fm2_ip, vir0_ip, network, gateway, dns, relay_host, sender_domain, ntp_server, alert_emails)

        :return: Returns the validation status
        """
        res = result()
        ret = []
        ret = validate_input_data({'blade_name': 'FlashBlade Name',
                                   'fm1_ip': 'Flash Module 1 IP address',
                                   'fm2_ip': 'Flash Module 2 IP address',
                                   'vir0_ip': 'Virtual IP address',
                                   'network': 'Network Prefix',
                                   'gateway': 'Gateway',
                                   'dns': 'DNS Server Address',
                                   'ntp_server': 'NTP Server Address',
                                   'relay_host': 'SMTP Relay Host Address',
                                   'sender_domain': 'Sender Domain',
                                   'alert_emails': 'Alert Emails'},
                                  data)
        if len(ret) > 0:
            res.setResult(ret, PTK_INTERNALERROR,
                          "Please fill all mandatory fields.")
            return res
        ip_list = {
            'fm1_ip': data['fm1_ip'],
            'fm2_ip': data['fm2_ip'],
            'vir0_ip': data['vir0_ip'],
            'dns': data['dns']}
        res = self._fb_validate_ip(ip_list)
        return res
    

    def fbconfigure(self, data):
        """
        Configures the FlashBlade which is in factory reset state

        :param data: Dictionary (model, mac, blade_name, orig_ip, serial_number, fm1_ip, fm2_ip, vir0_ip, netmask, gateway, domain_name, dns, relay_host, sender_domain, ntp_server, alert_emails, timezone)

        :return: Returns the configuration status
        """
        res = result()
        loginfo("Serial number of FB is %s" % data['serial_number'])
        update_xml_element(
            get_discovery_store(),
            matching_key="mac",
            matching_value=data['mac'],
            data={
                "configured": "In-progress",
                "timestamp": str(
                    time.time())})

        request_dict = {'orig_ip': data['orig_ip'], 
                        'name': data['blade_name'], 
                        'ntp_servers': data['ntp_server'].split(','), 
                        'timezone': data['timezone'], 
                        'domain_name': data['domain_name'], 
                        'dns': data['dns'].split(','), 
                        'sender_domain': data['sender_domain'], 
                        'relay_host': data['relay_host'], 
                        'alert_emails': data['alert_emails'].split(','), 
                        'network': data['network'], 
                        'gateway': data['gateway'], 
                        'interfaces': [{'name':'fm1.admin0', 'address':data['fm1_ip']}, 
                                       {'name':'fm2.admin0', 'address':data['fm2_ip']}, 
                                       {'name':'vir0', 'address':data['vir0_ip']}]
                       }

        loginfo("Triggering FB ZTP...")
        status, msg = self.fb_ztp(request_dict)
        if not status:
            loginfo("FB ZTP failed")
            update_xml_element(
                get_discovery_store(),
                matching_key="mac",
                matching_value=data['mac'],
                data={
                    "configured": "Re-validate",
                    "reval_msg": msg})
        else:
            loginfo("FB ZTP success")
            res.setResult(True, PTK_OKAY, "Successfully configured FlashBlade")
            return res
        return


    def fbreconfigure(self, data, force):
        """
        Re-configures the FlashBlade in case of failure

        :param data: Dictionary (model, mac, blade_name, orig_ip, serial_number, fm1_ip, fm2_ip, vir0_ip, netmask, gateway, domain_name, dns, relay_host, sender_domain, ntp_server, alert_emails, timezone)

        :param force: Confirmation before going for a reconfigure

        :return: Returns the reconfiguration status
        """
        # To fetch timezone value from globals
        status, details = get_xml_element(settings, "stacktype")
        if status:
            status, global_data = get_xml_childelements(
                get_global_wf_config_file(), 'htype', 'input', [
                    'name', 'value'], 'stacktype', details[0]['stacktype'])
            if not status:
                res.setResult(False, PTK_INTERNALERROR, _("PDT_FAILED_MSG"))

        input_dict = {
            "blade_name": data['name'],
            "fm1_ip": data['fm1_ip'],
            "fm2_ip": data['fm2_ip'],
            "vir0_ip": data['vir0_ip'],
            "ipaddress": data['ipaddress'],
            "orig_ip": data['orig_ip'],
            "serial_number": data['serial_no'],
            "mac": data['mac'],
            "network": data['network'],
            "netmask": data['netmask'],
            "gateway": data['gateway'],
            "dns": data['dns'],
            "domain_name": data['domain_name'],
            "relay_host": data['relay_host'],
            "sender_domain": data['sender_domain'],
            "alert_emails": data['alert_emails'],
            "ntp_server": data['ntp_server'],
            "timezone": [
                config["value"] for config in global_data if config.get("name") == "zone"][0],
            "model": data['model'],
            "device_type": "FlashBlade",
            "configured": "Unconfigured",
            "reachability": "",
            "validated": "1"}
        if force == 0:
            populate_lst = []
            populate_lst.append(input_dict)
            return True, json.dumps(populate_lst)
        else:
            loginfo("FlashBlade Reconfigure: Configuring FB...")
            threading.Thread(target=self.fbconfigure,
                                     args=(input_dict,)).start()
            loginfo("FlashBlade Reconfigure: FB Configuration started successfully")
            return True, 0


    def fb_ztp(self, data):
        try:
            loginfo("Creating FB session token....")
            ret = self.create_session_token()
            if ret is None:
                msg = "FlashBlade configuration failed in creating session token"
                loginfo("Failed to create FB session token")
                return False, msg

            loginfo("Configuring FB hostname, ntp and timezone......")
            arrays_body = {'name':data['name'], 'ntp_servers':data['ntp_servers'], 'time_zone':data['timezone']}
            ret = self.set_fb_hostname_ntp_timezone(arrays_body)
            if ret is None:
                msg = "FlashBlade configuration failed in configuring hostname, ntp and timezone"
                loginfo("Failed to set FB hostname, NTP and Timezone")
                return False, msg

            loginfo("Configuring FB dns....")
            dns_body = {'domain':data['domain_name'], 'nameservers':data['dns']}
            ret = self.set_fb_dns(dns_body)
            if ret is None:
                msg = "FlashBlade configuration failed in configuring dns"
                loginfo("Failed to set FB dns")
                return False, msg

            loginfo("Configuring FB smtp....")
            smtp_body = {'relay_host':data['relay_host'], 'sender_domain':data['sender_domain']}
            ret = self.set_fb_smtp(smtp_body)
            if ret is None:
                msg = "FlashBlade configuration failed in configuring smtp"
                loginfo("Failed to set FB smtp")
                return False, msg

            loginfo("Configuring FB alert watchers....")
            alert_body = data['alert_emails']
            ret = self.set_fb_alert_watchers(alert_body)
            if ret is None:
                msg = "FlashBlade configuration failed in configuring alert watchers"
                loginfo("Failed to set FB alert watchers")
                return False, msg

            loginfo("Configuring FB subnet....")
            subnet_body = {'prefix':data['network'], 'gateway':data['gateway'], 'interfaces':data['interfaces'], 'link_aggregation_group': {'name': 'uplink', 'resource_type': 'link-aggregation-groups'}, 'out_of_band':True}
            ret = self.set_fb_subnet(subnet_body)
            if ret is None:
                msg = "FlashBlade configuration failed in configuring subnet"
                loginfo("Failed to create FB subnet")
                return False, msg

            loginfo("Configuring FB network interfaces....")
            interfaces_body = data['interfaces']
            ret = self.set_fb_network_interfaces(interfaces_body)
            if ret is None:
                loginfo("Failed to configure FB network interface")
                loginfo("Reverting back the FlashBlade subnet creation and network interface configuration")
                status = self.delete_fb_subnet(sc_subnet_name, interfaces_body)
                if status is False:
                    loginfo("Failed to revert back the FlashBlade subnet creation and network interface configuration")
                msg = "FlashBlade configuration failed in configuring network interfaces"
                return False, msg

            loginfo("Validating FB configuration....")
            ret = self.validate_configuration()
            if ret is False:
                msg = "FlashBlade configuration validation failed"
                loginfo("Failed to validate FB configuration")
                return False, msg
        
            loginfo("Finalizing FB configuration....")
            ret = self.finalize_configuration()
            if ret is False:
                msg = "FlashBlade configuration finalization failed"
                loginfo("Failed to finalize FB configuration")
                return False, msg
       
            return True, "Success"
 
        except Exception as e:
            msg = "Exception in configuring FlashBlade: " + str(e)
            loginfo("Exception in configuring FB")
            return False, msg


    def _fb_validate_ip(self, ip_list):
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
                    continue

                if ip != 'dns':
                    network_reach, ip_reach = ipv.validate_ip(ip_list[ip])
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


    def create_session_token(self):
        try:
            res = requests.post(self.base_url + '/login', headers={'api-token':'PURESETUP'}, verify=False)
            if res.status_code == 200:
                session_token = res.headers['x-auth-token']
                loginfo('FB session token is %s' % session_token)
                self.headers = {'x-auth-token':session_token}
                return session_token
            else:
                loginfo("Unable to get the FB session token. %s: %s" % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in creating FB session token: %s" % str(e))
            return None


    def logout_session(self):
        try:
            res = requests.post(self.base_url + '/logout', headers=self.headers, verify=False)
            if res.status_code == 200:
                loginfo('FB session logged out')
                return True
            else:
                loginfo('Unable to logout FB session. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in destroying session: %s" % str(e))
            return None


    def get_fb_info(self):
        try:
            res = requests.get(self.resource_url + '/arrays', headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_array_info = res.json()['items'][0]
                loginfo('FB array details: %s' % fb_array_info)
                return fb_array_info
            else:
                loginfo('Unable to get FB array info. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in getting FB array info: %s" % str(e))
            return None


    def get_fb_alert_watchers(self):
        try:
            res = requests.get(self.resource_url + '/alert-watchers', headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_alert_watchers = res.json()['items']
                loginfo('FB alert watchers: %s' % fb_alert_watchers)
                return fb_alert_watchers
            else:
                loginfo('Unable to get FB alert watchers. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in getting FB alert watchers: %s" % str(e))
            return None


    def get_fb_subnets(self):
        try:
            res = requests.get(self.resource_url + '/subnets', headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_subnets = res.json()['items']
                loginfo('FB subnets: %s' % fb_subnets)
                return fb_subnets
            else:
                loginfo('Unable to get FB subnets. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in getting FB subnets: %s" % str(e))
            return None


    def set_fb_hostname_ntp_timezone(self, data):
        try:
            res = requests.patch(self.resource_url + '/arrays', json=data, headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_array_info = res.json()['items'][0]
                loginfo('FB details after setting hostname, NTP and timezone: %s' % fb_array_info)
                return fb_array_info
            else:
                loginfo('Unable to set the FB hostname, NTP and timezone configuration. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in setting FB hostname, NTP and timezone configuration: %s" % str(e))
            return None


    def set_fb_dns(self, data):
        try:
            res = requests.patch(self.resource_url + '/dns', json=data, headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_dns = res.json()['items'][0]
                loginfo('FB DNS: %s' % fb_dns)
                return fb_dns
            else:
                loginfo('Unable to set the FB DNS configuration. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in setting FB DNS: %s" % str(e))
            return None


    def set_fb_smtp(self, data):
        try:
            res = requests.patch(self.resource_url + '/smtp', json=data, headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_smtp = res.json()['items'][0]
                loginfo('FB SMTP: %s' % fb_smtp)
                return fb_smtp
            else:
                loginfo('Unable to set the FB SMTP configuration. %s: %s' % (res.status_code, res.content))
                return None
        except Exception as e:
            loginfo("Exception in setting FB SMTP: %s" % str(e))
            return None


    def set_fb_alert_watchers(self, data):
        try:
            fb_alert_watchers_info = self.get_fb_alert_watchers()
            fb_alert_watchers = [email['name'] for email in fb_alert_watchers_info]
            loginfo('The current email list is %s' % fb_alert_watchers)
            for email in data:
                if email not in fb_alert_watchers:
                    res = requests.post(self.resource_url + '/alert-watchers', params={'names':email}, headers=self.headers, verify=False)
                    if res.status_code == 200:
                        fb_alert = res.json()['items'][0]
                        loginfo('FB alert_watcher added: %s' % fb_alert)
                    else:
                        loginfo('Unable to set the FB alert watcher %s. %s: %s' % (email, res.status_code, res.content))
                        return None
                else:
                    loginfo('FB alert watcher \'%s\' already added' % email)
            return data
        except Exception as e:
            loginfo("Exception in setting FB alert watchers: %s" % str(e))
            return None


    def set_fb_subnet(self, data):
        try:
            fb_subnets_info = self.get_fb_subnets()
            fb_subnets = [subnet['name'] for subnet in fb_subnets_info]
            if sc_subnet_name in fb_subnets:
                loginfo('A FB subnet with a name \'%s\' already exists' %  sc_subnet_name)
                status = self.delete_fb_subnet(sc_subnet_name, data['interfaces'])
                if status is False:
                    return None

            res = requests.post(self.resource_url + '/subnets', json={k:v for k,v in data.items() if k != 'interfaces'}, params={'names':sc_subnet_name}, headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_subnet = res.json()['items'][0]
                loginfo('FB subnet details: %s' % fb_subnet)
                return fb_subnet
            else:
                loginfo('Unable to set the FB subnet configuration. %s: %s' % (res.status_code, res.content))
                return None
            
        except Exception as e:
            loginfo("Exception in creating FB subnet: %s" % str(e))
            return None


    def set_fb_network_interfaces(self, data):
        try:
            for intf in data:
                res = requests.patch(self.resource_url + '/network-interfaces', params={'names':intf['name']}, json={'address':intf['address']}, headers=self.headers, verify=False)
                if res.status_code == 200:
                    loginfo('Configured the FB network interface %s with ip address %s' % (intf['name'], intf['address']))
                else:
                    loginfo('Unable to configure the FB network interface configuration for %s. %s: %s' % (intf['name'], res.status_code, res.content))
                    return None
            return data
        except Exception as e:
            loginfo("Exception in configuring FB network interfaces: %s" % str(e))
            return None


    def delete_fb_subnet(self, name, interfaces):
        try:
            fb_sc_intf_list = [intf['name'] for intf in interfaces]
            loginfo('Clearing the existing FB subnet required disabling the interfaces in the subnet')
            for intf in fb_sc_intf_list:
                res = requests.patch(self.resource_url + '/network-interfaces', data={'enabled':False}, params={'names':intf}, headers=self.headers, verify=False)
                if res.status_code == 200:
                    loginfo('Disabled the FB interface \'%s\'' % intf)
                else:
                    loginfo('Unable to bring down the FB interface \'%s\'. %s: %s' % (intf, res.status_code, res.content))
                    return False

            loginfo('Clearing the existing FB subnet')
            res = requests.delete(self.resource_url + '/subnets', params={'names':name}, headers=self.headers, verify=False)
            if res.status_code == 200:
                loginfo('Cleared out the existing FB subnet')
            else:
                loginfo('Unable to clear out the existing FB subnet configuration. %s: %s' % (res.status_code, res.content))
                return True
        except Exception as e:
            loginfo("Exception in deleting FB subnet: %s" % str(e))
            return False


    def validate_configuration(self):
        try:
            res = requests.get(self.resource_url + '/setup/validation', headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_conf_params = res.json()['items'][0]
                loginfo("FB configuration validation params: %s" % fb_conf_params)
                if all(val is True for val in fb_conf_params.values()):
                    loginfo("FB configuration validated successfully")
                    return True
                else:
                    loginfo("There is some problem in any of the above configurations. Please check.")
                    return False
            else:
                loginfo('Unable to validate the above FB configuration. %s: %s' % (res.status_code, res.content))
                return False
        except Exception as e:
            loginfo("Exception in validating FB configuration: %s" % str(e))
            return False


    def finalize_configuration(self):
        try:
            res = requests.patch(self.resource_url + '/setup/finalization', json={'setup_completed':True}, headers=self.headers, verify=False)
            if res.status_code == 200:
                fb_conf_params = res.json()['items'][0]
                loginfo("FB configuration finalization params: %s" % fb_conf_params)
                if all(val is True for val in fb_conf_params.values()):
                    loginfo("FB ZTP configuration successfully applied. System goes for a reboot now.")
                    return True
                else:
                    loginfo("There is some problem in applying the ZTP configuration. Please check.")
                    return False
            else:
                loginfo('Unable to validate the above FB configuration. %s: %s' % (res.status_code, res.content))
                return False
        except Exception as e:
            loginfo("Exception in finalizing FB configuration: %s" % str(e))
            return False
