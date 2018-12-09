import json
from pure_dir.infra.request.restrequest import*


def PDTReset_request():
    body_payload = {}
    query_payload = {}
    return generate_request('PDTReset', query_payload, body_payload, 'pdt', 'GET')


def System_request():
    body_payload = {}
    query_payload = {}
    return generate_request('System', query_payload, body_payload, 'pdt', 'GET')


def NetworkInfo_request():
    body_payload = {}
    query_payload = {}
    return generate_request('NetworkInfo', query_payload, body_payload, 'pdt', 'GET')


import json
from pure_dir.infra.request.restrequest import*


def DeleteAllConnection_request(wid):
    body_payload = {}
    query_payload = {'wid': wid}
    return generate_request('DeleteAllConnection', query_payload, body_payload, 'pdt', 'DELETE')


def ServiceRequestInfo_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('ServiceRequestInfo', query_payload, body_payload, 'pdt', 'GET')


def DeleteAllTask_request(wid):
    body_payload = {}
    query_payload = {'wid': wid}
    return generate_request('DeleteAllTask', query_payload, body_payload, 'pdt', 'DELETE')


def CreateWorkflow_request():
    body_payload = {}
    query_payload = {}
    return generate_request('CreateWorkflow', query_payload, body_payload, 'pdt', 'GET')


def JobDiscard_request(wname, force):
    body_payload = {}
    query_payload = {'wname': wname, 'force': force}
    return generate_request('JobDiscard', query_payload, body_payload, 'pdt', 'GET')


def Tasks_request(htype):
    body_payload = {}
    query_payload = {'htype': htype}
    return generate_request('Tasks', query_payload, body_payload, 'pdt', 'GET')


def GetOptions_request(jobid, execid, operation, isGroup, keys):
    body_payload = json.dumps(keys)
    query_payload = {'jobid': jobid, 'execid': execid,
                     'operation': operation, 'isGroup': isGroup}
    return generate_request('GetOptions', query_payload, body_payload, 'pdt', 'POST')


def JobStatus_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('JobStatus', query_payload, body_payload, 'pdt', 'GET')


def JobSaveAs_request(jobid, data):
    body_payload = json.dumps(data)
    query_payload = {'jobid': jobid}
    return generate_request('JobSaveAs', query_payload, body_payload, 'pdt', 'POST')


def TaskSuggestedInputs_request(id, execid, ttype, field):
    body_payload = {}
    query_payload = {'id': id, 'execid': execid,
                     'ttype': ttype, 'field': field}
    return generate_request('TaskSuggestedInputs', query_payload, body_payload, 'pdt', 'GET')


def Logs_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('Logs', query_payload, body_payload, 'pdt', 'GET')


def FlashStackTypes_request():
    body_payload = {}
    query_payload = {}
    return generate_request('FlashStackTypes', query_payload, body_payload, 'pdt', 'GET')


def RollbackStatus_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('RollbackStatus', query_payload, body_payload, 'pdt', 'GET')


def WorkflowGroupTasks_request(id, ttype):
    body_payload = {}
    query_payload = {'id': id, 'ttype': ttype}
    return generate_request('WorkflowGroupTasks', query_payload, body_payload, 'pdt', 'GET')


def AddTask_request(data):
    body_payload = json.dumps(data)
    query_payload = {}
    return generate_request('AddTask', query_payload, body_payload, 'pdt', 'POST')


def CheckPreReq_request(wid):
    body_payload = {}
    query_payload = {'wid': wid}
    return generate_request('CheckPreReq', query_payload, body_payload, 'pdt', 'GET')


def JobTaskInputs_request(execid, ttype, id):
    body_payload = {}
    query_payload = {'execid': execid, 'ttype': ttype, 'id': id}
    return generate_request('JobTaskInputs', query_payload, body_payload, 'pdt', 'GET')


def ExportWorkflow_request(jobid):
    body_payload = json.dumps(jobid)
    query_payload = {}
    return generate_request('ExportWorkflow', query_payload, body_payload, 'pdt', 'POST')


def WorkflowPrepare_request(id):
    body_payload = {}
    query_payload = {'id': id}
    return generate_request('WorkflowPrepare', query_payload, body_payload, 'pdt', 'GET')


def CreateConnection_request(data):
    body_payload = json.dumps(data)
    query_payload = {}
    return generate_request('CreateConnection', query_payload, body_payload, 'pdt', 'POST')


def DeleteConnection_request(wid, execid, ttype):
    body_payload = {}
    query_payload = {'wid': wid, 'execid': execid, 'ttype': ttype}
    return generate_request('DeleteConnection', query_payload, body_payload, 'pdt', 'DELETE')


def ResetWFStatus_request():
    body_payload = {}
    query_payload = {}
    return generate_request('ResetWFStatus', query_payload, body_payload, 'pdt', 'POST')


def DeleteImage_request(imagename):
    body_payload = {}
    query_payload = {'imagename': imagename}
    return generate_request('DeleteImage', query_payload, body_payload, 'pdt', 'GET')


