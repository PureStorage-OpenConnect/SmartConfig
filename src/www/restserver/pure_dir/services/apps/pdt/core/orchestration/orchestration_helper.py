"""
    Orchestration_helper
    ~~~~~~~~~~~~~~~~~~~~~~~

    Helper methods for orchestration tasks

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from xml.dom.minidom import *
import xmltodict
import os

TASK_SUCCESS = "SUCCESS"
TASK_FAILED = "FAILURE"


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def parseTaskResult(result):
    if result.getStatus() != PTK_OKAY:
        return {'status': TASK_FAILED}
    elif isinstance(result.getResult(), dict):
        result.getResult()['status'] = TASK_SUCCESS
        return result.getResult()
    else:
        return {'status': TASK_FAILED}


def getMappedOutputs(jobid, texecid):
    wftask_oputs = {}
    found = 0
    obj = result()
    try:
        with open(get_job_file(jobid), "r") as td:
            tdoc = xmltodict.parse(td.read())

    except EnvironmentError:
        obj.setResult(wftaskip_list, PTK_NOTEXIST, "No such Job")

    for task in tdoc['workflow']['tasks']['task']:
        if task['@texecid'] == texecid:
            found = 1
            oplist = task['outputs']['output'] if isinstance(
                task['outputs']['output'], list) else [task['outputs']['output']]
            for oput in oplist:
                # Maps the test value specified in the XML
                wftask_oputs[oput['@name']] = oput['@tvalue']
    if found == 0:
        obj.setResult(None, PTK_NOTEXIST, "No such task")
        return obj

    obj.setResult(wftask_oputs, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def getArg(keys, argname):
    for args in keys.values():
        for arg in args:
            if arg['key'] == argname:
                if arg['value']:
                    return arg['value']
    return None


def getGlobalArg(inputs, field_name):
    for input_val in inputs:
        if input_val['name'] == field_name:
            return input_val['value']
    return None


def job_input_save(jobid, execid, field_name, value):
    obj = result()
    path = get_job_file(jobid)
    if os.path.exists(path) == False:
        return False
    doc = parse(path)
    tasks = doc.documentElement.getElementsByTagName("task")
    for task in tasks:
        task_id = task.getAttribute("texecid")
        if task_id == execid:
            inputs = task.getElementsByTagName("arg")
            for inp in inputs:
                if field_name == inp.getAttribute('name'):
                    inp.setAttribute('value', value)
                    break
    with open(path, "w") as f:
        f.write(pretty_print(doc.toprettyxml(indent="")))

    obj.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def get_global_val(stacktype, field_name):
    xmldoc = None
    try:
        xmldoc = parse(get_global_wf_config_file())
    except IOError:
        loginfo("Globals file does not exist")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return obj
    g_val = {}
    xmldoc = parse(get_global_wf_config_file())
    htypes = xmldoc.getElementsByTagName('htype')
    for htype in htypes:
        if htype.getAttribute('stacktype') == stacktype:
            inpts = htype.getElementsByTagName('input')
            for i in inpts:
                g_val = {}
                if i.getAttribute('name') == field_name:
                    return i.getAttribute('value')
    return None


def get_global_arg_from_jid(jobid, fieldname):
    obj = result()
    path = get_job_file(jobid)
    if os.path.exists(path) == False:
        return None
    try:
        job_xml = get_job_file(jobid)
        fd = open(job_xml, 'r')
        doc = xmltodict.parse(fd.read())
        htype = doc['workflow']['@htype']
        field_val = get_global_val(htype, fieldname)
        return field_val

    except Exception as e:
        loginfo(str(e))
        loginfo("Exception occured in reading global argument")

    return None

# Method will only return from the first task with matching tid
# TODO needs to add texecid in the check


def get_field_value_from_jobid(jobid, task_id, fieldname):
    try:
        job_xml = get_job_file(jobid)
        fd = open(job_xml, 'r')
        doc = xmltodict.parse(fd.read())

        value = [[arg['@value'] for arg in task['args']['arg'] if arg['@name'] == fieldname][0]
                 for task in doc['workflow']['tasks']['task'] if
                 task['@id'] == task_id][0]
        return value

    except Exception as e:
        loginfo(str(e))
        loginfo("Exception occured in reading argument")

    return None
