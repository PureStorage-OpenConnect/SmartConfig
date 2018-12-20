#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :config_json.py
# description     :Export And Import Configuration
# author          :Vivek
# version         :1.0
###################################################################

import threading
from xml.dom.minidom import *
import shutil
import glob
import shelve
import os
import time
import xmltodict
import json

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *

from pure_dir.services.apps.pdt.core.discovery import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration import*
from pure_dir.services.apps.pdt.core.tasks.main.ucs import*
from pure_dir.services.apps.pdt.core.tasks.test.ucs import*

from pure_dir.services.apps.pdt.core.tasks.main.pure import *
from pure_dir.services.apps.pdt.core.tasks.test.pure import *

from pure_dir.services.apps.pdt.core.tasks.main.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.main.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.main.mds import*
from pure_dir.services.apps.pdt.core.tasks.test.mds import*
from pure_dir.services.apps.pdt.core.systemmanager import *

settings = "/mnt/system/pure_dir/pdt/settings.xml"


def export_configuration(stacktype):
    res = result()
    dicts = {}
    grp_wf_list = []
    os.chdir('/mnt/system/pure_dir/pdt/sreq/')
    for shlv_file in glob.glob("*.shlv"):
        fl = shlv_file.split('.')[0][4:]
        shelf = shelve.open(get_shelf_file(fl), flag='r')
        wflist = []
        for x in range(len(shelf['job'])):
            job_recs = shelf['job'][str(x)]['record']
            job_rec = job_recs['tasklist']
            keylist = ['taskstatus', 'inputs', 'outputs', 'class']
            wfdict = {
                "wfname": job_recs['wfname'], "desc": job_recs['desc'], "wid": job_recs['wid']}
            tasklist = []
            for key, value in job_rec.iteritems():
                data_list = []
                for k, v in value['inputs'].iteritems():
                    data = get_value_from_xml(
                        job_recs['jobid'], value['texecid'], k)
                    s = {
                        "name": k,
                        "value": data[0],
                        "mapval": data[1]
                    }
                    data_list.append(s)
                value['input'] = data_list
                for ky in keylist:
                    if ky in value:
                        value.pop(ky)
                tasklist.append(value)
            wfdict['tasks'] = tasklist
            wflist.append(wfdict)
        grp_wf = {
            "grp_workflow_name": shelf['name'],
            "grp_workflow_id": shelf['wid'],
            "subworkflows": wflist
        }
        grp_wf_list.append(grp_wf)
    if os.path.exists(get_global_wf_config_file()) == True:
        doc = parse(get_global_wf_config_file())
        htype_list = doc.getElementsByTagName('htype')
        input_list = []
        for htype in htype_list:
            if htype.getAttribute('stacktype') == stacktype:
                for ipt in htype.getElementsByTagName('input'):
                    if name != 'kvm_console_ip':
                        input_dict = {
                            "name": ipt.getAttribute('name'),
                            "value": ipt.getAttribute('value'),
                        }
                        input_list.append(input_dict)
    discovery_list = []
    if os.path.exists(get_devices_wf_config_file()) == True:
        doc = parse(get_devices_wf_config_file())
        device_list = doc.getElementsByTagName('device')
        for device in device_list:
            discovery_dict = {
                "device_type": device.getAttribute('device_type'),
                "model": device.getAttribute('model'),
                "ipaddress": device.getAttribute('ipaddress'),
                "serial_no": device.getAttribute('serial_no'),
                "tag": device.getAttribute('tag'),
                "name": device.getAttribute('name'),
                "mac": device.getAttribute('mac'),
                "ntp_server": device.getAttribute("ntp_server"),
                "gateway": device.getAttribute("gateway"),
                "netmask": device.getAttribute("netmask")
            }
            if device.getAttribute('device_type') == 'Nexus 5k':
                discovery_dict['system_image'] = device.getAttribute(
                    'system_image')
                discovery_dict['kickstart_image'] = device.getAttribute(
                    'kickstart_image')
                discovery_dict['image_version'] = device.getAttribute(
                    'image_version')
            elif device.getAttribute('device_type') == 'Nexus 9k':
                discovery_dict['system_image'] = device.getAttribute(
                    'switch_image')
                discovery_dict['image_version'] = device.getAttribute(
                    'image_version')
            elif device.getAttribute('device_type') == 'MDS':
                discovery_dict['kickstart_image'] = device.getAttribute(
                    'kickstart_image')
                discovery_dict['system_image'] = device.getAttribute(
                    'system_image')
                discovery_dict['image_version'] = device.getAttribute(
                    'image_version')
            elif device.getAttribute('device_type') == 'UCSM':
                discovery_dict['leadership'] = device.getAttribute(
                    'leadership')
                discovery_dict['vipaddress'] = device.getAttribute(
                    'vipaddress')
                discovery_dict['esxi_file'] = device.getAttribute(
                    'esxi_file')
                discovery_dict['dns'] = device.getAttribute('dns')
                discovery_dict['domain_name'] = device.getAttribute(
                    'domain_name')
                discovery_dict['blade_image'] = device.getAttribute(
                    'blade_image')
                discovery_dict['infra_image'] = device.getAttribute(
                    'infra_image')

            discovery_list.append(discovery_dict)
    dicts['components'] = discovery_list
    dicts['workflows'] = grp_wf_list
    dicts['global_config'] = input_list
    dicts['stacktype'] = stacktype
    with open(g_download_dir + stacktype + '.json', 'w') as outfile:
        json.dump(dicts, outfile, indent=4)
    res.setResult({"url": stacktype + ".json"}, PTK_OKAY, "success")
    return res


