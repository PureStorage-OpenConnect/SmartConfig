"""
    Orchestration_batch_executor
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements workflow execution logic

"""
from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import *
from pure_dir.services.apps.pdt.core.discovery import*
from pure_dir.services.apps.pdt.core.config_json import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_status import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_group_job_status import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_executor import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_workflows import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_batch_status import *
from xml.dom.minidom import *
import xmltodict
import os
import glob


def _get_workflow_list(htype):
    wfs = []
    res = result()
    if len(htype) > 0:
        wfs = glob.glob(get_workflow_files_pattern(htype))
    else:
        res.setResult(None, PTK_NOTEXIST, _("PDT_INVALID_FLASHSTACK_TYPE_MSG"))
        return res

    wf_list = []
    for wf in wfs:
        fd = None
        try:
            fd = open(wf, 'r')
            doc = xmltodict.parse(fd.read())
            if '@hidden' in doc['workflow'] and doc['workflow']['@hidden'] == '1':
                continue

            if '@wtype' not in doc['workflow'] or doc['workflow']['@wtype'] != 'wgroup':
                continue

            order = '0'
            if '@order' in doc['workflow']:
                order = doc['workflow']['@order']

            wf_entity = {
                'id': doc['workflow']['@id'],
                'name': doc['workflow']['@name'],
                'order': order,
            }
            wf_list.append(wf_entity)
        except IOError:
            continue

    wf_list = sorted(wf_list, key=lambda x: x["order"])
    res.setResult(wf_list, PTK_OKAY, _("PDT_INVALID_FLASHSTACK_TYPE_MSG"))
    return res


def flashstack_deploy(htype, wid):
    """
    Method executes all the workflows required for flash stack deployment one after another
    If wid is specified, it only executes the particular workflow alone
    :param htype: Hardware type 
    :param wid: Workflow ID 

    """
    res = _get_workflow_list(htype)
    if res.getStatus() != PTK_OKAY:
        return res

    if get_config_mode() == "json":
        json_config = 1
    else:
        json_config = 0

    wf_list = res.getResult()
    if wid == '':
        prepare_batch_status_file(htype, wf_list)
    else:
        wflow = [k for k in wf_list if k['id'] == wid]
        if wflow[0]['order'] == '1':
            prepare_batch_status_file(htype, wf_list)
        else:
            if os.path.exists(get_batch_status_file(htype)) == False:
                res.setResult(None, PTK_INTERNALERROR,
                              _("PDT_INVALID_FLASHSTACK_DEPLOYMENT_ORDER_MSG"))
                return res
        wf_list = wflow

    for wf in wf_list:
        update_batch_job_status_on_init(htype, wf['id'], 'EXECUTING')
        if wid == '':
            res = workflowprepare_helper(wf['id'])
        else:
            res = workflow_persistant_prepare_helper(wf['id'])

        if res.getStatus() != PTK_OKAY:
            update_batch_job_status_on_init(htype, wf['id'], 'FAILED')
            res.setResult(None, PTK_INTERNALERROR, "failed")
            return res
        job_details = res.getResult()

        if json_config == 1:
            job_list = [job['job_id'] for job in job_details['subjobs']]
            for jb in job_list:
                update_config_inputs(htype, jb)

        update_batch_job_status(
            htype, wf['id'],  job_details['jobid'], 'EXECUTING')
        jobexecute_helper(job_details['jobid'])
        res = group_job_status_api(job_details['jobid'])
        job_status = res.getResult()
        update_batch_job_status(
            htype, wf['id'],  job_details['jobid'], job_status['overallstatus'])
        if job_status['overallstatus'] == JOB_STATUS_FAILED:
            break
    res.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return res
