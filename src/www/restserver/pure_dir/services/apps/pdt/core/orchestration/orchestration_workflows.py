"""
    orchestration_workflows
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Supports worklow list, save as functionality

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.kickstart import *
from pure_dir.services.apps.pdt.core.discovery import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_globals import*
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


from xml.dom.minidom import *
import zipfile
from distutils.dir_util import copy_tree
from slugify import slugify
import xmltodict
import uuid
import os
import os.path
import shutil
import glob
import random
from pure_dir.infra.common_helper import *
import hashlib
g_persistant_prepare = 0

g_flash_stack_types = [
    {'label': 'FA//FI ', 'value': 'fs-mini', 'tag': 'FC',
        'enabled': False, 'req_hardwares': {'UCSM': 2, 'PURE': 1}},
    {'label': 'FA//FI ', 'value': 'fa-fi-iscsi', 'tag': 'iSCSI',
        'enabled': False, 'req_hardwares': {'UCSM': 2, 'PURE': 1}},
    {'label': 'FA//MDS//Nexus 9K//FI',
        'value': 'fa-n9k-fi-mds-fc', 'tag': 'FC', 'enabled': True, 'req_hardwares': {'UCSM': 2, 'Nexus 9k': 2, 'MDS': 2, 'PURE': 1}},
    {'label': 'FA//MDS//FI ', 'value': 'fa-mds-fi-fc', 'tag': 'FC', 'enabled': False,
        'req_hardwares': {'UCSM': 2, 'Nexus 9k': 2, 'MDS': 2, 'PURE': 1}},
    {'label': 'FA//MDS//Nexus 5K//FI', 'value': 'fa-mds-n5k-fi-fc',
        'tag': 'FC', 'enabled': False, 'req_hardwares': {'UCSM': 2, 'Nexus 5k': 2, 'PURE': 1}},
    {'label': 'FA//Nexus 5K//FI', 'value': 'fa-n5k-fi-fc',
        'tag': 'FC', 'enabled': True, 'req_hardwares': {'UCSM': 2, 'Nexus 5k': 2, 'PURE': 1}},

    {'label': 'FA//Nexus 5K//FI', 'value': 'fa-n5k-figen2-fc',
        'tag': 'FC', 'enabled': True, 'req_hardwares': {'UCSM': 2, 'Nexus 5k': 2, 'PURE': 1}, 'hidden': True},

    {'label': 'FA//Nexus 5K//FI', 'value': 'fa-n5k-figen2-iscsi',
        'tag': 'FC', 'enabled': True, 'req_hardwares': {'UCSM': 2, 'Nexus 5k': 2, 'PURE': 1}, 'hidden': True},

    {'label': 'FA//Nexus 5K//FI', 'value': 'fa-n5k-fi-iscsi',
        'tag': 'iSCSI', 'enabled': True, 'req_hardwares': {'UCSM': 2, 'Nexus 5k': 2, 'PURE': 1}},
    {'label': 'FA//Nexus 9K//FI ', 'value': 'fa-n9k-fi-iscsi',
        'tag': 'iSCSI', 'enabled': True, 'req_hardwares': {'UCSM': 2, 'Nexus 9k': 2, 'PURE': 1}},
]


def _get_all_file_paths(directory, jobid, allfiles):
    """
    #TODO not used, to be removed
    :param directory: 
    :param jobid: 
    :param allfiles: 

    """

    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            if os.path.splitext(filename)[1] == ".xml":
                if allfiles == 1:
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
                else:
                    jobidlist = []
                    for job in jobid['jobid']:
                        jobname = "wf-%s.xml" % job
                        jobidlist.append(jobname)
                    if filename in jobidlist:
                        filepath = os.path.join(root, filename)
                        file_paths.append(filepath)

    return file_paths


def get_all_workflows():
    wfs = []
    for stack_type in g_flash_stack_types:
        wfs = wfs + glob.glob(get_workflow_files_pattern(stack_type['value']))
    return wfs


def workflows_list_api(htype=''):
    """
     List of Workflows available
    :param htype: stacktype, if not provided, all worflows are returned

    """
    wfs = []
    if len(htype) > 0:
        wfs = glob.glob(get_workflow_files_pattern(htype))
    else:
        wfs = get_all_workflows()

    wf_list = []
    obj = result()

    for wf in wfs:
        fd = None
        wtype = ''
        try:
            loginfo("parsing file" + wf)
            fd = open(wf, 'r')
            doc = xmltodict.parse(fd.read())
            if '@hidden' in doc['workflow'] and doc['workflow']['@hidden'] == '1':
                loginfo("skipping workflow" + wf)
                continue

            if '@wtype' in doc['workflow'] and doc['workflow']['@wtype'] == 'wgroup':
                wtype = doc['workflow']['@wtype']
            else:
                wtype = 'standalone'

            order = '0'
            if '@order' in doc['workflow']:
                order = doc['workflow']['@order']

            if '@type' in doc['workflow'] and '@id' in doc['workflow'] \
                    and '@desc' in doc['workflow'] and '@isdeletable' in doc['workflow']:
                if len(htype) > 0:
                    if '@htype' in doc['workflow'] and doc['workflow']['@htype'] == htype:
                        wf_entity = {
                            'id': doc['workflow']['@id'],
                            'name': doc['workflow']['@name'],
                            'desc': doc['workflow']['@desc'],
                            'type': doc['workflow']['@type'],
                            'isdeletable': doc['workflow']['@isdeletable'],
                            'wtype': wtype,
                            'order': order,
                            'execstatus': 'ready'}
                        wf_list.append(wf_entity)
                    else:
                        pass
                else:
                    wf_entity = {
                        'id': doc['workflow']['@id'],
                        'name': doc['workflow']['@name'],
                        'desc': doc['workflow']['@desc'],
                        'type': doc['workflow']['@type'],
                        'isdeletable': doc['workflow']['@isdeletable'],
                        'wtype': wtype,
                        'order': order,
                        'execstatus': 'ready'}
                    wf_list.append(wf_entity)

        except IOError:
            continue
    obj.setResult(
        sorted(wf_list, key=lambda x: x["order"]), PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def workflows_group_info_api(id, ttype=''):
    """
    Returns workflow group info
    :param id: workflow ID 

    """
    doc = None
    obj = result()
    wf_list = []

    try:
        with open(get_job_file(id)) as td:
            doc = xmltodict.parse(td.read())
    except IOError:
        loginfo("No such workflow")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    if '@wtype' not in doc['workflow'] or doc['workflow']['@wtype'] != 'wgroup':
        loginfo("Not a workflow group")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    for wf in getAsList(doc['workflow']['wfs']['wf']):
        wf_entity = {
            'name': wf['@name'],
            'execid': wf['@wexecid'],
            'jobid': wf['@jid'],
            'onsuccess': wf['@OnSuccess'],
            'onfailure': wf['@OnFailure'],
            'isinitwf': wf['@initwf']}

        wf_list.append(wf_entity)

    obj.setResult(wf_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def workflow_info_api(wid):
    """
    Returns individual workflow
    :param wid: Workflow ID 

    """
    wfs = get_all_workflows()
    obj = result()
    flag = False
    for wf in wfs:
        fd = None
        try:
            fd = open(wf, 'r')
            doc = xmltodict.parse(fd.read())
            if '@wtype' in doc['workflow'] and doc['workflow']['@wtype'] == 'wgroup':
                wtype = doc['workflow']['@wtype']
            else:
                wtype = 'standalone'
            if doc['workflow']['@id'] == wid:
                flag = True
                wf_info = {
                    'id': doc['workflow']['@id'],
                    'name': doc['workflow']['@name'],
                    'desc': doc['workflow']['@desc'],
                    'type': doc['workflow']['@type'],
                    'isdeletable': doc['workflow']['@isdeletable'],
                    'wtype': wtype}

        except IOError:
            continue
    if flag == False:
        loginfo("Workflow does not exist")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
    else:
        obj.setResult(wf_info, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def delete_workflow_api(wid):
    """
    Deletes a workflow
    :param wid: Workflow ID 

    """
    wfs = get_all_workflows()
    obj = result()
    flag = False
    for wf in wfs:
        fd = None
        try:
            fd = open(wf, 'r')
            doc = xmltodict.parse(fd.read())
            gwflowtasks = wf.split("__")[-1]
            if doc['workflow']['@id'] == wid or gwflowtasks == wid + ".xml":
                flag = True
                os.remove(wf)

        except IOError:
            continue
    if flag == False:
        loginfo("Workflow does not exist")
        obj.setResult(None, PTK_NOTEXIST,  _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
    else:
        obj.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def get_workflow_file_path(wname):
    wfs = []
    for stack_type in g_flash_stack_types:
        fname = get_workflow_file(wname, stack_type['value'])
        if os.path.isfile(fname) == True:
            return fname
    return None


def prepare_tasks(jobid):
    """
    Prepares a workflow for execution.
    Triggers individual prepare on each task to pre-populate the job xml
    :param jobid: 
    return: returns res structure 
    """
    obj = result()
    try:
        with open(get_job_file(jobid)) as td:
            jobdoc = xmltodict.parse(td.read())

        is_simulated = "0"
        if '@simulate' in jobdoc['workflow']:
            is_simulated = jobdoc['workflow']['@simulate']
        if is_simulated == "1":
            obj.setResult(None, PTK_OKAY, "success")
            return obj

        ret = getglobalvals(jobdoc['workflow']['@htype'])
        if ret.getStatus() != PTK_OKAY:
            return res

        for task in jobdoc['workflow']['tasks']['task']:
            tid = task['@id']
            exec("%s = %s" % ("task_obj", tid + "." + tid + "()"))
            if 'prepare' in dir(task_obj):
                method = getattr(task_obj, "prepare")
                res = method(jobid, task['@texecid'], ret.getResult())
                if res.getStatus() != PTK_OKAY:
                    return res
            else:
                continue
        obj.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj

    except Exception as e:
        loginfo("Unable to prepare job" + str(e))
        obj.setResult(None, PTK_INTERNALERROR,
                      _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return obj


def check_job_with_wid_exists(wname):
    """
     Checks if workflow with same name exist 
     :param wname: workflow name 

    """
    jobs = glob.glob(get_job_file_pattern())
    job_details = []
    obj = result()
    for job in jobs:
        try:
            with open(job) as td:
                jobdoc = xmltodict.parse(td.read())

            sub_wfs = []
            if '@wtype' in jobdoc['workflow'] and jobdoc['workflow']['@wtype'] == 'wgroup':
                t_wfs = getAsList(jobdoc['workflow']['wfs']['wf'])
                for t_wf in t_wfs:
                    data = {'wid': t_wf['@id']}
                    sub_wfs.append(data)
            if job.find('job-') == -1:
                continue

            jobid = job[job.find('job-') + 4: -4]

            if '@wtype' in jobdoc['workflow'] and jobdoc['workflow']['@wtype'] == 'wgroup':
                job_det = {'jobid': jobid, 'wid': jobdoc['workflow']['@id'],
                           'wtype': jobdoc['workflow']['@wtype'], 'subwfs': sub_wfs}
            else:
                job_det = {
                    'jobid': jobid, 'wid': jobdoc['workflow']['@id'],  'wtype': 'standalone', 'subwfs': sub_wfs}

            job_details.append(job_det)
        except Exception as e:
            loginfo(str(e))
            obj.setResult(None, PTK_INTERNALERROR, _(
                "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
            return obj

    for job in job_details:
        if job['wid'] != wname:
            continue

        if job['wtype'] != 'wgroup':
            job_dict = {'jobid': jobid, 'subjobs': []}
            obj.setResult(job_dict, PTK_OKAY, "success")
            return obj
        else:
            subjobs = []
            for wfs in job['subwfs']:
                for tmp_job in job_details:
                    if tmp_job['wid'] == wfs['wid']:
                        subjobs.append(
                            {'job_id': tmp_job['jobid'], 'wid':  tmp_job['wid']})

            job_dict = {'jobid': job['jobid'], 'subjobs': subjobs}
            obj.setResult(job_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return obj

    obj.setResult(None, PTK_NOTEXIST, _("PDT_SUCCESS_MSG"))
    return obj


def workflowprepare_helper(wname):
    return workflowprepare_helper_safe(wname, 0)


def workflow_persistant_prepare_helper(wname):
    return workflowprepare_helper_safe(wname, 1)


def workflowprepare_helper_safe(wname, persistant_prepare):
    """
    Prepares job xml from workflow, prepopulate input values 
    :param wname: workflow name 
    :param persistant_prepare: if set, if a job with same wid exists, the job id
                                will be returned instead of a new job id 
    """

    jobid = str(uuid.uuid4())
    job_dict = {}
    obj = result()
    subjobs = []

    if persistant_prepare == 1:
        # do not prepare jobs with same workflow name
        res = check_job_with_wid_exists(wname)
        if res.getStatus() == PTK_OKAY:
            return res

    try:
        shutil.copyfile(get_workflow_file_path(wname), get_job_file(jobid))
        with open(get_job_file(jobid)) as td:
            if get_config_mode() != "json":
                prepare_tasks(jobid)
            jobdoc = xmltodict.parse(td.read())

        if '@wtype' not in jobdoc['workflow'] or jobdoc['workflow']['@wtype'] != 'wgroup':
            # its a workflow group
            job_dict = {'jobid': jobid, 'subjobs': []}
            obj.setResult(job_dict, PTK_OKAY, "success")
            return obj

        for wf in getAsList(jobdoc['workflow']['wfs']['wf']):
            tuuid = str(uuid.uuid4())
            subjobs.append({'job_id': tuuid, 'wid':  wf['@id']})
            shutil.copyfile(get_workflow_file_path(
                wf['@id']), get_job_file(tuuid))
            wf['@jid'] = tuuid
            if get_config_mode() != "json":
                prepare_tasks(tuuid)

        out = xmltodict.unparse(jobdoc, pretty=True)
        with open(get_job_file(jobid), 'w') as file:
            file.write(out.encode('utf-8'))

    except BaseException as e:
        loginfo("Unable to create log")
        obj.setResult(None, PTK_INTERNALERROR, _(
            "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return obj

    job_dict = {'jobid': jobid, 'subjobs': subjobs}
    obj.setResult(job_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def job_discard_api(jobid, force):
    """
    Deletes a Job
    :param jobid: jobid to delete 
    :param force: 

    """
    obj = result()
    # TODO execute only if force is specified
    try:
        os.remove(get_job_file(jobid))
    except BaseException:
        loginfo("unable to discard Job")
        obj.setResult(None, PTK_INTERNALERROR, _(
            "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return obj

    obj.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def job_save_as_api(jobid, data):
    """
    Saves a Job as a new workflow
    :param jobid: Jobid 
    :param data: name, desc .. for new workflow 

    """
    obj = result()
    new_wf_id = slugify(data['name'])
    path = get_job_file(jobid)
    if os.path.exists(path) == False:
        loginfo("Workflow not available! Invalid Jobid")
        obj.setResult(False, PTK_NOTEXIST,
                      _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj
    hw_type = None

    with open(path) as td:
        t_doc = xmltodict.parse(td.read())
        hw_type = t_doc['workflow']['@htype']

    dest = get_workflow_file(new_wf_id, hw_type)

    if os.path.exists(dest):
        loginfo("Name conflict")
        obj.setResult(False, PTK_NOTEXIST,
                      _("PDT_NAME_CONFLICT_ERR_MSG"))
        return obj

    shutil.copy2(path, dest)
    xmldoc = parse(dest)
    names = xmldoc.getElementsByTagName('workflow')
    for name in names:
        name.setAttribute('id', new_wf_id)
        name.setAttribute('name', data['name'])
        name.setAttribute('desc', data['desc'])
        name.setAttribute('isdeletable', "1")

    with open(dest) as td:  # Edit group workflow file to edit the id of workflows
        jobdoc = xmltodict.parse(td.read())
        if '@wtype' in jobdoc['workflow'] and jobdoc['workflow']['@wtype'] == 'wgroup':
            for wf in jobdoc['workflow']['wfs']['wf']:
                new_wf_id = wf['@id'] + "__" + slugify(data['name'])
                wfs = xmldoc.getElementsByTagName('wf')
                for wfelement in wfs:
                    if wfelement.getAttribute('id') in new_wf_id:
                        wfelement.setAttribute('id', new_wf_id)
        fd = open(dest, 'w')
        xmldoc.writexml(fd)
        fd.close()

        # edit the individual workflow files to modify the saved workflow id"
        with open(get_job_file(jobid)) as td:
            jobdoc = xmltodict.parse(td.read())

        if '@wtype' in jobdoc['workflow'] and jobdoc['workflow']['@wtype'] == 'wgroup':
            for wf in jobdoc['workflow']['wfs']['wf']:
                new_wf_id = wf['@id'] + "__" + slugify(data['name'])
                path = get_job_file(wf['@jid'])
                dest = get_workflow_file(new_wf_id, hw_type)
                shutil.copy2(path, dest)
                xmldoc = parse(dest)
                names = xmldoc.getElementsByTagName('workflow')
                for name in names:
                    name.setAttribute('id', new_wf_id)
                    name.setAttribute('isdeletable', "1")
                fd = open(dest, 'w')
                xmldoc.writexml(fd)
                fd.close()

    obj.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def zip(src, dst):
    """
    Ready zip to download workflows
    :param src: source folder path 
    :param dst: destination folder path

    """
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            if filename.endswith('.xml') or filename.endswith('.log') or len(filename.split(".")) == 1:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
    zf.close()


def export_workflow_api(wkflowlist):
    """
     Method to export workflow
    :param wkflowlist: workflow list 

    """
    res = result()
    filelist = []
    wkflow_path = get_workflow_path()
    dw_path = get_download_path()
    for wkf in wkflowlist['jobid']:
        for root, htypelist, filenames in os.walk(wkflow_path):
            for htype in htypelist:
                if os.path.exists(get_htype_workflow_path(htype, wkf)) == True:
                    with open(get_htype_workflow_path(htype, wkf)) as td:
                        doc = xmltodict.parse(td.read())
                    if '@wtype' in doc['workflow'] and doc['workflow']['@wtype'] == "wgroup":
                        src = get_htype_workflow_path(htype, wkf)
                        shutil.copy2(src, dw_path)
                        if type(doc['workflow']['wfs']['wf']) == list:
                            for wkflowgrp in doc['workflow']['wfs']['wf']:
                                if os.path.exists(get_htype_workflow_path(htype, wkflowgrp['@id'])) == True:
                                    src = get_htype_workflow_path(
                                        htype, wkflowgrp['@id'])
                                    shutil.copy2(src, dw_path)
                        else:
                            if os.path.exists(get_htype_workflow_path(htype, doc['workflow']['wfs']['wf']['@id'])) == True:
                                src = get_htype_workflow_path(
                                    htype, doc['workflow']['wfs']['wf']['@id'])
                                shutil.copy2(src, dw_path)
                    else:
                        src = get_htype_workflow_path(htype, wkf)
                        shutil.copy2(src, dw_path)
    zip(dw_path, dw_path + "workflows")
    for root, dirs, filenames in os.walk(dw_path):
        for fl in filenames:
            if fl.endswith('.xml'):
                os.remove(dw_path + fl)
    res.setResult("workflows.zip", PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def extract_zip(zip_file, extract_to):
    """

    :param zip_file: 
    :param extract_to: 

    """
    zip_ref = zipfile.ZipFile(zip_file, 'r')
    zip_ref.extractall(extract_to)
    zip_ref.close()


def import_workflow_api(uploadfile):
    """
    Method to import and export workflow
    :param uploadfile: Upload file path 

    """
    res = result()
    dw_path = get_download_path()
    if os.path.splitext(uploadfile.filename)[1] == ".zip":
        filepath = "%s%s" % (dw_path, uploadfile.filename)
        uploadfile.save(filepath)
        extract_zip(filepath, dw_path)
        for dirname, dirnames, filenames in os.walk(dw_path):
            for fl in filenames:
                if fl.endswith('.xml'):
                    fl_path = dw_path + fl
                    if os.path.exists(fl_path) == True:
                        with open(fl_path) as td:
                            doc = xmltodict.parse(td.read())
                        if '@htype' in doc['workflow']:
                            if os.path.exists(get_workflow_path() + doc['workflow']['@htype']) == True:
                                dest = get_workflow_path(
                                ) + doc['workflow']['@htype'] + "/"
                                shutil.copy2(fl_path, dest)
                            else:
                                os.mkdir(get_workflow_path() +
                                         doc['workflow']['@htype'])
                                dest = get_workflow_path(
                                ) + doc['workflow']['@htype'] + "/"
                                shutil.copy2(fl_path, dest)
        for root, dirs, filenames in os.walk(dw_path):
            for fl in filenames:
                if fl.endswith('.xml'):
                    os.remove(dw_path + fl)
        res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    else:
        res.setResult(False, PTK_INTERNALERROR, _(
            "PDT_UNSUPPORTED_FILE_TYPE_ERR_MSG"))
    return res


def flash_stack_type_api():
    """
    Returns flash stack types
    """

    res = result()
    f_types = []
    for flash_stack in g_flash_stack_types:
        if 'hidden' in flash_stack:
            continue

        f_types.append(flash_stack)
    res.setResult(f_types, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def check_pre_req_api(wid):
    """
    Looks for pre-requirement workflow
    :param wid: workflow ID 
    """

    res = result()
    prereq = "None"
    with open(get_workflow_file_path(wid)) as td:
        jobdoc = xmltodict.parse(td.read())
        if '@prereq' in jobdoc['workflow']:
            prereq = jobdoc['workflow']['@prereq']
        else:
            prereq = "None"
    if prereq == "None":
        res.setResult([], PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    with open(get_workflow_file_path(prereq)) as td:
        obj = xmltodict.parse(td.read())
        wf = [
            {
                "name": obj['workflow']['@name'],
                "msg":"Please ensure you have executed '" + obj['workflow']['@name'] + "' before executing this workflow",
                "prereq":obj['workflow']['@prereq']
            }
        ]
        res.setResult(wf, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    res.setResult([], PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res
