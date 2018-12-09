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

static_discovery_store = "/mnt/system/pure_dir/pdt/devices.xml"

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

    def _save_mds_details(self, ipaddress, netmask, gateway, ntp_server, username, password, serial_no, mac, model,
                          device_type, image_version, kickstart_image, system_image, configured, name, tag, reachability,
                          validated, domain_name):
        data = locals()
        data["timestamp"] = str(time.time())
        del data['self']
        add_xml_element(static_discovery_store, data)
        return

    def mdsconfigure(self, data):
        res = result()

        loginfo("Serial number of mds switch is %s" % data['switch_serial_no'])
        update_xml_element(static_discovery_store, matching_key="mac", matching_value=data['switch_mac'],
                           data={"configured": "In-progress", "timestamp": str(time.time())})

        host_ip = get_ip_address(get_filtered_ifnames()[0])
        loginfo("TFTP server ip is %s" % host_ip)

        image_version = re.search(
            'mz.(.*).bin', data['switch_kickstart_image']).group(1)
        loginfo("Image version used for the mds firmware images is %s" %
                image_version)

        loginfo("Creating poap.cfg file for mds switch %s" %
                data['switch_serial_no'])
        self.createconfig(data['switch_name'], data['ntp_server'], data['switch_gateway'],
                          data['switch_netmask'], data['switch_ip'], data['switch_serial_no'], data['domain_name'])
        loginfo("Creating device-recipe.cfg for mds switch %s" %
                data['switch_serial_no'])
        self.createdevrecipe(data['switch_kickstart_image'],
                             data['switch_system_image'], data['switch_serial_no'])
        loginfo("Creating server-list.cfg for mds switch")
        self.createserverlist(host_ip)
        loginfo("Making firmware images ready for bootflashing for mds switch %s" %
                data['switch_serial_no'])
        self.copymdsimages(data['switch_kickstart_image'],
                           data['switch_system_image'])
        loginfo("Creating poap_script.tcl for mds switch")
        self.createpoaptcl(image_version, host_ip)

        res.setResult(True, PTK_OKAY, "Successfully configured mds")
        return res

    def createpoaptcl(self, image_version, tftp_server_ip):
        mds_config = {}
        mds_config['server_ip'] = tftp_server_ip
        mds_config['image_version'] = image_version

        gen_from_template(
            poap_tcl_template, mds_config, poap_tcl_tgt)

        cmd = "cp %s %s" % (poap_tcl_tgt, tftp_dir)
        execute_local_command(cmd)
        self.createmd5_tcl(fl="poap_script.tcl", path=tftp_dir)
        return

    def mdskickstartimages(self):
        res = result()
        mds_images = glob.glob("%s/m9*.bin" % image_dir)
        image_list = [os.path.basename(
            f) for f in mds_images if isfile(f) and 'kickstart' in f]
        res.setResult(image_list, PTK_OKAY, "Success")
        return res

    def mdssystemimages(self):
        res = result()
        mds_images = glob.glob("%s/m9*.bin" % image_dir)
        image_list = [os.path.basename(f) for f in mds_images if isfile(
            f) and not 'kickstart' in f]
        res.setResult(image_list, PTK_OKAY, "Success")
        return res

    def mdsimages(self):
        res = result()
        image_list = []
        ks_images = self.mdskickstartimages().getResult()
        sys_images = self.mdssystemimages().getResult()
        mds_images = ks_images + sys_images
        version_lst = list(
            set([re.search('mz.(.+?).bin', x).group(1) for x in mds_images]))
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

    def mdsvalidateimages(self, data):
        res = result()
        if re.match(re.sub('-kickstart', '', data['kickstart_image']), data['system_image']):
            loginfo("Images correctly selected")
            res.setResult(True, PTK_OKAY, "Firmware images validated")
        else:
            loginfo("Images incorrectly selected")
            res.setResult(False, PTK_OKAY,
                          "Mismatch in selected firmware images")
        return res

    def mdsreconfigure(self, data, force):
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
        input_dict['switch_kickstart_image'] = data['kickstart_image']
        input_dict['switch_system_image'] = data['system_image']
        input_dict['domain_name'] = data['domain_name']
        if force == 0:
            input_dict['switch_image'] = {k: input_dict[k] for k in (
                'switch_kickstart_image', 'switch_system_image')}
            populate_lst = []
            populate_lst.append(input_dict)
            return True, json.dumps(populate_lst)
        loginfo("MDS Reconfigure: Validating MDS configuration params")
        validation_status = self.mdsvalidate(input_dict).getStatus()
        if validation_status == PTK_OKAY:
            loginfo("MDS Reconfigure: MDS Validation success. Configuring MDS")
            conf_status = self.mdsconfigure(input_dict).getStatus()
            if conf_status == PTK_OKAY:
                loginfo("MDS Reconfigure: MDS Configuration success")
                return True, 0
            else:
                loginfo("MDS Reconfigure: MDS Configuration failure")
                return False, -1
        else:
            loginfo("MDS Reconfigure: MDS Validation failure")
            return False, -1

    def copymdsimages(self, kickstart_img, system_img):
        cmd = "cp %s/%s %s/%s %s" % (image_dir, kickstart_img,
                                     image_dir, system_img, tftp_dir)
        execute_local_command(cmd)

        self.createmd5(fl=kickstart_img, path=tftp_dir)
        self.createmd5(fl=system_img, path=tftp_dir)
        return

    def createconfig(self, name, ntp, gateway, netmask, ip, serial_no, domain_name):
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
        self.createmd5(fl=cfg_name, path=tftp_switch_dir)
        return

    def createdevrecipe(self, kickstart_image, system_image, serial_no):
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

    def createserverlist(self, tftp_server_ip):
        mds_config = {}
        mds_config['server_ip'] = tftp_server_ip

        gen_from_template(
            server_list_template, mds_config, server_list_tgt)

        cmd = "cp %s %s" % (server_list_tgt, tftp_dir)
        execute_local_command(cmd)
        return

    def createmd5_tcl(self, fl, path):
        cmd = "cd %s; f=%s ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i \"s/^#md5sum=.*/#md5sum=\"$(md5sum $f.md5 | sed 's/ .*//')\"/\" $f" % (
            path, fl)
        os.system(cmd)

    def createmd5(self, fl, path):
        md5 = fl + ".md5"
        cmd = "cd %s; md5sum %s > %s" % (path, fl, md5)
        os.system(cmd)

    def mdsvalidate(self, data):
        res = result()
        ret = []
        ret = validate_input_data({'switch_name': 'Switch name', 'switch_gateway': 'Gateway', 'switch_ip': 'IP address',
                                   'switch_netmask': 'Netmask', 'switch_mac': 'MAC address',
                                   'ntp_server': 'NTP Server ip',
                                   'switch_system_image': 'System image', 'switch_kickstart_image': 'Kickstart image',
				   'pri_passwd': 'Password', 'conf_passwd': 'Confirm password',
                                   'switch_serial_no': 'Serial number', 'switch_vendor': 'Switch vendor'}, data)

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
        cmd = "rm -rf %s/%s" % (tftp_dir, device_id)
        os.system(cmd)
        return
