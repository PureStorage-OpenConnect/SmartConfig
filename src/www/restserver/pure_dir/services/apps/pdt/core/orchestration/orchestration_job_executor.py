"""
    Orchestration_job_helper
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements workflow execution logic

"""

from pure_dir.infra.logging.logmanager import loginfo, customlogs
from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import getAsList
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_status import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_group_job_status import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_batch_status import *
from pure_dir.services.apps.pdt.core.tasks.main.ucs import*
from pure_dir.services.apps.pdt.core.tasks.test.ucs import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_workflows import *
from pure_dir.services.apps.pdt.core.tasks.main.pure import *
from pure_dir.services.apps.pdt.core.tasks.test.pure import *

from pure_dir.services.apps.pdt.core.tasks.main.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.main.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.main.mds import*
from pure_dir.services.apps.pdt.core.tasks.test.mds import*
from time import gmtime, strftime
from copy import deepcopy
import xmltodict
import shelve
import time


def get_value_from_global_list(hw_type, key):
    """
    Reads and returns initial-config or global key value
    :param hw_type: FlashStack type
    :param key: variable to fetch

    """
    fd = None
    try:
        fd = open(get_global_wf_config_file(), 'r')

    except IOError:
        return

    doc = xmltodict.parse(fd.read())
    for g_vars in doc['globals']['htype']:
        if g_vars['@stacktype'] != hw_type:
            continue
        for i in g_vars['input']:
            if i['@name'] == key:
                return i['@value']
    return None


def _map_input_args(tasks, hw_type, dicts, outputdicts, input_obj):
    """
    Helper method to map values for values from previous task, also help values from global xml
    Keep tracks of all outputs produced by task
    :param tasks: task to track input for
    :param hw_type: FlashStack type
    :param dicts: inputs values to finally passed to task
    :param outputdicts: Holds outputs of all previous tasks
    :param input_obj: Inputs for the task

    """
    if tasks['args'] is None:
        return
    iplist = tasks['args']['arg'] if isinstance(tasks['args']['arg'], list) else [
        tasks['args']['arg']]
    for inputarg in iplist:
        exec("%s = %s.%s" % ("field", "input_obj", inputarg['@name']))
        if '@mapval' in inputarg and inputarg['@mapval'] == '1':
            if inputarg['@value'][0:2] != "__":
                loginfo("Error: Something went wrong map value set as 1 and no __")
                # continue
        if '@mapval' in inputarg and inputarg['@mapval'] == '1' and inputarg['@value'][0:2] == "__":
            if '|' in inputarg['@value']:
                inputargs_list = inputarg['@value'].split('|')
                inputvals = []
                for ip in inputargs_list:
                    inputvals.append(outputdicts[ip])
                    argsval = '|'.join(inputvals)
                dicts[inputarg['@name']] = argsval
            else:
                dicts[inputarg['@name']] = outputdicts[inputarg['@value']]
        elif '@mapval' in inputarg and inputarg['@mapval'] == '3' and field.ip_type != "group":
            val = get_value_from_global_list(hw_type, inputarg['@value'])
            if val is None:
                loginfo("Error: No such Global value")
            dicts[inputarg['@name']] = val
        else:
            if field.ip_type == "group":
                group_val = []
                inputs = inputarg['@value'].split('|')
                for ip in inputs:
                    ipt = None
		    try:		    
                    	ipt = eval(ip)
		    except SyntaxError as e:
			loginfo(str(e) + 'Name: ' + inputarg['@name'] + ' value: '+ inputarg['@value'])
			raise Exception('Failure while parsing group data')
                    for val in ipt:
                        if ipt[val]['ismapped'] == "3":
                            ipt[val]['value'] = get_value_from_global_list(
                                hw_type, ipt[val]['value'])
                    group_val.append(str(ipt))
                dicts[inputarg['@name']] = '|'.join(group_val)

            else:
                dicts[inputarg['@name']] = inputarg['@value']


