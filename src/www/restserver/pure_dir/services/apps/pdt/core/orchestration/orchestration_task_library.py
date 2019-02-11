#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :orchestration_task_library.py
# description     :Task Library for Orchestration
# author          :Guruprasad
# version         :1.0
############################################################

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from xml.dom.minidom import *
import glob
import importlib
import os
from os.path import dirname, basename, isfile

tasks_path = "pure_dir.services.apps.pdt.core.tasks.main"


def tasks_list_api(htype=''):
    obj = result()
    task_list = []
    file_paths = glob.glob(dirname(__file__) + "/../tasks/main/*/*.py")
    file_mods = [(os.path.dirname(f).split('/')[-1] + "." + basename(f)[:-3])
                 for f in file_paths if isfile(f) and not f.endswith('__init__.py')]
    for path in file_mods:
        task_dict = {}
        if not hasattr(importlib.import_module(tasks_path + "." + path), 'metadata'):
            continue
        task_meta = importlib.import_module(tasks_path + "." + path).metadata
        task_dict['id'] = task_meta['task_id']
        task_dict['name'] = task_meta['task_name']
        task_dict['desc'] = task_meta['task_desc']
        task_dict['type'] = task_meta['task_type']
        task_list.append(task_dict)

    if htype is not '':
        if htype not in ['UCSM', 'NEXUS', 'MDS', 'PURE']:
            obj.setResult([], PTK_INTERNALERROR,
                          _("PDT_ENTER_VALID_INPUT_ERR_MSG"))
            return obj
        else:
            task_list = [task for task in task_list if task['type'] == htype]

    obj.setResult(task_list, PTK_OKAY, _("PDT_SUCCESS_MSG"))
    return obj


