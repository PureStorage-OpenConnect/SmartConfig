
"""
    orchestration_job_status
    ~~~~~~~~~~~~~~~~~~~~~~~

    helper for workflow status

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_workflows import g_flash_stack_types
from time import gmtime, strftime
from xml.dom.minidom import *
import xmltodict
import os
import shelve


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def prepare_rollback_status_file(jid):
    """
    Creates rollback status file
    :param jid: Job id to rollback 

    """
    res = result()
    if os.path.exists(get_shelf_file(jid)) == False:
        loginfo("file dosen't exists")
        res.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return res
    doc = Document()
    root = doc.createElement("rollbackstatus")
    root.setAttribute("ostatus", "EXECUTING")
    root.setAttribute("jid", jid)
    root.setAttribute("time", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    doc.appendChild(root)
    tasks_node = doc.createElement("tasks")
    root.appendChild(tasks_node)

    shelf = shelve.open(get_shelf_file(jid), flag='r')
    wfcount = -1 if (len(shelf['job'])) == 0 else len(shelf['job']) - 1
    task_count = 0

    for x in range(wfcount, -1, -1):
        record = shelf['job'][str(x)]['record']
        taskcount = -1 if len(
            record['tasklist']) == 0 else len(
            record['tasklist']) - 1

        for i in range(taskcount, -1, -1):

            task = record['tasklist'][str(i)]
            tstatus = doc.createElement("task")
            tstatus.setAttribute("texecid", task['texecid'])
            tstatus.setAttribute("status", "READY")
            tstatus.setAttribute("order", str(task_count))
            tstatus.setAttribute(
                "jid", shelf['job'][str(x)]['record']['jobid'])
            task_count = task_count + 1
            tasks_node.appendChild(tstatus)

    shelf.close()
    try:
        o = open(get_rollback_status_file(jid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def rollback_batch_status_helper_api(jid):
    jid_list = []
    obj = result()
    if not any(d['value'] == jid for d in g_flash_stack_types):
        # Not a batch rollback, continue with jobid
        jid_list.append(jid)
        return rollback_status_helper(jid_list)

    try:
        fd = open(get_batch_status_file(jid), 'r')
        doc = xmltodict.parse(fd.read())
        wfs = sorted(doc['Batchstatus']['workflows']['workflow'],
                     key=lambda x: x["@order"], reverse=True)
        for wf in wfs:
            if wf['@status'] == 'READY':
                continue
            jid_list.append(wf['@jid'])
    except Exception as e:
        loginfo( "Exception" + str(e))
        obj.setResult(None, PTK_FAILED, _("PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
        return obj

    return rollback_status_helper(jid_list)


def rollback_status_helper(jid_list):
    """
    returns rollback status for each task
    :param jid: list of job id to get status for

    """
    obj = result()
    res = {}
    count = 0
    tmp_status_list = []
    for jid in jid_list:
        statuslist = []
        try:
            loginfo( "opening rollback status file" + \
                get_rollback_status_file(jid))
            fd = open(get_rollback_status_file(jid), 'r')
            doc = xmltodict.parse(fd.read())
        except IOError:
            res['rbstatus'] = statuslist
	    loginfo("Job status does not exist")
            obj.setResult(res, PTK_OKAY, _("PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
            return obj
        if doc['rollbackstatus']['tasks'] == None:
            # Workflow may have first task failed, skip
            continue
        for task in doc['rollbackstatus']['tasks']['task']:
            status_entity = {
                'execid': task['@jid']+"_"+task['@texecid'],
                'status': task['@status'],
                'order': task['@order'],
            }
            statuslist.append(status_entity)
        tmp_status = {'jid': jid, 'order': str(count), 'status':  statuslist}
        count = count + 1
        tmp_status_list.append(tmp_status)

    res['rbstatus'] = tmp_status_list
    #print res
    obj.setResult(res, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def update_rollback_task_status(jid, sub_jid, texecid, status):
    """
    Update roll back task status
    :param jid: Jobid 
    :param texecid: Task execution ID
    :param status: status ti update 

    """
    doc = parse(get_rollback_status_file(jid))
    res = result()
    found = 0
    for task in doc.getElementsByTagName('task'):
        if task.getAttribute("texecid") == texecid and task.getAttribute('jid') == sub_jid:
            task.setAttribute("status", status)
            found = 1

    try:
        if (found == 0):
            res.setResult(None, PTK_OKAY, "success")
            return res

        o = open(get_rollback_status_file(jid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res

