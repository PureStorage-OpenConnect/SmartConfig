"""
    orchestration_miscellaneous
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    helper, fetches workflow execution log

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from xml.dom.minidom import *
import shelve
import os


def get_logs_api(jobid):
    obj = result()
    logs_dict = {}
    if os.path.exists(get_log_file_path(jobid)) == False:
        logs_dict = {'logs': " "}

        obj.setResult(logs_dict, PTK_NOTEXIST, _("PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
        return obj
    with file(get_log_file_path(jobid)) as f:
        logs = f.read()
    logs_dict = {'logs': logs}
    obj.setResult(logs_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def deployment_logs(jobid):
    obj = result()
    logs_dict = {}
    if os.path.exists(get_log_file_path(jobid)) == False:
        logs_dict = {'logs': " "}

        obj.setResult(logs_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return obj
    with file(get_log_file_path(jobid)) as f:
        logs = f.read()
    logs_dict = {'logs': logs}
    obj.setResult(logs_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


def servicerequests():
    obj = result()
    shelfile = get_shelf_files_pattern()
    srs = glob.glob(shelfile)
    sr_list = []
    for sr in srs:
        loginfo(sr)
        shelf = shelve.open(sr, flag='r')
        sr_entity = {
            'wid': workflow['@id'],
            'name': workflow['@name'],
            'desc': workflow['@desc']}
        sr_list.append(sr_entity)
        shelf.close()

    obj.setResult(sr_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj
