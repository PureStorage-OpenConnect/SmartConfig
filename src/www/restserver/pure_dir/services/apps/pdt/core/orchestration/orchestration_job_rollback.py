"""
    orchestration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Performs Job Roll back and supporting methods

"""

import threading
import glob
import shelve
import os
import time
import xmltodict

from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_rollback_status import update_rollback_task_status, prepare_rollback_status_file
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_status import update_task_status, clear_job_failed_status 
from pure_dir.services.apps.pdt.core.orchestration.orchestration_workflows import g_flash_stack_types
from pure_dir.services.apps.pdt.core.orchestration.orchestration_batch_status import update_batch_job_status, clear_group_job_status 

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

from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.infra.apiresults import *


def jobrollback_helper(jobid):
    """
    Does rollback for individual Jobs

    :param jobid: Job ID

    """

    res = result()

    if os.path.exists(get_shelf_file(jobid)) == False:
        loginfo("No such service request exists")
        res.setResult(None, PTK_NOTEXIST, _("PDT_FAILED_MSG"))
        return res
    simulate_mode = 0

    prepare_rollback_status_file(jobid)
    shelf = shelve.open(get_shelf_file(jobid), flag='r')
    logfile = get_rb_log_file(jobid)
    if shelf['simulate'] == '1':
        simulate_mode = 1
    wfcount = -1 if (len(shelf['job'])) == 0 else len(shelf['job']) - 1

    for x in range(wfcount, -1, -1):
        record = shelf['job'][str(x)]['record']
        g_obj_list = {}
        loginfo("Beginning of roll back len=" + str(len(record['tasklist'])))

        taskcount = -1 if len(
            record['tasklist']) == 0 else len(
            record['tasklist']) - 1
        customlogs("------ <b> " + record['wfname'] + "</b> ------\n", logfile)
        for i in range(taskcount, -1, -1):
            update_rollback_task_status(jobid,
                                        record['jobid'],
                                        record['tasklist'][str(i)]['texecid'],
                                        TASK_STATUS_EXECUTING)
            task = record['tasklist'][str(i)]
            customlogs("Rolling back '" + task['name'] + "'\n", logfile)
            loginfo("Rolling back Task " + task['name'])
            if simulate_mode == 1:
                my_cls = _get_obj(g_obj_list, "Test_" + task['class'])
            else:
                my_cls = _get_obj(g_obj_list, task['class'])
            method = getattr(my_cls, "rollback")
            retval = method(task['inputs'], task['outputs'], logfile)

            time.sleep(TASK_ROLLBACK_DELAY)
            if isinstance(retval, dict) == False:
                if retval.getStatus() != PTK_OKAY:
                    update_rollback_task_status(jobid,
                                                record['jobid'],
                                                record['tasklist'][str(i)]['texecid'],
                                                TASK_STATUS_FAILED)
                    res.setResult(None, PTK_FAILED, "failed")
                    return res
                else:
                    update_rollback_task_status(jobid,
                                                record['jobid'],
                                                record['tasklist'][str(i)]['texecid'],
                                                TASK_STATUS_COMPLETED)

                    # Update the original Job status as READY
                    update_task_status(
                        record['jobid'], record['tasklist'][str(i)]['texecid'], "READY")

            else:
                if retval['status'] != 'SUCCESS':
                    update_rollback_task_status(jobid,
                                                record['jobid'],
                                                record['tasklist'][str(i)]['texecid'],
                                                TASK_STATUS_FAILED)
                    res.setResult(None, PTK_FAILED, _("PDT_FAILED_MSG"))
                    return res
                else:
                    update_rollback_task_status(jobid,
                                                record['jobid'],
                                                record['tasklist'][str(i)]['texecid'],
                                                TASK_STATUS_COMPLETED)
                    # Update the original Job status as READY
                    update_task_status(
                        record['jobid'], record['tasklist'][str(i)]['texecid'], "READY")
        clear_job_failed_status(record['jobid'])
    clear_group_job_status(jobid)
    shelf.close()
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def job_rollback_api(stacktype, jobid):
    """
    Does the pre check for Job Rollback and trigger rollback

    :param stacktype: Stack type
    :param jobid: Job ID

    """

    res = result()

    if stacktype is not None and jobid is not None:
        loginfo("can't specify both jobid and stacktype")
        obj.setResult(None, PTK_FAILED,
                      _("PDT_INVALID_INPUT_ERR_MSG"))
        return obj
    if stacktype is not None:
        jobid = stacktype

    if not any(d['value'] == jobid for d in g_flash_stack_types):
        if os.path.exists(get_shelf_file(jobid)) == False:
            loginfo("No such service request exists")
            res.setResult(None, PTK_NOTEXIST,
                          _("PDT_ROLLBACK_FAILED_INSUFF_DATA_MSG"))
            return res
    else:

        if os.path.exists(get_batch_status_file(jobid)) == False:
            res.setResult(None, PTK_NOTEXIST,
                          _("PDT_ROLLBACK_FAILED_INSUFF_DATA_MSG"))
            return res

        fd = open(get_batch_status_file(jobid), 'r')
        doc = xmltodict.parse(fd.read())
        wfs = sorted(doc['Batchstatus']['workflows']['workflow'],
                     key=lambda x: x["@order"], reverse=True)
        for wf in wfs:
            if wf['@status'] == 'READY':
                continue
            if os.path.exists(get_shelf_file(wf['@jid'])) == False:
                loginfo("No such service request exists")
                res.setResult(None, PTK_NOTEXIST,
                              _("PDT_ROLLBACK_FAILED_INSUFF_DATA_MSG"))
                return res

    loginfo("Calling Jobrevert stacktype =" + jobid)
    threading.Thread(target=job_rollback_safe, args=(jobid,)).start()
    res.setResult(0, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def get_htype_wid_from_jobid(jobid):
    """
    Get stack type from Job ID

    :param jobid: Job ID

    """

    try:
        fd = open(get_job_file(jobid), 'r')
        doc = xmltodict.parse(fd.read())
        res = {'stacktype': doc['workflow']
               ['@htype'], 'wid': doc['workflow']['@id']}
        return res

    except Exception as e:
        loginfo("Exception" + str(e))
        return None
    return None


def job_rollback_safe(jobid):
    """
    Incase of Batch Job, rollback all the Jobs involved

    :param jobid: Job ID

    """

    if not any(d['value'] == jobid for d in g_flash_stack_types):
        # Not a batch rollback, continue with jobid
        details = get_htype_wid_from_jobid(jobid)
        update_batch_job_status(
            details['stacktype'], details['wid'], None, 'ROLLBACK')
        res = jobrollback_helper(jobid)
        if res.getStatus() != PTK_OKAY:
            update_batch_job_status(
                details['stacktype'], details['wid'], None, 'ROLLBACK_FAILED')
            loginfo("Batch rollback failed")
            return res
        update_batch_job_status(
            details['stacktype'], details['wid'], None, 'READY')

    else:
        try:
            fd = open(get_batch_status_file(jobid), 'r')
            doc = xmltodict.parse(fd.read())
            wfs = sorted(doc['Batchstatus']['workflows']['workflow'],
                         key=lambda x: x["@order"], reverse=True)
            for wf in wfs:
                if wf['@status'] == 'READY':
                    continue
                loginfo("Attempting rollback for wid" + wf['@id'])
                update_batch_job_status(jobid, wf['@id'], None, 'ROLLBACK')
                res = jobrollback_helper(wf['@jid'])
                if res.getStatus() != PTK_OKAY:
                    update_batch_job_status(
                        jobid, wf['@id'], None, 'ROLLBACK_FAILED')
                    loginfo("Batch rollback failed")
                    return res
                update_batch_job_status(jobid, wf['@id'], None, 'READY')

        except Exception as e:
            loginfo("Exception" + str(e))


def service_request_list_api():
    """
    Returns service request list

    """
    srs = glob.glob(get_shelf_files_pattern())
    sr_list = []
    obj = result()
    for sr in srs:
        try:
            loginfo("parsing file" + sr)
            rec = shelve.open(sr, flag='r')
            res = {'name': rec['name'], 'jobid': rec['jid'],
                   'desc': rec['desc'], 'etime': rec['etime']}
            sr_list.append(res)
            rec.close()
        except Exception as e:
            loginfo("Error Ocoured" + str(e))
    obj.setResult(sr_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def service_request_info_helper(jobid, shelf):
    """
    Get details of service request for sub jobs

    :param shelf: Dict containing rollback data
    :param jobid: Job ID

    """

    res = result()
    job_list = []
    wfcount = 0 if (len(shelf['job'])) == -1 else len(shelf['job']) - 1

    for x in range(wfcount, -1, -1):
        task_list = []
        job_rec = shelf['job'][str(x)]['record']
        job = {'wname': job_rec['wfname'],
               'jobid': job_rec['jobid'], 'tasklist': []}
        taskcount = -1 if (len(job_rec['tasklist'])) == 0 else len(
            job_rec['tasklist']) - 1
        for y in range(taskcount, -1, -1):
            task = {'name': job_rec['tasklist'][str(
                y)]['name'], 'task_id': job_rec['tasklist'][str(y)]['texecid'], 'seq_no': str(y)}
            task_list.append(task)
        job['tasklist'] = task_list
        job_list.append(job)

    res.setResult(job_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def _get_shelve_file(jobid):
    res = result()
    if os.path.exists(get_shelf_file(jobid)) == False:
        loginfo("file dosen't exists")
        res.setResult([], PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return res
    shelf = shelve.open(get_shelf_file(jobid), flag='r')
    res.setResult(shelf, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def service_request_info_api(jobid):
    """
    Get details of service request

    :param stacktype: Stack type
    :param jobid: Job ID

    """

    data = []
    ret = result()
    if not any(d['value'] == jobid for d in g_flash_stack_types):
        # Not a batch rollback, continue with jobid
        shlv_res = _get_shelve_file(jobid)
        if shlv_res.getStatus() != PTK_OKAY:
            return shlv_res
        shlv = shlv_res.getResult()
        res = service_request_info_helper(jobid, shlv)
        tmp = {'jobid': jobid, 'name': shlv['name'],
               'order': '0', 'subwflist': res.getResult()}
        data.append(tmp)
        ret.setResult(data, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret
    else:
        try:
            fd = open(get_batch_status_file(jobid), 'r')
            doc = xmltodict.parse(fd.read())
            wfs = sorted(doc['Batchstatus']['workflows']['workflow'],
                         key=lambda x: x["@order"], reverse=True)
            seqno = 0
            for wf in wfs:
                if wf['@status'] == 'READY':
                    continue
                shlv_res = _get_shelve_file(wf['@jid'])
                if shlv_res.getStatus() != PTK_OKAY:
                    return shlv_res
                shlv = shlv_res.getResult()

                res = service_request_info_helper(wf['@jid'], shlv)
                if res.getStatus() == PTK_OKAY:
                    tmp = {'jobid': wf['@jid'], 'name': shlv['name'], 'order': str(
                        seqno), 'subwflist': res.getResult()}
                    seqno = seqno + 1
                    data.append(tmp)
        except Exception as e:
            loginfo("Error Ocoured" + str(e))
    ret.setResult(data, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return ret


def get_field_name(jobid, field_id, texecid):
    """
    Get details of an input field

    :param jobid: Job ID
    :param stacktype: field_id

    """

    try:
        fd = open(get_job_file(jobid), 'r')
        job_doc = xmltodict.parse(fd.read())
        for task in job_doc['workflow']['tasks']['task']:
            if task['@texecid'] != texecid:
                continue
            exec("%s = %s" %
                 ("input_obj", task['@id'] + "." + task['@id'] + "Inputs" + "()"))
            exec("%s = %s.%s" % ("field", "input_obj", field_id))
            if field.name == field_id:
                group_members = []
                if field.ip_type == "group":
                    for member in field.members:
                        exec("%s = %s.%s" %
                             ("member_data", "input_obj", member))
                        gmember = {'label': member_data.label,
                                   'name': member_data.name}
                        group_members.append(gmember)

           # is a group field
                return {'name': field.name, 'label': field.label, 'gmembers': group_members}
    except BaseException:
        return None
    return None


def rollback_task_data_api(jobid, pjobid, tid):
    res = result()
    if os.path.exists(
            get_shelf_file(pjobid)) == False or os.path.exists(
            get_job_file(pjobid)) == False:
        loginfo("file dosen't exists")
        res.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return res

    shelf = shelve.open(get_shelf_file(pjobid), flag='r')
    wfcount = 0 if (len(shelf['job'])) == 0 else len(shelf['job']) - 1
    data = {'inputlist': [], 'outputlist': []}
    for x in range(wfcount, -1, -1):
        job_rec = shelf['job'][str(x)]['record']

        taskcount = 0 if (len(job_rec['tasklist'])) == 0 else len(
            job_rec['tasklist']) - 1
        for y in range(taskcount, -1, -1):
            if job_rec['tasklist'][str(y)]['texecid'] != tid:
                continue
            if job_rec['jobid'] != jobid:
                continue
            for key in job_rec['tasklist'][str(y)]['inputs']:
                tmp = get_field_name(job_rec['jobid'], key, tid)
                g_list = []
                if tmp is not None:
                    label = tmp['label']
                    g_list = tmp['gmembers']
                else:
                    label = job_rec['tasklist'][str(y)]['inputs'][key]

                input_data = {'key': key, 'value': job_rec['tasklist'][str(
                    y)]['inputs'][key], 'label': label, 'gmembers': g_list}

                data['inputlist'].append(input_data)
            res.setResult(data, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

    res.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
    return res


def _get_obj(g_obj_list, classname):
    if classname in g_obj_list:
        return g_obj_list[classname]

    try:
        exec("%s = %s" % ("g_obj_list[classname]",
                          classname + "." + classname + "()"))
        return g_obj_list[classname]

    except BaseException:
        raise NotImplementedError(
            "Class `{}` does not implemented `".format(classname))
