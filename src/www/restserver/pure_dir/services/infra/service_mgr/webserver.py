#!/usr/bin/env python
# Project_Name    :Flashstack Deployment
# title           :webserver.py
# description     :Service Manager connexion app
# author          :Guruprasad
# version         :1.0
############################################################

import connexion

servicemgr_app = connexion.App(__name__, swagger_ui=False)
servicemgr_app.add_api('servicemanager_api.yaml', base_path='/pure',
                       validate_responses=True, strict_validation=True)
