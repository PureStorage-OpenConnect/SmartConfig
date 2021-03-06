"""
    orchestration_miscellaneous
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    helper, fetches workflow execution log

"""

from pure_dir.infra.apiresults import PTK_NOTEXIST, PTK_OKAY, result
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import get_log_file_path
import os


def get_logs_api(jobid):
    obj = result()
    logs_dict = {}
    if os.path.exists(get_log_file_path(jobid)) == False:
        logs_dict = {'logs': " "}

        obj.setResult(logs_dict, PTK_NOTEXIST, _(
            "PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
        return obj
    with open(get_log_file_path(jobid)) as f:
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
    with open(get_log_file_path(jobid)) as f:
        logs = f.read()
    logs_dict = {'logs': logs}
    obj.setResult(logs_dict, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj
