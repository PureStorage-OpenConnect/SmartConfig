from purestorage import PureError, PureHTTPError
import json
import time
import ast
import os
import urllib3
from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import parseTaskResult
from pure_dir.components.storage.purestorage.pure import PureHelper
from pure_dir.infra.apiresults import PTK_INTERNALERROR, PTK_OKAY, result
from purestorage import FlashArray
from purestorage import PureHTTPError
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_helper import *

from xml.dom.minidom import parse, Document

from pure_dir.infra.logging.logmanager import loginfo


class PureTasks:
    def __init__(self,  ipaddress='', username='', password=''):
        self.handle = self.pure_handler(
            ipaddress=ipaddress, username=username, password=password)
        self.username = username
        self.pwd = password
        pass

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def pure_handler(self, ipaddress="", username="", password=""):
        res = result()
        try:
            handle = FlashArray(ipaddress, username,
                                password, verify_https=False, user_agent="PureStorage SmartConfig /1.2 (Python, CentOS 7.4)")
            return handle
        except Exception as e:
            loginfo("Unable to get purestorage handle")
            loginfo("Error code {} and reason {}".format(e.code, e.reason))
            return None

    def flash_array_info(self, ip):
        """
        Returns FlashArray details

        :param ip: Management ip address of FlashArray
        :return: Returns array information
        """

        obj = result()
        loginfo("flash_array_info ip : {}".format(ip))
        switch = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to Connect to FlashArray")
            return switch

        res = self.get_network_interfaces(ip)

        if res.getStatus() != PTK_OKAY:
            return switch

        switch['mac_addr'] = res.getResult()
        switch['name'], switch['version'] = self.get_array()
        switch['serial_no'] = self.getSerial_no(ip)
        switch['model'] = self.get_array_controller()
        loginfo("switch array is :{}".format(switch))

        return switch

    def release_pure_handle(self):
        """
        Release handler

        :return: status
        """

        res = result()
        try:
            self.handle.invalidate_cookie()
        except PureError:
            res.setResult(None, PTK_INTERNALERROR,
                          "Failed to release the pure handle")
            return res

        res.setResult(None, PTK_OKAY, "Success")
        return res

    def get_multiple_host_names(self, name, st_no, count, num_digits):
        old_num_digit = num_digits
        result = []
        name = ("-").join(name.split("-")[:-1]) + "-"
        if count == 1 and num_digits == 0 and st_no == 0:  # for single host
            result.append(("-").join(name.split("-")[:-1]))
        else:
            for i in range(0, int(count)):
                for k in range(1, int(num_digits)):
                    if old_num_digit > len(str(st_no)):
                        name = name + "0"

                name = name + str(st_no)
                result.append(name)
                name = ("-").join(name.split("-")[:-1]) + "-"
                st_no = int(st_no) + 1
        return result

    def get_multiple_vol_names(self, name, st_no, count, num_digits):
        name = name.replace("Host", "Vol")
        old_num_digit = num_digits
        result = []
        name = ("-").join(name.split("-")[:-1]) + "-"
        if count == 1 and num_digits == 0 and st_no == 0:  # for single host
            result.append(("-").join(name.split("-")[:-1]))
        else:
            for i in range(0, int(count)):
                for k in range(1, int(num_digits)):
                    if old_num_digit > len(str(st_no)):
                        name = name + "0"

                name = name + str(st_no)
                result.append(name)
                name = ("-").join(name.split("-")[:-1]) + "-"
                st_no = int(st_no) + 1
        return result

    def create_shared_volume(self, inputs, logfile):
        """
        Creates Shared Volume

        :param inputs: Dictonary(name, size)
        :param logfile: Logfile name  
        :return: Retuns Name and status of volume created
        """

        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("Create Shared Volume inputs is : {}".format(inputs))
        vol_datas = inputs['vol_set']
        vol_size_data = eval(vol_datas)
        size = vol_size_data['size']['value']
        size_unit = vol_size_data['size_unit']['value']

        try:
            volName = inputs['name']
            volSize = size
            volSizeUnit = size_unit
            msg = "Creating shared volume %s" % volName
            customlogs(msg, logfile)
            vol_size = (int(volSize) * int(volSizeUnit))  # making size in GB
            loginfo("Create shared volume data is {} {}".format(volName, vol_size))
            opdict = self.handle.create_volume(volName, int(vol_size))
            obj.setResult(opdict, PTK_OKAY, "Success")
            customlogs("Shared volume created successfully\n", logfile)
        except PureHTTPError as e:
            loginfo("err e is {}".format(e))
            err = e.text
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            loginfo("err 0 is {}".format(eval(err)[0]))
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to create shared volume", logfile)
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Failed to create shared volume")
            loginfo(" Error {}".format(str(e)))
            return obj
        msg = "Shared volume created successfully\n"
        customlogs(msg, logfile)
        dicts['name'] = inputs['name']
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def create_multiple_volumes(self, inputs, logfile):
        """
        Creates multiple Volumes

        :param inputs: Dictonary(name, count)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("create volume inputs is {}".format(inputs))
        vol_datas = inputs['vol_set']
        vol_size_data = eval(vol_datas)
        size = vol_size_data['size']['value']
        size_unit = vol_size_data['size_unit']['value']

        name = inputs['name']  # here name is service profile
        st_no = inputs['st_no']
        count = inputs['count']  # count of service profile
        num_digits = inputs['num_digits']
        vol_datas = self.get_multiple_vol_names(name, st_no, count, num_digits)

        for vol_data in vol_datas:
            data = {}
            loginfo("vol_data is {} {}".format(vol_data, type(vol_data)))
            try:
                msg = "Creating volume %s" % vol_data
                volName = vol_data
                volSize = size
                volSizeUnit = size_unit
                loginfo("name size unit {} {} {}".format(
                    volName, volSize, volSizeUnit))
                customlogs(msg, logfile)
                # making size in GB
                vol_size = (int(volSize) * int(volSizeUnit))

                opdict = self.handle.create_volume(volName, int(vol_size))
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Volume created successfully", logfile)
            except PureHTTPError as e:
                loginfo("err e is {}".format(e))
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                loginfo("err 0 is {}".format(eval(err)[0]))
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Failed to create volume", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to create volume")
                return obj
        msg = "Volumes created successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def create_multiple_hosts(self, inputs, logfile):
        """
        Create Multiple hosts

        :param inputs: Dictonary(name, count)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        opdict = {}

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("create host inputs is {}".format(inputs))

        name = inputs['name']  # here name is service profile
        st_no = inputs['st_no']
        count = inputs['count']  # count of service profile
        num_digits = inputs['num_digits']
        loginfo("Create_multiple_hosts {}".format(inputs))
        hosts = self.get_multiple_host_names(name, st_no, count, num_digits)
        for host in hosts:
            try:
                msg = "Creating host %s" % host
                customlogs(msg, logfile)
                opdict = self.handle.create_host(host)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Host created successfully", logfile)
            except PureHTTPError as e:
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Failed to create host", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to create host")
                return obj
        msg = "Hosts created successfully\n"
        customlogs(msg, logfile)
        obj.setResult(opdict, PTK_OKAY,
                      msg)
        return obj

    def add_port_to_host(self, inputs, logfile):
        """
        Add Port to hosts

        :param inputs: Dictonary(name, count)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("add_port_to_host inputs: {}".format(inputs))

        dicts['host_set'] = inputs['host_set']
        hv_datas = inputs['host_set'].split('|')
        port_list = []
        for hv_data in hv_datas:
            data = {}
            data = ast.literal_eval(hv_data)
            try:
                msg = "Add port to host %s" % data['hosts']['value']
                customlogs(msg, logfile)
                host = data['hosts']['value']
                port = data['ports']['value']
                port_list = port.split(',')
                if "iqn" in port_list[0]:
                    opdict = self.handle.set_host(host, addiqnlist=port_list)
                else:
                    opdict = self.handle.set_host(host, addwwnlist=port_list)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Added port to host successfully", logfile)
            except PureHTTPError as e:
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Failed to add port to host", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to add port to host")
                return obj
        msg = "Added ports to hosts successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def create_host_group(self, inputs, logfile):
        """
        Create Host Group

        :param inputs: Dictonary(name)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        tdict = {}
        opdict = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle for FlashArray")
            return obj

        try:
            hgname = inputs['hgname']
            tdict = self.handle.create_hgroup(hgname)
            tdict['hgname'] = inputs['hgname']
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Host group created successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to create host group", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to create host group")
        return obj

    def connect_host(self, inputs, logfile):
        """
        Connect Voume to host

        :param inputs: Dictonary(hostname, volumename)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        dictopt = {}
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        dicts['hvmap_set'] = inputs['hvmap_set']
        hv_datas = inputs['hvmap_set'].split('|')
        for hv_data in hv_datas:
            data = {}
            data = ast.literal_eval(hv_data)
            try:
                msg = "Connecting volume %s to host %s" % (
                    data['volumename']['value'], data['hostname']['value'])
                customlogs(msg, logfile)
                hostname = data['hostname']['value']
                volName = data['volumename']['value']
                dictopt = self.handle.connect_host(hostname, volName)
                obj.setResult(dicts, PTK_OKAY, "Success")
                customlogs("Connected volume to host successfully", logfile)

            except PureHTTPError as e:
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("connect volume to host", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to connect volume to host")
                return obj

        msg = "Connected volumes to hosts successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY, "Connected volume to host successfully")
        return obj

    def connect_host_group(self, inputs, logfile):
        """
        Connect Voume to host group

        :param inputs: Dictonary(hgname, volumename)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        dicts = {}
        try:
            hgname = inputs['hgname']
            volName = inputs['volumename']
            dicts = self.handle.connect_hgroup(hgname, volName)
            obj.setResult(dicts, PTK_OKAY, "Success")
            customlogs(
                "Connected volume to host group successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to connect volume to host group", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to connect volume to hostgroup")
        return obj

    def add_host_to_hostgroup(self, inputs, logfile):
        """
        Add Host to host group

        :param inputs: Dictonary(hgname, hostlist)
        :param logfile: Logfile name  
        :return: Retuns status 
        """

        obj = result()
        opdict = {}
        tdict = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        try:
            name = inputs['hgname']
            host_list = inputs['hosts'].split("|")
            tdict = self.handle.set_hgroup(name, addhostlist=host_list)
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Added host to host group successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to add host to host group", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to add host to hostgroup")
        return obj

    def list_host_groups(self):
        """
        List host groups

        :return: Retuns host group list 
        """

        obj = result()
        tdict = {}
        try:
            tdict = self.handle.list_hgroups()
            obj.setResult(tdict, PTK_OKAY, "Success")
        except PureHTTPError as e:
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to list the host groups")
            loginfo(str(e))
        return obj

    def get_host_list(self):
        """
        List hosts

        :return: Retuns host list 
        """

        obj = result()
        opdict = {}

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        try:
            opdict = self.handle.list_hosts()
            obj.setResult(opdict, PTK_OKAY, "Success")
        except PureHTTPError as e:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Failed to get the list of hosts")
            loginfo(str(e))
        return obj

    def get_volume_list(self):
        """
        List volumes

        :return: Retuns volume list 
        """

        obj = result()
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        tdict = {}
        try:
            tdict = self.handle.list_volumes()
            obj.setResult(tdict, PTK_OKAY, "Success")
        except PureHTTPError as e:
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to get the list of volumes")
        return obj

    def get_ports(self, blade_cnt=0, fc_ports=False):
        """
        List ports, In case of FC waits for all ports to be discovered

        :param blade_cnt: Blade Count 
        :param fc_ports: if True FC ports are returned
        :return: Retuns the port list 
        """

        obj = result()
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        opdict = {}
        try:
            retry = 0
            all_wwn_cnt = blade_cnt * 2
            while retry < 20:
                opdict = self.handle.list_ports(initiators=True)
                if not opdict:
                    loginfo("Waiting for the port list to be available")
                    time.sleep(20)
                    retry += 1
                elif fc_ports:
                    ct0_wwns = []
                    ct1_wwns = []
                    for ports in opdict:
                        if "CT0" in str(ports['target']):
                            ct0_wwns.append(str(ports['wwn']))
                        if "CT1" in str(ports['target']):
                            ct1_wwns.append(str(ports['wwn']))
                    if len(set(ct0_wwns)) < all_wwn_cnt and len(set(ct1_wwns)) < all_wwn_cnt:
                        loginfo("Waiting to get the list of wwns for all host")
                        time.sleep(20)
                        retry += 1
                    else:
                        break
                else:
                    break
            if not opdict:
                dicts['status'] = "FAILURE"
                loginfo("Failed to get the ports ")
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to get the  ports")
                return obj

            obj.setResult(opdict, PTK_OKAY, "Success")
        except PureHTTPError as e:
            obj.setResult(opdict, PTK_INTERNALERROR, "Failed to get the ports")
            loginfo(str(e))
        return obj

    def get_network_interfaces(self, ip_addr):
        """
        returns MAC Address 

        :param ip_addr: ip address of interface 
        :return: MAC Address
        """

        dicts = {}
        res = result()
        hw_address = None
        try:
            dicts = self.handle.list_network_interfaces()
            for dd in dicts:
                if dd['address'] == ip_addr:
                    hw_address = dd['hwaddr']
        except PureHTTPError as e:
            loginfo(str(e))
            res.setResult(None, PTK_INTERNALERROR,
                          "Failed to get the Network interface details")
            return res

        res.setResult(hw_address, PTK_OKAY, "Success")
        return res

    def get_array(self):
        """
        returns FlashArray name, version

        :return: name, version
        """

        dicts = {}
        try:
            dicts = self.handle.get()
        except PureHTTPError as e:
            loginfo(str(e))
            return (None, None, None)
        return dicts['array_name'], dicts['version']

    def getSerial_no(self, ip):
        """
        returns Serial number for FlashArray 

        :param ip: ip address of managment interface 
        :return: serial no
        """

        import paramiko
        user = self.username
        pwd = self.pwd
        host = ip
        serial_no = ''
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=user, password=pwd)
            cmd = "purehw list --all --type ch"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdin.close()

            data = ' '
            data = stdout.read().splitlines()[1]
            res = data.split(' ')
            serial_no = str(res[-3])

        except PureHTTPError as e:
            loginfo(str(e))
            serial_no = None
        return serial_no

    def get_array_controller(self):
        """
        returns Model No

        :return: Model Number
        """

        dicts = {}
        model = None
        try:
            dicts = self.handle.get(controllers=True)
            model = dicts[0]['model']
            if model == None:
                model = dicts[1]['model']
        except PureHTTPError as e:
            loginfo("Get array controller is failed")
            loginfo(str(e))
        return model

    def get_fc_port_list(self):
        """
        returns FC port list from FlashArray 

        :return: FC port list
        """

        obj = result()
        data = []

        if self.handle == None:
            obj.setResult(data, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        try:
            ports = self.handle.list_ports()
            ports = json.loads(json.dumps(ports))
            for mdict in ports:
                kdict = {}
                kdict['name'] = mdict['name']
                kdict['wwn'] = mdict['wwn']
                data.append(kdict)
            obj.setResult(data, PTK_OKAY, "Success")

        except PureHTTPError as e:
            obj.setResult(data, PTK_INTERNALERROR,
                          "Failed to get the list of hosts")
            loginfo(str(e))
        return obj

    def get_iscsi_port_list(self):
        """
        returns iSCSI port list from FlashArray 

        :return: iSCSI port list
        """

        obj = result()
        data = []

        if self.handle == None:
            obj.setResult(data, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        try:
            ports = self.handle.list_ports()
            ports = json.loads(json.dumps(ports))
            for mdict in ports:
                kdict = {}
                kdict['name'] = mdict['name']
                kdict['iqn'] = mdict['iqn']
                data.append(kdict)
            obj.setResult(data, PTK_OKAY, "Success")

        except PureHTTPError as e:
            obj.setResult(data, PTK_INTERNALERROR,
                          "Failed to get the list of hosts")
            loginfo(str(e))
        return obj

    def getWwnFormat(self, wwn):
        k = 0
        u_wwn = ''
        for i in list(wwn):
            u_wwn = u_wwn + i
            k += 1
            if k % 2 == 0 and k != len(wwn):
                u_wwn += ':'
        return u_wwn

    def get_port_number(self, inputs, logfile):
        port_dict = {}
        obj = result()
        if self.handle == None:
            obj.setResult(port_dict, PTK_INTERNALERROR, "Unable to get Handle")
            return obj
        try:
            port_dict['pwwn'] = None
            name = inputs['name'].upper()
            ports = self.handle.list_ports()
            ports = json.loads(json.dumps(ports))
            for mdict in ports:
                cname = mdict["name"]
                if str(name) == str(cname):
                    if mdict['wwn'] is not None:
                        port_dict['pwwn'] = self.getWwnFormat(mdict['wwn'])
                    else:
                        port_dict['pwwn'] = mdict['iqn']
            obj.setResult(port_dict, PTK_OKAY, "Success")
            customlogs("Get port number successfull", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to get port number", logfile)
            obj.setResult(port_dict, PTK_INTERNALERROR,
                          "Failed to get port number")
            loginfo(str(e))
        return obj

    def get_iscsi_network_interfaces(self, inputs, logfile):
        """
        returns list of interface with 'iscsi' service configured 

        :param inputs: Dictionary
        :param logfile: Logfile name 
        :return: list of interfaces
        """

        dicts = {}
        res = result()
        try:
            dicts = self.handle.list_network_interfaces()
            iscsi_interfaces = []
            iscsi_list = []
            for mInterface in dicts:
                service = mInterface['services']
                if 'iscsi' in service:
                    iscsi_interfaces.append(mInterface['name'])
                    iscsi_list.append(mInterface)
                else:
                    loginfo("No iscsi network found")
        except PureHTTPError as e:
            loginfo(str(e))
            res.setResult(None, PTK_INTERNALERROR,
                          "Failed to get the iscsi network interfaces list")
            return res

        res.setResult(iscsi_list, PTK_OKAY, "Success")
        return res

    def set_iscsi_network_interface(self, inputs, logfile):
        """
        Configure Network Interface

        :param inputs: Dictionary(address, mtu, netmask, name)
        :param logfile: Logfile name 
        :return: status
        """

        res_dict = {}
        obj = result()
        if self.handle == None:
            obj.setResult(port_dict, PTK_INTERNALERROR, "Unable to get Handle")
            return obj
        try:
            address = inputs['address'].upper()
            enabled = True
            if inputs['enabled'] == "True":
                enabled = True
            else:
                enabled = False
            mtu = inputs['mtu']
            netmask = inputs['netmask']
            interface_name = inputs['name']
            data = {'address': address, 'enabled': enabled,
                    'netmask': netmask, 'mtu': mtu}
            interface_result = self.handle.set_network_interface(
                interface_name, enabled=enabled)
            interface_result = self.handle.set_network_interface(
                interface_name, address=address)
            interface_result = self.handle.set_network_interface(
                interface_name, netmask=netmask)
            interface_result = self.handle.set_network_interface(
                interface_name, mtu=mtu)
            obj.setResult(res_dict, PTK_OKAY, "Success")
            customlogs(
                "Set iscsi network interface completed successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to set iscsi network interface", logfile)
            obj.setResult(port_dict, PTK_INTERNALERROR,
                          "Failed to set iscsi network interface")
        return obj

    def delete_multiple_hosts(self, inputs, logfile):
        """
        Delete multiple Hosts

        :param inputs: Dictionary(name, count)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        opdict = {}

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("delete host inputs  {}".format(inputs))

        name = inputs['name']  # here name is service profile
        st_no = inputs['st_no']
        count = inputs['count']  # count of service profile
        num_digits = inputs['num_digits']
        loginfo("values in delete_multiple_hosts come is {}".format(inputs))
        hosts = self.get_multiple_host_names(name, st_no, count, num_digits)
        for host in hosts:
            try:
                msg = "Deleting host %s" % host
                customlogs(msg, logfile)
                opdict = self.handle.delete_host(host)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Deleted host successfully", logfile)
            except PureHTTPError as e:
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Failed to Delete host", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to delete host")
                loginfo(str(e))
                return obj
        msg = "Deleted hosts successfully\n"
        customlogs(msg, logfile)
        obj.setResult(opdict, PTK_OKAY, msg)
        return obj

    def remove_port_from_host(self, inputs, logfile):
        """
        Delete port from Hosts

        :param inputs: Dictionary(host, port)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("remove_port_from_host inputs  {}".format(inputs))

        dicts['host_set'] = inputs['host_set']
        hv_datas = inputs['host_set'].split('|')
        port_list = []
        for hv_data in hv_datas:
            data = {}
            data = ast.literal_eval(hv_data)
            try:
                msg = "Remove port from host %s" % data['hosts']['value']
                customlogs(msg, logfile)
                host = data['hosts']['value']
                port = data['ports']['value']
                port_list = port.split(',')
                if "iqn" in port_list[0]:
                    opdict = self.handle.set_host(host, remiqnlist=port_list)
                else:
                    opdict = self.handle.set_host(host, remwwnlist=port_list)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs(
                    "Remove port from host completed successfully", logfile)
            except PureHTTPError as e:
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Failed to remove port from host", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to Remove port from host")
                return obj
        msg = "Remove ports from hosts completed successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY, msg)
        return obj

    def delete_multiple_volumes(self, inputs, logfile):
        """
        Delete multiple volumes

        :param inputs: Dictionary(host, port)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("delete volume inputs is {}".format(inputs))

        name = inputs['name']  # here name is service profile
        st_no = inputs['st_no']
        count = inputs['count']  # count of service profile
        num_digits = inputs['num_digits']
        vol_datas = self.get_multiple_vol_names(name, st_no, count, num_digits)

        for vol_data in vol_datas:
            data = {}
            loginfo("vol_data is {} {}".format(vol_data, type(vol_data)))
            #data = eval(vol_data)
            try:
                msg = "Deleting volume %s" % vol_data
                volName = vol_data
                customlogs(msg, logfile)
                opdict = self.handle.destroy_volume(volName)
                opdict = self.handle.eradicate_volume(volName)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Volume deleted successfully", logfile)
            except PureHTTPError as e:
                loginfo("err e is {}".format(e))
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                loginfo("err 0 is {}".format(eval(err)[0]))
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Failed to delete volume", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to delete volume")
                return obj
        msg = "Volumes deleted successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY, msg)
        return obj

    def disconnect_host(self, inputs, logfile):
        """
        Delete multiple volumes

        :param inputs: Dictionary(hostname, volumename)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        dictopt = {}
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        dicts['hvmap_set'] = inputs['hvmap_set']
        hv_datas = inputs['hvmap_set'].split('|')
        for hv_data in hv_datas:
            data = {}
            data = ast.literal_eval(hv_data)
            try:
                msg = "Disconnecting volume %s from host %s" % (
                    data['volumename']['value'], data['hostname']['value'])
                customlogs(msg, logfile)
                hostname = data['hostname']['value']
                volName = data['volumename']['value']
                dictopt = self.handle.disconnect_host(hostname, volName)
                obj.setResult(dicts, PTK_OKAY, "Success")
                customlogs(
                    "Disconnected volume from host successfully", logfile)

            except PureHTTPError as e:
                err = e.text
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Disconnect volume from host task failed", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to disconnect volume from host")
                loginfo(str(e))
                return obj

        msg = "Disconnected volumes from host successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY,
                      "Disconnected volumes from host successfully")
        return obj

    def delete_host_group(self, inputs, logfile):
        """
        Delete Host Group

        :param inputs: Dictionary(hgname)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        tdict = {}
        opdict = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle for FlashArray")
            return obj

        try:
            hgname = inputs['hgname']
            tdict = self.handle.delete_hgroup(hgname)
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Deleted host group successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to delete host group", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to delete hostgroup")
            loginfo(str(e))
        return obj

    def remove_host_from_hostgroup(self, inputs, logfile):
        """
        Remove Host from Host Group

        :param inputs: Dictionary(hgname, hosts)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        opdict = {}
        tdict = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        try:
            name = inputs['hgname']
            host_list = inputs['hosts'].split("|")
            tdict = self.handle.set_hgroup(name, remhostlist=host_list)
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Removed host from host group successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to remove host from hostgroup", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to remove host from hostgroup")
            loginfo(str(e))
        return obj

    def delete_shared_volume(self, inputs, logfile):
        """
        Delete shared volume

        :param inputs: Dictionary(name)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("Delete Shared Volume inputs is : {}".format(inputs))

        try:
            volName = inputs['name']
            msg = "Deleting shared volume %s" % volName
            customlogs(msg, logfile)
            opdict = self.handle.destroy_volume(volName)
            opdict = self.handle.eradicate_volume(volName)
            obj.setResult(opdict, PTK_OKAY, "Success")
            customlogs("Deleted shared volume successfully", logfile)
        except PureHTTPError as e:
            loginfo("err e is {}".format(e))
            err = e.text
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            loginfo("err 0 is {}".format(eval(err)[0]))
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to delete shared volume", logfile)
            obj.setResult(opdict, PTK_INTERNALERROR, "Failed to delete volume")
            loginfo(" Error {}".format(str(e)))
            return obj
        msg = "Deleted shared volume successfully\n"
        customlogs(msg, logfile)
        obj.setResult(dicts, PTK_OKAY, msg)
        return obj

    def disconnect_host_group(self, inputs, logfile):
        """
        Disconnect volume from host group

        :param inputs: Dictionary(hgname, volumename)
        :param logfile: Logfile name 
        :return: status
        """

        obj = result()
        dicts = {}
        try:
            hgname = inputs['hgname']
            volName = inputs['volumename']
            dicts = self.handle.disconnect_hgroup(hgname, volName)
            obj.setResult(dicts, PTK_OKAY, "Success")
            customlogs(
                "Disconnected volume from host group successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs(
                "Failed to disconnect volume from host group", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to disconnect volume from hostgroup")
            loginfo(str(e))
        return obj

    def remove_iscsi_network_interface(self, inputs, logfile):
        res_dict = {}
        obj = result()
        if self.handle == None:
            obj.setResult(port_dict, PTK_INTERNALERROR, "Unable to get Handle")
            return obj
        try:
            address = None  # inputs['address'].upper()
            enabled = False  # inputs['enabled']
            mtu = inputs['mtu']
            netmask = inputs['netmask']
            interface_name = inputs['name']
            data = {'address': address, 'enabled': enabled,
                    'netmask': netmask, 'mtu': mtu}
            interface_result = self.handle.set_network_interface(
                interface_name, enabled=enabled)
            interface_result = self.handle.set_network_interface(
                interface_name, address=address)
            interface_result = self.handle.set_network_interface(
                interface_name, netmask=netmask)
            interface_result = self.handle.set_network_interface(
                interface_name, mtu=mtu)
            obj.setResult(res_dict, PTK_OKAY, "Success")
            customlogs(
                "Removed iscsi network interface successfully", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Failed to remove iscsi network interface", logfile)
            obj.setResult(port_dict, PTK_INTERNALERROR,
                          "Failed to remove iscsi network interface")
            loginfo(str(e))
        return obj

    def get_fa_ports(self):
        fc_ports = self.handle.list_ports()
        ethernet_ports = self.handle.list_network_interfaces()
#	model = "XR2"
        model = self.get_array_controller()
        if model in ["FA-X10R2", "FA-X20R2", "FA-X50R2", "FA-X70R2", "FA-X90R2"]:
            for port in ethernet_ports:
                if port['speed'] == 1000000000 and 'eth4' in port['name']:
                    return ["eth4", "eth5"]
                elif port['speed'] == 4000000000 and 'eth14' in port['name']:
                    return ["eth14", "eth15"]
        else:
            if fc_ports:
                return ["eth8", "eth9"]
            else:
                return ["eth4", "eth5"]
