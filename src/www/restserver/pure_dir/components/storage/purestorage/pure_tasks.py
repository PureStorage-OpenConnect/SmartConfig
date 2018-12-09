from purestorage import PureError, PureHTTPError
import json, time
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

    def pure_switch_info(self, ip):
        obj = result()
        loginfo("comes in pure_switch_info ip : {}".format(ip))
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
        if all(switch.values()) == True:
            loginfo("PURE Switch details: %s" % str(switch))
            return switch
        else:
            loginfo("PURE partial switch details: %s" % str(switch))
            loginfo("Failed to retrieve pure switch details fully")
            return switch

    def release_pure_handle(self):
        res = result()
        try:
            self.handle.invalidate_cookie()
        except PureError:
            res.setResult(None, PTK_INTERNALERROR,
                          "Failed to release the pure handle")
            return res

        res.setResult(None, PTK_OKAY, "Success")
        return res

    def get_multiple_names(self, name, st_no, count, num_digits):
        loginfo("data is {} {} {} {}".format(name, st_no, count, num_digits))
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
            customlogs("Create volume task is succeeded", logfile)
        except PureHTTPError as e:
            loginfo("err e is {}".format(e))
            err = e.text
            dicts['status'] = "FAILURE"
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            loginfo("err 0 is {}".format(eval(err)[0]))
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Create shared volume task is failed", logfile)
            obj.setResult(opdict, PTK_INTERNALERROR, "Failed to create volume")
            loginfo(" Error {}".format(str(e)))
            return obj
        msg = "Create shared volume succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
	dicts['name'] = inputs['name']
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def create_multiple_volumes(self, inputs, logfile):
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
        # st_no = int(a.split(':')[-1]) # getting list 01 of wwn
        st_no = inputs['st_no']
        count = inputs['count']  # count of service profile
        num_digits = inputs['num_digits']
        vol_datas = self.get_multiple_vol_names(name, st_no, count, num_digits)

        for vol_data in vol_datas:
            data = {}
            loginfo("vol_data is {} {}".format(vol_data, type(vol_data)))
            #data = eval(vol_data)
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
                customlogs("Create volume task is succeeded", logfile)
            except PureHTTPError as e:
                loginfo("err e is {}".format(e))
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                loginfo("err 0 is {}".format(eval(err)[0]))
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Create volume task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to create volume")
                return obj
        msg = "Crete volume succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def create_host(self, inputs, logfile):
        obj = result()
        opdict = {}
        dicts = {}
        mult_output = ""

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("create host inputs is {}".format(inputs))
        #dicts['host_set'] = inputs['host_set']
        #hv_datas = inputs['host_set'].split('|')
        #portlist = inputs['ports'].split('|')

        a = "20:00:00:25:B5:01:0A:01"  # wwn for getting prefix
        name = 'VM-Host-infra-#'  # here name is service profile
        st_no = int(a.split(':')[-1])  # getting list 01 of wwn
        st_no = st_no if st_no > 0 else st_no+1
        count = 3  # count of service profile
        num_digits = 2
        hv_datas = self.get_multiple_host_names(name, st_no, count, num_digits)
        k = 0
        ports = data['ports']['value']  # list of initiator ports
        for h in range(0, len(hv_datas)):
            host = hv_datas[h]
            port_list = []
            #global k
            data = {}
            data = eval(hv_data)
            try:
                msg = "Creating host %s" % host
                customlogs(msg, logfile)
                if k < len(ports):
                    for p in range(0, 2):
                        port_list.append(ports[k])
                        k = k+1
                if "iqn" in port_list[0]:
                    opdict = self.handle.create_host(host, iqnlist=port_list)
                else:
                    opdict = self.handle.create_host(host, wwnlist=port_list)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Create host task is succeeded", logfile)
            except PureHTTPError as e:
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Create host task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to create host")
                return obj
        msg = "Crete host succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def create_multiple_hosts(self, inputs, logfile):
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
        loginfo("values in create_multiple_hosts comes is {}".format(inputs))
        hosts = self.get_multiple_host_names(name, st_no, count, num_digits)
        for host in hosts:
            try:
                msg = "Creating host %s" % host
                customlogs(msg, logfile)
                opdict = self.handle.create_host(host)
                obj.setResult(opdict, PTK_OKAY, "Success")
                customlogs("Create host task is succeeded", logfile)
            except PureHTTPError as e:
                err = e.text
                opdict['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Create host task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to create host")
                return obj
        msg = "Create host succeeded\n"
        customlogs(msg, logfile)
        opdict['status'] = "SUCCESS"
        obj.setResult(opdict, PTK_OKAY,
                      msg)
        return obj

    def add_port_to_host(self, inputs, logfile):
        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("add_port_to_host inputs is {}".format(inputs))

        dicts['host_set'] = inputs['host_set']
        hv_datas = inputs['host_set'].split('|')
        port_list = []
        # ports = data['ports']['value'] #list of initiator ports
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
                customlogs("Add port to host task is succeeded", logfile)
            except PureHTTPError as e:
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Add port to host task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to add port to host")
                return obj
        msg = "Add port to host succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY,
                      msg)
        return obj

    def add_port_to_host_old(self, inputs, logfile):
        obj = result()
        opdict = {}
        tdict = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle for FlashArray")
            return obj

        a = "20:00:00:25:B5:01:0A:01"  # wwn for getting prefix
        name = 'VM-Host-infra-#'  # here name is service profile
        st_no = int(a.split(':')[-1])  # getting list 01 of wwn
        st_no = st_no if st_no > 0 else st_no+1
        count = 3  # count of service profile
        num_digits = 2
        hosts = self.get_multiple_host_names(name, st_no, count, num_digits)

        try:
            hostname = inputs['name']
            portlist = inputs['ports']
            portlist = portlist.split("|")
            if "iqn" in portlist[0]:
                tdict = self.handle.set_host(hostname, addiqnlist=portlist)
            else:
                tdict = self.handle.set_host(hostname, addwwnlist=portlist)
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Add port to host task is succeeded", logfile)

        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Add port to host task is failed", logfile)
            obj.setResult(dict, PTK_INTERNALERROR, "Failed to create host")
        return obj

    def create_host_group(self, inputs, logfile):
        obj = result()
        tdict = {}
        opdict = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle for FlashArray")
            return obj

        try:
            hgname = inputs['hgname']
            #hostlist = inputs['hostlist']
            #hostlist = hostlist.split("|")
            #tdict = self.handle.create_hgroup(hgname, hostlist=hostlist)
            tdict = self.handle.create_hgroup(hgname)
	    tdict['hgname'] = inputs['hgname']
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Create host group task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Create host group task is failed", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to create hostgroup")
        return obj

    def connect_host(self, inputs, logfile):
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
                customlogs("Connect host task is succeeded", logfile)

            except PureHTTPError as e:
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Connect volume to host task is failed", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to connect host to volume")
                return obj

        msg = "Connect volume to host succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY, "Connect volume to host  completed")
        return obj

    def connect_host_group(self, inputs, logfile):
        obj = result()
        dicts = {}
        try:
            hgname = inputs['hgname']
            volName = inputs['volumename']
            dicts = self.handle.connect_hgroup(hgname, volName)
            obj.setResult(dicts, PTK_OKAY, "Success")
            customlogs(
                "Connect volume to host group task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Connect volume to host group task is failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to connect host to hostgroup")
        return obj

    def add_host_to_hostgroup(self, inputs, logfile):
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
            #addhostlist = {"addhostlist": inputs['hostlist'].split("|")}
            tdict = self.handle.set_hgroup(name, addhostlist=host_list)
            obj.setResult(tdict, PTK_OKAY, "Success")
            customlogs("Add host to host group task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Add host to host group task is failed", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to add host to hostgroup")
        return obj

    def list_host_groups(self):
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

    def get_ports(self, blade_cnt=0, fc_ports= False):
        obj = result()
	dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj

        opdict = {}
        try:
	    retry = 0
	    all_wwn_cnt = blade_cnt*2
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
        	obj.setResult(dicts, PTK_INTERNALERROR,"Failed to get the  ports")
	        return obj

            obj.setResult(opdict, PTK_OKAY, "Success")
        except PureHTTPError as e:
            obj.setResult(opdict, PTK_INTERNALERROR, "Failed to get the ports")
            loginfo(str(e))
        return obj

    def get_network_interfaces(self, ip_addr):
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

# gives array name and id(serial)
    def get_array(self):
        dicts = {}
        try:
            dicts = self.handle.get()
        except PureHTTPError as e:
            loginfo(str(e))
            return (None, None, None)
        return dicts['array_name'], dicts['version']

    def getSerial_no(self, ip):
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

# gives model
    def get_array_controller(self):
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

    def get_fc_controller_list(self):
        obj = result()
        opdict = {}
        data = []

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
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
            opdict['status'] = "SUCCESS"
            opdict['name'] = data
            obj.setResult(data, PTK_OKAY, "Success")

        except PureHTTPError as e:
            obj.setResult(data, PTK_INTERNALERROR,
                          "Failed to get the list of hosts")
            loginfo(str(e))
        return obj

    def get_iscsi_controller_list(self):
        obj = result()
        opdict = {}
        data = []

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
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
            opdict['status'] = "SUCCESS"
            opdict['name'] = data
            obj.setResult(data, PTK_OKAY, "Success")

        except PureHTTPError as e:
            obj.setResult(data, PTK_INTERNALERROR,
                          "Failed to get the list of hosts")
            loginfo(str(e))
        return obj


    def get_controller(self, inputs, logfile):
        obj = result()
        controller_dict = {}
        if self.handle == None:
            obj.setResult(controller_dict, PTK_INTERNALERROR,
                          "Unable to get Handle")
            return obj

        try:
            controller_dict['name'] = None
            if "iqn" in inputs['pwwn']:
                pwwn = inputs['pwwn']
            else:
                pwwn = inputs['pwwn'].replace(':', '')
            ports = self.handle.list_ports()
            ports = json.loads(json.dumps(ports))
            for mdict in ports:
                if "iqn" in pwwn:
                    iqnOrwwn = mdict["iqn"]
                else:
                    iqnOrwwn = mdict["wwn"]
                if str(pwwn) == str(iqnOrwwn):
                    controller_dict['name'] = mdict['name']
            controller_dict['status'] = "SUCCESS"
            obj.setResult(controller_dict, PTK_OKAY, "Success")
            customlogs("Get controller task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Get controller task is failed", logfile)
            obj.setResult(controller_dict, PTK_INTERNALERROR,
                          "Failed to get controller")
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

# gives port number
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
            port_dict['status'] = "SUCCESS"
            obj.setResult(port_dict, PTK_OKAY, "Success")
            customlogs("Get port number task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Get port number task is failed", logfile)
            obj.setResult(port_dict, PTK_INTERNALERROR,
                          "Failed to get port number")
            loginfo(str(e))
        return obj

# list network interfaces for iscsi
    def get_iscsi_network_interfaces(self, inputs, logfile):
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
                    loginfo( "No iscsi network found")
        except PureHTTPError as e:
            loginfo(str(e))
            res.setResult(None, PTK_INTERNALERROR,
                          "Failed to get the iscsi network interfaces list")
            return res

        res.setResult(iscsi_list, PTK_OKAY, "Success")
        return res

# configures iscsi network interface
    def set_iscsi_network_interface(self, inputs, logfile):
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
            #interface_result = self.handle.set_network_interface(address=address)
            interface_result = self.handle.set_network_interface(
                interface_name, enabled=enabled)
            interface_result = self.handle.set_network_interface(
                interface_name, address=address)
            interface_result = self.handle.set_network_interface(
                interface_name, netmask=netmask)
            interface_result = self.handle.set_network_interface(
                interface_name, mtu=mtu)
            res_dict['status'] = "SUCCESS"
            obj.setResult(res_dict, PTK_OKAY, "Success")
            customlogs("Set iscsi network interface task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Set iscsi network interface task is failed", logfile)
            obj.setResult(port_dict, PTK_INTERNALERROR,
                          "Failed to set iscsi network interface")
        return obj


# rollback functionality ....................................................

    def delete_multiple_hosts(self, inputs, logfile):
        obj = result()
        opdict = {}

        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("delete host inputs is {}".format(inputs))

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
                customlogs("Delete host task is succeeded", logfile)
            except PureHTTPError as e:
                err = e.text
                opdict['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Delete host task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to delete host")
                loginfo(str(e))
                return obj
        msg = "Delete host succeeded\n"
        customlogs(msg, logfile)
        opdict['status'] = "SUCCESS"
        obj.setResult(opdict, PTK_OKAY, msg)
        return obj

    def remove_port_from_host(self, inputs, logfile):
        obj = result()
        opdict = {}
        dicts = {}
        if self.handle == None:
            obj.setResult(opdict, PTK_INTERNALERROR,
                          "Unable to get Handle to FlashArray")
            return obj
        loginfo("remove_port_from_host inputs is {}".format(inputs))

        dicts['host_set'] = inputs['host_set']
        hv_datas = inputs['host_set'].split('|')
        port_list = []
        # ports = data['ports']['value'] #list of initiator ports
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
                customlogs("Remove port from host task is succeeded", logfile)
            except PureHTTPError as e:
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Remove port to host task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to Remove port from host")
                return obj
        msg = "Remove port from host succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY, msg)
        return obj

    def delete_multiple_volumes(self, inputs, logfile):
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
                customlogs("Delete volume task is succeeded", logfile)
            except PureHTTPError as e:
                loginfo("err e is {}".format(e))
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                loginfo("err 0 is {}".format(eval(err)[0]))
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Delete volume task is failed", logfile)
                obj.setResult(opdict, PTK_INTERNALERROR,
                              "Failed to delete volume")
                return obj
        msg = "Delete volume succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY, msg)
        return obj

    def disconnect_host(self, inputs, logfile):
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
                msg = "Disconnecting volume %s to host %s" % (
                    data['volumename']['value'], data['hostname']['value'])
                customlogs(msg, logfile)
                hostname = data['hostname']['value']
                volName = data['volumename']['value']
                dictopt = self.handle.disconnect_host(hostname, volName)
                obj.setResult(dicts, PTK_OKAY, "Success")
                customlogs("Disconnect host task is succeeded", logfile)

            except PureHTTPError as e:
                err = e.text
                dicts['status'] = "FAILURE"
                customlogs(msg, logfile)
                customlogs("Error message is :", logfile)
                customlogs(eval(err)[0]['msg'], logfile)
                customlogs("Disconnect volume to host task is failed", logfile)
                obj.setResult(dicts, PTK_INTERNALERROR,
                              "Failed to disconnect host to volume")
                loginfo(str(e))
                return obj

        msg = "Disconnect volume to host succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY, "Disconnect volume to host completed")
        return obj

    def delete_host_group(self, inputs, logfile):
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
            customlogs("Delete host group task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Delete host group task is failed", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to delete hostgroup")
            loginfo(str(e))
        return obj

    def remove_host_from_hostgroup(self, inputs, logfile):
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
            customlogs("Remove host from host group task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Remove host from host group task is failed", logfile)
            obj.setResult(tdict, PTK_INTERNALERROR,
                          "Failed to remove host from hostgroup")
            loginfo(str(e))
        return obj

    def delete_shared_volume(self, inputs, logfile):
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
            customlogs("Delete volume task is succeeded", logfile)
        except PureHTTPError as e:
            loginfo("err e is {}".format(e))
            err = e.text
            dicts['status'] = "FAILURE"
            customlogs(msg, logfile)
            customlogs("Error message is :", logfile)
            loginfo("err 0 is {}".format(eval(err)[0]))
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Delete shared volume task is failed", logfile)
            obj.setResult(opdict, PTK_INTERNALERROR, "Failed to delete volume")
            loginfo(" Error {}".format(str(e)))
            return obj
        msg = "Delete shared volume succeeded\n"
        customlogs(msg, logfile)
        dicts['status'] = "SUCCESS"
        obj.setResult(dicts, PTK_OKAY, msg)
        return obj

    def disconnect_host_group(self, inputs, logfile):
        obj = result()
        dicts = {}
        try:
            hgname = inputs['hgname']
            volName = inputs['volumename']
            dicts = self.handle.disconnect_hgroup(hgname, volName)
            obj.setResult(dicts, PTK_OKAY, "Success")
            customlogs(
                "Disconnect volume to host group task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs(
                "Disconnect volume to host group task is failed", logfile)
            obj.setResult(dicts, PTK_INTERNALERROR,
                          "Failed to disconnect host to hostgroup")
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
            #interface_result = self.handle.set_network_interface(address=address)
            interface_result = self.handle.set_network_interface(
                interface_name, enabled=enabled)
            interface_result = self.handle.set_network_interface(
                interface_name, address=address)
            interface_result = self.handle.set_network_interface(
                interface_name, netmask=netmask)
            interface_result = self.handle.set_network_interface(
                interface_name, mtu=mtu)
            res_dict['status'] = "SUCCESS"
            obj.setResult(res_dict, PTK_OKAY, "Success")
            customlogs(
                "Remove iscsi network interface task is succeeded", logfile)
        except PureHTTPError as e:
            err = e.text
            customlogs(eval(err)[0]['msg'], logfile)
            customlogs("Remove iscsi network interface task is failed", logfile)
            obj.setResult(port_dict, PTK_INTERNALERROR,
                          "Failed to remove iscsi network interface")
            loginfo(str(e))
        return obj

    def get_fa_ports(self):
        fc_ports = self.handle.list_ports()
        ethernet_ports = self.handle.list_network_interfaces()
#	model = "XR2"
	model = self.get_array_controller()
	if model in ["FA-X10R2", "FA-X20R2", "FA-X50R2", "FA-X70R2", "FA-X90R2"] :
            for port in ethernet_ports:
	        if port['speed'] == 1000000000 and 'eth4' in port['name']:
                    return ["eth4","eth5"]
	        elif port['speed'] == 4000000000 and 'eth14' in port['name']:
                    return ["eth14","eth15"]
	else:
            if fc_ports:
                return ["eth8","eth9"]
            else:
                return ["eth4","eth5"]