def get_value_from_xml(jid, texecid, name):
    if jid != None and os.path.exists(get_job_file(jid)) is True:
        job_file = get_job_file(jid)
        fd = open(job_file, 'r')
        doc = xmltodict.parse(fd.read())
        if doc['workflow']['@id'] != None and 'wtype' not in doc['workflow']:
            for i in doc['workflow']['tasks']['task']:
                if i['@texecid'] == texecid:
                    if isinstance(i['args']['arg'], (list,)):
                        for j in i['args']['arg']:
                            if j is not None and j['@name'] == name:
                                return j['@value'], j['@mapval'] if '@mapval' in j else ''
                    else:
                        if i['args']['arg']['@name'] == name:
                            return i['args']['arg']['@value'], i['args']['arg']['@mapval'] if '@mapval' in i['args']['arg'] else ''
    return "", ""


def import_configuration(configfile):
    res = result()
    configfile.save("/tmp/" + configfile.filename)
    with open("/tmp/" + configfile.filename) as f:
        tmp_data = json.load(f)
    status, details = get_xml_element(settings, 'subtype')
    if details[0]['subtype'] != tmp_data['stacktype']:
        res.setResult(False, PTK_INTERNALERROR, "Upload Valid Stacktype JSON")
        return res
    shutil.copy2("/tmp/" + configfile.filename, get_download_path() +
                 'import-' + tmp_data['stacktype'] + '.json')
    with open(get_download_path() + 'import-' + tmp_data['stacktype'] + '.json') as f:
        data = json.load(f)
    for wfs in data['workflows']:
        for wf in wfs['subworkflows']:
            if len(wf['tasks']) > 0:
                for i in wf['tasks']:
                    exec("%s = %s" % ("input_obj",
                                      i['taskid'] + "." + i['taskid'] + "Inputs" + "()"))
                    inputs = [x for x in dir(input_obj) if not x.startswith(
                        '__') and not x.endswith('__')]
                    for j in i['input']:
                        if j['name'] not in inputs:
                            return j['name']
                        exec("%s = %s.%s" % ("field", "input_obj", j['name']))
                        wftaskip = job_task_inputs(
                            field=field, tid=i['taskid'])
                        if 'mandatory' in wftaskip and not str(j['value']):
                            res.setResult(
                                False, PTK_INTERNALERROR, "Invalid JSON")
                            return res
    global_file = open(get_global_wf_config_file(), 'r')
    doc = xmltodict.parse(global_file.read())
    stacktype = False
    for k in doc['globals']['htype']:
        if k['@stacktype'] == data['stacktype']:
            stacktype = True
            for gl in data['global_config']:
                inpt = False
                for inp in k['input']:
                    if gl['name'] == inp['@name']:
                        inpt = True
                        break
                if inpt == False:
                    res.setResult(False, PTK_INTERNALERROR, "Invalid JSON")
                    return res
    for comp in data['components']:
        if 'device_type' in comp and comp['device_type'] == 'Nexus 5k':
            if 'system_image' not in comp or 'kickstart_image' not in comp:
                res.setResult(False, PTK_INTERNALERROR, "Invalid JSON")
                return res
        elif 'device_type' in comp and comp['device_type'] == 'Nexus 9k':
            if 'system_image' not in comp:
                res.setResult(False, PTK_INTERNALERROR, "Invalid JSON")
                return res
        elif 'device_type' in comp and comp['device_type'] == 'MDS':
            if 'system_image' not in comp or 'kickstart_image' not in comp:
                res.setResult(False, PTK_INTERNALERROR, "Invalid JSON")
                return res
        elif 'device_type' in comp and comp['device_type'] == 'UCSM':
            if 'domain_name' not in comp or 'esxi_file' not in comp or 'infra_image' not in comp or 'blade_image' not in comp:
                res.setResult(False, PTK_INTERNALERROR, "Invalid JSON")
                return res
    if stacktype == False:
        res.setResult(False, PTK_INTERNALERROR, "Invalid JSON")
        return res
    res.setResult(True, PTK_OKAY, "success")
    return res


