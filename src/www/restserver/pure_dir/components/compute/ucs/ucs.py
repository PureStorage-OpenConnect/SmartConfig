import ucsmsdk
import os
import string
import threading
import requests
import time
import re
import json
from requests_toolbelt import MultipartEncoder
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.fabric.FabricEthLanEp import FabricEthLanEp
from ucsmsdk.mometa.fabric.FabricDceSwSrvEp import FabricDceSwSrvEp
from ucsmsdk.mometa.fabric.FabricFcoeSanEp import FabricFcoeSanEp
from ucsmsdk.mometa.fabric.FabricFcoeEstcEp import FabricFcoeEstcEp
from ucsmsdk.mometa.fabric.FabricEthEstcEp import FabricEthEstcEp
from pure_dir.services.utils.miscellaneous import *
# from pure_dir.services.apps.pdt.core.discovery import *
# from pure_dir.services.apps.pdt.core.orchestration.orchestration_task_data import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.common import *
from pure_dir.components.compute.ucs.ucs_upgrade import *

from isc_dhcp_leases import IscDhcpLeases
from xml.dom.minidom import Document, parse
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

ucsm_credentials_store = "/mnt/system/pure_dir/pdt/ucsmlogin.xml"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UCSManager:
    dhcp_lease_file = '/var/lib/dhcpd/dhcpd.leases'

    def __init__(self):
        pass

    def _dhcpdiscovery(self):
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
        res = result()
        ucsm_list = []
        if os.path.exists(static_discovery_store) is True:
            doc = parse_xml(static_discovery_store)
            for subelement in doc.getElementsByTagName("device"):
                if subelement.getAttribute("device_type") == "UCSM" and subelement.getAttribute(
                        "leadership") != "subordinate":
                    details = {}
                    details['name'] = subelement.getAttribute("name")
                    details['mac'] = subelement.getAttribute("mac")
                    ucsm_list.append(details)

        res.setResult(ucsm_list, PTK_OKAY, "success")
        return res

    def _is_ucsm(self, ip, dev_type, dev_status):
        url = "https://" + ip + "/cgi-bin/initial_setup_new.cgi"
        try:
            r = requests.get(url, timeout=5, verify=False)
            if r.status_code == 200:
                if "already configured" in r.content:
                    with lock:
                        dev_type[ip] = 'UCSM'
                        dev_status[ip] = True
                else:
                    with lock:
                        dev_type[ip] = 'UCSM'
                        dev_status[ip] = False
            else:
                status = self._is_ucsm_simulator(ip)
                if status:
                    with lock:
                        dev_type[ip] = 'UCSM'
                        dev_status[ip] = True
                else:
                    with lock:
                        dev_type[ip] = 'Unknown'
                        dev_status[ip] = False
        except BaseException:
            status = self._is_ucsm_simulator(ip)
            if status:
                with lock:
                    dev_type[ip] = 'UCSM'
                    dev_status[ip] = True
            else:
                with lock:
                    dev_type[ip] = 'Unknown'
                    dev_status[ip] = False

    def requests_retry_session(self,
                               retries=100,
                               backoff_factor=0.3,
                               status_forcelist=(500, 502, 504),
                               session=None,
                               ):
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
        #    session.mount('https://', adapter)
        return session

    def is_ucsm_up(self, ip):
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
            except:
                loginfo("Fabric module " + ip + " is down")
                return "ucs down"
            else:
                break

    def verify_ucsm_accessible(self, ip):
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
            loginfo('Took'+ str (t1 - t0) + 'seconds')

    def ucsmdiscovery(self):
        disc_list = []
        res = result()
        dhcp_client_list = parseResult(self._dhcpdiscovery())
        thread = {}
        deviceinfolst = {}
        for d_client in dhcp_client_list['data']:

            thread[d_client.ip_address] = threading.Thread(
                target=self._is_ucsm, args=(d_client.ip_address, deviceinfolst))
            thread[d_client.ip_address].start()

        for d_client in dhcp_client_list['data']:
            thread[d_client.ip_address].join()

        for d_client in dhcp_client_list['data']:
            if deviceinfolst[d_client.ip_address] == 'UCSM':
                disc_list.append({"ip_address": d_client.ip_address,
                                  "device_type": "Fabric Interconnect",
                                  "device_model": "Cisco UCS-FI-6248UP",
                                  "mac_address": d_client.mac_address})
        res.setResult(disc_list, PTK_OKAY, "success")
        return res

    def ucsmlogin(self, ipaddress, username, password):
        res = result()
        handle = self._ucsm_handler(ipaddress, username, password)
        if handle is not None:
            self._save_ucsm_login_details(ipaddress, username, password)
            self._release_ucsm_handler(handle)
            res.setResult("", PTK_OKAY, "success")
        else:
            res.setResult("", PTK_INTERNALERROR, "failure")
        return res

    def ucsmchassisblades(self):
        blades_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            blades = handle.query_classid("ComputeBlade")
            for blade in blades:
                eq = string.split(blade.server_id, '/')
                blade_ent = {
                    'chassis': eq[0],
                    'blade': eq[1],
                    'dn': blade.dn,
                    'oper_state': blade.oper_state}
                blades_list.append(blade_ent)
        self._release_ucsm_handler(handle)
        res.setResult(blades_list, PTK_OKAY, "success")
        return res

    def ucsmrackunits(self):
        racks_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            racks = handle.query_classid("ComputeRackUnit")
            for rack in racks:
                rack_dict = {
                    'server_id': rack.server_id,
                    'dn': rack.dn,
                    'vendor': rack.vendor,
                    'num_of_cpus': rack.num_of_cpus,
                    'total_memory': rack.total_memory,
                    'available_memory': rack.available_memory,
                    'num_of_adaptors': rack.num_of_adaptors,
                    'operability': rack.operability,
                    'availability': rack.availability,
                    'num_of_fc_host_ifs': rack.num_of_fc_host_ifs,
                    'serial': rack.serial,
                    'model': rack.model,
                    'uuid': rack.uuid,
                    'oper_power': rack.oper_power,
                    'num_of_cores': rack.num_of_cores,
                    'num_of_cores_enabled': rack.num_of_cores_enabled,
                    'usr_lbl': rack.usr_lbl,
                    'check_point': rack.check_point,
                    'discovery': rack.discovery,
                    'association': rack.association,
                    'oper_state': rack.oper_state}
                racks_list.append(rack_dict)
        self._release_ucsm_handler(handle)
        res.setResult(racks_list, PTK_OKAY, "success")
        return res

    def ucsmrackunitinfo(self, serverid):
        rack_dict = {}
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            racks = handle.query_classid("ComputeRackUnit")
            for rack in racks:
                if rack.server_id == serverid:
                    rack_dict = {
                        'server_id': rack.server_id,
                        'dn': rack.dn,
                        'vendor': rack.vendor,
                        'num_of_cpus': rack.num_of_cpus,
                        'total_memory': rack.total_memory,
                        'available_memory': rack.available_memory,
                        'num_of_adaptors': rack.num_of_adaptors,
                        'operability': rack.operability,
                        'availability': rack.availability,
                        'num_of_fc_host_ifs': rack.num_of_fc_host_ifs,
                        'serial': rack.serial,
                        'model': rack.model,
                        'uuid': rack.uuid,
                        'oper_power': rack.oper_power,
                        'num_of_cores': rack.num_of_cores,
                        'num_of_cores_enabled': rack.num_of_cores_enabled,
                        'usr_lbl': rack.usr_lbl,
                        'check_point': rack.check_point,
                        'discovery': rack.discovery,
                        'association': rack.association,
                        'oper_state': rack.oper_state}
        self._release_ucsm_handler(handle)
        res.setResult(rack_dict, PTK_OKAY, "success")
        return res

    def ucsmservers(self):
        servers_list = []
        res = result()
        blades = self.ucsmchassisblades()
        rackservers = self.ucsmrackunits()
        for blade in blades.getResult():
            server_dict = {
                'dn': blade['dn'],
                'oper_state': blade['oper_state']}
            servers_list.append(server_dict)
        for rackserver in rackservers.getResult():
            rack_dict = {
                'dn': rackserver['dn'],
                'oper_state': rackserver['oper_state']}
            servers_list.append(rack_dict)
        res.setResult(servers_list, PTK_OKAY, "success")
        return res

    def ucsmfexs(self):
        fexs_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            fexs = handle.query_classid("equipmentFex")
            for fex in fexs:
                fex_dict = {
                    'id': fex.id,
                    'dn': fex.dn,
                    'oper_state': fex.oper_state,
                    'model': fex.model,
                    'vendor': fex.vendor,
                    'serial': fex.serial,
                    'revision': fex.revision}
                fexs_list.append(fex_dict)
        self._release_ucsm_handler(handle)
        res.setResult(fexs_list, PTK_OKAY, "success")
        return res

    def ucsmfexinfo(self, fexid):
        fex_dict = {}
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            fexs = handle.query_classid("equipmentFex")
            for fex in fexs:
                if fex.id == fexid:
                    fex_dict = {
                        'id': fex.id,
                        'dn': fex.dn,
                        'oper_state': fex.oper_state,
                        'model': fex.model,
                        'vendor': fex.vendor,
                        'serial': fex.serial,
                        'revision': fex.revision}
        self._release_ucsm_handler(handle)
        res.setResult(fex_dict, PTK_OKAY, "success")
        return res

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

    def ucsm_version(self, ip, username, password):
        handle = self._ucsm_handler(
            ipaddress=ip, username=username, password=password)
        if handle is not None:
            version_info = handle.query_dn("sys/mgmt/fw-system")
            return version_info.version
        return None

    def fabric_cluster_info(self, ip, username, password):
        handle = self._ucsm_handler(
            ipaddress=ip, username=username, password=password)
        cluster_info = []
        if handle is not None:
            fabrics = handle.query_classid("networkelement")
            mo = handle.query_dn("sys")
            for fabric in fabrics:
                switch = {}
                switch['mac_addr'] = fabric.oob_if_mac
                switch['model'] = fabric.model
                switch['serial_no'] = fabric.serial
                switch['name'] = mo.name
                switch['ip'] = fabric.oob_if_ip
                switch['version'] = self.ucsm_version(ip, username, password)
                cluster_info.append(switch)
        return cluster_info

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

    def ucsmfabricinterconnects(self):
        ''' Returns detailed information on fabric Interconnects'''
        res = result()
        fabrics_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            fabrics = handle.query_classid("networkelement")
            for fabric in fabrics:
                mgmtentities = handle.query_classid("MgmtEntity")
                for mgmtentity in mgmtentities:
                    if fabric.id == mgmtentity.id:
                        leadership = mgmtentity.leadership
                fabrics_dict = {
                    'id': fabric.id,
                    'dn': fabric.dn,
                    'rn': fabric.rn,
                    'total_memory': fabric.total_memory,
                    'expected_memory': fabric.expected_memory,
                    'model': fabric.model,
                    'serial': fabric.serial,
                    'vendor': fabric.vendor,
                    'revision': fabric.revision,
                    'operability': fabric.operability,
                    'thermal': fabric.thermal,
                    'admin_evac_state': fabric.admin_evac_state,
                    'oper_evac_state': fabric.oper_evac_state,
                    'oob_if_ip': fabric.oob_if_ip,
                    'oob_if_gw': fabric.oob_if_gw,
                    'oob_if_mask': fabric.oob_if_mask,
                    'leadership': leadership,
                    'displayname': "Fabric Interconnect " + fabric.id + "(" + leadership + ")"}
                fabrics_list.append(fabrics_dict)
        self._release_ucsm_handler(handle)
        res.setResult(fabrics_list, PTK_OKAY, "success")
        return res

    def getfisuggestion(self, default):
        ''' Minimal information of FI'''
        ret = self.ucsmfabricinterconnects()

        fis = ret.getResult()
        res = result()
        filist = []
        for fi in fis:
            if default == fi['leadership']:
                filist.append(
                    {
                        'id': fi['id'],
                        'selected:': '1',
                        'name': "Fabric Interconnect " + fi['id'] + "(" + fi['leadership'] + ")"})
            else:
                filist.append(
                    {
                        'id': fi['id'],
                        'selected:': '0',
                        'name': "Fabric Interconnect " + fi['id'] + "(" + fi['leadership'] + ")"})

        res.setResult(filist, PTK_OKAY, "success")
        return res

    def ucsmfabricinterconnectinfo(self, fi_id):
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        res = result()
        fabrics_dict = []
        if handle is not None:
            fabrics = handle.query_classid("networkelement")
            for fabric in fabrics:
                if fi_id == fabric.id:
                    mgmtentities = handle.query_classid("MgmtEntity")
                    for mgmtentity in mgmtentities:
                        if fabric.id == mgmtentity.id:
                            leadership = mgmtentity.leadership
                    fabrics_dict = [{'id': fabric.id,
                                     'dn': fabric.dn,
                                     'rn': fabric.rn,
                                     'total_memory': fabric.total_memory,
                                     'expected_memory': fabric.expected_memory,
                                     'model': fabric.model,
                                     'serial': fabric.serial,
                                     'vendor': fabric.vendor,
                                     'revision': fabric.revision,
                                     'operability': fabric.operability,
                                     'thermal': fabric.thermal,
                                     'admin_evac_state': fabric.admin_evac_state,
                                     'oper_evac_state': fabric.oper_evac_state,
                                     'oob_if_ip': fabric.oob_if_ip,
                                     'oob_if_gw': fabric.oob_if_gw,
                                     'oob_if_mask': fabric.oob_if_mask,
                                     'leadership': leadership}]
        self._release_ucsm_handler(handle)
        res.setResult(fabrics_dict, PTK_OKAY, "success")
        return res

    def _ucsm_handler(self, ipaddress="", username="", password=""):
        try:
            if not ipaddress:
                doc = parse(ucsm_credentials_store)
                ipaddress = doc.childNodes[0].getAttribute("ipaddress")
                username = doc.childNodes[0].getAttribute("username")
                password = doc.childNodes[0].getAttribute("password")
                doc.unlink()
            handle = UcsHandle(ipaddress, username, password)
            login_state = handle.login()
            if login_state:
                return handle
            else:
                return None
        except BaseException:
            return None

    def _save_ucsm_login_details(self, ipaddress, username, password):
        if os.path.exists(ucsm_credentials_store) == False:
            o = open(ucsm_credentials_store, "w")
            doc = Document()
            roottag = doc.createElement("ucsmuser")
            roottag.setAttribute("ipaddress", ipaddress)
            roottag.setAttribute("username", username)
            roottag.setAttribute("password", password)
            doc.appendChild(roottag)
            o.write(doc.toprettyxml(indent=""))
            o.close()
        else:
            doc = parse(ucsm_credentials_store)
            # users = doc.documentElement.getElementsByTagName("ucsmuser")
            doc.childNodes[0].setAttribute("ipaddress", ipaddress)
            doc.childNodes[0].setAttribute("username", username)
            doc.childNodes[0].setAttribute("password", password)
            o = open(ucsm_credentials_store, "w")
            o.write(doc.toprettyxml(indent=""))
            o.close()
            doc.unlink()

    def ucsmchassis(self):
        chassis_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            chassislist = handle.query_classid("EquipmentChassis")
            for chassis in chassislist:
                chassis_ent = {
                    'chassisname': chassis.rn,
                    'availability': chassis.availability,
                    'id': chassis.id}
                chassis_list.append(chassis_ent)
        self._release_ucsm_handler(handle)
        res.setResult(chassis_list, PTK_OKAY, "success")

        return res

    def ucsmchassisinfo(self, chassisId):
        chassis_info = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            info = handle.query_classid("EquipmentChassis")
            for chassis in info:
                if chassisId == chassis.id:
                    info_ent = {
                        'chassisname': chassis.rn,
                        'id': chassis.id,
                        'discovery': chassis.discovery,
                        'availability': chassis.availability,
                        'product_name': chassis.model,
                        'vendor': chassis.vendor,
                        'PID': chassis.model,
                        'revision': chassis.revision,
                        'serial': chassis.serial,
                        'operable_status': chassis.operability}
                    chassis_info.append(info_ent)
        self._release_ucsm_handler(handle)
        res.setResult(chassis_info, PTK_OKAY, "success")
        return res

    def ucsmethernetports(self, fid='', port_type=''):
        port_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            if fid:
                switch_id = 'sys/switch-' + fid
            else:

                filist = parseResult(self.ucsmfabricinterconnects())
                for fi in filist['data']:
                    if fi['leadership'] == "primary":
                        switch_id = "sys/switch-" + fi['id']
            ports_dn = switch_id + "/slot-1"
            ports = handle.query_dn(ports_dn)
            # for i in range(7, int(num_ports)+1):
            # port_dn = switch_id + "/slot-1/switch-ether/port-" + str(i)
            ports_list_obj = handle.query_children(in_mo=ports)
            for port in ports_list_obj:
                if port.if_role == "unknown":
                    port_if_role = "unconfigured"
                else:
                    port_if_role = port.if_role
                if port_type:
                    if port_if_role == port_type:
                        if port_if_role == port_type:
                            port_ent = {
                                'pid': port.port_id,
                                'if_role': port_if_role,
                                'oper_state': port.oper_state,
                                'admin_state': port.admin_state}
                else:
                    port_ent = {
                        'pid': port.port_id,
                        'if_role': port_if_role,
                        'oper_state': port.oper_state,
                        'admin_state': port.admin_state}
                port_list.append(port_ent)
        self._release_ucsm_handler(handle)
        res.setResult(port_list, PTK_OKAY, "success")
        return res

    def ucsmethernetportconfig(self, fid, plist, ptype):
        res = result()
        ret = ""
        ptype_list = [
            "server",
            "network",
            "fcoe-uplink",
            "fcoe-storage",
            "appliance"]
        ptype_dn = [
            "fabric/server/sw-",
            "fabric/lan/",
            "fabric/san/",
            "fabric/fc-estc/",
            "fabric/eth-estc/"]
        if ptype in ptype_list:
            port_dn = ptype_dn[ptype_list.index(ptype)]
        else:
            ret = "Invalid port type"

        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            for pid in plist:
                pdn = port_dn + fid
                if ptype == "server":
                    mo = FabricDceSwSrvEp(
                        parent_mo_or_dn=pdn,
                        name="",
                        auto_negotiate="yes",
                        usr_lbl="",
                        slot_id="1",
                        admin_state="enabled",
                        port_id=str(pid))
                elif ptype == "network":
                    mo = FabricEthLanEp(
                        parent_mo_or_dn=pdn,
                        eth_link_profile_name="default",
                        name="",
                        flow_ctrl_policy="default",
                        admin_speed="10gbps",
                        auto_negotiate="yes",
                        usr_lbl="",
                        slot_id="1",
                        admin_state="enabled",
                        port_id=str(pid))
                elif ptype == "fcoe-uplink":
                    mo = FabricFcoeSanEp(
                        parent_mo_or_dn=pdn,
                        eth_link_profile_name="default",
                        name="",
                        auto_negotiate="yes",
                        usr_lbl="",
                        slot_id="1",
                        admin_state="enabled",
                        port_id=str(pid))
                elif ptype == "fcoe-storage":
                    mo = FabricFcoeEstcEp(
                        parent_mo_or_dn=pdn,
                        name="",
                        auto_negotiate="yes",
                        usr_lbl="",
                        slot_id="1",
                        admin_state="enabled",
                        port_id=str(pid))
                elif ptype == "appliance":
                    mo = FabricEthEstcEp(
                        parent_mo_or_dn=pdn,
                        port_mode="trunk",
                        name="",
                        prio="best-effort",
                        flow_ctrl_policy="default",
                        admin_speed="10gbps",
                        usr_lbl="",
                        auto_negotiate="yes",
                        slot_id="1",
                        admin_state="enabled",
                        pin_group_name="",
                        port_id=str(pid),
                        nw_ctrl_policy_name="default")
                try:
                    handle.add_mo(mo)
                    handle.commit()
                    ret = "success"
                    res.setResult("", PTK_OKAY, ret)
                except ucsmsdk.ucsexception.UcsException:
                    ret = "Unexpected Internal Error"
                    res.setResult("", PTK_INTERNALERROR, ret)
                    self._release_ucsm_handler(handle)
                except BaseException:
                    ret = "Unexpected Internal Error"
                    res.setResult("", PTK_INTERNALERROR, ret)
                    self._release_ucsm_handler(handle)
        self._release_ucsm_handler(handle)
        return res

    def ucsmethernetportunconfig(self, fid, plist):
        res = result()
        ptype_list = [
            "server",
            "network",
            "fcoe-uplink",
            "fcoe-storage",
            "nas-storage"]
        ptype_dn = [
            "fabric/server/sw-",
            "fabric/lan/",
            "fabric/san/",
            "fabric/fc-estc/",
            "fabric/eth-estc/"]

        fi_ports = parseResult(self.ucsmfiethernetports(fid=fid))

        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            for pid in plist:
                ptype = ""
                for p in fi_ports:
                    if p['pid'] == str(pid):
                        ptype = p['if_role']

                if ptype in ptype_list:
                    port_dn = ptype_dn[ptype_list.index(ptype)]
                else:
                    res.setResult("", PTK_INTERNALERROR, "Port not configured")
                    continue

                if ptype == "server":
                    pdn = port_dn + fid + "/slot-1-port-" + str(pid)
                    mo = handle.query_dn(pdn)
                elif ptype == "network":
                    pdn = port_dn + fid + "/phys-slot-1-port-" + str(pid)
                    mo = handle.query_dn(pdn)
                elif ptype == "fcoe-uplink":
                    pdn = port_dn + fid + \
                        "/phys-fcoesanep-slot-1-port-" + str(pid)
                    mo = handle.query_dn(pdn)
                elif ptype == "fcoe-storage":
                    pdn = port_dn + fid + "/phys-fcoe-slot-1-port-" + str(pid)
                    mo = handle.query_dn(pdn)
                elif ptype == "nas-storage":
                    pdn = port_dn + fid + "/phys-eth-slot-1-port-" + str(pid)
                    mo = handle.query_dn(pdn)
                try:
                    handle.remove_mo(mo)
                    handle.commit()
                except ucsmsdk.ucsexception.UcsException as e:
                    self._release_ucsm_handler(handle)
                    res.setResult("", PTK_INTERNALERROR, str(e))
                    return res
                except BaseException:
                    self._release_ucsm_handler(handle)
                    res.setResult("", PTK_INTERNALERROR, "Failure")
                    return obj
        else:
            res.setResult(
                "",
                PTK_INTERNALERROR,
                "Unable to retrieve Fabric Interconnect details")

        self._release_ucsm_handler(handle)
        return res

    def ucsmtopology(self, mac):
        res = result()
        cred = get_device_credentials(
            key="mac", value=mac)
        topology_list = []

        if cred:
            handle = self._ucsm_handler(
                cred['ipaddress'], cred['username'], cred['password'])
        else:
            res.setResult(
                topology_list,
                PTK_INTERNALERROR,
                "Unable to get the details")
            return res

        if handle is not None:
            chassislist = handle.query_classid("EquipmentChassis")
            for chassis in chassislist:
                conn = string.split(chassis.conn_path, ',')
                for i in range(0, len(conn)):
                    if i == 0:
                        parent = "fabric" + "|" + conn[i]
                    else:
                        parent += "," + "fabric" + "|" + conn[i]
                chassis_new_list = {
                    "name": chassis.rn,
                    "type": "chassis",
                    "id": chassis.id,
                    "parent": parent}
                topology_list.append(chassis_new_list)
            fabrics = handle.query_classid("networkelement")
            for fabric in fabrics:
                split = string.split(fabric.rn, '-')
                name = "fabric interconnect " + split[1]
                mgmts = handle.query_classid("MgmtEntity")
                parent = False
                for mgmt in mgmts:
                    if mgmt.leadership == "primary":
                        if mgmt.id == split[1]:
                            parent = True

                fabric_new_list = {
                    "name": name,
                    "type": "fabric",
                    "id": split[1],
                    "parent": parent}
                topology_list.append(fabric_new_list)
            fexs = handle.query_classid("equipmentFex")
            for fex in fexs:
                parent = "fabric" + "|" + fex.switch_id
                fex_new_list = {
                    "name": fex.rn,
                    "type": "fex",
                    "id": fex.id,
                    "parent": parent}
                topology_list.append(fex_new_list)

            paths = handle.query_classid("FabricPath")
            pathlist = []
            for path in paths:
                if path.c_type == "switch-to-host":
                    pathlist.append(path.dn)
            servers = handle.query_classid("ComputeRackUnit")
            for server in servers:
                flag = 0
                for i in range(0, len(pathlist)):
                    path = string.split(pathlist[i], "/")
                    if server.rn == path[1]:
                        flag = 1
                        element = string.split(path[2], "-")
                        if i == 0:
                            parent = "fabric" + "|" + element[1]
                        else:
                            parent += "," + "fabric" + "|" + element[1]
                if flag:
                    topology_list.append(
                        {"name": server.rn, "type": "server", "id": server.server_id, "parent": parent})
                    continue
                conn = string.split(server.conn_path, ',')
                for i in range(0, len(conn)):
                    fexs = handle.query_classid("equipmentFex")
                    for fex in fexs:
                        if fex.switch_id == conn[i]:
                            conn[i] = fex.id
                    if i == 0:
                        parent = "fex" + "|" + conn[i]
                    else:
                        parent += "," + "fex" + "|" + conn[i]
                topology_list.append(
                    {"name": server.rn, "type": "server", "id": server.server_id, "parent": parent})
            res.setResult(topology_list, PTK_OKAY, "success")

        else:
            res.setResult(
                topology_list,
                PTK_INTERNALERROR,
                "Unable to login to FI")
            return res

        self._release_ucsm_handler(handle)
        return res

    def ucsmserviceprofile(self):
        response_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            sp_list = handle.query_classid("LsServer")
            for sp in sp_list:
                if sp.type == "instance":
                    response_list.append({"name": sp.name,
                                          "overall_state": sp.oper_state,
                                          "assoc_state": sp.assoc_state})
            res.setResult(response_list, PTK_OKAY, "success")
        else:
            res.setResult(
                response_list,
                PTK_NOTEXIST,
                "Unable to retrieve service profiles list")
        self._release_ucsm_handler(handle)
        return res

    def ucsmserviceprofiletemp(self):
        response_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            sp_list = handle.query_classid("LsServer")
            for sp in sp_list:
                if sp.type == "initial-template":
                    response_list.append({"name": sp.name})
            res.setResult(response_list, PTK_OKAY, "success")
        else:
            res.setResult(
                response_list,
                PTK_NOTEXIST,
                "Unable to retrieve service profile template list")
        self._release_ucsm_handler(handle)
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
		    vnic_data = handle.query_children(in_mo=mo, class_id='VnicFc')
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

    def ucsmchassisbladeinfo(self, chassisid):
        chassis_info_list = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            blades = handle.query_classid("ComputeBlade")
            for blade in blades:
                eq = string.split(blade.server_id, '/')
                if chassisid == eq[0]:
                    name = "server " + blade.slot_id
                    chassis_info_list.append({"servername": name,
                                              "model": blade.model,
                                              "status": blade.oper_state,
                                              "operability_status": blade.operability,
                                              "power_state": blade.oper_power,
                                              "assoc_state": blade.status,
                                              "fault_status": "N/A"})
            res.setResult(chassis_info_list, PTK_OKAY, "success")
        else:
            res.setResult(
                chassis_info_list,
                PTK_INTERNALERROR,
                "Unexpected Internal Error")
        self._release_ucsm_handler(handle)
        return res

    def getusmdetails(self):
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        res = result()
        # self._save_ucsm_login_details("192.168.1.1", "username", "password"):
        ucsm_details = []
        mo = handle.query_dn("sys/mgmt/fw-system")
        dicts = {}
        dicts['version'] = mo.version
        ucsm_details.append({"version": dicts['version']})
        res.setResult(ucsm_details, PTK_OKAY, "success")
        self._release_ucsm_handler(handle)
        return res

    def _save_ucsm_primary_details(self, ipaddress, username, password, serial_no, mac, model, device_type, configured,
                                   name, tag, vipaddress, leadership, reachability, dns, domain_name, gateway, ipformat,
                                   netmask, pri_cluster, pri_id, pri_orig_ip, pri_setup_mode, validated, esxi_file, esxi_kickstart, infra_image, blade_image, ucs_upgrade):
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(static_discovery_store, data)
        return

    def _save_ucsm_subordinate_details(self, ipaddress, username, password, pri_ip, serial_no, mac, model, device_type,
                                       configured, name, tag, vipaddress, leadership, reachability, sec_cluster, sec_id,
                                       sec_orig_ip, netmask, gateway, validated, infra_image, blade_image, ucs_upgrade):
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(static_discovery_store, data)
        return

    def ucsmficonfigure(self, mode, config):
        res = result()

        if mode == "cluster":
            update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['pri_switch_mac'],
                               data={"configured": "In-progress", "timestamp": str(time.time())})
            update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['sec_switch_mac'],
                               data={"configured": "In-progress", "timestamp": str(time.time())})

            threading.Thread(target=self.ucsmclusterficonfigure,
                             args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        elif mode == "primary":
            update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['pri_switch_mac'],
                               data={"configured": "In-progress", "timestamp": str(time.time())})

            threading.Thread(target=self.ucsmprimaryficonfigure,
                             args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        elif mode == "subordinate":
            update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['sec_switch_mac'],
                               data={"configured": "In-progress", "timestamp": str(time.time())})

            threading.Thread(
                target=self.ucsmsubordinateficonfigure, args=(config,)).start()
            res.setResult(
                '',
                PTK_OKAY,
                "Success")
            return res

        elif mode == "standalone":
            update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['pri_switch_mac'],
                               data={"configured": "In-progress", "timestamp": str(time.time())})

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
                fi_dict['switch_ip'] = dt['ipaddress']
                fi_dict['virtual_ip'] = dt['vipaddress']
                fi_dict['switch_name'] = dt['name'].rsplit('-', 1)[0]
                fi_dict['switch_tag'] = dt['tag']
                fi_dict['switch_mac'] = dt['mac']
                fi_dict['ucs_upgrade'] = dt['ucs_upgrade']
                fi_dict['infra_image'] = dt['infra_image']
                fi_dict['blade_image'] = dt['blade_image']
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
                          "virtual_ip": primary_data["vipaddress"],
                          "dns": primary_data["dns"],
                          "domain_name": primary_data["domain_name"],
                          "ucs_upgrade": primary_data["ucs_upgrade"],
                          "infra_image": primary_data["infra_image"],
                          "blade_image": primary_data["blade_image"],
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
            input_dict["ucs_upgrade"] = data["ucs_upgrade"],
            input_dict["infra_image"] = data["infra_image"],
            input_dict["blade_image"] = data["blade_image"],
            if data['leadership'] == "primary":
                loginfo("FI Reconfigure: Gathering inputs for primary mode")
                input_dict['dns'] = data['dns']
                input_dict['domain_name'] = data['domain_name']
                input_dict['netmask'] = data['netmask']
                input_dict['gateway'] = data['gateway']
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
                ip_val = ipvalidation(ip_list[ip])
                if ip_val == False:
                    err.append({"field": ip, "msg": "Please Enter Valid IP"})
                if ip != 'dns':
                    network_reach, ip_reach = ipv.validate_ip(
                        ip_list[ip], netmask, gateway)
                    if network_reach == True:
                        if ip_reach == True:
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
            ret = validate_input_data({'pri_ip': 'Mgmt IP for primary FI', 'pri_passwd': 'Password',
                                       'conf_passwd': 'Confirm password',
                                       'pri_switch_serial_no': 'Serial number of primary FI',
                                       'pri_switch_mac': 'MAC of primary FI',
                                       'pri_switch_vendor': 'Vendor of primary FI', 'pri_name': 'Name for primary FI',
                                       'pri_orig_ip': 'DHCP IP of primary FI',
                                       'pri_setup_mode': 'Set up mode for primary FI',
                                       'pri_cluster': 'Cluster mode for primary FI', 'pri_id': 'ID for primary FI',
                                       'ipformat': 'IP format', 'netmask': 'Netmask', 'gateway': 'Gateway',
                                       'virtual_ip': 'Virtual IP',
                                       'sec_ip': 'IP for subordiate FI',
                                       'sec_switch_serial_no': 'Serial number of subordiate FI',
                                       'sec_switch_mac': 'MAC of subordiate FI',
                                       'sec_switch_vendor': 'Vendor of subordiate FI',
                                       'sec_orig_ip': 'DHCP IP of subordiate FI',
                                       'sec_cluster': 'Cluster mode for subordiate FI',
                                       'sec_id': 'ID for subordinate FI', 'esxi_file': 'Remote ESX file', 'dns':'DNS IP'}, config)
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

                ip_list = {'pri_ip': config['pri_ip'], 'sec_ip': config['sec_ip'], 'virtual_ip': config['virtual_ip'],
                           'dns': config['dns']}
                # ip_list = [config['pri_ip'],
                #         config['sec_ip'], config['virtual_ip']]
                res = self.ucsm_validate_ip(
                    ip_list, config['netmask'], config['gateway'])
                return res

        elif mode == "primary":
            ret = validate_input_data({'pri_ip': 'Mgmt IP for primary FI', 'pri_passwd': 'Password for primary FI',
                                       'pri_switch_serial_no': 'Serial number of primary FI',
                                       'pri_switch_mac': 'MAC of primary FI',
                                       'pri_switch_vendor': 'Vendor of primary FI', 'pri_name': 'Name for primary FI',
                                       'pri_orig_ip': 'DHCP IP of primary FI',
                                       'pri_setup_mode': 'Set up mode for primary FI',
                                       'pri_cluster': 'Cluster mode for primary FI', 'pri_id': 'ID for primary FI',
                                       'ipformat': 'IP format', 'netmask': 'Netmask', 'gateway': 'Gateway',
                                       'virtual_ip': 'Virtual IP'}, config)
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
            ret = validate_input_data({'pri_ip': 'Mgmt IP for standalone FI', 'sec_ip': 'IP for subordiate FI',
                                       'sec_switch_serial_no': 'Serial number of subordiate FI',
                                       'sec_switch_mac': 'MAC of subordiate FI',
                                       'sec_switch_vendor': 'Vendor of subordiate FI',
                                       'sec_orig_ip': 'DHCP IP of subordiate FI',
                                       'sec_cluster': 'Cluster mode for subordiate FI',
                                       'sec_id': 'ID for subordinate FI'}, config)
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
                if ipv.is_ip_up(config['sec_ip']) == True:
                    res.setResult(
                        ret, PTK_INTERNALERROR, "Mgmt IP Address provided is already active, provide a free IP")
                    return res
                res.setResult(ret, PTK_OKAY, "Success")
                return res

        elif mode == "standalone":
            ret = validate_input_data(
                {'pri_ip': 'Mgmt IP for standalone FI', 'pri_passwd': 'Password for standalone FI',
                 'pri_switch_serial_no': 'Serial number of standalone FI', 'pri_switch_mac': 'MAC of standalone FI',
                 'pri_switch_vendor': 'Vendor of standalone FI', 'pri_name': 'Name for standalone FI',
                 'pri_orig_ip': 'DHCP IP of standalone FI', 'pri_setup_mode': 'Set up mode for standalone FI',
                 'pri_cluster': 'Cluster mode for standalone FI', 'pri_id': 'ID for standalone FI',
                 'ipformat': 'IP format', 'netmask': 'Netmask', 'gateway': 'Gateway'}, config)
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
            dns1=config['dns'],
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
                        "Failed to configure the primary FI %s. Maximum attempts reached" % config['pri_name'])
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
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" % config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" % config['sec_ip'])
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
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" % config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" % config['sec_ip'])
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

            loginfo("Triggering UCS upgrade")
            staus, msg = ucsm_upgrade(
                ip=config['virtual_ip'], username="admin", password=config['pri_passwd'], infra=config['infra_image'])
            if not status:
                loginfo("UCS upgrade failed. Updating device status")
                update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['sec_switch_mac'],
                                   data={"configured": "Re-validate", "reval_msg": msg})
            else:
                loginfo("UCS upgrade done. Updating device status")
                update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['sec_switch_mac'],
                                   data={"configured": "Configured"})

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
            dns1=config['dns'],
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
                        "Failed to configure the standalone FI %s. Maximum attempts reached" % config['pri_name'])
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
            dns1=config['dns'],
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
                        "Failed to configure the primary FI %s. Maximum attempts reached" % config['pri_name'])
                    return
                loginfo("Failed to configure the primary FI %s. Retrying once more" %
                        config['pri_name'])
                retry += 1
                time.sleep(2)

        retry = 0
        while retry < 5:
            (error, status) = execute_remote_command(
                config['pri_ip'], "admin", config['pri_passwd'], "show version")
            if status is False:
                time.sleep(10)
                retry += 1
            else:
                break

        if status is False:
            loginfo("Failed to configure the primary FI %s" %
                    config['pri_name'])
            return

        self._save_ucsm_login_details(
            ipaddress=config['pri_ip'],
            username="admin",
            password=config['pri_passwd'])

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
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" % config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" % config['sec_ip'])
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
                        "Failed to configure the subordinate FI %s. Maximum attempts reached" % config['sec_ip'])
                    return
                loginfo(
                    "Failed to configure the subordinate FI %s. Retrying once more" % config['sec_ip'])
                retry += 1
                time.sleep(2)

        loginfo(
            "Successfully configured subordinate FI %s. Cluster configuration done" % config['sec_ip'])

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

            loginfo("Triggering UCS upgrade")
            staus, msg = ucsm_upgrade(
                ip=config['virtual_ip'], username="admin", password=config['pri_passwd'], infra=config['infra_image'])
            if not status:
                loginfo("UCS upgrade failed. Updating device status")
                update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['pri_switch_mac'],
                                   data={"configured": "Re-validate", "reval_msg": msg})
                update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['sec_switch_mac'],
                                   data={"configured": "Re-validate", "reval_msg": msg})
            else:
                loginfo("UCS upgrade done. Updating device status")
                update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['pri_switch_mac'],
                                   data={"configured": "Configured"})
                update_xml_element(static_discovery_store, matching_key="mac", matching_value=config['sec_switch_mac'],
                                   data={"configured": "Configured"})

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
            if not ipaddress:
                doc = parse(ucsm_credentials_store)
                ipaddress = doc.childNodes[0].getAttribute("ipaddress")
                username = doc.childNodes[0].getAttribute("username")
                password = doc.childNodes[0].getAttribute("password")
                doc.unlink()
            handle = UcsHandle(ipaddress, username, password)
            login_state = handle.login()
            if login_state:
                return handle
            else:
                return None
        except BaseException:
            return None

    def list_service_profiles(self):
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        splist = []
        res = result()
        if handle is not None:
            sp_list = handle.query_classid("LsServer")
            for sp in sp_list:
                if sp.type == "instance":
                    splist.append(sp.name)
            self._release_ucsm_handler(handle)
        res.setResult(splist, PTK_OKAY, "success")
        return res

    def list_service_profile_templates(self):
        sptemplist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            sp_templist = handle.query_classid("LsServer")
            for sptemp in sp_templist:
                if sptemp.type == "initial_template":
                    sptemplist.append(sptemp.name)

            self._release_ucsm_handler(handle)
        res.setResult(sptemplist, PTK_OKAY, "success")
        return res

    ############################# UCSSafe functions ##########################

    def ucsmscrubpolicy(self):
        obj = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("ComputeScrubPolicy")
            for policy in policies:
                if "org-root" in policy.dn:
                    obj.append({"name": policy.name})
            obj.append({"name": "default"})
            res.setResult(obj, PTK_OKAY, "success")
        else:
            res.setResult(
                obj,
                PTK_INTERNALERROR,
                "Unable to retrieve scrub policy")
        self._release_ucsm_handler(handle)
        return res

    def ucsmuuidpools(self):
        poollist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            pools = handle.query_classid("UuidpoolPool")
            for pool in pools:
                name = pool.name
                poollist.append({"name": name})
            res.setResult(poollist, PTK_OKAY, "success")
            return res

    def ucsmlocaldiskpolicies(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("StorageLocalDiskConfigPolicy")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmlocalconnectivitypolicies(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("VnicLanConnPolicy")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmsanconnectivitypolicies(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("VnicSanConnPolicy")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmvmediapolicies(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("CimcvmediaMountConfigPolicy")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmbootpolicies(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("LsbootPolicy")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmserverpoolqualifications(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("ComputeQual")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmpowercontrolpolicies(self):
        policieslist = []
        res = result()
        handle = self._ucsm_handler(ipaddress="", username="", password="")
        if handle is not None:
            policies = handle.query_classid("PowerPolicy")
            for policy in policies:
                name = policy.name
                policieslist.append({"name": name})
            res.setResult(policieslist, PTK_OKAY, "success")
            return res

    def ucsmtimezone(self):
        obj = []
        res = result()
        zonelist = ["Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara",
                    "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre",
                    "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca",
                    "Africa/Ceuta (Ceuta & Melilla)", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam",
                    "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone",
                    "Africa/Harare", "Africa/Johannesburg", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali",
                    "Africa/Kinshasa (west Dem. Rep. of Congo)", "Africa/Lagos", "Africa/Libreville", "Africa/Lome",
                    "Africa/Luanda", "Africa/Lubumbashi (east Dem. Rep. of Congo)", "Africa/Lusaka", "Africa/Malabo",
                    "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia",
                    "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou",
                    "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek",
                    "America/Adak (Aleutian Islands)", "America/Anchorage (Alaska Time)", "America/Anguilla",
                    "America/Antigua", "America/Araguaina (Tocantins)",
                    "America/Argentina/Buenos_Aires (Buenos Aires (BA, CF))",
                    "America/Argentina/Catamarca (Catamarca (CT), Chubut (CH))",
                    "America/Argentina/Cordoba (most locations (CB, CC, CN, ER, FM, MN, SE, SF))",
                    "America/Argentina/Jujuy (Jujuy (JY))", "America/Argentina/La_Rioja (La Rioja (LR))",
                    "America/Argentina/Mendoza (Mendoza (MZ))", "America/Argentina/Rio_Gallegos (Santa Cruz (SC))",
                    "America/Argentina/Salta ((SA, LP, NQ, RN))", "America/Argentina/San_Juan (San Juan (SJ))",
                    "America/Argentina/San_Luis (San Luis (SL))", "America/Argentina/Tucuman (Tucuman (TM))",
                    "America/Argentina/Ushuaia (Tierra del Fuego (TF))", "America/Aruba", "America/Asuncion",
                    "America/Atikokan (Eastern Standard Time - Atikokan, Ontario and Southampton I, Nunavut)",
                    "America/Bahia (Bahia)", "America/Barbados", "America/Belem (Amapa, E Para)", "America/Belize",
                    "America/Blanc-Sablon (Atlantic Standard Time - Quebec - Lower North Shore)",
                    "America/Boa_Vista (Roraima)", "America/Bogota",
                    "America/Boise (Mountain Time - south Idaho & east Oregon)",
                    "America/Cambridge_Bay (Mountain Time - west Nunavut)", "America/Campo_Grande (Mato Grosso do Sul)",
                    "America/Cancun (Central Time - Quintana Roo)", "America/Caracas", "America/Cayenne",
                    "America/Cayman",
                    "America/Chicago (Central Time)",
                    "America/Chihuahua (Mexican Mountain Time - Chihuahua away from US border)", "America/Costa_Rica",
                    "America/Cuiaba (Mato Grosso)", "America/Curacao",
                    "America/Danmarkshavn (east coast, north of Scoresbysund)",
                    "America/Dawson_Creek (Mountain Standard Time - Dawson Creek & Fort Saint John, British Columbia)",
                    "America/Dawson (Pacific Time - north Yukon)", "America/Denver (Mountain Time)",
                    "America/Detroit (Eastern Time - Michigan - most locations)", "America/Dominica",
                    "America/Edmonton (Mountain Time - Alberta, east British Columbia & west Saskatchewan)",
                    "America/Eirunepe (W Amazonas)", "America/El_Salvador",
                    "America/Fortaleza (NE Brazil (MA, PI, CE, RN, PB))",
                    "America/Glace_Bay (Atlantic Time - Nova Scotia - places that did not observe DST 1966-1971)",
                    "America/Godthab (most locations)", "America/Goose_Bay (Atlantic Time - Labrador - most locations)",
                    "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala",
                    "America/Guayaquil (mainland)", "America/Guyana",
                    "America/Halifax (Atlantic Time - Nova Scotia (most places), PEI)", "America/Havana",
                    "America/Hermosillo (Mountain Standard Time - Sonora)",
                    "America/Indiana/Indianapolis (Eastern Time - Indiana - most locations)",
                    "America/Indiana/Knox (Central Time - Indiana - Starke County)",
                    "America/Indiana/Marengo (Eastern Time - Indiana - Crawford County)",
                    "America/Indiana/Petersburg (Eastern Time - Indiana - Pike County)",
                    "America/Indiana/Tell_City (Central Time - Indiana - Perry County)",
                    "America/Indiana/Vevay (Eastern Time - Indiana - Switzerland County)",
                    "America/Indiana/Vincennes (Eastern Time - Indiana - Daviess, Dubois, Knox & Martin Counties)",
                    "America/Indiana/Winamac (Eastern Time - Indiana - Pulaski County)",
                    "America/Inuvik (Mountain Time - west Northwest Territories)",
                    "America/Iqaluit (Eastern Time - east Nunavut - most locations)", "America/Jamaica",
                    "America/Juneau (Alaska Time - Alaska panhandle)",
                    "America/Kentucky/Louisville (Eastern Time - Kentucky - Louisville area)",
                    "America/Kentucky/Monticello (Eastern Time - Kentucky - Wayne County)", "America/La_Paz",
                    "America/Lima", "America/Los_Angeles (Pacific Time)", "America/Maceio (Alagoas, Sergipe)",
                    "America/Managua", "America/Manaus (E Amazonas)", "America/Marigot", "America/Martinique",
                    "America/Matamoros (US Central Time - Coahuila, Durango, Nuevo Leon, Tamaulipas near US border)",
                    "America/Mazatlan (Mountain Time - S Baja, Nayarit, Sinaloa)",
                    "America/Menominee (Central Time - Michigan - Dickinson, Gogebic, Iron & Menominee Counties)",
                    "America/Merida (Central Time - Campeche, Yucatan)",
                    "America/Mexico_City (Central Time - most locations)", "America/Miquelon",
                    "America/Moncton (Atlantic Time - New Brunswick)",
                    "America/Monterrey (Mexican Central Time - Coahuila, Durango, Nuevo Leon, Tamaulipas away from US border)",
                    "America/Montevideo", "America/Montreal (Eastern Time - Quebec - most locations)",
                    "America/Montserrat",
                    "America/Nassau", "America/New_York (Eastern Time)",
                    "America/Nipigon (Eastern Time - Ontario & Quebec - places that did not observe DST 1967-1973)",
                    "America/Nome (Alaska Time - west Alaska)", "America/Noronha (Atlantic islands)",
                    "America/North_Dakota/Center (Central Time - North Dakota - Oliver County)",
                    "America/North_Dakota/New_Salem (Central Time - North Dakota - Morton County (except Mandan area))",
                    "America/Ojinaga (US Mountain Time - Chihuahua near US border)", "America/Panama",
                    "America/Pangnirtung (Eastern Time - Pangnirtung, Nunavut)", "America/Paramaribo",
                    "America/Phoenix (Mountain Standard Time - Arizona)", "America/Port-au-Prince",
                    "America/Port_of_Spain",
                    "America/Porto_Velho (Rondonia)", "America/Puerto_Rico",
                    "America/Rainy_River (Central Time - Rainy River & Fort Frances, Ontario)",
                    "America/Rankin_Inlet (Central Time - central Nunavut)", "America/Recife (Pernambuco)",
                    "America/Regina (Central Standard Time - Saskatchewan - most locations)",
                    "America/Resolute (Eastern Standard Time - Resolute, Nunavut)", "America/Rio_Branco (Acre)",
                    "America/Santa_Isabel (Mexican Pacific Time - Baja California away from US border)",
                    "America/Santarem (W Para)", "America/Santiago (most locations)", "America/Santo_Domingo",
                    "America/Sao_Paulo (S & SE Brazil (GO, DF, MG, ES, RJ, SP, PR, SC, RS))",
                    "America/Scoresbysund (Scoresbysund / Ittoqqortoormiit)",
                    "America/Shiprock (Mountain Time - Navajo)",
                    "America/St_Barthelemy", "America/St_Johns (Newfoundland Time, including SE Labrador)",
                    "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent",
                    "America/Swift_Current (Central Standard Time - Saskatchewan - midwest)", "America/Tegucigalpa",
                    "America/Thule (Thule / Pituffik)", "America/Thunder_Bay (Eastern Time - Thunder Bay, Ontario)",
                    "America/Tijuana (US Pacific Time - Baja California near US border)",
                    "America/Toronto (Eastern Time - Ontario - most locations)", "America/Tortola",
                    "America/Vancouver (Pacific Time - west British Columbia)",
                    "America/Whitehorse (Pacific Time - south Yukon)",
                    "America/Winnipeg (Central Time - Manitoba & west Ontario)",
                    "America/Yakutat (Alaska Time - Alaska panhandle neck)",
                    "America/Yellowknife (Mountain Time - central Northwest Territories)",
                    "Antarctica/Casey (Casey Station, Bailey Peninsula)",
                    "Antarctica/Davis (Davis Station, Vestfold Hills)",
                    "Antarctica/DumontDUrville (Dumont-d'Urville Station, Terre Adelie)",
                    "Antarctica/Mawson (Mawson Station, Holme Bay)",
                    "Antarctica/McMurdo (McMurdo Station, Ross Island)",
                    "Antarctica/Palmer (Palmer Station, Anvers Island)",
                    "Antarctica/Rothera (Rothera Station, Adelaide Island)",
                    "Antarctica/South_Pole (Amundsen-Scott Station, South Pole)",
                    "Antarctica/Syowa (Syowa Station, E Ongul I)",
                    "Antarctica/Vostok (Vostok Station, S Magnetic Pole)",
                    "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty (most locations)", "Asia/Amman",
                    "Asia/Anadyr (Moscow+10 - Bering Sea)",
                    "Asia/Aqtau (Atyrau (Atirau, Gur'yev), Mangghystau (Mankistau))", "Asia/Aqtobe (Aqtobe (Aktobe))",
                    "Asia/Ashgabat", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Beirut",
                    "Asia/Bishkek", "Asia/Brunei", "Asia/Choibalsan (Dornod, Sukhbaatar)",
                    "Asia/Chongqing (central China - Sichuan, Yunnan, Guangxi, Shaanxi, Guizhou, etc.)", "Asia/Colombo",
                    "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Gaza",
                    "Asia/Harbin (Heilongjiang (except Mohe), Jilin)", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong",
                    "Asia/Hovd (Bayan-Olgiy, Govi-Altai, Hovd, Uvs, Zavkhan)", "Asia/Irkutsk (Moscow+05 - Lake Baikal)",
                    "Asia/Jakarta (Java & Sumatra)", "Asia/Jayapura (Irian Jaya & the Moluccas)", "Asia/Jerusalem",
                    "Asia/Kabul", "Asia/Kamchatka (Moscow+09 - Kamchatka)", "Asia/Karachi",
                    "Asia/Kashgar (west Tibet & Xinjiang)", "Asia/Kathmandu", "Asia/Kolkata",
                    "Asia/Krasnoyarsk (Moscow+04 - Yenisei River)", "Asia/Kuala_Lumpur (peninsular Malaysia)",
                    "Asia/Kuching (Sabah & Sarawak)", "Asia/Kuwait", "Asia/Macau", "Asia/Magadan (Moscow+08 - Magadan)",
                    "Asia/Makassar (east & south Borneo, Celebes, Bali, Nusa Tengarra, west Timor)", "Asia/Manila",
                    "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk (Moscow+03 - Novokuznetsk)",
                    "Asia/Novosibirsk (Moscow+03 - Novosibirsk)", "Asia/Omsk (Moscow+03 - west Siberia)",
                    "Asia/Oral (West Kazakhstan)", "Asia/Phnom_Penh", "Asia/Pontianak (west & central Borneo)",
                    "Asia/Pyongyang", "Asia/Qatar", "Asia/Qyzylorda (Qyzylorda (Kyzylorda, Kzyl-Orda))", "Asia/Rangoon",
                    "Asia/Riyadh", "Asia/Sakhalin (Moscow+07 - Sakhalin Island)", "Asia/Samarkand (west Uzbekistan)",
                    "Asia/Seoul", "Asia/Shanghai (east China - Beijing, Guangdong, Shanghai, etc.)", "Asia/Singapore",
                    "Asia/Taipei", "Asia/Tashkent (east Uzbekistan)", "Asia/Tbilisi", "Asia/Tehran", "Asia/Thimphu",
                    "Asia/Tokyo", "Asia/Ulaanbaatar (most locations)", "Asia/Urumqi (most of Tibet & Xinjiang)",
                    "Asia/Vientiane", "Asia/Vladivostok (Moscow+07 - Amur River)",
                    "Asia/Yakutsk (Moscow+06 - Lena River)",
                    "Asia/Yekaterinburg (Moscow+02 - Urals)", "Asia/Yerevan", "Atlantic/Azores (Azores)",
                    "Atlantic/Bermuda", "Atlantic/Canary (Canary Islands)", "Atlantic/Cape_Verde", "Atlantic/Faroe",
                    "Atlantic/Madeira (Madeira Islands)", "Atlantic/Reykjavik", "Atlantic/South_Georgia",
                    "Atlantic/Stanley", "Atlantic/St_Helena", "Australia/Adelaide (South Australia)",
                    "Australia/Brisbane (Queensland - most locations)",
                    "Australia/Broken_Hill (New South Wales - Yancowinna)", "Australia/Currie (Tasmania - King Island)",
                    "Australia/Darwin (Northern Territory)", "Australia/Eucla (Western Australia - Eucla area)",
                    "Australia/Hobart (Tasmania - most locations)", "Australia/Lindeman (Queensland - Holiday Islands)",
                    "Australia/Lord_Howe (Lord Howe Island)", "Australia/Melbourne (Victoria)",
                    "Australia/Perth (Western Australia - most locations)",
                    "Australia/Sydney (New South Wales - most locations)", "Europe/Amsterdam", "Europe/Andorra",
                    "Europe/Athens", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels",
                    "Europe/Bucharest", "Europe/Budapest", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin",
                    "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul",
                    "Europe/Jersey", "Europe/Kaliningrad (Moscow-01 - Kaliningrad)", "Europe/Kiev (most locations)",
                    "Europe/Lisbon (mainland)", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg",
                    "Europe/Madrid (mainland)", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco",
                    "Europe/Moscow (Moscow+00 - west Russia)", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica",
                    "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara (Moscow+01 - Samara, Udmurtia)",
                    "Europe/San_Marino", "Europe/Sarajevo", "Europe/Simferopol (central Crimea)", "Europe/Skopje",
                    "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Uzhgorod (Ruthenia)",
                    "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius",
                    "Europe/Volgograd (Moscow+00 - Caspian Sea)", "Europe/Warsaw", "Europe/Zagreb",
                    "Europe/Zaporozhye (Zaporozh'ye, E Lugansk / Zaporizhia, E Luhansk)", "Europe/Zurich",
                    "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro",
                    "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte",
                    "Indian/Reunion", "Pacific/Apia", "Pacific/Auckland (most locations)",
                    "Pacific/Chatham (Chatham Islands)", "Pacific/Easter (Easter Island & Sala y Gomez)",
                    "Pacific/Efate",
                    "Pacific/Enderbury (Phoenix Islands)", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti",
                    "Pacific/Galapagos (Galapagos Islands)", "Pacific/Gambier (Gambier Islands)", "Pacific/Guadalcanal",
                    "Pacific/Guam", "Pacific/Honolulu (Hawaii)", "Pacific/Johnston (Johnston Atoll)",
                    "Pacific/Kiritimati (Line Islands)", "Pacific/Kosrae (Kosrae)", "Pacific/Kwajalein (Kwajalein)",
                    "Pacific/Majuro (most locations)", "Pacific/Marquesas (Marquesas Islands)",
                    "Pacific/Midway (Midway Islands)", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk",
                    "Pacific/Noumea",
                    "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Ponape (Ponape (Pohnpei))",
                    "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Tahiti (Society Islands)",
                    "Pacific/Tarawa (Gilbert Islands)", "Pacific/Tongatapu", "Pacific/Truk (Truk (Chuuk) and Yap)",
                    "Pacific/Wake (Wake Island)", "Pacific/Wallis"]
        for time_zone in zonelist:
            obj.append({"zone": time_zone})
        res.setResult(obj, PTK_OKAY, "success")
        return res

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
