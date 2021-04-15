import ipaddress
import subprocess

from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *


class IpValidator:

    def __init__(self):
        pass

    def subnet_calc(self):
        nw_info = network_info()
        nw_details = ipaddress.ip_network(f"{nw_info['ip']}/{nw_info['netmask']}", strict=False)
        subnet = str(nw_details.network_address)
        host_range = [str(x) for x in list(nw_details.hosts())]
        broadcast = str(nw_details.broadcast_address)
        num_addr = nw_details.num_addresses
        num_hosts = len(host_range)
        nw_with_maskbit = ipaddress.IPv4Network(nw_details.with_netmask)
        mask_bits = str(nw_with_maskbit).split('/')[1]

        subnet_info = dict(subnet=subnet, host_range=host_range, broadcast=broadcast,
                           num_addr=num_addr, num_hosts=num_hosts, nw_with_maskbit=nw_with_maskbit,
                           mask_bits=mask_bits)
        return subnet_info

    def get_ips_in_range(self):
        subnet_info = self.subnet_calc()
        return subnet_info['host_range']

    def is_ip_in_network(self, ip):
        subnet_info = self.subnet_calc()
        if ipaddress.IPv4Address(ip) in subnet_info['nw_with_maskbit']:
            return True
        return False

    def is_ip_up(self, ip):
        loginfo("Pinging IP %s" % ip)
        p = subprocess.Popen(["ping", "-q", "-c", "1", ip],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        response = p.wait()
        loginfo("IP ping response %s" % response)
        if response == 0:
            return True
        else:
            return False

    def is_kvm_ip_up(self, ip, result):
        loginfo("Pinging IP %s" % ip)
        p = subprocess.Popen(["ping", "-q", "-c", "1", ip],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        response = p.wait()
        loginfo("IP ping response %s" % response)
        if response == 0:
            result[ip] = True
        else:
            result[ip] = False

    def validate_ip(self, ip):
        if self.is_ip_in_network(ip):
            isUp = self.is_ip_up(ip)
            if isUp:
                # Returning Network status, Ip reachability
                return True, True
            else:
                return True, False
        return False, False
