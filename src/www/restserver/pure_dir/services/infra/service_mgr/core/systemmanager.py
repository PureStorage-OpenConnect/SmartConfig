#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :systemmanager.py
# description     :Service Information
# author          :Guruprasad
# version         :1.0
############################################################

from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *

ula_path = "ula/ula.txt"


def system_info():
    res = result()
    sysinfo = {
        'name': 'FlashStack Applications',
        'version': '1.0',
        'copyright': 'Pure Storage',
        'ula': ula_path
    }

    res.setResult(sysinfo, PTK_OKAY, "Success")
    return res
