#####################################################################
#!/usr/bin/env python3
# Project_Name    :SmartConfig
# title           :reset_devices.py
# description     :Flashstack Hardware Reset
# author          :Aishwarya
# version         :1.0
#####################################################################

from threading import Thread
import time
import xmltodict
import glob
#from netmiko import Netmiko
from xml.dom.minidom import Document, parse
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.components.common import decrypt
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import get_xml_element, update_xml_element, pretty_print
from pure_dir.components.compute.ucs.ucs_info_netmiko import *
from pure_dir.global_config import get_settings_file
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_batch_status_file, get_job_file, get_workflow_files_pattern
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_rollback import job_rollback_api
from pure_dir.services.apps.pdt.core.systemmanager import pdtreset

static_discovery_store = '/mnt/system/pure_dir/pdt/devices.xml'
device_reset_file = '/mnt/system/pure_dir/pdt/devices_reset.xml'
settings = get_settings_file()


def reset_switch(ipaddress, username, password, device_name):
    """
    Reset Nexus/MDS Switch.
    Parameters:
        ipaddress(str) : IP address of MDS/Nexus switch Primary/Secondary
        username(str) : Username of MDS/Nexus switch Primary/Secondary
        password(str) : Password of MDS/Nexus switch Primary/Secondary
        device_name(str) : Name of MDS/Nexus switch Primary/Secondary
    """
    try:
        loginfo("{} Reset started".format(device_name))
        net_connect = netmiko_obj(ipaddress, username, password)
        net_connect.send_command("terminal dont-ask persist", expect_string=r"#")
        net_connect.send_command("write erase", expect_string=r"#")
        net_connect.send_command("reload", 
            expect_string=r"")
        loginfo("{} is getting reset".format(device_name))
        net_connect.disconnect()
        update_xml_element(
                device_reset_file,
                matching_key="ip",
                matching_value=ipaddress,
                data={
                    "reset_status": "completed",
                    "timestamp": str(
                        time.time())},
                element_name="device")
    except Exception as e:
        loginfo("An exception occured while resetting {} {}. Please check the console and \
                 reset it manually.".format(device_name, str(e)))
        update_xml_element(
                device_reset_file,
                matching_key="ip",
                matching_value=ipaddress,
                data={
                    "reset_status": "failed",
                    "error" : "{} reset failed.".format(device_name),
                    "timestamp": str(
                        time.time())},
                element_name="device")


def reset_ucs(ipaddress, username, password, device_name):
    """
    Reset Fabric Interconnect.
    Parameters:
        ipaddress(str) : IP address of Fabric Interconnect Primary/Secondary
        username(str) : Username of Fabric Interconnect Primary/Secondary
        password(str) : Password of Fabric Interconnect Primary/Secondary
        device_name(str) : Name of Fabric Interconnect Primary/Secondary
    """

    try:
        loginfo("{} Reset started".format(device_name))
        net_connect = netmiko_obj(ipaddress, username, password)
        net_connect.send_command("connect local-mgmt", expect_string=r"#")
        net_connect.send_command("erase configuration", expect_string=r"yes/no")
        net_connect.send_command("yes", expect_string=r"Removing all the configuration")
        loginfo("{} is getting reset".format(device_name))
        net_connect.disconnect()
        update_xml_element(
                device_reset_file,
                matching_key="ip",
                matching_value=ipaddress,
                data={
                    "reset_status": "completed",
                    "timestamp": str(
                        time.time())},
                element_name="device")
    except Exception as e:
        loginfo("An exception occured while resetting {} {}. Please check the console and \
                 reset it manually.".format(device_name, str(e)))
        update_xml_element(
                device_reset_file,
                matching_key="ip",
                matching_value=ipaddress,
                data={
                    "reset_status": "failed",
                    "error" : "{} reset failed.".format(device_name),
                    "timestamp": str(
                        time.time())},
                element_name="device")