def _get_obj(g_obj_list, classname):
    """
    Creates object for the task class, if already exist, return it
    :param g_obj_list: Global obj list
    :param classname: Class for which the object needs to be created

    """
    if classname in g_obj_list:
        return g_obj_list[classname]

    try:
        exec("%s = %s" % ("g_obj_list[classname]",
                          classname + "." + classname + "()"))
        return g_obj_list[classname]

    except BaseException:
        raise NotImplementedError(
            "Class `{}` does not implemented `".format(classname))


def _get_initial_task(tasks):
    """
    Method helps in identifying the first task of a workflow
    :param tasks: List of tasks in workflow
    :returns : First task
    """
    for task in tasks:
        if task['@inittask'] == "1":
            return task
    return None


def _get_initial_wf(wfs):
    """
    Method helps in identifying the initial workflow
    :param wfs: list of workflows
    :returns : Initial workflow
    """
    for wf in wfs:
        if wf['@initwf'] == "1":
            return wf
    return None


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


def _get_next_task(cur_task, prev_task_state, task_list):
    """
    Get next task to be executed
    :param cur_task: current task
    :param prev_task_state: previous task status
    :param task_list: Entire task list

    """
    next_task_id = None
    if prev_task_state == 'SUCCESS':
        next_task_id = cur_task['@OnSuccess']
    else:
        next_task_id = cur_task['@Onfailure']

    if next_task_id == "None":
        return None

    for task in task_list:
        if next_task_id == task['@texecid']:
            return task
    return None


def _get_recorder_data(task, seqno, inputs, outputs):
    """
    Returns job recorder data
    :param task: current task data
    :param seqno: sequence number
    :param inputs: inputs for the task
    :param outputs: outputs for the task

    """
    name = task['@name']
    if '@label' in task:
        name = task['@label']

    return {
        'taskid': task['@id'],
        'name': name,
        'class': task['@id'],
        'inputs': inputs,
        'outputs': outputs,
        'taskstatus': outputs['status'],
        'texecid': task['@texecid']}


