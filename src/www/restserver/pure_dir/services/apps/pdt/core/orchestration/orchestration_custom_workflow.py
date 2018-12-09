"""
    orchestration_custom workflows
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Supports worklow list, save as functionality

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.kickstart import *
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
from slugify import slugify
import xmltodict
import os
import os.path
import random
from pure_dir.infra.common_helper import *
g_persistant_prepare = 0


def create_workflow_api():
    """
    Creates a temporary workflow XML, used for custom workflows
    """
    res = result()
    rm_no = str(random.randrange(1000))
    filename = rm_no+".xml"
    doc = Document()
    roottag = doc.createElement("workflow")
    tasks = doc.createElement("tasks")
    roottag.appendChild(tasks)
    doc.appendChild(roottag)
    fd = open("/tmp/"+filename, 'w')
    fd.write(pretty_print(doc.toprettyxml(indent="")))
    fd.close()
    e = {
        "wid": rm_no
    }
    res.setResult(e, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def add_task_api(data):
    """

    :param data: 

    """
    res = result()
    if os.path.exists("/tmp/"+str(data['wid'])+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(data['wid'])+".xml")
    if len(doc.getElementsByTagName("task")) == 0:
        execid = "100"
    else:
        val = getlasttask(data['wid'])
        execid = int(val[1:])+1
    tsk = doc.getElementsByTagName("tasks")
    newtask = doc.createElement("task")
    newtask.setAttribute('id', data['taskid'])
    newtask.setAttribute('texecid', "t"+str(execid))
    newtask.setAttribute('name', data['taskid'])
    tsk[0].appendChild(newtask)
    fd = open("/tmp/"+str(data['wid'])+".xml", 'w')
    fd.write(pretty_print(doc.toprettyxml(indent="")))
    fd.close()
    obj = {"execid": "t"+str(execid)}
    res.setResult(obj, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def delete_task_api(execid, wid):
    """

    :param execid: 
    :param wid: 

    """
    res = result()
    if os.path.exists("/tmp/"+str(wid)+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(wid)+".xml")
    tsk_ls = doc.getElementsByTagName("task")
    for tsk in tsk_ls:
        if tsk.getAttribute("texecid") == execid:
            parent = tsk.parentNode
            parent.removeChild(tsk)
        if tsk.getAttribute("OnSuccess") == execid:
            tsk.setAttribute("OnSuccess", "")
        if tsk.getAttribute("Onfailure") == execid:
            tsk.setAttribute("Onfailure", "")
        fd = open("/tmp/"+str(wid)+".xml", 'w')
        fd.write(pretty_print(doc.toprettyxml(indent="")))
        fd.close()
    res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def delete_all_task_api(wid):
    """

    :param wid: 

    """
    res = result()
    if os.path.exists("/tmp/"+str(wid)+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(wid)+".xml")
    tsk_ls = doc.getElementsByTagName("task")
    for tsk in tsk_ls:
        parent = tsk.parentNode
        parent.removeChild(tsk)
        fd = open("/tmp/"+str(wid)+".xml", 'w')
        fd.write(pretty_print(doc.toprettyxml(indent="")))
        fd.close()
    res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def getlasttask(wid):
    """

    :param wid: 

    """
    doc = parse("/tmp/"+str(wid)+".xml")
    tsk = doc.getElementsByTagName("task")
    return tsk[-1].getAttribute("texecid")


def create_connection_api(data):
    """

    :param data: 

    """
    res = result()
    if os.path.exists("/tmp/"+str(data['wid'])+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(data['wid'])+".xml")
    tsk_ls = doc.getElementsByTagName("task")
    for tsk in tsk_ls:
        if tsk.getAttribute("texecid") == data['fmexecid']:
            tsk.setAttribute(data['ttype'], data['toexecid'])
            fd = open("/tmp/"+str(data['wid'])+".xml", 'w')
            fd.write(pretty_print(doc.toprettyxml(indent="")))
            fd.close()
            res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

    loginfo("Execution ID not Available")
    res.setResult(False, PTK_INTERNALERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))

    return res


def delete_connection_api(wid, execid, ttype):
    """

    :param wid: 
    :param execid: 
    :param ttype: 

    """
    res = result()
    if os.path.exists("/tmp/"+str(wid)+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR,  _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(wid)+".xml")
    tsk_ls = doc.getElementsByTagName("task")
    for tsk in tsk_ls:
        if tsk.getAttribute("texecid") == execid:
            tsk.setAttribute(ttype, "")
            fd = open("/tmp/"+str(wid)+".xml", 'w')
            fd.write(pretty_print(doc.toprettyxml(indent="")))
            fd.close()
            res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
            return res

    loginfo("Execution ID not Available")
    res.setResult(False, PTK_INTERNALERROR, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
    return res


def delete_all_connection_api(wid):
    """
     Deletes all connections in custom workflow
    :param wid: workflowid 

    """
    res = result()
    if os.path.exists("/tmp/"+str(wid)+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR,  _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(wid)+".xml")
    tsk_ls = doc.getElementsByTagName("task")
    for tsk in tsk_ls:
        tsk.setAttribute("OnSuccess", "")
        tsk.setAttribute("Onfailure", "")
        fd = open("/tmp/"+str(wid)+".xml", 'w')
        fd.write(pretty_print(doc.toprettyxml(indent="")))
        fd.close()
    res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res


def save_workflow_api(self, data):
    """
    Save as a new workflow
    :param data: new workflow, name, desc .. 

    """
    res = result()
    if os.path.exists("/tmp/"+str(data['wid'])+".xml") == False:
	loginfo("File Not Found")
        res.setResult({}, PTK_INTERNALERROR,  _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return res
    doc = parse("/tmp/"+str(data['wid'])+".xml")
    wkf_ls = doc.getElementsByTagName("workflow")
    for wfk in wkf_ls:
        wfk.setAttribute('name', data['name'])
        wfk.setAttribute('id', data['name'].replace(" ", ""))
        wfk.setAttribute('desc', data['descr'])
        wfk.setAttribute('isdeletable', "1")
        wfk.setAttribute('type', "Custom")
    fd = open("/mnt/system/pure_dir/pdt/workflows/wf-" +
              data['name'].replace(" ", "")+".xml", 'w')
    fd.write(pretty_print(doc.toprettyxml(indent="")))
    fd.close()
    res.setResult(True, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res