def get_stacktype():    
    """Returns the stacktype"""
    stacktype = ""
    status, details = get_xml_element(settings, 'stacktype')
    if status:
        stacktype = details[0]['subtype']
    return stacktype

def create_reset_config(devices_dict, rollback_dict):
    """
    Creates Device Reset File to monitor the reset status.
    Parameters:
        devices_dict (dict): Info of the devices selected to be reset.
    """
    loginfo("Creating Device Reset file")
    doc = Document()
    roottag = doc.createElement("devices")
    for device in devices_dict.items():
        dev = doc.createElement("device")
        dev.setAttribute("name", device[1]['name'])
        dev.setAttribute("ip", device[1]['ip'])
        dev.setAttribute("device_type", device[0])
        dev.setAttribute("serial_no", device[1]['serial_no'])
        dev.setAttribute("reset_status", "in-progress")
        if rollback_dict and device[0] in rollback_dict.keys() and rollback_dict[device[0]]:
            dev.setAttribute("reset_status", "in-progress")
        if device[1].get('leadership'): 
            dev.setAttribute("leadership", device[1]['leadership'])
        roottag.appendChild(dev)
    doc.appendChild(roottag)
    fd = open(device_reset_file, 'w')
    fd.write(pretty_print(doc.toprettyxml(indent="")))

def initiate_reset_threads(device_dict, rollback_dict):
    """
    Initiates reset for each configured device selected
    Parameters:
        device_dict (dict): Info of the devices selected to be reset.
        rollback_dict (dict) : Dict of device types with a boolean to indicate rollback
    """
    threads = []
    for device in device_dict.items():
        if (('Nexus' in device[0]) or
           ('MDS' in device[0])):
            t = Thread(
                name=device[1]['name'],
                target=reset_switch,
                args=(reset_switch(
                device[1]['ip'],
                device[1]['username'],
                decrypt(device[1]['password']),
                device[1]['name'])))
            t.start()
        elif 'UCSM' in device[0]:
            t = Thread(
                name=device[1]['name'],
                target=reset_switch,
                args=(reset_ucs(
                device[1]['ip'],
                device[1]['username'],
                decrypt(device[1]['password']),
                device[1]['name'])))
            t.start()
        else:
            continue
        threads.append(t)
    for t in threads:
        loginfo("Waiting for thread: {}".format(t.name))
        t.join()



def batch_status(job_list):
    """
    Returns current execution status for the batch job
    Parameters:
        job_list (list): List of JobIds for which the status is queried
    """
    wf_list = []
    stacktype = get_stacktype()
    doc = parse(get_batch_status_file(stacktype))
    batches = doc.getElementsByTagName('workflow')
    for batch in batches:
        if ((batch.hasAttribute('jid')) and (batch.hasAttribute('rollbackOnReset')) and 
           (batch.getAttribute('rollbackOnReset') == '1')):
            if batch.getAttribute('jid') in job_list:
                wf_entity = {
                            'wid': batch.getAttribute('id'),
                            'jid': batch.getAttribute('jid'),
                            'status': batch.getAttribute('status'),
                            'order' : batch.getAttribute('order')
                            }
                wf_list.append(wf_entity)
    return wf_list

def call_batch_status(job_list, query_status=False):
    """
    Returns the rollback status for the workflows/specific job with rollbackOnReset being set
    Parameters:
        job_list (list): List of JobIds for which the status is queried
        query_status (bool) (optional): Status of the JobId queried
    """
    wf_list = batch_status(job_list)
    #Return the status of a particular job
    if query_status:
        for wf in wf_list:
            if wf['jid'] == job_list[0]:
                return wf['status']
    return wf_list

