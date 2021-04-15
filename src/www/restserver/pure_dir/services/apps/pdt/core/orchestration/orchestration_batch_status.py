"""
    Orchestration_batch_executor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements workflow execution logic

"""
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_batch_status_file, get_log_file_path
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import JOB_STATUS_COMPLETED
from pure_dir.services.apps.pdt.core.orchestration.orchestration_group_job_status import *
from time import gmtime, strftime
from xml.dom.minidom import parse, Document
import os


def batch_status_api(stacktype):
    """
    Returns current execution status for the batch job
    :param stacktype: flashstack type

    """
    wf_list = []
    res = result()
    if len(stacktype) < 0 or os.path.exists(get_batch_status_file(stacktype)) == False:
        res.setResult(wf_list, PTK_OKAY, _("PDT_INVALID_FLASHSTACK_TYPE_MSG"))
        return res
    doc = parse(get_batch_status_file(stacktype))
    batches = doc.getElementsByTagName('workflow')
    for batch in batches:
        if batch.hasAttribute('jid'):
            jobid = batch.getAttribute('jid')
        else:
            jobid = 'None'

        wf_entity = {
            'wid': batch.getAttribute('id'),
            'jid': jobid,
            'status': batch.getAttribute('status'),
            'msg': 'Failed, please check the log for more information' if batch.getAttribute('status') != JOB_STATUS_COMPLETED else 'completed',
        }
        wf_list.append(wf_entity)
    res.setResult(wf_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def prepare_batch_status_file(hwtype, wflist):
    """
    Prepares  initial status file for Batch Job
    :param hwtype: Hardware type
    :param wflist: Workflow list

    """
    doc = Document()
    res = result()
    root = doc.createElement("Batchstatus")
    root.setAttribute("time", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    doc.appendChild(root)
    tasks_node = doc.createElement("workflows")
    root.appendChild(tasks_node)
    for wf in wflist:
        tstatus = doc.createElement("workflow")
        tstatus.setAttribute("id", wf['id'])
        tstatus.setAttribute("name", wf['name'])
        tstatus.setAttribute("order", wf['order'])
        if wf.get('rollbackOnReset'):
            tstatus.setAttribute("rollbackOnReset", wf['rollbackOnReset'])
        tstatus.setAttribute("status", "READY")
        tasks_node.appendChild(tstatus)

    try:
        o = open(get_batch_status_file(hwtype), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_batch_job_status(hwtype, wid, jobid, status):
    """

    :param hwtype: Hardware type
    :param wid: Workflow id
    :param jobid: Job id, Job id will be recovered from batch status file incase of a rollback
    :param status: Job status

    """
    doc = parse(get_batch_status_file(hwtype))
    res = result()
    batches = doc.getElementsByTagName('workflow')

    for batch in batches:
        if batch.getAttribute('id') == wid:
            if status == 'FAILED' or status == 'COMPLETED' or status == 'READY':
                if jobid is None:
                    jobid = batch.getAttribute('jid')
                with open(get_log_file_path(jobid), 'r') as infile, open(get_log_file_path(hwtype), 'a') as outfile:
                    static_content = "<a name=log_" + jobid + "></a> \n <h5>" + \
                        batch.getAttribute('name') + ":</h5> \n"
                    outfile.write(static_content + infile.read())
                if status == 'READY':
                    f = open(get_log_file_path(jobid), 'r+')
                    f.truncate(0)
            batch.setAttribute("status", status)
            if jobid is not None:
                batch.setAttribute("jid", jobid)

    try:
        o = open(get_batch_status_file(hwtype), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_batch_job_status_on_init(hwtype, wid, status):
    """

    :param hwtype: Hardware type
    :param wid: Workflow id
    :param jobid: Job id, Job id will be recovered from batch status file incase of a rollback
    :param status: Job status

    """
    doc = parse(get_batch_status_file(hwtype))
    res = result()
    batches = doc.getElementsByTagName('workflow')

    for batch in batches:
        if batch.getAttribute('id') == wid:
            batch.setAttribute("status", status)

    try:
        o = open(get_batch_status_file(hwtype), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res
