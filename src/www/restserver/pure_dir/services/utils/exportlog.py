
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
import os
import shutil
import zipfile


def zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            if filename.endswith('.xml') or filename.endswith(
                    '.log') or len(filename.split(".")) == 1:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
    zf.close()


def exportlog_helper():
    res = result()
    dw_path = get_download_path()
    os.mkdir(g_base_dir + "logs/")
    dest = g_base_dir + "logs/"
    error_log = get_error_log()
    if os.path.exists(error_log):
        shutil.copy2(error_log, dest)
    message_log = get_message_log()
    if os.path.exists(message_log):
        shutil.copy2(message_log, dest)
    pure_log = get_pure_log()
    if os.path.exists(pure_log):
        shutil.copy2(pure_log, dest)
    zip(g_base_dir + "logs/", dw_path + "logs")
    shutil.rmtree(g_base_dir + "logs/")
    res.setResult("logs.zip", PTK_OKAY, "Success")
    return res