def rollback_on_reset(job_input_list):
    """
    Returns the rollback status for the workflows with rollbackOnReset being set after doing rollback
    Parameters:
        job_input_list (list): List of JobIds for which the status is queried
    """
    timeout = 600 #To handle jobs crashing in rollback 
    start_time = time.time()
    job_list = call_batch_status(job_input_list)
    job_list_sorted = sorted(job_list,key=lambda job:job['order'], reverse=True)
    rollback_status = dict.fromkeys([job['jid'] for job in job_list_sorted], False)
    try:
        for job in job_list_sorted:
            job_revert_api = job_rollback_api(stacktype=None, jobid=job['jid'])
            #Query to check if the job rollback is complete
            job_status = call_batch_status([job['jid']], query_status=True)
            while job_status in ['ROLLBACK_FAILED', 'READY', 'ROLLBACK']:
                if ((job_status == 'ROLLBACK_FAILED') or 
                   ((job_status == 'ROLLBACK') and (time.time() - start_time > timeout))):
                    break
                elif job_status == 'READY':
                    rollback_status[job['jid']] = True
                    break
                time.sleep(5) #Query the job status every 5 sec
                job_status = call_batch_status([job['jid']], query_status=True)
        return rollback_status
    except Exception as e:
        loginfo("An exception occured during rollback. {}".str(e))
        return rollback_status
        
 
def get_device_details(devices_list, rollback_dict):
    """
    Returns the devices that are configured and to rolledback
    Parameters:
        device_details (list): List of configured devices.
        rollback_dict (dict): Dict of device types with a boolean to indicate rollback.
    """
    device_reset_dict = {}
    status, device_details = get_xml_element(static_discovery_store, 'device_type')
    if status:
        for device_detail in device_details:
            if device_detail.get('serial_no') in devices_list:
                device_name = device_detail.get('device_type') + " - " + device_detail.get('tag', '')
                if not device_detail.get('tag', ''):
                    device_name = device_detail.get('device_type')
                if ((device_detail.get('device_type') in rollback_dict.keys()) and 
                   (not rollback_dict.get(device_detail['device_type']))):
                    continue
                device_reset_dict[device_name] = {'name' : device_detail['name'],
                                                  'ip' : device_detail['ipaddress'],
                                                  'username' : device_detail['username'],
                                                  'password' : device_detail['password'],
                                                  'serial_no' : device_detail['serial_no']}
                if device_detail.get('leadership'):
                    device_reset_dict[device_name]['leadership'] = device_detail['leadership']

        return device_reset_dict

def update_rollback_status(rollback_status, device_type):
    """
    Updates rollback status to device reset file.
    Parameters:
        rollback_status(dict) : Rollback status of jobs
        device_type(str) : Device Type for which rollback was done.
    """
    update_data={
        "reset_status": "completed",
        "timestamp": str(
        time.time())}
    if not all(rollback_status.values()):
        update_data['error'] = "{} rollback failed.".format(device_name)
        update_data['reset_status'] = "failed"
    update_xml_element(
            device_reset_file,
            matching_key="device_type",
            matching_value=device_type,
            data=update_data,
            element_name="device")

def call_rollback_on_reset(job_dict, device_reset_dict, rollback_dict, reset):
    """
    Initiates device and tool reset based on rollback status
    Parameters
        job_dict(dict) : Dict of device type and jobs 
        device_reset_dict(dict) : Devices to reset
        rollback_dict(dict) : Device types for which rollback is to be done
        reset(boolean) : Indicates SmartConfig Reset to be done
    """
    for reset_dev in job_dict.items():
        if reset_dev[1]:
            rollback_status = rollback_on_reset(reset_dev[1])
            update_rollback_status(rollback_status, reset_dev[0])
    # If rollback failed, devices will have to be manually reset
    reset_failed_list = [device['reset_status'] for device in reset_status().getResult() 
                             if device['reset_status'] == "failed"]
    if not reset_failed_list:
        initiate_reset_threads(device_reset_dict, rollback_dict)
    # If device reset failed, tool reset wiil not be triggered
    reset_failed_list = [device['reset_status'] for device in reset_status().getResult() 
                             if device['reset_status'] == "failed"]
    if reset and not reset_failed_list:
        pdtreset()

