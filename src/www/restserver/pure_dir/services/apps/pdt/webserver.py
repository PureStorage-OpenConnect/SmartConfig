#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :webserver.py
# description     :PDT connexion app
# author          :Guruprasad
# version         :1.0
############################################################

import connexion
from sys import dont_write_bytecode
from pure_dir.services.apps.pdt.core.init_service import init_service
dont_write_bytecode = True

init_service()
#pdt_app = connexion.App(__name__, swagger_ui=True)
# pdt_app.add_api('smartconfig_api.yaml', base_path='/pdt',
#                validate_responses=True, strict_validation=True)

################For Python3#####################################
pdt_app = connexion.App(__name__, options={"swagger_ui": True})
pdt_app.add_api('smartconfig_api.yaml', base_path='/pdt',
                validate_responses=True, strict_validation=True)
