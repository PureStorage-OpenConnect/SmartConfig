from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
import os
import shutil
import zipfile
from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.global_config import get_settings_file
from pure_dir.services.utils.miscellaneous import *
from pure_dir.services.apps.pdt.core.config_json import export_configuration
from threading import Lock
import subprocess

lock = Lock()


def zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            loginfo(filename)
            if filename.endswith('.xml') or filename.endswith(
                    '.log') or filename.endswith('.json') or len(filename.split(".")) == 1:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
    zf.close()


def modify_apachelog(error_file):
    edit_file = "/var/www/restserver/apache_log"
    error_log = "/mnt/system/pure_dir/pdt/error_log"
    if os.path.exists(error_file):
        if os.path.exists(edit_file):
            os.remove(edit_file)
        if os.path.exists(error_log):
            os.remove(error_log)
        shutil.copy2(error_file, edit_file)
        cmd = r"sed 's/\[:error\]//g' " + edit_file + " >> " + error_log
        execute_cmd = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            shell=True,
            stderr=subprocess.PIPE)
        (output, err) = execute_cmd.communicate()
        os.remove(edit_file)
        if err != '':
            loginfo("error: failed to edit apache logs. %s" % err)
            return False
        else:
            return True


def exportlog_helper():
    res = result()
    settings_path = get_settings_file()
    with lock:
        dw_path = get_download_path()
        os.mkdir(g_base_dir + "logs/")
        dest = g_base_dir + "logs/"
        error_log = get_error_log()
        if os.path.exists(error_log):
            err_log = modify_apachelog(error_log)
            if err_log:
                error_log = get_log()
                shutil.copy2(error_log, dest)

        try:
            stacktype = get_xml_element(
                settings_path, "stacktype")[1][0]['subtype']
            export_configuration(stacktype, dest)
        except BaseException:
            loginfo("JSON export in logdump failed")

        message_log = get_message_log()
        if os.path.exists(message_log):
            shutil.copy2(message_log, dest)

        if os.path.exists(settings_path):
            shutil.copy2(settings_path, dest)

        pure_log = get_pure_log()
        if os.path.exists(pure_log):
            shutil.copy2(pure_log, dest)

        build_xml = get_build_xml()
        if os.path.exists(build_xml):
            shutil.copy2(build_xml, dest)
        zip(g_base_dir + "logs/", dw_path + "logs")
        shutil.rmtree(g_base_dir + "logs/")
        res.setResult("logs.zip", PTK_OKAY, "Success")
        return res
