"""
    orchestration
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Performs Orchestration functionalities

"""

import threading
from xml.dom.minidom import *
from pure_dir.services.utils.exportlog import *
from pure_dir.services.utils.eula_setup import *
from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_status import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_task_data import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_workflows import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_task_library import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_validator import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_miscellaneous import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_executor import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_rollback import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_rollback_status import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_globals import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_batch_executor import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_batch_status import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_retry import *
from pure_dir.services.utils.images import *


class Orchestration:
    def __init__(self):
        pass

    def workflows(self, htype=''):
        return workflows_list_api(htype)

    def tasks(self, htype=''):
        return tasks_list_api(htype)

    def workflowgroups(self, id, ttype=''):
        return workflows_group_info_api(id, ttype)

    def workflowinfo(self, wid):
        return workflow_info_api(wid)

    def flashstacktype(self):
        return flash_stack_type_api()

    def deleteworkflow(self, wid):
        return delete_workflow_api(wid)

    def jobtasks(self, id, ttype=''):
        return job_tasks_api(id, ttype)

    def workflowprepare(self, wname):
        # Current design all prepare to be persistant
        return workflow_persistant_prepare_helper(wname)

    def workflowpersistantprepare(self, wname):
        return workflow_persistant_prepare_helper(wname)

    def jobdiscard(self, jobid, force):
        return job_discard_api(jobid, force)

    def jobtaskinputsave(self, id, execid, input_list, ttype=''):
        return job_task_input_save_api(id, execid, input_list, ttype)

    def jobtaskmandatoryinputsave(self, id, input_list, ttype=''):
        return job_task_mandatory_input_save_api(id, input_list, ttype)

    def librarytaskinfo(self, tid):
        # TODO Unimplemented
        return library_task_information_api(tid)

    def jobtaskinputs(self, execid, id, ttype=''):
        return job_task_inputs_api(execid, id, ttype)

    def taskinputvalue(self, jid, taskid):
        return task_input_value_api(jid, taskid)

    def jobtaskoutputs(self, texecid, jid):
        return job_task_outputs_api(texecid, jid)

    def librarytasks(self):
        # TODO Umimplemented method
        return library_task_list_api()

    def jobstatus(self, jid):
        return job_status_helper_api(jid)

    def groupjobstatus(self, jid):
        return group_job_status_api(jid)

    def tasksuggestedinputs(self, id, execid, ttype='', field=''):
        return task_suggested_inputs_api(id, execid, ttype, field)

    def logs(self, jid):
        return get_logs_api(jid)

    def deploymentlogs(self, jid):
        return deployment_logs(jid)

    def checkprereq(self, wid):
        return check_pre_req_api(wid)

    def jobvalidate(self, jid, execid=''):
        ''' Validate the job before execution'''
        return job_validate(jid, execid)

    def createworkflow(self):
        return create_workflow_api()

    def addtask(self, data):
        return add_task_api(data)

    def deletetask(self, execid, wid):
        return delete_task_api(execid, wid)

    def deletealltask(self, wid):
        return delete_all_task_api(wid)

    def createconnection(self, data):
        return create_connection_api(data)

    def deleteconnection(self, wid, execid, ttype):
        return delete_connection_api(wid, execid, ttype)

    def deleteallconnection(self, wid):
        return delete_all_connection_api(wid)

    def saveworkflow(self, data):
        return save_workflow_api(self, data)

    def jobmandatoryvalidate(self, jid):
        ''' Validate the  mandatory fields before job execution'''
        return job_mandatory_validate_api(jid)

    def servicerequests(self):
        return service_request_list_api()

    def servicerequestinfo(self, jobid):
        return service_request_info_api(jobid)

    def jobexecute(self, jid):
        obj = result()
        threading.Thread(target=jobexecute_helper, args=(jid,)).start()
        obj.setResult(0, PTK_OKAY, "success")
        return obj

    def batchexecute(self, stack_type, wid):
        obj = result()
        threading.Thread(target=flashstack_deploy,
                         args=(stack_type, wid,)).start()
        sleep(2)  # Workaround, give UI time to call status
        obj.setResult(0, PTK_OKAY, "success")
        return obj

    def jobretry(self, stacktype=None, jid=None):
        return job_retry_api(stacktype, jid)

    def jobrevert(self,  stacktype=None, jid=None):
        return job_rollback_api(stacktype, jid)

    def rollbacktaskdata(self, jobid, pjobid, tid):
        return rollback_task_data_api(jobid, pjobid,  tid)

    def rollbackstatus(self, jobid):
        return rollback_batch_status_helper_api(jobid)

    def jobsaveas(self, jobid, data):
        return job_save_as_api(jobid, data)

    def exportworkflow(self, jobid):
        return export_workflow_api(jobid)

    def exportlog(self):
        return exportlog_helper()

    def importworkflow(self, uploadfile):
        return import_workflow_api(uploadfile)

    def jobtaskmandatoryinputs(self, jobid, ttype=''):
        return job_task_mandatory_inputs_api(jobid, ttype)

    def workflowinputs(self, id, stacktype):
        return workflow_inputs_api(id, stacktype)

    def listimages(self, imagetype=''):
        return list_images(imagetype)

    def deleteimage(self, imagename):
        return delete_image(imagename)

    def importimage(self, uploadfile, image_type, image_sub_type='',image_os_sub_type=''):
        return import_image(uploadfile,image_type, image_sub_type,image_os_sub_type)

    #def isobinding(self, isofile,kickstart):
    #    return iso_binding(isofile,kickstart)


    def getglobals(self, stacktype, hidden):
        return get_globals_api(stacktype, hidden)

    def setglobals(self, stacktype, input_list):
        return set_globals_api(stacktype, input_list)

    def batchstatus(self, stacktype):
        return batch_status_api(stacktype)

    def getglobaloptions(self, operation, ttype, keys):
        return get_global_options(operation, ttype, keys)

    def eulacontent(self):
        return eula_content()

    def eulaagreement(self, isagree):
        return eula_agreement(isagree)
