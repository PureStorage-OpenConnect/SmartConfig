#!/usr/bin/env python
# Project_Name    :pure-director
# title           :logmanager.py
# description     :log manager
# author          :guruprasad
# date            :07/06/16
# version         :1.0
# ==============================================================================

import logging
import connexion
g_log_dir = "/mnt/system/pure_dir/logs/"
g_custom_log_dir = "/mnt/system/pure_dir/pdt/jobs/logs"
g_log_filename = "pure_dir.log"
g_log_format = '[%(asctime)s] (%(processName)-10s) %(module)s %(funcName)s [%(levelname)s] %(lineno)s %(message)s'


logging.DEPLOY = 21  # INFO is 20. So having in that range
logging.addLevelName(logging.DEPLOY, 'DEPLOY')

def loginfo(message):
    releasehandler()
    logging.basicConfig(level=logging.INFO, filename=g_log_dir +
                        '/' + g_log_filename, format=g_log_format)
    logging.info("%s- %s - %s" % (get_apiname(), get_currentuser(), message))
    print "%s- %s - %s" % (get_apiname(), get_currentuser(), message)


def customlogs(message, logfile):
    releasehandler()
    g_custom_log_format = '%(message)s'
    logging.basicConfig(level=logging.DEPLOY, filename=g_custom_log_dir + '/' +
                        logfile, format=g_custom_log_format)
    log = logging.getLogger("Deployment")
    log.deploy = lambda msg, *args: log._log(logging.DEPLOY, msg, args)
    log.deploy("%s" % (message))
    print "%s- %s - %s" % (get_apiname(), get_currentuser(), message)


def logerror(message):
    releasehandler()
    logging.basicConfig(level=logging.INFO, filename=g_log_dir +
                        '/' + g_log_filename, format=g_log_format)
    logging.error("%s- %s - %s" % (get_apiname(), get_currentuser(), message))
    print "%s- %s - %s" % (get_apiname(), get_currentuser(), message)


def logwarn(message):
    releasehandler()
    logging.basicConfig(level=logging.INFO, filename=g_log_dir +
                        '/' + g_log_filename, format=g_log_format)
    logging.warn("%s- %s - %s" % (get_apiname(), get_currentuser(), message))
    print "%s- %s - %s" % (get_apiname(), get_currentuser(), message)


def logcritical(message):
    releasehandler()
    logging.basicConfig(level=logging.INFO, filename=g_log_dir +
                        '/' + g_log_filename, format=g_log_format)
    logging.critical("%s- %s - %s" %
                     (get_apiname(), get_currentuser(), message))
    print "%s- %s - %s" % (get_apiname(), get_currentuser(), message)


def get_currentuser():
    """
    if flask.has_request_context():
        return (g.user)
    else:
        return("System")
    """
    return "admin"


def releasehandler():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def get_apiname():
    if connexion.request:
        return(connexion.request.path)
    else:
        return ("Background")
