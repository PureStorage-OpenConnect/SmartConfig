import netaddr
import subprocess

from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *


class IpValidator:

    def __init__(self):
        pass

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
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=False)
        response = p.wait()
        loginfo("IP ping response %s" % response)
        if response == 0:
            result[ip] = True
        else:
            result[ip]= False

    def netmask_range(self, netmask):
        netmask_range = sum([bin(int(x)).count("1")
                             for x in netmask.split(".")])
        return netmask_range

    def ip_range(self, ip, netmask, gateway):
        network_ip = ""
        ip_lt = gateway.split(".")[:-1]
        for gt in ip_lt:
            network_ip += gt + "."
        netmask_range = self.netmask_range(netmask)
        for ipaddr in netaddr.IPNetwork(str(network_ip) + "0/" + str(netmask_range)):
            if str(ipaddr) == ip:
                return True
        return False

    def get_ips_in_range(self):
        network_ip = ""
        nw_info = network_info()
        ip_lt = nw_info['gateway'].split(".")[:-1]
        for gt in ip_lt:
            network_ip += gt + "."
        netmask_range = self.netmask_range(nw_info['netmask'])
        ip_range = netaddr.IPNetwork(
            str(network_ip) + "0/" + str(netmask_range))
        ip_list = list(netaddr.IPNetwork(ip_range))
        return ip_list

    def validate_network(self, ip, netmask, gateway):
        details = verify_network_info()
        for info in details:
            if info['netmask'] == netmask and info['gateway'] == gateway:
                return self.ip_range(ip, netmask, gateway)
        return False

    def validate_ip(self, ip, netmask, gateway):
        if self.validate_network(ip, netmask, gateway):
            isUp = self.is_ip_up(ip)
            if isUp:
                # Returning Network status, Ip reachability
                return True, True
            else:
                return True, False

        return False, False
