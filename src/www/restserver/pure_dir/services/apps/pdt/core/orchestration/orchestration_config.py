"""
    orchestration_congig
    ~~~~~~~~~~~~~

    Global configuration file for Orchestration

"""

import os
import gettext

g_base_dir = "/mnt/system/pure_dir/pdt/"
g_download_dir = "/var/www/html/static/downloads/"
g_workflows_dir = "%s/workflows" % (g_base_dir)
g_task_lib_file_path = "%s/task.xml" % (g_base_dir)
g_jobs_dir_path = "%s/jobs" % (g_base_dir)
g_service_req_dir = "%s/sreq" % (g_base_dir)
g_job_status_dir = "%s/jobs/status" % (g_base_dir)
g_rollback_status_file = "%s/rollback/status" % (g_base_dir)
g_wkflow_path = "%s/workflows/" % (g_base_dir)
g_upload_path = '/mnt/system/uploads/'
g_job_dump_dir = "%s/jobs/dumps" % (g_base_dir)
g_log_dir = "%s/jobs/logs" % (g_base_dir)
g_tmp_export_location = "/tmp/export/"
g_error_log = "/usr/local/apache2/logs/error_log"
g_message_log = "/var/log/messages"
g_pure_log = "/mnt/system/pure_dir/pure_dir.log"

TASK_STATUS_EXECUTING = "EXECUTING"
TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_FAILED = "FAILED"
TASK_STATUS_READY = "READY"
TASK_STATUS_COMPLETED = "COMPLETED"


JOB_STATUS_EXECUTING = "EXECUTING"
JOB_STATUS_PENDING = "PENDING"
JOB_STATUS_FAILED = "FAILED"
JOB_STATUS_READY = "READY"
JOB_STATUS_COMPLETED = "COMPLETED"


TASK_DELAY = 2
TASK_ROLLBACK_DELAY = 2

try:
    _
except NameError:
    locale_path = "/var/www/restserver/pure_dir/services/apps/pdt/locales/"
    os.system("msgfmt " + locale_path + "en_US/LC_MESSAGES/messages.po -o " +
              locale_path + "en_US/LC_MESSAGES/messages.mo")
    language = gettext.translation(
        'messages', localedir=locale_path, languages=['en_US'])
    language.install()


def get_error_log():
    return g_error_log


def get_message_log():
    return g_message_log


def get_pure_log():
    return g_pure_log


def get_download_path():
    return g_download_dir


def get_tmp_export_location():
    return g_tmp_export_location


def get_global_wf_config_file():
    return "%s/globals.xml" % (g_base_dir)


def get_devices_wf_config_file():
    return "%s/devices.xml" % (g_base_dir)


def get_job_file(jobid):
    return "%s/job-%s.xml" % (g_jobs_dir_path, jobid)


def get_batch_status_file(hw_type):
    return "%s/batch-%s.xml" % (g_jobs_dir_path, hw_type)


def get_job_dump_file(jobid):
    return "%s/job-%s-dump" % (g_job_dump_dir, jobid)


def get_log_file(jobid):
    return "job-%s.log" % (jobid)


def get_rb_log_file(jobid):
    return "job-%s.log" % (jobid)


def get_log_file_path(jobid):
    return "%s/job-%s.log" % (g_log_dir, jobid)


def get_shelf_file(jobid):
    return "%s/job-%s.shlv" % (g_service_req_dir, jobid)


def get_shelf_files_pattern():
    return "%s/job-*.shlv" % (g_service_req_dir)


def get_workflow_file(wid, hwtype):
    return "%s/%s/wf-%s.xml" % (g_workflows_dir, hwtype, wid)


def get_workflow_dir():
    return g_workflows_dir


def get_tmp_file(wid):
    return "/tmp/%s.xml" % (wid)


def get_workflow_files_pattern(hwtype):
    return "%s/%s/wf-*.xml" % (g_workflows_dir, hwtype)


def get_job_status_file(jobid):
    return "%s/job-status-%s.xml" % (g_job_status_dir, jobid)


def get_rollback_status_file(jobid):
    return "%s/rollback-status-%s.xml" % (g_rollback_status_file, jobid)


def get_job_group_status_file(jobid):
    return "%s/job-status-%s.xml" % (g_job_status_dir, jobid)


def get_task_library_file():
    return g_task_lib_file_path


def generate_field_key(texecid, task_name, field_name):
    return "__" + texecid + "." + task_name + "." + field_name


def get_workflow_path():
    return g_wkflow_path


def get_htype_workflow_path(htype, wid):
    return "%s/workflows/%s/wf-%s.xml" % (g_base_dir, htype, wid)


def get_job_file_pattern():
    return "%s/job-*.xml" % (g_jobs_dir_path)


def get_wk_file_pattern():
    return "%s/*/wf-*.xml" % (g_wkflow_path)
