# Project_Name    :FlashStack SmartConfig
# title           :emulate.py
# description     :Emulate SmartConfig
# version         :1.0
###################################################################

from xml.dom.minidom import *
import xmltodict

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


def check_if_emulated():
    global emulated
    if emulated is not None:
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


def unset_emulate_mode():
    pass