def initiate_rollback_thread(job_dict, device_reset_dict, rollback_dict, reset):
    """
    Initiates rollback thread 
    Parameters
        job_dict(dict) : Dict of device type and jobs
        device_reset_dict(dict) : Devices to reset
        rollback_dict(dict) : Device types for which rollback is to be done
        reset(boolean) : Indicates SmartConfig Reset to be done
    """ 
    loginfo("Initiating rollback....")
    t = Thread(name="rollback",
               target=call_rollback_on_reset,
               args=(job_dict,
                     device_reset_dict, 
                     rollback_dict, 
                     reset)).start()

def device_reset(devices_list, force=0, reset=True):
    """
    API Returns the status of device reset initiation
    Parameters:
        devices_list (list): Devices selected to be reset.
        force(boolean)     : Prompt for confirmation from user
    """
    res = result()
    rollback_devtype = ""
    if not force:
       res.setResult(True, PTK_CONFIRMCHK, _("PDT_CONFIRMCHK_MSG"))
       return res

    stacktype = get_stacktype()
    rollback_dict = get_rollback_devices(stacktype)
    job_dict = dict.fromkeys(rollback_dict.keys(), [])
    if os.path.exists(get_batch_status_file(stacktype)):
        doc_batch = parse(get_batch_status_file(stacktype))
        batches = doc_batch.getElementsByTagName('workflow')
        for batch in batches:
            if batch.hasAttribute('jid') and batch.hasAttribute('status'):
                if batch.getAttribute('status') in ['EXECUTING', 'ROLLBACK']:
                    res.setResult(False, PTK_BANNER_ERROR, _("PDT_RESET_UNSUPPORTED"))
                    return res
                if batch.hasAttribute('rollbackOnReset') and batch.getAttribute('rollbackOnReset') == '1':
                    if batch.getAttribute('status') == 'ROLLBACK_FAILED':
                       res.setResult(False, PTK_BANNER_ERROR, _("PDT_RESET_ROLLBACK_FAILED"))
                       return res
                    if os.path.exists(get_job_file(batch.getAttribute('jid'))):
                       with open(get_job_file(batch.getAttribute('jid'))) as td:
                           doc_job = xmltodict.parse(td.read())
                           rollback_devtype = 'PURE' if doc_job['workflow']['@type'] == 'FlashArray' else doc_job['workflow']['@type']
                       if batch.getAttribute('status') in ['COMPLETED', 'FAILED']:
                           rollback_dict[rollback_devtype] = True
                           job_dict[rollback_devtype].append(batch.getAttribute('jid'))
    
    #Check before triggering rollback
    device_reset_dict = get_device_details(devices_list, rollback_dict)
    create_reset_config(device_reset_dict, rollback_dict)
    initiate_rollback_thread(job_dict, device_reset_dict, rollback_dict, reset)
    res.setResult(True, PTK_OKAY, _("PDT_RESET"))
    return res