def JobTaskOutputs_request(texecid, jobid):
    body_payload = {}
    query_payload = {'texecid': texecid, 'jobid': jobid}
    return generate_request('JobTaskOutputs', query_payload, body_payload, 'pdt', 'GET')


def GetGroupMemberValues_request(jobid, execid, groupid, membername):
    body_payload = {}
    query_payload = {'jobid': jobid, 'execid': execid,
                     'groupid': groupid, 'membername': membername}
    return generate_request('GetGroupMemberValues', query_payload, body_payload, 'pdt', 'GET')


def ImportWorkflow_request(uploadfile):
    body_payload = {}
    query_payload = {}
    return generate_request('ImportWorkflow', query_payload, body_payload, 'pdt', 'POST')


def JobTaskMandatoryInputs_request(id, ttype):
    body_payload = {}
    query_payload = {'id': id, 'ttype': ttype}
    return generate_request('JobTaskMandatoryInputs', query_payload, body_payload, 'pdt', 'GET')


def ServiceRequests_request():
    body_payload = {}
    query_payload = {}
    return generate_request('ServiceRequests', query_payload, body_payload, 'pdt', 'GET')


def Workflows_request(htype):
    body_payload = {}
    query_payload = {'htype': htype}
    return generate_request('Workflows', query_payload, body_payload, 'pdt', 'GET')


def JobValidate_request(jobid, execid):
    body_payload = {}
    query_payload = {'jobid': jobid, 'execid': execid}
    return generate_request('JobValidate', query_payload, body_payload, 'pdt', 'GET')


def JobTasks_request(id, ttype):
    body_payload = {}
    query_payload = {'id': id, 'ttype': ttype}
    return generate_request('JobTasks', query_payload, body_payload, 'pdt', 'GET')


def TaskInputValue_request(jid, taskid):
    body_payload = {}
    query_payload = {'jid': jid, 'taskid': taskid}
    return generate_request('TaskInputValue', query_payload, body_payload, 'pdt', 'GET')


def GroupJobStatus_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('GroupJobStatus', query_payload, body_payload, 'pdt', 'GET')


def GetFieldValue_request(jobid, execid, fieldname):
    body_payload = {}
    query_payload = {'jobid': jobid, 'execid': execid, 'fieldname': fieldname}
    return generate_request('GetFieldValue', query_payload, body_payload, 'pdt', 'GET')


def ListImages_request(imagetype):
    body_payload = {}
    query_payload = {'imagetype': imagetype}
    return generate_request('ListImages', query_payload, body_payload, 'pdt', 'GET')


def JobTaskInputSave_request(id, execid, input_list, ttype):
    body_payload = json.dumps(input_list)
    query_payload = {'id': id, 'execid': execid, 'ttype': ttype}
    return generate_request('JobTaskInputSave', query_payload, body_payload, 'pdt', 'POST')


def WorkflowInfo_request(wid):
    body_payload = {}
    query_payload = {'wid': wid}
    return generate_request('WorkflowInfo', query_payload, body_payload, 'pdt', 'GET')


def JobExecute_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('JobExecute', query_payload, body_payload, 'pdt', 'GET')


def JobValidateMandatoryInputs_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('JobValidateMandatoryInputs', query_payload, body_payload, 'pdt', 'GET')


def JobTaskMandatoryInputSave_request(id, ttype, input_list):
    body_payload = json.dumps(input_list)
    query_payload = {'id': id, 'ttype': ttype}
    return generate_request('JobTaskMandatoryInputSave', query_payload, body_payload, 'pdt', 'POST')


def DeleteWorkflow_request(wid):
    body_payload = {}
    query_payload = {'wid': wid}
    return generate_request('DeleteWorkflow', query_payload, body_payload, 'pdt', 'GET')


def ImportISO_request(uploadfile, iso_file, iso_image_type):
    body_payload = {}
    query_payload = {}
    return generate_request('ImportISO', query_payload, body_payload, 'pdt', 'POST')


def SaveWorkflow_request(data):
    body_payload = json.dumps(data)
    query_payload = {}
    return generate_request('SaveWorkflow', query_payload, body_payload, 'pdt', 'POST')


def LibraryTasks_request():
    body_payload = {}
    query_payload = {}
    return generate_request('LibraryTasks', query_payload, body_payload, 'pdt', 'GET')


def JobRevert_request(jobid):
    body_payload = {}
    query_payload = {'jobid': jobid}
    return generate_request('JobRevert', query_payload, body_payload, 'pdt', 'GET')


def RollBackTaskData_request(jobid, tid):
    body_payload = {}
    query_payload = {'jobid': jobid, 'tid': tid}
    return generate_request('RollBackTaskData', query_payload, body_payload, 'pdt', 'GET')


def DeleteTask_request(wid, execid):
    body_payload = {}
    query_payload = {'wid': wid, 'execid': execid}
    return generate_request('DeleteTask', query_payload, body_payload, 'pdt', 'DELETE')


def LibraryTaskInfo_request(tid):
    body_payload = {}
    query_payload = {'tid': tid}
    return generate_request('LibraryTaskInfo', query_payload, body_payload, 'pdt', 'GET')
