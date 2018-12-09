from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.infra.common_helper import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_task_data import*
from pure_dir.services.apps.pdt.core.globalvar.main.fi_nexus9k_mds_fc import *
from pure_dir.services.apps.pdt.core.globalvar.main.fi_nexus9k_fa_iscsi import *
from pure_dir.services.apps.pdt.core.globalvar.main.fa_nexus5k_fi_fc import *
from pure_dir.services.apps.pdt.core.globalvar.main.fa_nexus5k_fi_iscsi import *
from pure_dir.services.apps.pdt.core.globalvar.main.fa_nexus5k_figen2_fc import *
from pure_dir.services.apps.pdt.core.globalvar.main.fa_nexus5k_figen2_iscsi import *
from pure_dir.services.utils.ipvalidator import *
import xmltodict
import os.path
from xml.dom.minidom import *
g_simulated = 0


def get_globals_api(stacktype, hidden):
    obj = result()
    global_list = []
    xmldoc = None
    try:
        xmldoc = parse(get_global_wf_config_file())
    except IOError:
	loginfo("Globals file does not exist")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return obj
    g_val = {}
    #xmldoc = parse(get_global_wf_config_file())
    htypes = xmldoc.getElementsByTagName('htype')
    for htype in htypes:
        if htype.getAttribute('stacktype') == stacktype:
            inpts = htype.getElementsByTagName('input')
            for i in inpts:
                g_val = {}
                g_val['name'] = i.getAttribute('name')
                g_val['label'] = i.getAttribute('label')
                g_val['iptype'] = i.getAttribute('ip_type')
                g_val['svalue'] = i.getAttribute('value')
                if i.getAttribute('static') == "False":
                    g_val['isstatic'] = False
                else:
                    g_val['isstatic'] = True
                g_val['helptext'] = i.getAttribute('helptext')
                g_val['api'] = apivalidator(i.getAttribute(
                    'api'), i.getAttribute('tasktype'))
                g_val['view'] = i.getAttribute('view')
                if i.hasAttribute('additional'):
                    g_val['additional'] = i.getAttribute('additional')
                dfhwtype = []
                hwtype = i.getAttribute('hwtype').split("|")
                for j in hwtype:
                    dfhwtype.append(j)
                g_val['hwtype'] = dfhwtype
                if i.hasAttribute('hidden') and i.getAttribute('hidden') == 'True':
                    g_val['hidden'] = True
                    if hidden == False:
                        continue
                else:
                    g_val['hidden'] = False

                dfvaluelist = []
                if i.getAttribute('static') == "True":
                    dfvalues = i.getAttribute('static_values').split('|')
                    if i.getAttribute('ip_type') == 'ip-range':
                        for dfval in dfvalues:
                            dfvaluelist.append({'min_range': int(dfval.split(':')[0]), 'max_range': int(dfval.split(':')[
                                1]), 'min_interval': int(dfval.split(':')[2]), 'max_interval': int(dfval.split(':')[3])})
                    else:
                        for dfval in dfvalues:
                            dfvaluelist.append({'id': dfval.split(':')[0], 'selected': dfval.split(':')[
                                1], 'label': dfval.split(':')[2]})
                g_val['dfvalues'] = dfvaluelist
                g_val['mandatory'] = True
                global_list.append(g_val)
    obj.setResult(global_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def getglobalvals(stacktype):
    obj = result()
    global_list = []
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
                g_val['name'] = i.getAttribute('name')
                g_val['value'] = i.getAttribute('value')
                global_list.append(g_val)
    obj.setResult(global_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def apivalidator(api_arg, tid):
    api = {
        'tasktype': tid,
        'name': api_arg.split('|')[0]}
    inputlist = []
    args = []
    if '|' in api_arg:
        args = api_arg.split('|', 1)[1][1:-1].split('|')
    for arg in args:
        if len(str(arg)) > 0:
            input_entity = {
                'field': arg.split(':')[0],
                'isdynamic': True if arg.split(':')[1].lower() == 'true' or arg.split(':')[1] == '1' else False,
                'value': arg.split(':')[2]}
            inputlist.append(input_entity)
    api['args'] = inputlist
    return api


def set_globals_api(stacktype, input_list):
    obj = result()
    if os.path.exists(get_global_wf_config_file()) == False:
	loginfo("Globals file does not exist")
        obj.setResult(None, PTK_NOTEXIST, _("PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
        return obj

    if 'kvm_console_ip' in input_list:
        kvm_err = set_globals_validate_api(input_list['kvm_console_ip'])
        if len(kvm_err) > 0:
            obj.setResult(kvm_err, PTK_INTERNALERROR,
                          _("PDT_INCORRECT_DETAILS_ERR_MSG"))
            return obj
    err = get_value(input_list, stacktype)
    valid_err = validate_data(stacktype, input_list)
    if len(err) == 0:
        if len(valid_err) != 0:
            obj.setResult(valid_err, PTK_INTERNALERROR,
                          _("PDT_INCORRECT_DETAILS_ERR_MSG"))
            return obj
        xmldoc = parse(get_global_wf_config_file())
        htypes = xmldoc.getElementsByTagName('htype')
        for htype in htypes:
            if htype.getAttribute('stacktype') == stacktype:
                inpts = htype.getElementsByTagName('input')
                for inpt in inpts:
                    if inpt.getAttribute('name') in input_list.keys():
                        inpt.setAttribute(
                            'value', input_list[inpt.getAttribute('name')])
                fd = open(get_global_wf_config_file(), 'w')
                xmldoc.writexml(fd)
                fd.close()
        obj.setResult(err, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj
    else:
        obj.setResult(err, PTK_NOTEXIST, _("PDT_INCOMPLETE_MANDATORY_FIELD_ERR_MSG"))
        return obj


def set_globals_validate_api(ip_range):
    ip_list = IpValidator().get_ips_in_range()
    valid_err = []
    subnet = '.'.join(str(ip_list[0]).split('.', 3)[:-1])
    ip_obj = ip_range.split('-')
    for i in range(int(ip_obj[0]), int(ip_obj[1])+1):
        ip = subnet + "."+str(i)
        xmldoc = parse(get_devices_wf_config_file())
        devices = xmldoc.getElementsByTagName('device')
        for device in devices:
            if device.getAttribute('device_type') == "UCSM":
                if device.getAttribute('ipaddress') == ip or device.getAttribute('vipaddress') == ip and IpValidator().is_ip_up(ip) == True:
                    valid_err.append(
                        {"field": "kvm_console_ip", "msg": ip + " Ip is not available"})
                    return valid_err
            else:
                if device.getAttribute('ipaddress') == ip and IpValidator().is_ip_up(ip) == True:
                    valid_err.append(
                        {"field": "kvm_console_ip", "msg": ip + " Ip is not available"})
                    return valid_err
    return valid_err


def get_value(input_list, stacktype):
    valid_msg_list = []
    for inpts in input_list:
        dicts = {}
        if not inpts == 'undefined':
            if len(input_list[inpts]) == 0:
                dicts = {"field": inpts, "msg": get_label(stacktype, inpts) + " should not be empty"}
                valid_msg_list.append(dicts)
    return valid_msg_list

def get_label(stacktype, name):
    xmldoc = parse(get_global_wf_config_file())
    htypes = xmldoc.getElementsByTagName('htype')
    for htype in htypes:
        if htype.getAttribute('stacktype') == stacktype:
            inpts = htype.getElementsByTagName('input')
            for inpt in inpts:
                if inpt.getAttribute('name') == name:
                    return inpt.getAttribute('label')

def validate_data(stacktype, input_list):
    valid_err = []
    xmldoc = parse(get_global_wf_config_file())
    htypes = xmldoc.getElementsByTagName('htype')
    for htype in htypes:
        if htype.getAttribute('stacktype') == stacktype:
            inpts = htype.getElementsByTagName('input')
            for inpt in inpts:
                if inpt.getAttribute('name') in input_list.keys() and inpt.hasAttribute('validation_criteria'):
                    isvalid = validation(inpt.getAttribute(
                        'validation_criteria'), input_list[inpt.getAttribute('name')])
                    if not isvalid[0]:
                        valid_err.append(
                            {"field": inpt.getAttribute('name'), "msg": isvalid[1]})
    return valid_err


def get_global_options(operation, realm, keys):
    ret = result()
    # TODO Ensure such a class exist, can exploit
    try:
        if g_simulated == 1:
            exec("%s = %s" % ("obj", ".Test_" + realm + "()"))
            loginfo("simulated mode")
        else:
            exec("%s = %s" % ("obj",  str(realm) + "()"))

    except Exception as e:
        ret.setResult([], PTK_INTERNALERROR, str(e) + "failed")
        return ret

    try:
        method = getattr(obj, operation)
        res = method(keys)
        return res

    except Exception as e:
        ret = result()
        ret.setResult([], PTK_INTERNALERROR, str(e) + "failed")
        return ret


def reset_global_config():
    xmldoc = parse(get_global_wf_config_file())
    htypes = xmldoc.getElementsByTagName('htype')
    for htype in htypes:
        inpts = htype.getElementsByTagName('input')
        for inp in inpts:
            if inp.hasAttribute('deleteOnReset') and inp.getAttribute('deleteOnReset') == '1':
                inp.setAttribute('value', '')
    fd = open(get_global_wf_config_file(), 'w')
    xmldoc.writexml(fd)
    fd.close()
    return 0
