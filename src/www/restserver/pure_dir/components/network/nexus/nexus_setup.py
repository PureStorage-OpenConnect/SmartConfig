from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.common import *
import os
import time
import glob
import json

static_discovery_store = "/mnt/system/pure_dir/pdt/devices.xml"

poap_n9k_py_template = "/mnt/system/pure_dir/pdt/templates/components/nexus/poap.n9k.py.template"
poap_n5k_py_template = "/mnt/system/pure_dir/pdt/templates/components/nexus/poap.n5k.py.template"
poap_n9k_cfg_template = "/mnt/system/pure_dir/pdt/templates/components/nexus/poap.n9k.cfg.template"
poap_n5k_fc_cfg_template = "/mnt/system/pure_dir/pdt/templates/components/nexus/poap.n5k.fc.cfg.template"
poap_n5k_iscsi_cfg_template = "/mnt/system/pure_dir/pdt/templates/components/nexus/poap.n5k.iscsi.cfg.template"
poap_n9k_py_tgt = "/mnt/system/pure_dir/pdt/targets/nexus/poap_n9k.py"
poap_n5k_py_tgt = "/mnt/system/pure_dir/pdt/targets/nexus/poap_n5k.py"
tgt_dir = "/mnt/system/pure_dir/pdt/targets/nexus"
poap_n9k_py = "/var/lib/tftpboot/poap_n9k.py"
poap_n5k_py = "/var/lib/tftpboot/poap_n5k.py"
tftp_dir = "/var/lib/tftpboot/"
image_dir = "/mnt/system/uploads/"


