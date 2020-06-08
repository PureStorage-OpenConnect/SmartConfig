#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :mds_setup.py
# description     :MDSSetup class for handling initial configuration
# author          :Guruprasad
# version         :1.0
#####################################################################

from pure_dir.global_config import *
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.services.utils.ipvalidator import *
from pure_dir.components.common import *
import os
import time
import glob
import json
from os.path import isfile
from pure_dir.global_config import get_discovery_store

templates_dir = "/mnt/system/pure_dir/pdt/templates/components/mds/"
tgt_dir = "/mnt/system/pure_dir/pdt/targets/mds/"
tftp_dir = "/var/lib/tftpboot/"
image_dir = "/mnt/system/uploads/"

poap_tcl_template = templates_dir + "poap_script.tcl.template"
server_list_template = templates_dir + "server-list.cfg.template"
poap_cfg_template = templates_dir + "poap.cfg.template"
device_recipe_template = templates_dir + "device-recipe.cfg.template"

poap_tcl_tgt = tgt_dir + "poap_script.tcl"
server_list_tgt = tgt_dir + "server-list.cfg"
poap_cfg_tgt = tgt_dir + "poap.cfg"
device_recipe_tgt = tgt_dir + "device-recipe.cfg"


class MDSSetup:
    def __init__(self):
        cmd = "mkdir %s" % (tgt_dir)
        execute_local_command(cmd)

    def mdsvalidate(self, data):
        """
        Validates the details provided for MDS configuration

        :param data: Dictionary (switch_name, switch_mac, switch_serial_no, switch_vendor, ntp_server, switch_gateway, switch_ip, switch_netmask, switch_kickstart_image,
                                 switch_system_image, pri_passwd, conf_password)

        :return: Returns the validation status
        """
        res = result()
        ret = []
        ret = validate_input_data({'switch_name': 'Switch name',
                                   'switch_gateway': 'Gateway',
                                   'switch_ip': 'IP address',
                                   'switch_netmask': 'Netmask',
                                   'switch_mac': 'MAC address',
                                   'ntp_server': 'NTP Server ip',
                                   'switch_system_image': 'System image',
                                   'switch_kickstart_image': 'Kickstart image',
                                   'pri_passwd': 'Password',
                                   'conf_passwd': 'Confirm password',
                                   'switch_serial_no': 'Serial number',
                                   'switch_vendor': 'Switch vendor'},
                                  data)

        firmware_valid = self.mdsvalidateimages({'switch_kickstart_image':data['switch_kickstart_image'], 'switch_system_image':data['switch_system_image']}).getResult()
        if firmware_valid is False:
            ret.append({"field": "switch_system_image",
                    "msg": "Select similar system and kickstart version"})
            ret.append({"field": "switch_kickstart_image",
                    "msg": "Select similar system and kickstart version"})
            res.setResult(ret, PTK_INTERNALERROR,
                    "Make sure details are correct")
            return res

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
            ipv = IpValidator()
            network_reach, ip_reach = ipv.validate_ip(
                data['switch_ip'], data['switch_netmask'], data['switch_gateway'])
            if network_reach:
                if not ip_reach:
                    res.setResult(ret, PTK_OKAY, "Success")
                else:
                    res.setResult([{"field": "switch_ip",
                                    "msg": "IP Address is already occupied"}],
                                  PTK_INTERNALERROR,
                                  "Please check the IP address.")
            else:
                res.setResult([{"field": "switch_ip", "msg": "Please check the network settings"},
                               {"field": "switch_gateway", "msg": "Please check the network settings"}, {
                                   "field": "switch_netmask", "msg": "Please check the network settings"}],
                              PTK_INTERNALERROR, "Please check the network settings.")
            return res

    def mdsconfigure(self, data):
        """
        Configures the MDS switch which is in factory reset state

        :param data: Dictionary (switch_name, switch_mac, switch_serial_no, switch_vendor, ntp_server, switch_gateway, switch_ip, switch_netmask, switch_kickstart_image, switch_system_image)

        :return: Returns the configuration status
        """
        res = result()

        res = result()

        loginfo("Serial number of mds switch is %s" % data['switch_serial_no'])
        update_xml_element(
            get_discovery_store(),
            matching_key="mac",
            matching_value=data['switch_mac'],
            data={
                "configured": "In-progress",
                "timestamp": str(
                    time.time())})

        host_ip = get_ip_address(get_filtered_ifnames()[0])
        loginfo("TFTP server ip is %s" % host_ip)

        image_version = re.search(
            'mz.(.*).bin', data['switch_kickstart_image']).group(1)
        loginfo("Image version used for the mds firmware images is %s" %
                image_version)

        loginfo("Creating poap.cfg file for mds switch %s" %
                data['switch_serial_no'])
        self._createconfig(
            data['switch_name'],
            data['ntp_server'],
            data['switch_gateway'],
            data['switch_netmask'],
            data['switch_ip'],
            data['switch_serial_no'],
            data['domain_name'])
        loginfo("Creating device-recipe.cfg for mds switch %s" %
                data['switch_serial_no'])
        self._createdevrecipe(data['switch_kickstart_image'],
                              data['switch_system_image'], data['switch_serial_no'])
        loginfo("Creating server-list.cfg for mds switch")
        self._createserverlist(host_ip)
        loginfo("Making firmware images ready for bootflashing for mds switch %s" %
                data['switch_serial_no'])
        self._copymdsimages(data['switch_kickstart_image'],
                            data['switch_system_image'])
        loginfo("Creating poap_script.tcl for mds switch")
        self._createpoaptcl(image_version, host_ip)

        res.setResult(True, PTK_OKAY, "Successfully configured mds")
        return res

    def mdsimages(self):
        """
        List of MDS NX-OS kickstart and system images available in our tool

        :return: List of MDS kickstart and system images
        """
        res = result()
        image_list = []
        ks_images = self.mdskickstartimages().getResult()
        sys_images = self.mdssystemimages().getResult()
        mds_images = ks_images + sys_images
        try:
            version_lst = list(
                set([re.search('\.(.+).bin', x).group(1) for x in mds_images]))
            version_lst.sort(key=lambda s: map(int, s.split('.')), reverse=True)
            for ver in version_lst:
                img_dict = {}
                ks_list = [ks for ks in filter(lambda x: ver in x, ks_images)]
                sys_list = [ks for ks in filter(lambda x: ver in x, sys_images)]
                img_dict['switch_kickstart_image'] = '' if ks_list == [
                ] else ks_list[0]
                img_dict['switch_system_image'] = '' if sys_list == [
                ] else sys_list[0]
                image_list.append(img_dict)
            res.setResult(image_list, PTK_OKAY, "Success")
            return res
        except BaseException:
            res.setResult([], PTK_OKAY, "Success")
            return res

    def mdskickstartimages(self):
        """
        List of MDS NX-OS kickstart images available in our tool

        :return: List of MDS NX-OS kickstart images
        """
        res = result()
        mds_images = glob.glob("%s/m9*.bin" % image_dir)
        image_list = [os.path.basename(
            f) for f in mds_images if isfile(f) and 'kickstart' in f]
        res.setResult(image_list, PTK_OKAY, "Success")
        return res

    def mdssystemimages(self):
        """
        List of MDS NX-OS system images available in our tool

        :return: List of MDS NX-OS system images
        """
        res = result()
        mds_images = glob.glob("%s/m9*.bin" % image_dir)
        image_list = [os.path.basename(f) for f in mds_images if isfile(
            f) and 'kickstart' not in f]
        res.setResult(image_list, PTK_OKAY, "Success")
        return res

    def mdsvalidateimages(self, data):
        """
        Validates the MDS kickstart-system images version provided for MDS Configuration

        :param data: Dictionary (switch_kickstart_image, switch_system_image)

        :return: Returns the validation status
        """
        res = result()
        if re.match(
                re.sub(
                    '-kickstart',
                    '',
                    data['switch_kickstart_image']),
                data['switch_system_image']):
            loginfo("Images correctly selected")
            res.setResult(True, PTK_OKAY, "Firmware images validated")
        else:
            loginfo("Images incorrectly selected")
            res.setResult(False, PTK_PRECHECKFAILURE,
                          "Mismatch in selected firmware images")
        return res

    def mdsreconfigure(self, data, force):
        """
        Re-configures the MDS switch in case of failure

        :param data : Dictionary (ntp_server, switch_ip, switch_netmask, switch_gateway, switch_mac, switch_name, switch_tag, switch_serial_no, switch_vendor, switch_kickstart_image,
                                 switch_system_image, domain_name)
        :param force: Confirmation before going for a reconfigure

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
        if force == 0:
            input_dict['switch_image'] = {
                'switch_kickstart_image': data['switch_kickstart_image'],
                'switch_system_image': data['switch_system_image']}
            populate_lst = []
            populate_lst.append(input_dict)
            return True, json.dumps(populate_lst)
        else:
            input_dict['switch_kickstart_image'] = data['switch_kickstart_image']
            input_dict['switch_system_image'] = data['switch_system_image']
            loginfo("MDS Reconfigure: Configuring MDS")
            conf_status = self.mdsconfigure(input_dict).getStatus()
            if conf_status == PTK_OKAY:
                loginfo("MDS Reconfigure: MDS Configuration success")
                return True, 0
            else:
                loginfo("MDS Reconfigure: MDS Configuration failure")
                return False, -1

    def _save_mds_details(
            self,
            ipaddress,
            netmask,
            gateway,
            ntp_server,
            username,
            password,
            serial_no,
            mac,
            model,
            device_type,
            image_version,
            switch_kickstart_image,
            switch_system_image,
            configured,
            name,
            tag,
            reachability,
            validated,
            domain_name):
        """
        Saves the MDS device details to devices.xml

        :param ipaddress             : IP address of mds switch
        :param netmask               : Netmask address
        :param gateway               : Gateway address
        :param ntp_server            : NTP server
        :param username              : Username for mds switch
        :param password              : Password for mds switch
        :param serial_no             : Serial number of mds switch
        :param mac                   : MAC address of mds switch
        :param model                 : Model number of mds switch
        :param device_type           : Device Type
        :param image_version         : NX-OS Image version
        :param switch_kickstart_image: NX-OS Kickstart Image
        :param switch_system_image   : NX-OS System Image
        :param configured            : Configuration state
        :param name                  : Name of the MDS switch
        :param tag                   : Tag for the switch A/B
        :param reachability          : Reachability status
        :param validated             : Validated state
        :param domain_name           : Domain name
        """
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(get_discovery_store(), data)
        return

    def _copymdsimages(self, kickstart_img, system_img):
        """
        Copies MDS kickstart and system images to TFTP directory

        :param kickstart_img: NX-OS Kickstart Image
        :param system_img   : NX-OS System Image
        """
        cmd = "cp %s/%s %s/%s %s" % (image_dir, kickstart_img,
                                     image_dir, system_img, tftp_dir)
        execute_local_command(cmd)

        self._createmd5(fl=kickstart_img, path=tftp_dir)
        self._createmd5(fl=system_img, path=tftp_dir)
        return

    def _createconfig(self, name, ntp, gateway, netmask, ip, serial_no, domain_name):
        """
        Creates the configuration file for the MDS switch

        :param name       : Name of the mds switch
        :param ntp        : NTP address
        :param gateway    : Gateway address
        :param ip         : IP address of mds switch
        :param netmask    : Netmask address
        :param serial_no  : Serial number of mds switch
        :param domain_name: Domain name
        """
        mds_config = {}
        mds_config['switch_name'] = name
        mds_config['ntp_server_ip'] = ntp
        mds_config['switch_gateway'] = gateway
        mds_config['switch_netmask'] = netmask
        mds_config['switch_ip'] = ip

        tftp_switch_dir = tftp_dir + serial_no
        cmd = "mkdir %s" % (tftp_switch_dir)
        execute_local_command(cmd)

        cfg_name = "conf_" + serial_no + ".cfg"
        poap_cfg_tgt = tgt_dir + cfg_name
        gen_from_template(
            poap_cfg_template, mds_config, poap_cfg_tgt)

        if domain_name:
            msg = "\nip domain-name %s" % domain_name
            with open(poap_cfg_tgt, 'a') as fp:
                fp.write(msg)

        cmd = "cp %s %s" % (poap_cfg_tgt, tftp_switch_dir)
        execute_local_command(cmd)
        self._createmd5(fl=cfg_name, path=tftp_switch_dir)
        return

    def _createpoaptcl(self, image_version, tftp_server_ip):
        """
        Creates poap_script.tcl for MDS poap boot mode

        :param image_version : MDS switch image version
        :param tftp_server_ip: TFTP Server IP
        """
        mds_config = {}
        mds_config['server_ip'] = tftp_server_ip
        mds_config['image_version'] = image_version

        gen_from_template(
            poap_tcl_template, mds_config, poap_tcl_tgt)

        cmd = "cp %s %s" % (poap_tcl_tgt, tftp_dir)
        execute_local_command(cmd)
        self._createmd5_tcl(fl="poap_script.tcl", path=tftp_dir)
        return

    def _createdevrecipe(self, kickstart_image, system_image, serial_no):
        """
        Creates device-recipe.cfg for MDS poap boot mode

        :param kickstart_image: NX-OS Kickstart Image
        :param system_image   : NX-OS System Image
        :param serial_no      : Switch serial number
        """
        mds_config = {}
        mds_config['kickstart_image'] = kickstart_image
        mds_config['system_image'] = system_image
        mds_config['serial_number'] = serial_no

        tftp_switch_dir = tftp_dir + serial_no
        cmd = "mkdir %s" % (tftp_switch_dir)
        execute_local_command(cmd)

        cfg_name = "device-recipe_" + serial_no + ".cfg"
        device_recipe_tgt = tgt_dir + cfg_name

        gen_from_template(
            device_recipe_template, mds_config, device_recipe_tgt)

        tftp_switch_dir = tftp_dir + serial_no
        cmd = "cp %s %s/device-recipe.cfg" % (
            device_recipe_tgt, tftp_switch_dir)
        execute_local_command(cmd)
        return

    def _createserverlist(self, tftp_server_ip):
        """
        Creates server-list.cfg for MDS poap boot mode

        :param tftp_server_ip: TFTP Server IP
        """
        mds_config = {}
        mds_config['server_ip'] = tftp_server_ip

        gen_from_template(
            server_list_template, mds_config, server_list_tgt)

        cmd = "cp %s %s" % (server_list_tgt, tftp_dir)
        execute_local_command(cmd)
        return

    def _createmd5_tcl(self, fl, path):
        """
        Creates md5 for the poap_script.tcl file

        :param fl  : poap_script.tcl file
        :param path: TFTP directory
        """
        cmd = "cd %s; f=%s ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i \"s/^#md5sum=.*/#md5sum=\"$(md5sum $f.md5 | sed 's/ .*//')\"/\" $f" % (
            path, fl)
        os.system(cmd)
        return

    def _createmd5(self, fl, path):
        """
        Creates md5 for the configuration file

        :param fl  : poap_script.tcl file
        :param path: TFTP directory
        """
        md5 = fl + ".md5"
        cmd = "cd %s; md5sum %s > %s" % (path, fl, md5)
        os.system(cmd)
        return

    def confcleanup(self, device_id):
        """
        Cleans up the configuration files used for MDS switch ocnfiguration, when the device goes to configured state

        :param device_id: Serial number of the mds switch
        """
        cmd = "rm -rf %s/%s" % (tftp_dir, device_id)
        os.system(cmd)
        return
