from pure_dir.global_config import *
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.common import *
import requests
import json
from pure_dir.global_config import get_discovery_store


class FASetup:
    def __init__(self):
        pass

    def _fa_validate_ip(self, ip_list, netmask, gateway):
        res = result()
        err = []
        ipv = IpValidator()
        valid = True
        if len(ip_list) == len(set(ip_list)):
            for ip in ip_list:
                ip_val = ipvalidation(ip_list[ip])
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

    def favalidate(self, data):
        """
        Validates the details provided for FlashArray configuration

        :param data: Dictionary (model, mac, array_name, orig_ip, serial_number, ct0_ip, ct1_ip, vir0_ip, netmask, gateway, domain_name, dns, relay_host, sender_domain, ntp_server, alert_emails, timezone, organization, full_name, job_title)

        :return: Returns the validation status
        """
        res = result()
        ret = []
        ret = validate_input_data({'array_name': 'Array Name',
                                   'ct0_ip': 'Controller0 IP address',
                                   'ct1_ip': 'Controller1 IP address',
                                   'vir0_ip': 'Virtual IP address',
                                   'netmask': 'Netmask',
                                   'gateway': 'Gateway',
                                   'dns': 'DNS Server Address',
                                   'ntp_server': 'NTP Server Address',
                                   'relay_host': 'SMTP Relay Host Address',
                                   'sender_domain': 'Sender Domain',
                                   'alert_emails': 'Alert Emails',
                                   'timezone': 'Timezone',
                                   'organization': 'Organization',
                                   'full_name': 'Full Name',
                                   'job_title': 'Job Title'},
                                  data)
        if len(ret) > 0:
            res.setResult(ret, PTK_INTERNALERROR,
                          "Please fill all mandatory fields.")
            return res
        ip_list = {
            'ct0_ip': data['ct0_ip'],
            'ct1_ip': data['ct1_ip'],
            'vir0_ip': data['vir0_ip'],
            'dns': data['dns']}
        res = self._fa_validate_ip(
            ip_list, data['netmask'], data['gateway'])
        return res

    def faconfigure(self, data):
        """
        Configures the FlashArray which is in factory reset state

        :param data: Dictionary (model, mac, array_name, orig_ip, serial_number, ct0_ip, ct1_ip, vir0_ip, netmask, gateway, domain_name, dns, relay_host, sender_domain, ntp_server, alert_emails, timezone, organization, full_name, job_title)

        :return: Returns the configuration status
        """
        res = result()
        loginfo("Serial number of FlashArray is %s" % data['serial_number'])
        update_xml_element(
            get_discovery_store(),
            matching_key="mac",
            matching_value=data['mac'],
            data={
                "configured": "In-progress",
                "timestamp": str(
                    time.time())})

        request_dict = {}
        request_dict['array_name'] = data['array_name']
        request_dict['ct0.eth0'] = {
            "address": data['ct0_ip'],
            "netmask": data['netmask'],
            "gateway": data['gateway']}
        request_dict['ct1.eth0'] = {
            "address": data['ct1_ip'],
            "netmask": data['netmask'],
            "gateway": data['gateway']}
        request_dict['vir0'] = {
            "address": data['vir0_ip'],
            "netmask": data['netmask'],
            "gateway": data['gateway']}
        request_dict['dns'] = {"domain": data['domain_name'], "nameservers": [data['dns']]}
        request_dict['ntp_servers'] = [data['ntp_server']]
        request_dict['timezone'] = data['timezone']
        request_dict['eula_acceptance'] = {
            "accepted": True,
            "accepted_by": {
                "organization": data['organization'],
                "full_name": data['full_name'],
                "job_title": data['job_title']}}
        request_dict['smtp'] = {
            "sender_domain": data['sender_domain'],
            "relay_host": data['relay_host']}
        request_dict['alert_emails'] = data['alert_emails'].split(",")

        url = "http://" + data['orig_ip'] + ":8081/array-initial-config"
        r = requests.patch(url, json=request_dict)
        if r.status_code == 200:
            res.setResult(True, PTK_OKAY, "Successfully started configuring FlashArray")
        else:
            res.setResult(False, PTK_FAILED, "Failed to configure FlashArray")
        return res

    def fareconfigure(self, data, force):
        """
        Re-configures the FA  in case of failure

        :param data: Dictionary (model, mac, array_name, orig_ip, serial_number, ct0_ip, ct1_ip, vir0_ip, netmask, gateway, domain_name, dns, relay_host, sender_domain, ntp_server, alert_emails, timezone, organization, full_name, job_title)
        :param force: Confirmation before going for a reconfigure

        :return: Returns the reconfiguration status
        """
        input_dict = {
            "array_name": data['name'],
            "ct0_ip": data['ct0_ip'],
            "ct1_ip": data['ct1_ip'],
            "vir0_ip": data['vir0_ip'],
            "ipaddress": data['ipaddress'],
            "orig_ip": data['orig_ip'],
            "serial_number": data['serial_no'],
            "mac": data['mac'],
            "netmask": data['netmask'],
            "gateway": data['gateway'],
            "dns": data['dns'],
            "domain_name": data['domain_name'],
            "relay_host": data['relay_host'],
            "sender_domain": data['sender_domain'],
            "alert_emails": data['alert_emails'],
            "ntp_server": data['ntp_server'],
            "timezone": data['timezone'],
            "organization": data['organization'],
            "full_name": data['full_name'],
            "job_title": data['job_title'],
            "model": data['model'],
            "device_type": "PURE",
            "configured": "Unconfigured",
            "reachability": "",
            "validated": "1"}
        if force == 0:
            populate_lst = []
            populate_lst.append(input_dict)
            return True, json.dumps(populate_lst)
        else:
            loginfo("FA Reconfigure: Configuring FA")
            conf_status = self.faconfigure(input_dict).getStatus()
            if conf_status == PTK_OKAY:
                loginfo("FA Reconfigure: FA Configuration success")
                return True, 0
            else:
                loginfo("FA Reconfigure: FA Configuration failure")
                return False, -1