class NEXUSSetup:
    def __init__(self):
        cmd = "mkdir %s" % (tgt_dir)
        execute_local_command(cmd)

    def _save_nexus_9k_details(self, ipaddress, netmask, gateway, ntp_server, username, password, serial_no, mac, model,
                               device_type, image_version, switch_image, configured, name, tag, reachability,
                               validated, domain_name):
        """
        Saves the nexus device details to devices.xml

        :param ipaddress: IP address of nexus switch
        :param netmask: Netmask address
        :param gateway: Gateway address
        :param ntp_server: NTP server
        :param username: Username for nexus switch
        :param password: Password for nexus switch
        :param serial_no: Serial number of nexus switch
        :param mac: MAC address of nexus switch
        :param model: Model number of nexus switch
        :param device_type: Device Type
        :param image_version: NX-OS Image version
        :param switch_image: NX-OS Image
        :param configured: Configuration state
        :param name: Name of the nexus switch
        :param reachability: Reachability status
        :param validated: Validated state
        :param domain_name: Domain name for nexus switch
        """
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(static_discovery_store, data)

    def _save_nexus_5k_details(self, ipaddress, netmask, gateway, ntp_server, username, password, serial_no, mac, model,
                               device_type, image_version, switch_kickstart_image, switch_system_image, configured,
                               name, tag, reachability, validated, domain_name):
        """
        Saves the nexus device details to devices.xml

        :param ipaddress: IP address of nexus switch
        :param netmask: Netmask address
        :param gateway: Gateway address
        :param ntp_server: NTP server
        :param username: Username for nexus switch
        :param password: Password for nexus switch
        :param serial_no: Serial number of nexus switch
        :param mac: MAC address of nexus switch
        :param model: Model number of nexus switch
        :param device_type: Device Type
        :param image_version: NX-OS Image version
        :param switch_kickstart_image: NX-OS kickstart image
        :param switch_system_image: NX-OS system image
        :param configured: Configuration state
        :param name: Name of the nexus switch
        :param reachability: Reachability status
        :param validated: Validated state
        :param domain_name: Domain name for nexus switch
        """
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(static_discovery_store, data)

    def nexus9kconfigure(self, data):
        """
        Configures the nexus 9k switch which is in factory reset state

        :param data: Dictionary (switch_name, switch_mac, switch_serial_no, switch_vendor, ntp_server, switch_gateway, switch_ip, switch_netmask, switch_image)

        :return: Returns the configuration status
        """
        res = result()

        loginfo("Initial Configuration of Nexus 9k switch %s started" %
                data['switch_name'])
        loginfo(data)

        update_xml_element(static_discovery_store, matching_key="mac", matching_value=data['switch_mac'],
                           data={"configured": "In-progress", "timestamp": str(time.time())})
        self.createconfig(data['switch_name'], data['ntp_server'], data['switch_gateway'],
                          data['switch_ip'], data['switch_netmask'], data['switch_mac'], poap_n9k_cfg_template, data['domain_name'])

        nexus_py = {}
        nexus_py['server_ip'] = get_ip_address(get_filtered_ifnames()[0])
        nexus_py['switch_image'] = data['switch_image']
        gen_from_template(
                poap_n9k_py_template, nexus_py, poap_n9k_py_tgt)

        loginfo("Created poap file for Nexus switch %s" % data['switch_name'])

        cmd = "cp %s %s" % (poap_n9k_py_tgt, poap_n9k_py)
        execute_local_command(cmd)
        self.createmd5_py(poap_n9k_py)

        image_path = image_dir + data['switch_image']
        cmd = "cp %s %s" % (image_path, tftp_dir)
        execute_local_command(cmd)
        self.createmd5(data['switch_image'])

        loginfo("All configuration files ready for Nexus 9k switch %s" %
                data['switch_name'])

        loginfo("Initial Configuration of Nexus 9k switch %s completed" %
                data['switch_name'])
        res.setResult(True, PTK_OKAY, "Successfully configured nexus 9k")
        return res

    def nexus5kconfigure(self, data):
        """
        Configures the nexus 5k switch which is in factory reset state

        :param data: Dictionary (switch_name, switch_mac, switch_serial_no, switch_vendor, ntp_server, switch_gateway, switch_ip, switch_netmask, switch_kickstart_image, switch_system_image)

        :return: Returns the configuration status
        """
        res = result()

        loginfo("Initial Configuration of Nexus 5k switch %s started" %
                data['switch_name'])
        loginfo(data)

        update_xml_element(static_discovery_store, matching_key="mac", matching_value=data['switch_mac'],
                           data={"configured": "In-progress", "timestamp": str(time.time())})

        stacktype = get_xml_element("/mnt/system/pure_dir/pdt/settings.xml", "stacktype")[1][0]['stacktype']
	if "fc" in stacktype:
            self.createconfig(data['switch_name'], data['ntp_server'], data['switch_gateway'],
                          data['switch_ip'], data['switch_netmask'], data['switch_mac'], poap_n5k_fc_cfg_template, data['domain_name'])
	else:
            self.createconfig(data['switch_name'], data['ntp_server'], data['switch_gateway'],
                          data['switch_ip'], data['switch_netmask'], data['switch_mac'], poap_n5k_iscsi_cfg_template, data['domain_name'])

        nexus_py = {}
        nexus_py['server_ip'] = get_ip_address(get_filtered_ifnames()[0])
        nexus_py['switch_kickstart_image'] = data['switch_kickstart_image']
        nexus_py['switch_system_image'] = data['switch_system_image']
        gen_from_template(
                poap_n5k_py_template, nexus_py, poap_n5k_py_tgt)

        loginfo("Created poap file for Nexus switch %s" % data['switch_name'])

        cmd = "cp %s %s" % (poap_n5k_py_tgt, poap_n5k_py)
        execute_local_command(cmd)
        self.createmd5_py(poap_n5k_py)

        image_path = image_dir + data['switch_kickstart_image']
        cmd = "cp %s %s" % (image_path, tftp_dir)
        execute_local_command(cmd)
        self.createmd5(data['switch_kickstart_image'])

        image_path = image_dir + data['switch_system_image']
        cmd = "cp %s %s" % (image_path, tftp_dir)
        execute_local_command(cmd)
        self.createmd5(data['switch_system_image'])

        loginfo("All configuration files ready for Nexus 5k switch %s" %
                data['switch_name'])

        loginfo("Initial Configuration of Nexus 5k switch %s completed" %
                data['switch_name'])
        res.setResult(True, PTK_OKAY, "Successfully configured nexus 5k")
        return res

    def createconfig(self, name, ntp, gateway, ip, netmask, mac_addr, poap_cfg_template, domain_name):
        """
        Creates the configuration file for the nexus switch

        :param name: Name of the nexus switch
        :param ntp: NTP address
        :param gateway: Gateway address
        :param ip: IP address of nexus switch
        :param netmask: Netmask address
        :param mac_addr: MAC address of nexus switch
        :param domain_name: Domain name for nexus switch
        """
        loginfo("Creating configuration file for Nexus switch %s" % name)
        nexus_config = {}
        nexus_config['switch_name'] = name
        nexus_config['ntp_server'] = ntp
        nexus_config['switch_gateway'] = gateway
        nexus_config['switch_ip'] = ip
        nexus_config['switch_netmask'] = netmask

        mac = mac_addr.replace(':', '')
        cfg_name = "conf_" + mac + ".cfg"
        poap_cfg_tgt = tgt_dir + "/" + cfg_name
        gen_from_template(
                poap_cfg_template, nexus_config, poap_cfg_tgt)

        if domain_name:
	    msg = "\nip domain-name %s" % domain_name
	    with open(poap_cfg_tgt, 'a') as fp:
		fp.write(msg)

        cmd = "cp %s %s" % (poap_cfg_tgt, tftp_dir)
        execute_local_command(cmd)
        self.createmd5(cfg_name)

        loginfo("Created configuration file for Nexus switch %s" % name)

    def createmd5_py(self, py):
        """
        Creates md5 for the poap.py file

        :param py: poap.py file location
        """
        loginfo("Creating md5 for poap %s" % py)
        cmd = "f=%s ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i \"s/^#md5sum=.*/#md5sum=\"$(md5sum $f.md5 | sed 's/ .*//')\"/\" $f" % py
        os.system(cmd)

    def createmd5(self, cfg):
        """
        Creates md5 for the configuration file

        :param cfg: configuration file location
        """
        md5 = cfg + ".md5"
        loginfo("Creating md5 for %s" % md5)
        cmd = "cd %s; md5sum %s > %s" % (tftp_dir, cfg, md5)
        os.system(cmd)

    def nexusreconfigure(self, data, force):
        """
        Re-configures the nexus switch in case of failure

        :param data: Dictionary (ntp_server, switch_ip, switch_netmask, switch_gateway, switch_mac, switch_name, switch_serial_no, switch_vendor, switch_image)
        :return: Returns the reconfiguration status
        """
        input_dict = {}
        input_dict['ntp_server'] = data['ntp_server']
        input_dict['switch_ip'] = data['ipaddress']
        input_dict['switch_netmask'] = data['netmask']
        input_dict['switch_gateway'] = data['gateway']
        input_dict['switch_mac'] = data['mac']
        input_dict['switch_name'] = data['name']
        input_dict['switch_tag'] = data['tag']
        input_dict['switch_serial_no'] = data['serial_no']
        input_dict['switch_vendor'] = data['model']
        input_dict['domain_name'] = data['domain_name']
        if data['device_type'] == 'Nexus 9k':
            model = "n9k"
            input_dict['switch_image'] = {
                'switch_system_image': data['switch_image']}
        elif data['device_type'] == 'Nexus 5k':
            model = "n5k"
            input_dict['switch_image'] = {
                'switch_kickstart_image': data['switch_kickstart_image'],
                'switch_system_image': data['switch_system_image']}

        if force == 0:
            populate_lst = []
            populate_lst.append(input_dict)
            return True, json.dumps(populate_lst)
        loginfo("Nexus Reconfigure: Validating Nexus configuration params")
        validation_status = self.nexusvalidate(input_dict, model).getStatus()
        if validation_status == PTK_OKAY:
            loginfo("Nexus Reconfigure: Nexus Validation success. Configuring Nexus")
            if model == "n9k":
                conf_status = self.nexus9kconfigure(input_dict).getStatus()
            elif model == "n5k":
                conf_status = self.nexus5kconfigure(input_dict).getStatus()
            else:
                loginfo("Nexus Reconfigure: Invalid Nexus model")
                return False, -1

            if conf_status == PTK_OKAY:
                loginfo("Nexus Reconfigure: Nexus Configuration success")
                return True, 0
            else:
                loginfo("Nexus Reconfigure: Nexus Configuration failure")
                return False, -1
        else:
            loginfo("Nexus Reconfigure: Nexus Validation failure")
            return False, -1

    def nexus9kimages(self):
        """
        List of N9K NX-OS images available in our tool

        :return: List of NX-OS images
        """
        res = result()
        images = [os.path.basename(fn) for fn in glob.glob(
                '/mnt/system/uploads/nxos.*')]
        version_lst = list(
                set([re.search('nxos.(.+?).I', x).group(1) for x in images]))
        version_lst.sort(key=lambda s: map(int, s.split('.')), reverse=True)
        images = [ks for ver in version_lst for ks in filter(
                lambda x: ver in x, images)]
        res.setResult(images, PTK_OKAY, "success")
        return res

    def nexus5kkickstartimages(self):
        """
        List of N5K NX-OS kickstart images available in our tool

        :return: List of NX-OS kickstart images
        """
        res = result()
        images = [os.path.basename(fn) for fn in glob.glob(
                '/mnt/system/uploads/n5000-uk9-kickstart.*')]
        version_lst = list(
                set([re.search('n5000-uk9-kickstart.(.+?).N', x).group(1) for x in images]))
        version_lst.sort(key=lambda s: map(int, s.split('.')), reverse=True)
        images = [ks for ver in version_lst for ks in filter(
                lambda x: ver in x, images)]
        res.setResult(images, PTK_OKAY, "success")
        return res

    def nexus5ksystemimages(self):
        """
        List of N5K NX-OS system images available in our tool

        :return: List of NX-OS system images
        """
        res = result()
        images = [os.path.basename(fn) for fn in glob.glob(
                '/mnt/system/uploads/n5000-uk9.*')]
        version_lst = list(
                set([re.search('n5000-uk9.(.+?).N', x).group(1) for x in images]))
        version_lst.sort(key=lambda s: map(int, s.split('.')), reverse=True)
        images = [ks for ver in version_lst for ks in filter(
                lambda x: ver in x, images)]
        res.setResult(images, PTK_OKAY, "success")
        return res

    def nexusvalidate(self, data, model):
        """
        Validates whether the details provided for nexus configuration are correct

        :param data: Dictionary (switch_name, switch_mac, switch_serial_no, switch_vendor, ntp_server, switch_gateway, switch_ip, switch_netmask, switch_image)
        :return: Returns the validation status
        """
        res = result()
        ret = []
        if model == "n9k":
            ret = validate_input_data(
                    {'switch_name': 'Switch name', 'switch_gateway': 'Gateway', 'switch_ip': 'IP address',
                     'switch_netmask': 'Netmask', 'switch_mac': 'MAC address',
                     'ntp_server': 'NTP Server ip', 'switch_image': 'Switch image',
		     'pri_passwd': 'Password', 'conf_passwd': 'Confirm password',
                     'switch_serial_no': 'Serial number', 'switch_vendor': 'Switch vendor'}, data)
        else:
            ret = validate_input_data(
                    {'switch_name': 'Switch name', 'switch_gateway': 'Gateway', 'switch_ip': 'IP address',
                     'switch_netmask': 'Netmask', 'switch_mac': 'MAC address',
                     'ntp_server': 'NTP Server ip', 'switch_system_image': 'System image',
                     'switch_kickstart_image': 'Kickstart image', 'switch_serial_no': 'Serial number',
		     'pri_passwd': 'Password', 'conf_passwd': 'Confirm password',
                     'switch_vendor': 'Switch vendor'}, data)

        if data['pri_passwd'] != data['conf_passwd']:
            ret.append({'field': 'conf_passwd',
                        'msg': 'Password does not match'})
            res.setResult(ret, PTK_INTERNALERROR,
                          "Make sure details are correct")
            return res

        ip_valid = ipvalidation(data['switch_ip'])
        ntp_valid = ipvalidation(data['ntp_server'])
        if len(ret) > 0:
            res.setResult(ret, PTK_INTERNALERROR,
                          "Please fill all mandatory fields.")
            return res
        elif not ip_valid or not ntp_valid:
            if not ip_valid:
                ret.append(
                        {"field": "switch_ip", "msg": "Please Enter Valid IP Address"})
            if not ntp_valid:
                ret.append(
                        {"field": "ntp_server", "msg": "Please Enter Valid IP Address"})
            res.setResult(ret, PTK_INTERNALERROR,
                          "Make sure details are correct")
            return res
        else:
            if model == "n5k":
                system_ver = re.search(
                        'n5000-uk9.(.+?).bin', data['switch_system_image']).group(1)
                kickstart_ver = re.search(
                        'n5000-uk9-kickstart.(.+?).bin', data['switch_kickstart_image']).group(1)
                if system_ver != kickstart_ver:
                    ret.append({"field": "switch_system_image",
                                "msg": "Select similar system and kickstart version"})
                    ret.append({"field": "switch_kickstart_image",
                                "msg": "Select similar system and kickstart version"})
                    res.setResult(ret, PTK_INTERNALERROR,
                                  "Make sure details are correct")
                    return res
            ipv = IpValidator()
            network_reach, ip_reach = ipv.validate_ip(
                    data['switch_ip'], data['switch_netmask'], data['switch_gateway'])
            if network_reach == True:
                if ip_reach == False:
                    res.setResult(ret, PTK_OKAY, "Success")
                else:
                    res.setResult([{"field": "switch_ip", "msg": "IP Address is already occupied"}], PTK_INTERNALERROR,
                                  "Please check the IP address.")
            else:
                res.setResult([{"field": "switch_ip", "msg": "Please check the network settings"},
                               {"field": "switch_gateway", "msg": "Please check the network settings"}, {
                                   "field": "switch_netmask", "msg": "Please check the network settings"}],
                              PTK_INTERNALERROR, "Please check the network settings.")
            return res

    def confcleanup(self, device_id):
        """
        Cleans up the configuration files used for nexus switch ocnfiguration, when the device goes to configured state

        :param device_id: Serial number of the nexus switch
        """
        cmd = "rm -rf %s/conf_%s.*" % (tftp_dir, device_id)
        os.system(cmd)