def json_config_defaults(stacktype):
    res = result()
    comp_list = []
    conf_list = []
    if os.path.exists(get_download_path() + 'import-' + stacktype + '.json') is True:
        with open(get_download_path() + 'import-' + stacktype + '.json') as f:
            data = json.load(f)
        for comp in data['components']:
            component = {
                "device_type": comp['device_type'],
                "switch_name": comp['name'],
                "tag": comp['tag'] if comp['device_type'] != 'PURE' else '',
            }
            if comp['device_type'] == 'Nexus 5k':
                component['switch_image'] = {
                    "switch_system_image": comp['system_image'], "switch_kickstart_image": comp['kickstart_image']}
            elif comp['device_type'] == 'Nexus 9k':
                component['switch_image'] = {
                    "switch_system_image": comp['system_image']}
            elif comp['device_type'] == 'MDS':
                component['switch_image'] = {
                    "switch_system_image": comp['system_image'], "switch_kickstart_image": comp['kickstart_image']}
            elif comp['device_type'] == 'UCSM':
                component['mode'] = comp['leadership']
                component['dns'] = comp['dns']
                component['domain_name'] = comp['domain_name']
                component['blade_image'] = comp['blade_image']
                component['infra_image'] = comp['infra_image']
                component['esxi_file'] = comp['esxi_file']
            comp_list.append(component)
        for conf in data['global_config']:
            config = {
                "name": conf['name'],
                "value": conf['value']
            }
            conf_list.append(config)
    dt = {"devices": comp_list, "global_config": conf_list}
    res.setResult(dt, PTK_OKAY, "success")
    return res


def deploy_workflows(stacktype):
    init = 0
    while 1:
        status, devices = get_xml_element(static_discovery_store, 'validated')
        if status == True:
            if any(dev['configured'] == 'Re-validate' for dev in devices) == True:
                loginfo(
                    "%s configuration failed. Please retry the configuration" % dev['name'])
                return False

            conf_list = [dev['name']
                         for dev in devices if dev['configured'] == 'Configured']
            if len(devices) == len(conf_list):
                loginfo("Initial configuration completed for %s" %
                        str(conf_list))
                init = 1
                break
            else:
                loginfo(
                    "Waiting for all devices to be configured, current:" + str(len(conf_list)))
                time.sleep(5)

    if init == 1:
        obj = Orchestration()
        res = obj.batchexecute(stacktype, '')
        if res.getStatus() == PTK_OKAY:
            loginfo("Workflow execution started...")
            return True
        else:
            loginfo("Failed to deploy workflows. %s" % res.getMsg())
            return False
    else:
        loginfo("Initial configuration failed")
        return False


def restore_config(stacktype, datas):
    res = result()
    res_1 = save_config(stacktype, datas)
    if res_1.getStatus() == PTK_OKAY:
        res_2 = initialconfig()
        if res_2.getStatus() == PTK_OKAY:
            threading.Thread(target=deploy_workflows,
                             args=(stacktype,)).start()
            res.setResult([], PTK_OKAY, "success")
        else:
            res.setResult([], PTK_INTERNALERROR,
                          "Component Initialization Failed")
    else:
        res.setResult(res_1.getResult(), PTK_INTERNALERROR,
                      "Failed to save the configuration details")
    return res


def update_config_inputs(stacktype, jid):
    loginfo("Updating json config to xml")
    conf_json = get_download_path() + 'import-' + stacktype + '.json'
    if os.path.exists(conf_json) is True:
        with open(conf_json, 'r') as fd:
            json_config = json.loads(fd.read())
    else:
        loginfo("JSON configuration file not found")
        return False

    with open(get_job_file(jid)) as td:
        jobdoc = xmltodict.parse(td.read())

    wf_list = []
    for gwf in json_config['workflows']:
        for wf in gwf['subworkflows']:
            wf_list.append(wf)

    for jwf in wf_list:
        if '@id' in jobdoc['workflow'] and jobdoc['workflow']['@id'] == jwf['wid']:
            taskset = [(xtask, jtask) for xtask in jobdoc['workflow']['tasks']['task']
                       for jtask in jwf['tasks'] if xtask['@texecid'] == jtask['texecid']]
            for task in taskset:
                task_dict = {}
                xml_task, json_task = task[0], task[1]
                xml_args = [xml_task['args']['arg']] if type(
                    xml_task['args']['arg']) != list else xml_task['args']['arg']
                argset = [(xarg, jarg) for xarg in xml_args for jarg in json_task['input']
                          if xarg['@name'] == jarg['name']]
                for arg in argset:
                    arg_dict = {}
                    xml_arg, json_arg = arg[0], arg[1]
                    arg_dict['execid'] = json_task['texecid'].encode('utf-8')
                    arg_dict['ismapped'] = json_arg['mapval'].encode('utf-8')
                    arg_dict['values'] = str(json_arg['value']).encode('utf-8')
                    task_dict[json_arg['name']] = arg_dict

                loginfo("Updating task id %s of workflow %s" %
                        (json_task['texecid'].encode('utf-8'), jwf['wid']))
                job_task_input_save_api(
                    jid, json_task['texecid'], task_dict, "job")
    return True
