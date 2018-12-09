"""
    orchestration_group_job_status.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    helper for group job status

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from time import gmtime, strftime
from xml.dom.minidom import *
import xmltodict
from pure_dir.infra.common_helper import *


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def group_job_status_api(jobid):
    obj = result()
    res = {}
    statuslist = []
    try:
        fd = open(get_job_group_status_file(jobid), 'r')
        doc = xmltodict.parse(fd.read())
    except IOError:
        res['overallstatus'] = ""
        res['taskstatus'] = statuslist
	loginfo("Job status does not exist")
        obj.setResult(res, PTK_OKAY, _("PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
        return obj

    res['overallstatus'] = doc['Workflowstatus']['@ostatus']
    for wf in getAsList(doc['Workflowstatus']['workflows']['workflow']):
        status_entity = {
            'id': wf['@id'],
            'jid': wf['@jid'],
            'execid': wf['@wexecid'],
            'status': wf['@status']}
        statuslist.append(status_entity)

    res['taskstatus'] = statuslist
    obj.setResult(res, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj

def clear_group_job_status(p_jobid):
    doc = parse(get_job_group_status_file(p_jobid))
    res = result()
    doc.getElementsByTagName('Workflowstatus')[0].setAttribute("ostatus", "READY")
    for task in doc.getElementsByTagName('workflow'):
            task.setAttribute("status", "READY")

    try:
        o = open(get_job_group_status_file(p_jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    except Exception as e:
        loginfo(" exception " + str(e))
        res.setResult(None, PTK_FILEACCESSERROR,  _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res

#clear_group_job_status('643d95ab-ffb0-4f61-9df7-9bbef81ebeba')

def prepare_workflow_status_file(wid, jobid, wflist):
    doc = Document()
    res = result()
    root = doc.createElement("Workflowstatus")
    root.setAttribute("ostatus", "EXECUTING")
    root.setAttribute("wid", wid)
    root.setAttribute("jid", jobid)
    root.setAttribute("time", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    doc.appendChild(root)
    tasks_node = doc.createElement("workflows")
    root.appendChild(tasks_node)

    for wf in wflist:
        tstatus = doc.createElement("workflow")
        tstatus.setAttribute("id", wf['@id'])
        tstatus.setAttribute("wexecid", wf['@wexecid'])
        tstatus.setAttribute("jid", wf['@jid'])
        tstatus.setAttribute("status", "READY")
        tasks_node.appendChild(tstatus)

    try:
        o = open(get_job_group_status_file(jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()
    except Exception as e:
	loginfo(" exception " + str(e))
        res.setResult(None, PTK_FILEACCESSERROR,  _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res

    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_group_job_status(p_jobid, jobid, status):
    doc = parse(get_job_group_status_file(p_jobid))
    res = result()
    found = 0
    for task in doc.getElementsByTagName('workflow'):
        if task.getAttribute("jid") == jobid:
            task.setAttribute("status", status)
            found = 1

    try:
        if (found == 0):
            res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

        o = open(get_job_status_file(p_jobid), "w")
        o.write(pretty_print(doc.toprettyxml(indent="")))
        o.close()
        doc.unlink()

    except Exception as e:
	loginfo(" exception " + str(e))
        res.setResult(None, PTK_FILEACCESSERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return re
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def update_overall_group_job_status(jobid, status):
    doc = parse(get_job_group_status_file(jobid))
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
