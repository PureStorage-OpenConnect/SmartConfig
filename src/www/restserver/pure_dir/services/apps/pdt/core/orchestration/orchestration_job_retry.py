"""
    Orchestration_job_retry
    ~~~~~~~~~~~~~~~~~~~~~~~

    Retry failed workflow

"""


from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import getAsList
#from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_file, get_job_dump_file, get_shelf_file
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_status import update_workflow_status, update_overall_status
from pure_dir.services.apps.pdt.core.orchestration.orchestration_group_job_status import group_job_status_api
from pure_dir.services.apps.pdt.core.orchestration.orchestration_batch_status import update_batch_job_status
from pure_dir.services.apps.pdt.core.orchestration.orchestration_workflows import g_flash_stack_types, workflowprepare_helper
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_executor import execute_task, jobexecute, jobexecute_helper
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_rollback import get_htype_wid_from_jobid
import os
import shelve
import xmltodict
import threading
from xml.dom.minidom import parse


def group_job_retry(doc, jid):
    """
    Retry a group job

    :param doc: XML document object
    :param jid: Job ID

    """
    res = result()
    failed_job = get_group_workflow_failed_job(jid)
    if failed_job is None:
        loginfo("No Failed Job Found in group job id=" + jid)
        res.setResult(None, PTK_INTERNALERROR, _(
            "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res

    update_workflow_status(jid, failed_job['jid'], TASK_STATUS_EXECUTING)
    ret = trigger_job_from_dump(jid, failed_job['jid'])
    if ret < 0:
        update_workflow_status(jid, failed_job['jid'], TASK_STATUS_FAILED)
        loginfo("Job Failed again" + failed_job['jid'])
        res.setResult(None, PTK_FAILED, "Job Failed again")
        return res

    update_workflow_status(jid, failed_job['jid'], TASK_STATUS_COMPLETED)
    # Finished executing failed Job, now  retrigger the rest
    wfs = getAsList(doc['workflow']['wfs']['wf'])
    wf = None
    for tmp_wf in wfs:
        if tmp_wf['@wexecid'] == failed_job['execid']:
            wf = tmp_wf
    if wf is None:
        loginfo("Unable to locate workflow")
        res.setResult(None, PTK_INTERNALERROR, "Unable to locate WF")
        return res

    wf = _getNextWf(doc, wf, ret)
    if wf is None:
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return res
    seqno = 0

    dump_shelf = shelve.open(get_job_dump_file(failed_job['jid']), flag="c")
    logfile = get_log_file(jid)

    master_record = shelve.open(get_shelf_file(jid), flag="w", writeback=True)

    seqno = get_job_seq_no(failed_job['jid'], master_record)
    if seqno < -1:
        loginfo("something went wrong")
    error = 0
    while True:
        update_workflow_status(jid, wf['@jid'], TASK_STATUS_EXECUTING)
        seqno = seqno + 1
        ret = jobexecute(wf['@jid'], seqno, master_record['job'], logfile)
        error = ret
        if ret == 0:
            update_workflow_status(jid, wf['@jid'], TASK_STATUS_COMPLETED)
        else:
            update_workflow_status(jid, wf['@jid'], TASK_STATUS_FAILED)
            update_overall_status(jid, TASK_STATUS_FAILED)

        wf = _getNextWf(doc, wf, ret)
        if wf is None:
            break

    update_overall_status(jid, TASK_STATUS_COMPLETED)
    master_record.close()

    if error == -1:
        update_overall_status(jid, TASK_STATUS_FAILED)
        res.setResult(None, PTK_FAILED, _("PDT_FAILED_MSG"))
    else:
        res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def _getNextWf(doc, wf, ret):
    """
    Get Next workflow to be executed

    :param doc: workflow doc object
    :param wf:  current workflow
    :param ret: status of current workflow

    """

    nexttask = wf['@OnSuccess'] if ret == 0 else wf['@OnFailure']
    if nexttask == 'None':
        return None

    for twf in doc['workflow']['wfs']['wf']:
        if twf['@wexecid'] == nexttask:
            return twf
    return None


def group_job_retry_precheck_helper(jobid):
    """
    Ensures the pre requsites for group job retry is met before actual trigger

    :param jobid: Job ID

    """

    res = result()
    err_msg = "Something went wrong. Unable to retry"
    if os.path.exists(get_job_file(jobid)) == False:
        res.setResult(None, PTK_FAILED, err_msg)
        return res

    if os.path.exists(get_shelf_file(jobid)) == False:
        loginfo("Missing Shelf file" + jobid)
        res.setResult(None, PTK_FAILED, err_msg)
        return res
    failed_job = get_group_workflow_failed_job(jobid)
    if failed_job is None:
        loginfo("No Failed Job Found in group job id=" + jobid)
        res.setResult(None, PTK_INTERNALERROR, err_msg)
        return res

    if os.path.exists(get_job_dump_file(failed_job['jid'])) == False:
        loginfo("No such dump file" + jobid)
        res.setResult(None, PTK_INTERNALERROR, err_msg)
        return res
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def job_retry_precheck(jobid):
    """
    Ensures the pre requsites for job retry is met before actual trigger

    :param jobid: Job ID

    """

    res = result()
    err_msg = _("PDT_UNABLE_TO_RETRY_ERR_MSG")
    if not any(d['value'] == jobid for d in g_flash_stack_types):
        # Not a batch resume, continue with jobid
        res = group_job_retry_precheck_helper(jobid)
        if res.getStatus() != PTK_OKAY:
            return res

    else:
        if os.path.exists(get_batch_status_file(jobid)) == False:
            loginfo("No such batch Job" + jobid)
            res.setResult(None, PTK_FAILED, err_msg)
            return res

        doc = None
        try:
            doc = parse(get_batch_status_file(jobid))

        except IOError:
            loginfo("Failed to open job file" + get_batch_status_file(jobid))
            res.setResult(None, PTK_FILEACCESSERROR, err_msg)
            return res

        batches = doc.getElementsByTagName('workflow')
        for batch in batches:
            if batch.hasAttribute('jid') and batch.getAttribute('status') == 'FAILED':
                failed_jid = batch.getAttribute('jid')
                break
        if failed_jid is None:
            loginfo("No failed Job in batch Job")
            res.setResult(None, PTK_FAILED, err_msg)
            return res
        res = group_job_retry_precheck_helper(failed_jid)
        if res.getStatus() != PTK_OKAY:
            return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def job_retry_api(stacktype, jobid):
    """
    Triggers a job retry, can specify either or parameter and not both

    :param stacktype: FlashStack type
    :param jobid: Job ID

    """

    obj = result()
    if stacktype is not None and jobid is not None:
        loginfo("can't specify both jobid and stacktype")
        obj.setResult(None, PTK_FAILED,
                      _("PDT_INVALID_INPUT_ERR_MSG"))
        return obj
    if stacktype is not None:
        jobid = stacktype

    res = job_retry_precheck(jobid)
    if res.getStatus() != PTK_OKAY:
        return res

    threading.Thread(target=job_retry_helper, args=(jobid,)).start()
    obj.setResult(0, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def job_retry_helper(jobid):
    """
    Triggers a job retry.

    :param jobid: Job ID or stacktype

    """

    loginfo("Attempting Job resume for jid:" + jobid)
    if not any(d['value'] == jobid for d in g_flash_stack_types):
        # Not a batch resume, continue with jobid

        details = get_htype_wid_from_jobid(jobid)
        update_batch_job_status(
            details['stacktype'], details['wid'], None, 'EXECUTING')
        res = job_retry_standalone(jobid)
        if res.getStatus() != PTK_OKAY:
            update_batch_job_status(
                details['stacktype'], details['wid'], None, 'FAILED')
            return res

        update_batch_job_status(
            details['stacktype'], details['wid'], None, 'COMPLETED')
        return res

    else:
        return job_retry_batch(jobid)


def job_retry_batch(jobid):
    """
    Triggers a batch job retry.

    :param jobid: stacktype

    """

    res = result()
    loginfo("Job resume for Batch Job" + jobid)
    if os.path.exists(get_batch_status_file(jobid)) == False:
        loginfo("No such batch Job" + jobid)
        res.setResult(None, PTK_FAILED, _("PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
        return res

    failed_jid = None
    failed_wid = None

    doc = None
    try:
        doc = parse(get_batch_status_file(jobid))

    except IOError:
        loginfo("Failed to open job file" + get_batch_status_file(jobid))
        res.setResult(None, PTK_FILEACCESSERROR,
                      _("PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
        return res

    batches = doc.getElementsByTagName('workflow')
    pending_wfs = []
    for batch in batches:
        if batch.hasAttribute('jid') and batch.getAttribute('status') == 'FAILED':
            failed_jid = batch.getAttribute('jid')
            failed_wid = batch.getAttribute('id')
            break

    for batch in batches:
        if batch.hasAttribute('jid') == False and batch.getAttribute('status') == 'READY':
            wf = {'id': batch.getAttribute(
                'id'), 'order': batch.getAttribute('order')}
            pending_wfs.append(wf)

    pending_wfs = sorted(pending_wfs, key=lambda x: x["order"])

    if failed_jid is None:
        loginfo("No failed Job in batch Job")
        res.setResult(None, PTK_FAILED, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res

    update_batch_job_status(jobid, failed_wid, failed_jid, 'EXECUTING')
    retry_res = job_retry_standalone(failed_jid)
    if retry_res.getStatus() != PTK_OKAY:
        loginfo("Workflow Failed again" + get_batch_status_file(jobid))
        ''' The failure can be either from  a task failed earlier or could be any other task in the workflow '''
        update_batch_job_status(jobid, failed_wid, failed_jid, 'FAILED')
        return retry_res

    update_batch_job_status(jobid, failed_wid, failed_jid, 'COMPLETED')
    for wf in pending_wfs:
        res = workflowprepare_helper(wf['id'])
        if res.getStatus() != PTK_OKAY:
            res.setResult(None, PTK_INTERNALERROR, "failed")
            loginfo("Job Prepare failed for WID:" + wf['id'])
            return res
        job_details = res.getResult()
        update_batch_job_status(
            jobid, wf['id'], job_details['jobid'], 'EXECUTING')
        jobexecute_helper(job_details['jobid'])
        res = group_job_status_api(job_details['jobid'])
        job_status = res.getResult()
        update_batch_job_status(
            jobid, wf['id'], job_details['jobid'], job_status['overallstatus'])
        if job_status['overallstatus'] == JOB_STATUS_FAILED:
            break

    loginfo("Successfully completed batch Job retrigger")
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def get_job_seq_no(jid, record):
    wfcount = -1 if (len(record['job'])) == 0 else len(record['job']) - 1

    for x in range(wfcount, -1, -1):
        if record['job'][str(x)]['record']['jobid'] == jid:
            return x
    return -1


def trigger_job_from_dump(pjid, jid):
    loginfo("Re triggering job" + jid)
    g_obj_list = {}
    shelf = shelve.open(get_job_dump_file(jid), flag="c")
    cur_task = shelf['cur_task']

    record = shelve.open(get_shelf_file(pjid), flag="c", writeback=True)

    loginfo("Retrying :" + cur_task['@name'])
    seq_no = get_job_seq_no(jid, record)
    if seq_no < 0:
        loginfo("Something went Wrong")

    customlogs("<b>Retrying Task</b> '%s'...\n" %
               cur_task['@name'], shelf['logfile'])
    ret = execute_task(shelf['cur_task'],
                       shelf['seqno'],
                       record['job'][str(seq_no)]['record'],
                       shelf['task_list'],
                       shelf['outputdicts'],
                       g_obj_list,
                       shelf['logfile'],
                       shelf['hw_type'])

    if ret == -1:
        update_overall_status(jid, JOB_STATUS_FAILED)
    else:
        update_overall_status(jid, JOB_STATUS_COMPLETED)
    record.close()
    shelf.close()
    return ret


def job_retry_standalone(jid):
    """

    # Stanalone has two cases group workflow or individual workflow
    Retry a failed Job
    :param jid: jobid

    """
    loginfo("job_retry_standalone")
    res = result()
    fd = None
    try:
        fd = open(get_job_file(jid), 'r')

    except IOError:
        loginfo("Failed to open job file:" + get_job_file(jid))
        res.setResult(None, PTK_NOTEXIST, "No Such Job")
        return res

    doc = xmltodict.parse(fd.read())

    if '@wtype' in doc['workflow'] and doc['workflow']['@wtype'] == 'wgroup':
        loginfo("Attempting to resume group Job" + get_job_file(jid))
        return group_job_retry(doc, jid)
    else:
        loginfo("Induvidual Job Resume is not supported" + jid)
        res.setResult(None, PTK_UNSUPPORTED,
                      _("PDT_OPERATION_UNSUPPORTED_ERR_MSG"))
        return res


def get_group_workflow_failed_job(jid):
    res = group_job_status_api(jid)
    if res.getStatus() != PTK_OKAY:
        return res
    status_list = res.getResult()
    for job in status_list['taskstatus']:
        if job['status'] == 'FAILED':
            return {'wid': job['id'], 'jid': job['jid'], 'execid': job['execid']}
    return None
