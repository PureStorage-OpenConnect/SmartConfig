#####################################################################
#!/usr/bin/env python3
# Project_Name    :SmartConfig
# title           :fs_config.py
# description     :Configuration Backup of Flashstack Components 
# author          :Guruprasad
# version         :1.0
#####################################################################

import os
import shutil
import zipfile
import queue
import time
from threading import Thread, Lock

from pure_dir.services.utils.ipvalidator import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import decrypt
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.components.compute.ucs.ucs_tasks import UCSTasks
from pure_dir.components.network.nexus.nexus import Nexus
from pure_dir.components.storage.mds.mds import MDS

static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'
config_backup_store = '/mnt/system/pure_dir/pdt/configs/'

lock = Lock()

def gather_configs():
    threads = []
    q = queue.Queue()
    if not os.path.exists(config_backup_store):
        os.makedirs(config_backup_store)
    status, details = get_xml_element(static_discovery_store, 'configured', 'Configured')
    if status:
        for device in details:
            if device.get('device_type') in ['Nexus 5k', 'Nexus 9k', 'MDS']:
                loginfo("Backing up %s config" % device.get('name'))
                t = Thread(name=device.get('name'), target=nxos_backup_config, args=(device.get('device_type'), device.get('name'), device.get('ipaddress'), device.get('username'), decrypt(device.get('password', '')), config_backup_store, q))
                t.start()
           
            elif device.get('device_type') == 'UCSM' and device.get('leadership') == 'primary':
                loginfo("Backing up %s config" % device.get('name'))
                t = Thread(name=device.get('name'), target=ucs_backup_config, args=(device.get('name'), device.get('vipaddress'), device.get('username'), decrypt(device.get('password', '')), config_backup_store, q))
                t.start()

            else:
                continue

            threads.append(t)

        for t in threads:
            loginfo("Waiting for config backup thread: %s" % t.name)
            t.join()
        
        bkp_status = [q.get() for _ in threads]
        return all(bkp_status)
    else:
        loginfo("Failed to gather the configurations of FlashStack components")
        return False


def config_download():
    res = result()
    try:
        status = gather_configs()
        if status is False:
            loginfo("Failed to gather the configuration")
            res.setResult({"url":""}, PTK_INTERNALERROR, "Failed to gather the configuations")
            return res
        with lock:
            dw_path = get_download_path()
            os.system("sync")
            time.sleep(2)
            zip(config_backup_store, dw_path + "fs_configs")
            time.sleep(2)
            shutil.rmtree(config_backup_store)
            loginfo("Successfully zipped the configuration files")
        res.setResult({"url":"fs_configs.zip"}, PTK_OKAY, "Success")
        return res
    except Exception as e:
        loginfo("Unable to gather the configurations from the FlashStack components. %s" % str(e))
        res.setResult({"url":""}, PTK_INTERNALERROR, "Failed to download the configurations of the FlashStack components")
        return res


def nxos_backup_config(switch_type, switch_name, ipaddress, username, password, config_store, queue):
    try:
        sc_ip = network_info().get('ip')
        if "Nexus" in switch_type:
            obj = Nexus(ipaddress, username, password)
        elif "MDS" in switch_type:
            obj = MDS(ipaddress, username, password)
        else:
            loginfo("An unknown nxos device type %s with name %s has been passed on here" % (switch_type, switch_name))
            queue.put(False)
            return False
        if obj:
            cfg_bkp_res = obj.backup_config(sc_ip)
            if cfg_bkp_res.getStatus() == PTK_OKAY:
                cmd_config_store = "mv /var/lib/tftpboot/%s-running-config %s" % (switch_name, config_store)
                os.system(cmd_config_store)
                queue.put(True)
                return True
        loginfo("Unable to backup the config of %s" % switch_name)
        queue.put(False)
        return False
    except Exception as e:
        loginfo("Exception in backing up the config of %s: %s" % (switch_name, str(e)))
        queue.put(False)
        return False
    

def ucs_backup_config(switch_name, ipaddress, username, password, config_store, queue):
    try:
        ucs_obj = UCSTasks(ipaddress, username, password)
        fi_name = switch_name[:-2]
        ret = ucs_obj.backup_config(fi_name, config_backup_store)
        ucs_obj.release_ucs_handle()
        queue.put(ret)
        return ret
    except Exception as e:
        loginfo("Exception in backing up the config of %s: %s" % (switch_name, str(e)))
        queue.put(False)
        return False


def zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            loginfo(filename)
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()
    return