def reset_status():
    """
    API Returns the list of devices with corresponding reset status
    """

    reset_list = []
    res = result()
    if not os.path.exists(device_reset_file):
        res.setResult(reset_list, PTK_OKAY, "Device Reset File doesn't exist")
        return res
    doc = parse(device_reset_file)
    devices = doc.getElementsByTagName('device')
    for device in devices:
        reset_dict = {'device_name' : device.getAttribute('name'), 'serial_no' : device.getAttribute('serial_no'), 
                      'device_type' : device.getAttribute('device_type'), 'ipaddress' : device.getAttribute('ip'),
                      'reset_status' : device.getAttribute('reset_status')}
        if reset_dict['reset_status'] == "failed":
            reset_dict['error'] = device.getAttribute('error')
        reset_list.append(reset_dict)
    res.setResult(reset_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res

def get_rollback_devices(stacktype):
    """
    Returns the devices to be rolledback based on stacktype.
    Parameters:
        stacktype (str): Stacktype for which the devices list is to be populated.
    """ 
    rollback_dict = {}
    rollback_devtype = ""
    wfs = glob.glob(get_workflow_files_pattern(stacktype))
    for wf in wfs:
        with open(wf, 'r') as fd:
            doc = xmltodict.parse(fd.read())
            if '@hidden' in doc['workflow'] and doc['workflow']['@hidden'] == '1':
                continue
            if '@wtype' in doc['workflow'] and doc['workflow']['@wtype'] == 'wgroup':
                if doc['workflow']['@type'] in ['UCSM', 'Nexus', 'MDS']:
                    continue
                if '@rollbackOnReset' in doc['workflow']:
                    rollback_devtype = 'PURE' if doc['workflow']['@type'] == 'FlashArray' else doc['workflow']['@type']
                    rollback_dict.update({rollback_devtype:False})
    return rollback_dict

def check_device_reset_file(query_failed=False):
    """
    Check if the devices have already been reset/failed
    Parameters:
        query_failed(bool) : query the devices for whch reset failed
    """
    reset_devices_list = []
    failed_device_list = []
    if os.path.exists(device_reset_file):
        with open(device_reset_file) as dr:
            doc_reset = xmltodict.parse(dr.read())
            for device in doc_reset['devices']['device']:
                if device['@reset_status'] == "completed" :
                    reset_devices_list.append(device['@serial_no'])
                if query_failed and device['@reset_status'] == "failed":
                    failed_device_list.append(device['@serial_no'])
    if query_failed:
        return failed_device_list
    return reset_devices_list

def get_devices_to_reset(rollback_dict):
    """
    Returns devices to rollback/reset.
    Parameters:
        rollback_dict(dict) : Dict of device types with a boolean to indicate rollback
    """
    reset_list = []
    doc = parse(static_discovery_store)
    devices = doc.getElementsByTagName('device')
    reset_devices_list = check_device_reset_file()
    for device in devices:
        if rollback_dict and device.getAttribute('device_type') in rollback_dict.keys() and not rollback_dict[device.getAttribute('device_type')]:
            continue
        if device.getAttribute('configured') != 'Configured':
            continue
        if device.getAttribute('serial_no') in reset_devices_list:
            continue
        reset_dict = {'device_name' : device.getAttribute('name'), 'serial_no' : device.getAttribute('serial_no'),
                      'device_type' : device.getAttribute('device_type'), 'ipaddress' : device.getAttribute('ipaddress')}
        reset_list.append(reset_dict)
    return reset_list

def devices_to_reset():
    """
    API Returns the list of devices to reset
    """
    res = result()
    rollback_devtype = ""
    reset_list = []
    # Check if device reset is triggered again
    failed_devices_list = check_device_reset_file(query_failed=True)
    if failed_devices_list:
        res.setResult(reset_list, PTK_BANNER_ERROR, _("PDT_RESET_DEVICES_FAILED"))
        return res
    stacktype = get_stacktype()
    if stacktype:
        rollback_dict = get_rollback_devices(stacktype)
        if os.path.exists(get_batch_status_file(stacktype)):
            doc_batch = parse(get_batch_status_file(stacktype))
            batches = doc_batch.getElementsByTagName('workflow')
            for batch in batches:
                if ((batch.hasAttribute('jid')) and (batch.hasAttribute('status')) and 
                   (batch.hasAttribute('rollbackOnReset')) and (batch.getAttribute('rollbackOnReset') == '1')):
                   if ((os.path.exists(get_job_file(batch.getAttribute('jid')))) and 
                      (batch.getAttribute('status') != 'READY')):
                       with open(get_job_file(batch.getAttribute('jid'))) as td:
                           doc_job = xmltodict.parse(td.read())
                           rollback_devtype = 'PURE' if doc_job['workflow']['@type'] == 'FlashArray' else doc_job['workflow']['@type']
                       rollback_dict[rollback_devtype] = True
    reset_list = get_devices_to_reset(rollback_dict)
    res.setResult(reset_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res