def _init_job_recorder(jid, doc):
    """
    Initialise the job recorder data structure, used for rollback operation
    :param jid: jobid
    :param doc: XML document object

    """
    job_recorder = {'jobid': jid, 'tasklist': {
    }, 'wid': doc['workflow']['@id'], 'wfname': doc['workflow']['@name']}
    job_recorder['etime'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    job_recorder['desc'] = doc['workflow']['@desc']
    job_recorder['status'] = JOB_STATUS_EXECUTING
    if '@simulate' in doc['workflow']:
        job_recorder['simulate'] = doc['workflow']['@simulate']
    return job_recorder


def execute_task(
        cur_task,
        seqno,
        job_recorder,
        task_list,
        outputdicts,
        g_obj_list,
        logfile, hw_type):
    return _execute_task(
        cur_task,
        seqno,
        job_recorder,
        task_list,
        outputdicts,
        g_obj_list,
        logfile, hw_type)


def _execute_task(
        cur_task,
        seqno,
        job_recorder,
        task_list,
        outputdicts,
        g_obj_list,
        logfile, hw_type):
    """
    Executes a task (smallest unit of execution), using the values from job data and by mapping
    global data when ever applicable.

    Each task has a success path and failure path defined in job XML

    Incase of a success or failure,it will look for the next task to be executed as per the job xml data and continues.
    If next task is None, it simply returns

    If there is no failure path defined and a failure happends to task, the method will dump the current stack so that it can be used to retry execution

    The resulting data from the task execution is saved to 'outputdicts' for reference by any subsequent task.

    :param cur_task: pointer to the current task
    :param seqno: sequence number
    :param job_recorder: job recorder pointer
    :param task_list:  list of tasks
    :param outputdicts: list of outputs generated by all previously executed task
    :param g_obj_list: object list for task class
    :param logfile: logfile
    :param hw_type: flash stack type

    """

    if cur_task is None:
        return 0

    jid = job_recorder['jobid']

    name = cur_task['@name']
    if '@label' in cur_task:
        name = cur_task['@label']
    customlogs("Executing '%s'\n" % name, logfile)
    if ('simulate' in job_recorder.keys() and job_recorder['simulate'] == "1") or (
            '@simulate' in cur_task.keys() and cur_task['@simulate'] == "1"):
        my_cls = _get_obj(g_obj_list, "Test_" + cur_task['@id'])
    else:
        my_cls = _get_obj(g_obj_list, cur_task['@id'])

    inputs = {}

    exec("%s = %s" %
         ("input_obj", cur_task['@id'] + "." + cur_task['@id'] + "Inputs" + "()"))
    _map_input_args(cur_task, hw_type, inputs, outputdicts, input_obj)
    method = getattr(my_cls, "execute")
    update_task_status(jid, cur_task['@texecid'], TASK_STATUS_EXECUTING)

    time.sleep(TASK_DELAY)

    taskinfo = {'inputs': deepcopy(
        inputs), 'jid': jid, 'texecid': cur_task['@texecid']}
    try:
        retval = method(taskinfo, logfile)
    except Exception as e:
        customlogs("Exception " + str(e), logfile)
        # Dump stack for retry in case of exception
        dump_stack(jid, cur_task, seqno, job_recorder,
                   task_list, logfile, outputdicts, hw_type)
        update_task_status(jid, cur_task['@texecid'], TASK_STATUS_FAILED)
        update_overall_status(jid, TASK_STATUS_FAILED)
        return -1

    if retval['status'] != 'SUCCESS':

        next_task = _get_next_task(cur_task, retval['status'], task_list)
        if next_task is None:
            # Task failed and OnFailure is None, Dump the stack for Retry
            dump_stack(jid, cur_task, seqno, job_recorder,
                       task_list, logfile, outputdicts, hw_type)

        update_task_status(jid, cur_task['@texecid'], TASK_STATUS_FAILED)
        update_overall_status(jid, TASK_STATUS_FAILED)
        customlogs("Task " + cur_task['@name'] + " failed", logfile)
        return -1

    update_task_status(jid, cur_task['@texecid'], TASK_STATUS_COMPLETED)

    for outputarg in getAsList(cur_task['outputs']['output']):
        key = generate_field_key(
            cur_task['@texecid'], cur_task['@name'], outputarg['@name'])
        outputdicts[key] = retval[outputarg['@name']]

    job_recorder['tasklist'][str(seqno)] = _get_recorder_data(
        cur_task, seqno, inputs, retval)

    return _execute_task(
        _get_next_task(
            cur_task,
            retval['status'],
            task_list),
        seqno + 1,
        job_recorder,
        task_list,
        outputdicts,
        g_obj_list,
        logfile,
        hw_type)


def jobexecute_helper(jid):
    """
    Executes job
    :param jid: Job ID

    """

    try:
        jobexecute_helper_safe(jid)
    except Exception as e:
        loginfo("Critical failure" + str(e))
        update_overall_group_job_status(jid, JOB_STATUS_FAILED)


def jobexecute_helper_safe(jid):
    """
    Method can executes standalone job or group jobs.
    Standalone job will point to a single Job file where as Batch Job will point to group file which has reference to multiple job files
    Method also does the initialisation steps to create shelve file, jobrecord used for rollback and retry respectively.
    Also ensures all workflows with in a batch job is executed

    :param jid: Jobid

    """
    fd = None
    try:
        fd = open(get_job_file(jid), 'r')

    except IOError:
        loginfo("Could not read file:" + str(get_job_file(jid)))

    logfile = get_log_file(jid)
    doc = xmltodict.parse(fd.read())
    seqno = 0
    shelf = shelve.open(get_shelf_file(jid), flag="c")
    shelf['jid'] = jid
    shelf['etime'] = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    shelf['desc'] = doc['workflow']['@desc']
    shelf['name'] = doc['workflow']['@name']
    shelf['wid'] = doc['workflow']['@id']
    shelf['job'] = {}
    jobrecord = {}

    if '@simulate' in doc['workflow']:
        shelf['simulate'] = doc['workflow']['@simulate']

    if '@wtype' not in doc['workflow'] or doc['workflow']['@wtype'] != 'wgroup':
        ret = jobexecute(jid, 0, jobrecord, logfile)
        shelf['job'] = jobrecord
        shelf.close()
        return ret

    wfs = getAsList(doc['workflow']['wfs']['wf'])
    wf = _get_initial_wf(wfs)

    prepare_workflow_status_file(
        doc['workflow']['@id'],
        jid,
        wfs)

    update_overall_group_job_status(jid, JOB_STATUS_EXECUTING)
    while True:
        update_group_job_status(jid, wf['@jid'], JOB_STATUS_EXECUTING)
        ret = jobexecute(wf['@jid'], seqno, jobrecord, logfile)
        shelf['job'] = jobrecord
        seqno = seqno + 1

        if ret == 0:
            update_group_job_status(jid, wf['@jid'], JOB_STATUS_COMPLETED)
        else:
            update_workflow_status(jid, wf['@jid'], JOB_STATUS_FAILED)

        wf = _getNextWf(doc, wf, ret)
        if wf is None:
            if ret == -1:
                update_overall_group_job_status(jid, JOB_STATUS_FAILED)
                shelf.close()
                return
            shelf.close()
            update_overall_group_job_status(jid, JOB_STATUS_COMPLETED)
            return

    shelf.close()
    update_overall_group_job_status(jid, JOB_STATUS_COMPLETED)


def jobexecute(jid, seqno, shelf, logfile):
    """
    Executes an individual Job

    :param jid: Jobid
    :param shelf: Shelf data structure to be saved for rollback
    :param seqno: Sequence number, helps to track order of execution
    :param logfile: Path to log file

    """

    outputdicts = {}
    g_obj_list = {}

    fd = None
    try:
        fd = open(get_job_file(jid), 'r')

    except IOError:
        return -1

    doc = xmltodict.parse(fd.read())

    message = "------<b> " + doc['workflow']['@name'] + " </b>------\n"
    customlogs(message, logfile)

    hw_type = doc['workflow']['@htype']

    job_recorder = _init_job_recorder(jid, doc)

    init_task = _get_initial_task(doc['workflow']['tasks']['task'])
    prepare_status_file(
        doc['workflow']['@id'],
        jid,
        doc['workflow']['tasks']['task'])

    ret = _execute_task(
        init_task,
        0,
        job_recorder,
        doc['workflow']['tasks']['task'],
        outputdicts,
        g_obj_list,
        logfile, hw_type)

    if ret == -1:
        update_overall_status(jid, JOB_STATUS_FAILED)
    else:
        update_overall_status(jid, JOB_STATUS_COMPLETED)
    shelf[str(seqno)] = {}
    shelf[str(seqno)]['record'] = job_recorder
    if ret == -1:
        shelf[str(seqno)]['record']['status'] = JOB_STATUS_FAILED
    else:
        shelf[str(seqno)]['record']['status'] = JOB_STATUS_COMPLETED
    return ret


def dump_stack(jid, cur_task, seqno, job_recorder, task_list, logfile, outputdicts, hw_type):
    """
    Dumps the all the parameters of executes task in case of a failure with out any failure path
    Dump is used to retry the task

    :param jid:
    :param cur_task:
    :param seqno:
    :param job_recorder:
    :param task_list:
    :param logfile:
    :param outputdicts:

    """
    # method helps in restarting a task incase of failure
    # dumps the meta required for restart to a dump file
    shelf = shelve.open(get_job_dump_file(jid), flag="c")
    shelf['record'] = job_recorder
    shelf['jid'] = jid
    shelf['cur_task'] = cur_task
    shelf['seqno'] = seqno
    shelf['task_list'] = task_list
    shelf['logfile'] = logfile
    shelf['outputdicts'] = outputdicts
    shelf['hw_type'] = hw_type
    shelf.close()
    return 0
