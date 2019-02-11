"""
    orchestration_job_status
    ~~~~~~~~~~~~~~~~~~~~~~~

    helper for workflow status

"""


import xmltodict
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_status_file
from time import gmtime, strftime
from xml.dom.minidom import parse, parseString, Document


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def job_status_helper_api(jobid):
    obj = result()
    res = {}
    statuslist = []
    try:
        fd = open(get_job_status_file(jobid), 'r')
        doc = xmltodict.parse(fd.read())
    except IOError:
        res['overallstatus'] = ""
        res['taskstatus'] = statuslist
        obj.setResult(res, PTK_OKAY, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    res['overallstatus'] = doc['Workflowstatus']['@ostatus']
    for task in doc['Workflowstatus']['tasks']['task']:
        status_entity = {
            'id': task['@id'],
            'execid': task['@texecid'],
            'status': task['@status']}
        statuslist.append(status_entity)

    res['taskstatus'] = statuslist
    obj.setResult(res, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def prepare_status_file(wid, jobid, tasklist):
    doc = Document()
    res = result()
    root = doc.createElement("Workflowstatus")
    root.setAttribute("ostatus", "EXECUTING")
    root.setAttribute("wid", wid)
    root.setAttribute("jid", jobid)
    root.setAttribute("time", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    doc.appendChild(root)
    tasks_node = doc.createElement("tasks")
    root.appendChild(tasks_node)

    for task in tasklist:
        tstatus = doc.createElement("task")
        tstatus.setAttribute("id", task['@id'])
        tstatus.setAttribute("texecid", task['@texecid'])
        tstatus.setAttribute("status", "READY")
        tasks_node.appendChild(tstatus)

    try:
        o = open(get_job_status_file(jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_workflow_status(p_jobid, jobid, status):
    doc = parse(get_job_status_file(p_jobid))
    res = result()
    found = 0
    for task in doc.getElementsByTagName('workflow'):
        if task.getAttribute("jid") == jobid:
            task.setAttribute("status", status)
            found = 1

    try:
        if (found == 0):
            res.setResult(None, PTK_OKAY, "success")
            return res

        o = open(get_job_status_file(p_jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_task_status(jobid, texecid, status):
    doc = parse(get_job_status_file(jobid))
    res = result()
    found = 0
    for task in doc.getElementsByTagName('task'):
        if task.getAttribute("texecid") == texecid:
            task.setAttribute("status", status)
            found = 1

    try:
        if (found == 0):
            res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        o = open(get_job_status_file(jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_overall_status(jobid, status):
    doc = parse(get_job_status_file(jobid))
    res = result()
    root = doc.getElementsByTagName('Workflowstatus')
    root[0].setAttribute("ostatus", status)

    try:
        o = open(get_job_status_file(jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def clear_job_failed_status(jobid):
    doc = parse(get_job_status_file(jobid))
    res = result()
    found = 0
    for task in doc.getElementsByTagName('task'):
        if task.getAttribute("status") == 'FAILED':
            task.setAttribute("status", 'READY')
            found = 1

    try:
        if (found == 0):
            res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        o = open(get_job_status_file(jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
        res.setResult(None, PTK_FILEACCESSERROR, str(e) + "failed")
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res
