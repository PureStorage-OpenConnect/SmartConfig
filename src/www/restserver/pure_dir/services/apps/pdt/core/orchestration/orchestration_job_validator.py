"""
    orchestration_job_validator
    ~~~~~~~~~~~~~~~~~~~~~~~

    validate workflow before execution

"""

import os
from xml.dom.minidom import parse
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_job_file


def job_validate(jobid, execid=''):
    error_info = []
    obj = result()
    if os.path.exists(get_job_file(jobid)) == False:
        loginfo("No such Job found")
        obj.setResult(0, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj
    doc = parse(get_job_file(jobid))
    validate_task_attr(doc, error_info)
    validate_task_attr_value(doc, error_info)
    validate_task_input(doc, error_info)
    #validate_static_value(doc, error_info)
    validate_onsuccess(doc, error_info)
    #validate_type(doc, error_info)
    return status(error_info, execid)


def job_mandatory_validate_api(jobid):
    obj = result()
    error_info = []
    if os.path.exists(get_job_file(jobid)) == False:
        loginfo("No such Job found")
        obj.setResult(0, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
        return obj
    doc = parse(get_job_file(jobid))
    wflist = doc.getElementsByTagName('wf')
    for wf in wflist:
        err_info = []
        if os.path.exists(get_job_file(wf.getAttribute('jid'))) == False:
            loginfo("No such Job found")
            obj.setResult(0, PTK_NOTEXIST, _("PDT_ITEM_NOT_FOUND_ERR_MSG"))
            return obj
        doc = parse(get_job_file(wf.getAttribute('jid')))
        #validate_task_attr(doc, err_info)
        #validate_task_attr_value(doc, err_info)
        validate_task_input(doc, err_info, mandatory=1)
        validate_static_value(doc, err_info, mandatory=1)
        #validate_onsuccess(doc, err_info)
        validate_type(doc, err_info, mandatory=1)

        texecid_list = []
        for er_obj in err_info:
            texecid_list.append(er_obj['execid'])
        texecid = list(set(texecid_list))
        error_content = []
        for texec in texecid:
            for info in err_info:
                if texec == info['execid']:
                    for info_obj in info['error']:
                        error_content.append(info_obj)
        if len(error_content) > 0:
            error_info.append({"execid": wf.getAttribute(
                'wexecid'), "error": error_content})
    if len(error_info) == 0:
        obj.setResult({"isvalid": True, "task": error_info},
                      PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj
    else:
        obj.setResult({"isvalid": False, "task": error_info},
                      PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj


def validate_task_attr(doc, error_info):
    task_attr = [
        #        'class',
        'id',
        'desc',
        'name',
        'inittask',
        'texecid',
        'OnSuccess',
        'Onfailure']
    itemlist = doc.getElementsByTagName('task')
    for node in itemlist:
        error_content = []
        attr_key = node.attributes.keys()
        for node_key in task_attr:
            if node_key not in attr_key:
                errStr = node_key + " attribute is not available in the task execution id " + \
                    node.attributes['texecid'].value
                er = {
                    "fieldname": node_key,
                    "msg": errStr
                }
                error_content.append(er)
        error_info.append(
            {"execid": node.attributes['texecid'].value, "error": error_content})


def validate_task_attr_value(doc, error_info):
    itemlist = doc.getElementsByTagName('task')
    for node in itemlist:
        attr_key = node.attributes.keys()
        error_content = []
        for key_val in attr_key:
            attr_value = node.attributes[key_val].value
            if len(attr_value) == 0:
                errStr = key_val + " attribute value is empty for the task execution id " + \
                    node.attributes['texecid'].value
                er = {
                    "fieldname": key_val,
                    "msg": errStr
                }
                error_content.append(er)
        error_info.append(
            {"execid": node.attributes['texecid'].value, "error": error_content})


def validate_task_input(doc, error_info, mandatory=''):
    itemlist = doc.getElementsByTagName('task')
    for node in itemlist:
        error_content = []
        arglist = node.getElementsByTagName('arg')
        for node_arg in arglist:

            if mandatory and node_arg.getAttribute('mandatory') == "1":
                pass
            elif mandatory:
                continue

            if len(node_arg.attributes['value'].value) == 0:
                errStr = " Value is empty for the task execution ID '" + \
                    node.attributes['texecid'].value + "'"
                er = {
                    "fieldname": node_arg.attributes['name'].value,
                    "msg": errStr
                }
                error_content.append(er)
        error_info.append(
            {"execid": node.attributes['texecid'].value, "error": error_content})


def validate_static_value(doc, error_info, mandatory=''):
    itemlist = doc.getElementsByTagName('task')
    for node in itemlist:
        arglist = node.getElementsByTagName('arg')
        error_content = []
        for node_arg in arglist:

            if mandatory and node_arg.getAttribute('mandatory') == "1":
                pass
            elif mandatory:
                continue

            if node_arg.attributes['static'].value == 'True':
                if node_arg.attributes['ip_type'].value == 'text-box':
                    continue

                if len(node_arg.attributes['static_values'].value) == 0:
                    errStr = " Static value is empty for " + \
                        node_arg.attributes['name'].value + "in task execution id " + node.attributes['texecid'].value
                    er = {
                        "fieldname": node_arg.attributes['name'].value,
                        "msg": errStr
                    }
                    error_content.append(er)

                else:
                    stat_obj = node_arg.attributes['static_values'].value.split(
                        "|")
                    for stat in stat_obj:
                        stat_val = stat.split(":")
                        if len(stat_val) != 3:
                            errStr = " Incorrect Static value format for " + \
                                node_arg.attributes['name'].value + " in task execution id " + node.attributes['texecid'].value
                            er = {
                                "fieldname": node_arg.attributes['name'].value,
                                "msg": errStr
                            }
                            error_content.append(er)

            else:
                if node_arg.attributes['ip_type'].value != 'text-box' and node_arg.attributes['ip_type'].value != 'group':
                    if len(node_arg.attributes['api'].value) == 0:
                        errStr = " Api is empty for " + node_arg.attributes['name'].value + " in task execution id  " + \
                            node.attributes['texecid'].value
                        er = {
                            "fieldname": node_arg.attributes['name'].value,
                            "msg": errStr
                        }
                        error_content.append(er)
                    else:
                        api = node_arg.attributes['api'].value.split("|")
                        if len(api) > 1:
                            api_param_list = api[1].split(",")
                            for api_param_obj in api_param_list:
                                api_param = api_param_obj.split(":")
                                if len(api_param) != 3:
                                    errStr = "Incorrect Api format for " + \
                                        node_arg.attributes['name'].value + " in task execution id  " + node.attributes['texecid'].value
                                    er = {
                                        "fieldname": node_arg.attributes['name'].value,
                                        "msg": errStr
                                    }
                                    error_content.append(er)
                                if len(api_param) == 3:
                                    api = api_param[2].split(".")
                                    flag = False
                                    for node_arg in arglist:
                                        if api[0] == node_arg.attributes['name'].value:
                                            flag = True
                                    if not flag:
                                        errStr = node_arg.attributes['name'].value
                                        er = er = {
                                            "fieldname": node_arg.attributes['name'].value,
                                            "msg": "api param " + errStr + "not available in the task"}
                                        error_content.append(er)

        error_info.append(
            {"execid": node.attributes['texecid'].value, "error": error_content})


def validate_onsuccess(doc, error_info):
    texecid_list = []
    itemlist = doc.getElementsByTagName('task')
    for node in itemlist:
        error_content = []
        suc_id = node.attributes['OnSuccess'].value
        if suc_id != 'None':
            for node_obj in itemlist:
                su_texecid = node_obj.attributes['texecid'].value
                texecid_list.append(su_texecid)
            if suc_id not in texecid_list:
                errStr = "Test execution id " + suc_id + \
                    " is not available in Onsuccess attribute"
                er = {
                    "fieldname": "Onsuccess",
                    "msg": errStr
                }

                error_content.append(er)
            error_info.append(
                {"execid": node.attributes['texecid'].value, "error": error_content})


def validate_type(doc, error_info, mandatory=''):
    ip_type = [
        'drop-down',
        'radio-button',
        'check-box',
        'drop-box',
        'multi-select',
        'multiselect-dropdown',
        'text-box',
        'multi-select-text',
        'group']
    itemlist = doc.getElementsByTagName('task')
    for node in itemlist:
        error_content = []
        arglist = node.getElementsByTagName('arg')
        for node_arg in arglist:

            if mandatory and node_arg.getAttribute('mandatory') == "1":
                pass
            elif mandatory:
                continue

            if node_arg.attributes['ip_type'].value not in ip_type:
                errStr = "Input Type '" + \
                    node_arg.attributes['ip_type'].value + "'is  not available"
                er = {
                    "fieldname": "ip_type",
                    "msg": errStr
                }
                error_content.append(er)
        error_info.append(
            {"execid": node.attributes['texecid'].value, "error": error_content})


def status(er, execid):
    error_info = []
    texecid_list = []
    for er_obj in er:
        texecid_list.append(er_obj['execid'])
    texecid = list(set(texecid_list))
    for texec in texecid:
        error_content = []
        for info in er:
            if texec == info['execid']:
                for info_obj in info['error']:
                    error_content.append(info_obj)
        if len(error_content) > 0:
            error_info.append({"execid": texec, "error": error_content})
    for i in error_info:
        if i['execid'] == execid:
            error_info = [{"error": i['error'], "execid":i['execid']}]
    obj = result()
    if len(error_info) == 0:
        obj.setResult({"isvalid": True, "task": error_info},
                      PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj
    else:
        obj.setResult({"isvalid": False, "task": error_info},
                      PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj
