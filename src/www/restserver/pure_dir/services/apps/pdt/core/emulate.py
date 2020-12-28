# Project_Name    :FlashStack SmartConfig
# title           :emulate.py
# description     :Emulate SmartConfig
# version         :1.0
###################################################################

import threading
from xml.dom.minidom import *
import shutil
import shelve
import os
import time
import xmltodict
import json
import copy
from collections import OrderedDict
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, PatternFill, Font
from openpyxl.styles.borders import Border, Side

from pure_dir.infra.logging.logmanager import loginfo
from pure_dir.infra.apiresults import *
from pure_dir.services.utils.miscellaneous import *
from pure_dir.global_config import get_settings_file


def set_emulate_mode(emulate):
    res = result()
    with open(get_settings_file()) as s_file:
        rf_doc = xmltodict.parse(s_file.read())
    if emulate:
        rf_doc['settings']['system']['@emulate'] = '1'
    else:
        rf_doc['settings']['system']['@emulate'] = '0'
    rf_out = xmltodict.unparse(rf_doc, pretty=True)
    with open(get_settings_file(), 'w') as w_file:
        w_file.write(rf_out.encode('utf-8'))
    res.setResult(None, PTK_OKAY, "Enabled Emulate")
    return res


emulated = None
#assumes a restart in emulated mode
def check_if_emulated():
    global emulated
    if emulated != None:
        return emulated
    with open(get_settings_file()) as s_file:
        rf_doc = xmltodict.parse(s_file.read())
        if '@emulate' not in rf_doc['settings']['system']:
            emulated = False
            return emulated

        if rf_doc['settings']['system']['@emulate'] == '0':
            emulated = False
            return emulated
        else:
            emulated = True
            return emulated

#print (check_if_emulated())
def unset_emulate_mode():
    pass
