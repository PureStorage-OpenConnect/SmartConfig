"""
    orchestration_task_data
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    helpes manupulate, save form data

"""


import xmltodict
import json
import os
import socket
import ast
from operator import itemgetter
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
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
from xml.dom.minidom import parse, parseString
from pure_dir.infra.common_helper import getAsList


def pretty_print(data): return '\n'.join([line for line in parseString(
    data).toprettyxml(indent=' ' * 2).split('\n') if line.strip()])


def job_tasks_api(id, ttype=''):
    doc = None
    obj = result()
    tasks_list = []

    try:
        if ttype == 'job':
            with open(get_job_file(id)) as td:
                doc = xmltodict.parse(td.read())
        elif ttype == 'workflow':
            with open(get_workflow_file(id)) as td:
                doc = xmltodict.parse(td.read())
        else:
            with open("/tmp/" + id + ".xml") as td:
                doc = xmltodict.parse(td.read())
    except IOError:
        loginfo("Job does not exist")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj
    for task in getAsList(doc['workflow']['tasks']['task']):
        name = task['@name']
        if '@label' in task:
            name = task['@label']
        task_entity = {
            'tid': task['@id'],
            'execid': task['@texecid'],
            'name': name,
            'desc': task['@desc'] if 'desc' in task else "",
            'onsuccess': task['@OnSuccess'] if '@OnSuccess' in task else "",
            'onfailure': task['@Onfailure'] if '@Onfailure' in task else "",
            'isinittask': task['@inittask'] if '@inittask' in task else ""
        }

        if '@gtag' in task:
            task_entity['gtag'] = task['@gtag']

        if '@gt_desc' in task:
            task_entity['gtdesc'] = task['@gt_desc']

        tasks_list.append(task_entity)
    obj.setResult(tasks_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def ipvalidation(ip):
    try:
        if len(ip.split('.')) != 4:
            return False, "Enter Valid IP Address"
        socket.inet_aton(ip)
        return True, ""
    except socket.error:
        return False, "Enter Valid IP Address"


def fieldvalidation(value):
    try:
        val = int(value)
        return True, ""
    except ValueError:
        return False, "Enter Valid Number"


def job_task_input_save_api(id, execid, input_list, ttype=''):
    obj = result()
    input_args = eval(str(input_list))
    path = get_file_location(execid=execid, ttype=ttype, id=id)
    if not path:
        obj.setResult(None, PTK_NOTEXIST, "No such instance")
        return obj

    doc = parse(path)
    err = []
    order = 0
    tasks = doc.documentElement.getElementsByTagName("task")
    for task in tasks:
        task_id = task.getAttribute("texecid")
        task_name = task.getAttribute("name")
        print task_name
        if task_id == execid:
            if len(task._get_childNodes()) > 0:
                inputs = task.getElementsByTagName("arg")
                for argname in input_args:
                    for inp in inputs:
                        if argname == inp.getAttribute('name'):
                            tid = task.getAttribute("id")
                            exec("%s = %s" % ("input_obj", tid +
                                              "." + tid + "Inputs" + "()"))
                            exec("%s = %s.%s" %
                                 ("field", "input_obj", argname))
                            tvalue, mapval = form_value(input_args, argname)
                            if field.ip_type == 'text-box' and mapval == "0" and field.validation_criteria == "function":
                                exec("%s = %s" %
                                     ("cl_obj", tid + "." + tid + "()"))
                                isvalid = cl_obj.validate(tvalue)
                                if isvalid[0]:
                                    inp.setAttribute('value', str(tvalue))
                                    inp.setAttribute('mapval', mapval)
                                else:
                                    err.append(
                                        {"field": argname, "msg": isvalid[1], "order": order})
                            #TODO Changes requires on **kwargs
                            elif field.ip_type == 'text-box' and mapval == "0" and field.validation_criteria == "function_rand":
                                exec("%s = %s" %
                                     ("cl_obj", tid + "." + tid + "()"))
                                isvalid = cl_obj.validate(tvalue, task_name[-1])
                                if isvalid[0]:
                                    inp.setAttribute('value', str(tvalue))
                                    inp.setAttribute('mapval', mapval)
                                else:
                                    err.append(
                                        {"field": argname, "msg": isvalid[1], "order": order})
                            elif field.ip_type == 'text-box' and mapval == "0":
                                isvalid = validation(
                                    field.validation_criteria, tvalue)
                                if isvalid[0]:
                                    inp.setAttribute('value', str(tvalue))
                                    inp.setAttribute('mapval', mapval)
                                else:
                                    err.append(
                                        {"field": argname, "msg": isvalid[1], "order": order})
                            elif field.ip_type == 'group' and mapval == "0" and field.validation_criteria != "function":
                                val_dict = tvalue.split("|")
                                for val in val_dict:
                                    order += 1
                                    for key in ast.literal_eval(val).keys():
                                        exec("%s = %s.%s" %
                                             ("field", "input_obj", key))
                                        ky = ast.literal_eval(val)[key]
                                        if ky['ismapped'] == "0" and field.ip_type == "text-box":
                                            isvalid = validation(
                                                field.validation_criteria, ky['value'])
                                            if not isvalid[0]:
                                                err.append(
                                                    {"field": key, "msg": isvalid[1], "order": order})
                                        elif ky['value'] == "":
                                            if 'validation_criteria' in dir(
                                                    field) and field.validation_criteria == "None":
                                                pass
                                            else:
                                                err.append(
                                                    {"field": key, "msg": "Cannot be empty", "order": order})

                                if len(err) == 0:
                                    inp.setAttribute('value', str(tvalue))
                                    inp.setAttribute('mapval', str(mapval))
                            elif field.ip_type == 'group' and mapval == "0" and field.validation_criteria == "function":
                                items = tvalue.split("|")
                                for item in items:
                                    order += 1
                                    member = eval(item)
                                    exec("%s = %s" %
                                         ("cl_obj", tid + "." + tid + "()"))
                                    isvalid = cl_obj.validate(item)
                                    if not isvalid[0]:
                                        err.append(
                                            {"field": isvalid[1], "msg": isvalid[2], "order": order})
                                if len(err) == 0:
                                    inp.setAttribute('value', tvalue)
                                    inp.setAttribute('mapval', mapval)

                            elif tvalue == "":
                                if 'validation_criteria' in dir(
                                        field) and field.validation_criteria == "None":
                                    inp.setAttribute('value', tvalue)
                                    inp.setAttribute('mapval', mapval)
                                else:
                                    err.append(
                                        {"field": argname, "msg": "Cannot be empty", "order": order})

                            else:
                                inp.setAttribute('value', tvalue)
                                inp.setAttribute('mapval', mapval)

            else:
                args = doc.createElement("args")
                for argname in input_args:
                    arg = doc.createElement("arg")
                    tid = task.getAttribute("id")
                    exec("%s = %s" %
                         ("input_obj", tid + "." + tid + "Inputs" + "()"))
                    exec("%s = %s.%s" % ("field", "input_obj", argname))
                    tvalue, mapval = form_value(input_args, argname)
                    if field.ip_type == 'text-box' and mapval == "0":
                        isvalid = validation(field.validation_criteria, tvalue)
                    elif field.ip_type == 'group' and mapval == "0" and field.validation_criteria != 'function':
                        val_dict = tvalue.split("|")
                        for val in val_dict:
                            for key in ast.literal_eval(obj).keys():
                                exec("%s = %s.%s" %
                                     ("field", "input_obj", key))
                                ky = ast.literal_eval(val)[key]
                                isvalid = validation(
                                    field.validation_criteria, ky['value'])
                                if not isvalid[0]:
                                    err.append(
                                        {"field": key, "msg": isvalid[1]})
                                else:
                                    inp.setAttribute('value', str(ky['value']))
                                    inp.setAttribute(
                                        'mapval', str(ky['ismapped']))

                    else:
                        isvalid = True, ""

                    if isvalid[0]:
                        tvalue, mapval = form_value(input_args, argname)
                        arg.setAttribute('name', argname)
                        arg.setAttribute('value', str(tvalue))
                        arg.setAttribute('mapval', mapval)
                        args.appendChild(arg)
                    else:
                        err.append({"field": argname, "msg": isvalid[1]})

                    task.appendChild(args)
                outputs = doc.createElement("outputs")
                tid = task.getAttribute("id")
                exec("%s = %s" % ("output_obj", tid + "." + tid + "Outputs" + "()"))
                output_fields = [x for x in dir(output_obj) if not x.startswith(
                    '__') and not x.endswith('__')]
                for opt in output_fields:
                    exec("%s = %s.%s" % ("field", "output_obj", opt))
                    output = doc.createElement("output")
                    output.setAttribute('name', field.name)
                    output.setAttribute('value', "")
                    output.setAttribute('tvalue', field.tvalue)
                    outputs.appendChild(output)
                task.appendChild(outputs)
    if len(err) > 0:
        obj.setResult(err, PTK_NOTEXIST, _("PDT_INVALID_INPUT_ERR_MSG"))
        return obj
    with open(path, "w") as f:
        f.write(pretty_print(doc.toprettyxml(indent="")))
    obj.setResult(err, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def validation(validation_criteria, value):
    if validation_criteria:
        val = validation_criteria.split("|")
        if val[0] == "ip":
            ip = value.split('/')
            if len(ip) > 1:
                if int(ip[1]) >= 0 and int(ip[1]) < 32:
                    isvalid = ipvalidation(ip[0])
                    if isvalid[0]:
                        return True, ""
                return False, "Provide valid route"
            else:
                isvalid = ipvalidation(value)
                return isvalid
        elif val[0] == "int":
            isvalid = fieldvalidation(value)
            if isvalid[0] and len(val) > 1:
                if int(val[1].split(":")[1]) <= int(value) <= int(val[2].split(":")[1]):
                    return True, ""
                return False, "Valid Range is " + \
                    val[1].split(":")[1] + " - " + val[2].split(":")[1]
            return isvalid
        elif val[0] == "str":
            value = value.strip()
            if int(val[1].split(":")[1]) <= len(value) <= int(val[2].split(":")[1]):
                return True, ""
            return False, "Valid Length is " + val[1].split(":")[1] + " - " + val[2].split(":")[1]
        elif val[0] == "ip-range":
            if '-' in value:
                if int(value.split("-")[0]) < int(value.split("-")[1]):
                    return True, ""
                return False, "IP Not in the range"
            else:
                return False, "Not valid format"
    return True, ""


def form_value(input_args, argname):
    value = input_args[argname]
    mapval = value['ismapped']
    tvalue = value['values']
    if isinstance(tvalue, list):
        tmp_list = []
        for element in tvalue:
            if isinstance(element, dict):
                tmp_list.append(json.dumps(
                    element).replace('\"', '\''))
            else:
                tmp_list.append(element)
        tvalue = "|".join(tmp_list)
    return tvalue, mapval


def get_file_location(execid, id, ttype=''):
    if execid and ttype:
        if ttype == "job":
            path = get_job_file(id)
            if os.path.exists(path) == False:
                return False
        elif ttype == "workflow":
            path = get_workflow_file(id)
            if os.path.exists(path) == False:
                return False
    elif execid:
        path = get_tmp_file(id)
        if os.path.exists(path) == False:
            return False
    return path


def job_task_mandatory_input_save_api(id, input_list, ttype=''):
    obj = result()
    input_args = eval(str(input_list))

    if os.path.exists(get_job_file(id)) == False:
        loginfo("No such job")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))

    doc = parse(get_job_file(id))

    texec_list = []
    tasks = doc.documentElement.getElementsByTagName("task")
    for task in tasks:
        texec_list.append(task.getAttribute("texecid"))

    for texec in texec_list:
        input_dict = {}
        for argname in input_args:
            value = input_args[argname]
            if value['execid'] == texec:
                name = argname.split('_', 1)[1]
                input_dict[name] = {
                    'ismapped': value['ismapped'], 'values': value['values']}
        if input_dict:
            jobtaskinputsave_helper(
                id, texec, json.dumps(input_dict), ttype="job")

    obj.setResult(None, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def job_task_inputs_api(execid, id, ttype=''):
    ''' Lists input argumenst for specified task execid'''
    obj = result()
    wftaskip_list = []

    path = get_file_location(execid=execid, ttype=ttype, id=id)
    if not path:
        loginfo("No such Instance")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    with open(path) as fd:
        doc = xmltodict.parse(fd.read())

    for task in doc['workflow']['tasks']['task']:
        if isinstance(task, unicode):
            tid = doc['workflow']['tasks']['task']['@id']
            break
        if task['@texecid'] == execid:
            tid = task['@id']
    exec("%s = %s" % ("input_obj", tid + "." + tid + "Inputs" + "()"))
    inputs = [x for x in dir(input_obj) if not x.startswith(
        '__') and not x.endswith('__')]
  
    for ipt in inputs:
        exec("%s = %s.%s" % ("field", "input_obj", ipt))
        if isinstance(field, list) or field.group_member == "1":
            continue
        if execid:
            wftaskip = job_task_inputs(
                field=field, tid=tid, doc=doc, texecid=execid)
        else:
            wftaskip = job_task_inputs(field=field, tid=tid)
        
        if field.ip_type == "group":
            group_members = []
            for member in field.members:
                exec("%s = %s.%s" % ("member_data", "input_obj", member))
                if execid:
                    group_members.append(job_task_inputs(
                        field=member_data, tid=tid, doc=doc, texecid=execid))
                else:
                    group_members.append(job_task_inputs(
                        field=member_data, tid=tid))
 
            wftaskip['svalue'] = wftaskip['svalue'].replace('\'', '\"')
            wftaskip['addmore'] = True if field.add.lower(
            ) == 'true' or field.add.lower == '1' else False
            wftaskip['group_fields'] = group_members
        wftaskip['order'] = field.order
        wftaskip_list.append(wftaskip)
    obj.setResult(sorted(wftaskip_list, key=itemgetter('order')),
                  PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def job_task_mandatory_inputs_api(jid, ttype=''):
    ''' Lists input argumenst for specified task execid'''
    obj = result()
    wftaskip_list = []

    path = get_job_file(jid)
    if not path:
        obj.setResult(None, PTK_NOTEXIST, "No such instance")
        return obj

    with open(path) as fd:
        doc = xmltodict.parse(fd.read())

    for task in getAsList(doc['workflow']['tasks']['task']):
        tid = task['@id']
        exec("%s = %s" % ("input_obj", tid + "." + tid + "Inputs" + "()"))
        inputs = [x for x in dir(input_obj) if not x.startswith(
            '__') and not x.endswith('__')]
        tmplist = []
        for ipt in inputs:
            exec("%s = %s.%s" % ("field", "input_obj", ipt))
            if isinstance(field, list) or field.group_member == "1":
                continue
            mandatory = True if 'mandatory' in dir(
                field) and field.mandatory == "1" else False
            if mandatory:
                wftaskip = job_task_inputs(
                    field=field, doc=doc, tid=tid, mandatory="1", texecid=task['@texecid'])
                if field.ip_type == "group":
                    group_members = []
                    for member in field.members:
                        exec("%s = %s.%s" %
                             ("member_data", "input_obj", member))
                        group_members.append(
                            job_task_inputs(
                                field=member_data,
                                doc=doc,
                                tid=tid,
                                mandatory="1",
                                texecid=task['@texecid']))
                    wftaskip['svalue'] = wftaskip['svalue'].replace('\'', '\"')
                    wftaskip['addmore'] = True if field.add.lower(
                    ) == 'true' or field.add.lower == '1' else False
                    wftaskip['group_fields'] = group_members
                wftaskip['execid'] = task['@texecid']
                wftaskip['name'] = task['@texecid'] + "_" + field.name
                wftaskip['desc'] = task['@desc']
                wftaskip['order'] = field.order
                tmplist.append(wftaskip)
        wftaskip_list.extend(sorted(tmplist, key=itemgetter('order')))
    obj.setResult(wftaskip_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def workflow_inputs_api(wid, stacktype):
    obj = result()
    wftaskip_list = []

    path = get_workflow_file(wid, stacktype)
    if not os.path.exists(path):
        loginfo("No such Instance")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    wf_group = parse(path)
    for wf in wf_group.getElementsByTagName("wf"):
        wf_path = get_workflow_file(wf.getAttribute('id'), stacktype)

        if not os.path.exists(wf_path):
            loginfo("No such Instance")
            obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
            return obj

        with open(wf_path) as fd:
            doc = xmltodict.parse(fd.read())

        for task in getAsList(doc['workflow']['tasks']['task']):
            tid = task['@id']
            exec("%s = %s" % ("input_obj", tid + "." + tid + "Inputs" + "()"))
            inputs = [x for x in dir(input_obj) if not x.startswith(
                '__') and not x.endswith('__')]
            tmplist = []
            for ipt in inputs:
                exec("%s = %s.%s" % ("field", "input_obj", ipt))
                if isinstance(field, list) or field.group_member == "1":
                    continue
                recommended = True if 'recommended' in dir(
                    field) and field.recommended == "1" else False
                if recommended:
                    wftaskip = job_task_inputs(
                        field=field, doc=doc, tid=tid, texecid=task['@texecid'])
                    if field.ip_type == "group":
                        group_members = []
                        for member in field.members:
                            exec("%s = %s.%s" %
                                 ("member_data", "input_obj", member))
                            group_members.append(job_task_inputs(
                                field=member_data, doc=doc, tid=tid, texecid=task['@texecid']))
                        wftaskip['svalue'] = wftaskip['svalue'].replace(
                            '\'', '\"')
                        wftaskip['addmore'] = True if field.add.lower(
                        ) == 'true' or field.add.lower == '1' else False
                        wftaskip['group_fields'] = group_members
                    wftaskip['execid'] = task['@texecid']
                    wftaskip['desc'] = task['@desc']
                    wftaskip['order'] = field.order
                    tmplist.append(wftaskip)
            wftaskip_list.extend(sorted(tmplist, key=itemgetter('order')))
    obj.setResult(wftaskip_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def job_task_inputs(field, tid, mandatory='', doc='', texecid=''):
    wftaskip = {
        'name': field.name,
        'label': field.label,
        'iptype': field.ip_type,
        'svalue': field.svalue,
        'ismapped': field.mapval,
        'helptext': field.helptext,
        'isstatic': True if field.static.lower() == 'true' or field.static == '1' else False,
        'hidden': True if field.hidden.lower() == 'true' or field.hidden == '1' else False,
        'isbasic': True if field.isbasic.lower() == 'true' or field.isbasic == '1' else False,
        'allow_multiple_values': True if 'allow_multiple_values' in dir(field) and field.allow_multiple_values == "1" else False}

    if doc:
        for task in doc['workflow']['tasks']['task']:
            if isinstance(task, unicode):
                if 'args' not in doc['workflow']['tasks']['task']:
                    wftaskip['svalue'] = field.svalue
                    wftaskip['ismapped'] = field.mapval
                else:
                    for targ in doc['workflow']['tasks']['task']['args']['arg']:
                        if targ['@name'] == field.name:
                            wftaskip['svalue'] = field.svalue if targ['@value'] == "" else targ['@value']
                            wftaskip['ismapped'] = targ['@mapval'] if '@mapval' in targ and targ['@mapval'] in [
                                '1', '2'] else field.mapval
                break
            if task['@texecid'] == texecid:
                iplist = task['args']['arg'] if 'args' in task else []
                for targ in getAsList(iplist):
                    if targ['@name'] == field.name:
                        wftaskip['svalue'] = field.svalue if targ['@value'] == "" else targ['@value']
                        wftaskip['ismapped'] = targ['@mapval'] if '@mapval' in targ and targ['@mapval'] in [
                            '1', '2', '3'] else field.mapval

    api = {}
    dfvaluelist = []
    if field.static == "True":
        dfvalues = field.static_values.split('|')
        for dfval in dfvalues:
            dfvaluelist.append({'id': dfval.split(':')[0], 'selected': dfval.split(':')[
                               1], 'label': dfval.split(':')[2]})
    elif len(field.api) > 0:
        api = {
            'tasktype': tid,
            'name': field.api.split('|')[0]}
        inputlist = []
        args = []
        if '|' in field.api:
            args = field.api.split('|', 1)[1][1:-1].split('|')

        for arg in args:
            if len(str(arg)) > 0:
                input_entity = {'field': arg.split(':')[0], 'isdynamic': True if arg.split(
                    ':')[1].lower() == 'true' or arg.split(':')[1] == '1' else False, 'value': arg.split(':')[2]}
                if mandatory:
                    input_entity['value'] = texecid + "_" + \
                        arg.split(':')[
                        2] if input_entity['isdynamic'] is True else arg.split(':')[2]
                inputlist.append(input_entity)
        api['args'] = inputlist

    wftaskip['api'] = api
    wftaskip['dfvalues'] = dfvaluelist
    return wftaskip


def job_task_outputs_api(texecid, jid):
    ''' Lists output argumenst for specified task execid'''
    wftask_oputs = []
    found = 0
    obj = result()
    try:
        with open(get_job_file(jid)) as td:
            tdoc = xmltodict.parse(td.read())

    except EnvironmentError:
        loginfo("No such Job")
        obj.setResult(wftask_oputs, PTK_NOTEXIST,
                      _("PDT_ITEM_NOT_FOUND_ERR_MSG"))

    for task in tdoc['workflow']['tasks']['task']:
        if task['@texecid'] == texecid:
            found = 1
            oplist = task['outputs']['output'] if isinstance(
                task['outputs']['output'], list) else [task['outputs']['output']]
            for oput in oplist:
                wftask_oput_entity = {
                    'argname': oput['@name'],
                    'argtype': oput['@dt_type']}
                wftask_oputs.append(wftask_oput_entity)
    if found == 0:
        loginfo("No such task")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    obj.setResult(wftask_oputs, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def _get_parent_output_list(
        inputs_list,
        origexecid,
        texecid,
        tasks,
        processedtasks):

    for task in tasks:
        if texecid in processedtasks:
            return

        if task['@OnSuccess'] == texecid or task['@Onfailure'] == texecid:
            oplist = task['outputs']['output'] if isinstance(
                task['outputs']['output'], list) else [task['outputs']['output']]
            for output in oplist:
                if task['@texecid'] == origexecid:
                    break
                inputs_dict = {
                    'input': generate_field_key(task['@texecid'], task['@name'], output['@name'])}
		if output['@name'] != 'status':
                	inputs_list.append(inputs_dict)
                processedtasks[texecid] = texecid
                _get_parent_output_list(
                    inputs_list,
                    origexecid,
                    task['@texecid'],
                    tasks,
                    processedtasks)


''' Method returns the list of suggested arguments
       TODO: If an invalid task id given, return proper error msg'''


def task_suggested_inputs_api(id, execid, ttype='', field=''):
    obj = result()
    fd = None
    inputs_list = []
    try:
        if ttype == 'job':
            fd = open(get_job_file(id), 'r')
        elif ttype == 'workflow':
            fd = open(get_workflow_file(id), 'r')
        else:
            fd = open("/tmp/" + id + ".xml", 'r')

    except IOError:
        loginfo("unable to read job file")
        obj.setResult(
            inputs_list,
            PTK_NOTEXIST,
            _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj

    processedtasks = {}
    doc = xmltodict.parse(fd.read())
    if field:
        task = doc['workflow']['tasks']['task']
        for tsk in task:
            if tsk['@texecid'] == execid:
                arg_ls = tsk['args']['arg']
                for arg in arg_ls:
                    if arg['@name'] == field:
                        val_obj = arg['@value'].split("|")
                        for val in val_obj:
                            inputs_list.append(val)
    else:
        _get_parent_output_list(
            inputs_list,
            execid,
            execid,
            doc['workflow']['tasks']['task'],
            processedtasks)
    obj.setResult(inputs_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def task_input_value_api(jid, taskid):
    obj = result()
    fd = None
    inputs_list = []
    try:
        fd = open(get_job_file(jid), 'r')

    except IOError:
        loginfo("unable to read log file")
        obj.setResult(
            [],
            PTK_NOTEXIST,
            _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj
    doc = xmltodict.parse(fd.read())
    s = taskid.split('.')
    texecid = s[0]
    for i in doc['workflow']['tasks']['task']:
        if i['@texecid'] == texecid[2:]:
            for j in i['args']['arg']:
                if j['@name'] == 'template_desc':
                    inputs_list.append(j['@value'])
                    obj.setResult(j['@value'], PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj
