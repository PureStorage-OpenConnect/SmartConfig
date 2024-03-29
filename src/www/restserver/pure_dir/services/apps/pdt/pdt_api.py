#!/usr/bin/env python
# Project_Name    :FlashStack SmartConfig
# title           :pdt_api.py
# description     :Landing place for PDT APIs
# author          :Guruprasad
# version         :1.0
############################################################


from pure_dir.components.compute.ucs.ucs import *
from pure_dir.components.compute.ucs.ucs_upgrade import *
from pure_dir.components.compute.ucs.ucs_report import *
from pure_dir.components.storage.purestorage import *
from pure_dir.components.storage.flashblade.flashblade_report import *
from pure_dir.components.common import *
from pure_dir.components.reset_devices import *
from pure_dir.components.network.nexus.nexus_setup import *
from pure_dir.components.storage.mds.mds_setup import *
from pure_dir.components.storage.purestorage.fa_setup import *
from pure_dir.components.storage.flashblade.flashblade_setup import *
from pure_dir.infra.logging.logmanager import *

from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration import *
from pure_dir.services.apps.pdt.core.orchestration.orchestration_form_data import *

from pure_dir.services.apps.pdt.core.reportmanager import *

from core import *




def log(data):
    try:
        loginfo(data)
    except BaseException:
        loginfo("failed to log")


def systeminfo():
    ret = systemmanager.system_info()
    return parseResult(ret)


def deploymentsettings(data):
    log(data)
    ret = systemmanager.deployment_settings(data)
    return parseResult(ret)


def networkinfo():
    ret = systemmanager.networkinfo()
    return parseResult(ret)


def importlogo(uploadfile):
    ret = systemmanager.import_logo(uploadfile)
    return parseResult(ret)


def pdtreset():
    ret = systemmanager.pdtreset()
    return parseResult(ret)


def fscomponents(mac='', initStage=False):
    log(mac)
    ret = discovery.fscomponents(mac, initStage)
    return parseResult(ret)


def freeip():
    ret = discovery.freeip()
    return parseResult(ret)


def exportdevices():
    ret = discovery.exportdevices()
    return parseResult(ret)


def initialconfig():
    ret = discovery.initialconfig()
    return parseResult(ret)


def dhcpenable(data):
    log(data)
    ret = discovery.dhcpenable(data)
    return parseResult(ret)


def dhcpvalidate(data):
    log(data)
    ret = discovery.dhcpvalidate(data)
    return parseResult(ret)


def dhcpdisable():
    ret = discovery.dhcpdisable()
    return parseResult(ret)


def dhcpinfo():
    ret = discovery.dhcpinfo()
    return parseResult(ret)


def genvalidate(data, stacktype):
    ret = discovery.genvalidate(data, stacktype)
    return parseResult(ret)


def adddevice(data):
    ret = discovery.adddevice(data)
    return parseResult(ret)


def importimage(uploadfile, image_type, image_sub_type='', image_os_sub_type=''):
    obj = Orchestration()
    ret = obj.importimage(uploadfile, image_type,
                          image_sub_type, image_os_sub_type)
    return parseResult(ret)

# def isobinding(isofile,kickstart):
#    obj = Orchestration()
#    ret = obj.isobinding(isofile,kickstart)
#    return parseResult(ret)


def listimages(imagetype=''):
    obj = Orchestration()
    ret = obj.listimages(imagetype)
    return parseResult(ret)


def deleteimage(imagename):
    obj = Orchestration()
    ret = obj.deleteimage(imagename)
    return parseResult(ret)


def infraimages():
    ret = ucsinfraimages()
    return parseResult(ret)


def bladeimages():
    ret = ucsbladeimages()
    return parseResult(ret)


def deletedevice(mac_list):
    ret = discovery.deletedevice(mac_list)
    return parseResult(ret)


def configdefaults(data):
    ret = discovery.configdefaults(data)
    return parseResult(ret)


def saveconfig(stacktype, data, update):
    if update == 0:
        ret = discovery.save_config(stacktype=stacktype, datas=data)
    else:
        ret = discovery.update_config(stacktype=stacktype, datas=data)
    return parseResult(ret)


def clearconfig():
    ret = discovery.clearconfig()
    return parseResult(ret)


def restore_config(stacktype, data):
    ret = config_json.restore_config(stacktype, data)
    return parseResult(ret)


def reconfigure(hwtype, mac, force):
    ret = discovery.reconfigure(hwtype, mac, force)
    return parseResult(ret)


def nexusconfigure(data):
    obj = NEXUSSetup()
    ret = obj.nexusconfigure(data)
    return parseResult(ret)


def nexusvalidate(data, model):
    obj = NEXUSSetup()
    ret = obj.nexusvalidate(data, model)
    return parseResult(ret)


def nexus9kimages():
    obj = NEXUSSetup()
    ret = obj.nexus9kimages()
    return parseResult(ret)


def nexus5ksystemimages():
    obj = NEXUSSetup()
    ret = obj.nexus5ksystemimages()
    return parseResult(ret)


def nexus5kkickstartimages():
    obj = NEXUSSetup()
    ret = obj.nexus5kkickstartimages()
    return parseResult(ret)


def faconfigure(data):
    obj = FASetup()
    ret = obj.faconfigure(data)
    return parseResult(ret)


def favalidate(data):
    obj = FASetup()
    ret = obj.favalidate(data)
    return parseResult(ret)


def fbvalidate(data):
    obj = FBSetup()
    ret = obj.fbvalidate(data)
    return parseResult(ret)


def fbconfigure(data):
    obj = FBSetup(data['orig_ip'])
    ret = obj.fbconfigure(data)
    return parseResult(ret)


def mdsconfigure(data):
    obj = MDSSetup()
    ret = obj.mdsconfigure(data)
    return parseResult(ret)


def mdsvalidate(data):
    obj = MDSSetup()
    ret = obj.mdsvalidate(data)
    return parseResult(ret)


def mdskickstartimages():
    obj = MDSSetup()
    ret = obj.mdskickstartimages()
    return parseResult(ret)


def mdssystemimages():
    obj = MDSSetup()
    ret = obj.mdssystemimages()
    return parseResult(ret)


def mdsimages():
    obj = MDSSetup()
    ret = obj.mdsimages()
    return parseResult(ret)


def mdsvalidateimages(data):
    obj = MDSSetup()
    ret = obj.mdsvalidateimages(data)
    return parseResult(ret)


def ucsmfexinfo(fexid):
    obj = UCSManager()
    ret = obj.ucsmfexinfo(fexid)
    return parseResult(ret)


def ucsmlist():
    obj = UCSManager()
    ret = obj.ucsmlist()
    return parseResult(ret)


def ucsmficonfigure(mode, data):
    obj = UCSManager()
    ret = obj.ucsmficonfigure(mode, data)
    return parseResult(ret)


def ucsmfivalidate(mode, data):
    obj = UCSManager()
    ret = obj.ucsmfivalidate(mode, data)
    return parseResult(ret)


def ucsmsetip(
        clusterip='',
        primaryip='',
        secondaryip='',
        gateway='',
        netmask=''):
    obj = UCSManager()
    ret = obj.ucsmsetip(
        clusterip='',
        primaryip='',
        secondaryip='',
        gateway='',
        netmask='')
    return parseResult(ret)


# Orchestration APIs

def workflows(stacktype=''):
    obj = Orchestration()
    ret = obj.workflows(stacktype)
    return parseResult(ret)


def tasks(htype=''):
    obj = Orchestration()
    ret = obj.tasks(htype)
    return parseResult(ret)


def workflowgroups(id, ttype=''):
    obj = Orchestration()
    ret = obj.workflowgroups(id, ttype)
    return parseResult(ret)


def workflowinfo(wid):
    obj = Orchestration()
    ret = obj.workflowinfo(wid)
    return parseResult(ret)


def flashstacktype():
    obj = Orchestration()
    ret = obj.flashstacktype()
    return parseResult(ret)


def jobtasks(id, ttype=''):

    obj = Orchestration()
    ret = obj.jobtasks(id, ttype)
    return parseResult(ret)


def jobtaskinputsave(id, execid, input_list, ttype=''):
    obj = Orchestration()
    ret = obj.jobtaskinputsave(id, execid, input_list, ttype)
    return parseResult(ret)


def jobtaskmandatoryinputsave(id, input_list, ttype=''):
    obj = Orchestration()
    ret = obj.jobtaskmandatoryinputsave(id, input_list, ttype)
    return parseResult(ret)


def workflowinputs(id, stacktype):
    obj = Orchestration()
    ret = obj.workflowinputs(id, stacktype)
    return parseResult(ret)


def workflowprepare(id):
    obj = Orchestration()
    ret = obj.workflowprepare(id)
    return parseResult(ret)


def workflowpersistantprepare(id):
    obj = Orchestration()
    ret = obj.workflowpersistantprepare(id)
    return parseResult(ret)


def jobvalidate(jobid, execid=''):
    obj = Orchestration()
    ret = obj.jobvalidate(jobid, execid)
    return parseResult(ret)


def jobmandatoryvalidate(jobid):
    obj = Orchestration()
    ret = obj.jobmandatoryvalidate(jobid)
    return parseResult(ret)


def jobexecute(jobid):
    obj = Orchestration()
    ret = obj.jobexecute(jobid)
    return parseResult(ret)


def batchexecute(stacktype, wid=''):
    obj = Orchestration()
    ret = obj.batchexecute(stacktype, wid)
    return parseResult(ret)


def jobrevert(stacktype=None, jobid=None):
    obj = Orchestration()
    ret = obj.jobrevert(stacktype, jobid)
    return parseResult(ret)


def jobretry(stacktype=None, jobid=None):
    obj = Orchestration()
    ret = obj.jobretry(stacktype, jobid)
    return parseResult(ret)


def servicerequests():
    obj = Orchestration()
    ret = obj.servicerequests()
    return parseResult(ret)


def servicerequestinfo(jobid):
    obj = Orchestration()
    ret = obj.servicerequestinfo(jobid)
    return parseResult(ret)


def rollbacktaskdata(jobid, pjobid, tid):
    obj = Orchestration()
    ret = obj.rollbacktaskdata(jobid, pjobid, tid)
    return parseResult(ret)


def rollbackstatus(jobid):
    obj = Orchestration()
    ret = obj.rollbackstatus(jobid)
    return parseResult(ret)


def jobtaskinputs(execid, id, ttype=''):
    obj = Orchestration()
    return parseResult(obj.jobtaskinputs(execid, id, ttype))


def jobtaskmandatoryinputs(id, ttype=''):
    obj = Orchestration()
    return parseResult(obj.jobtaskmandatoryinputs(id, ttype))


def jobtaskoutputs(texecid, jobid):
    obj = Orchestration()
    return parseResult(obj.jobtaskoutputs(texecid, jobid))


def jobstatus(jobid):
    obj = Orchestration()
    return parseResult(obj.jobstatus(jobid))


def groupjobstatus(jobid):
    obj = Orchestration()
    return parseResult(obj.groupjobstatus(jobid))


def tasksuggestedinputs(id, execid, ttype='', field=''):
    obj = Orchestration()
    return parseResult(obj.tasksuggestedinputs(id, execid, ttype, field))


def jobsaveas(jobid, data):
    obj = Orchestration()
    ret = obj.jobsaveas(jobid, data)
    return parseResult(ret)


def logs(jobid):
    obj = Orchestration()
    return parseResult(obj.logs(jobid))


def deploymentlogs(stacktype):
    obj = Orchestration()
    return parseResult(obj.deploymentlogs(stacktype))


def getoptions(jobid, execid, operation, keys, isGroup=False, ttype=''):
    obj = OrchestrationForm()
    return parseResult(obj.get_options_api(jobid, execid, operation, keys, isGroup, ttype))


def getglobaloptions(operation, ttype, keys):
    obj = Orchestration()
    ret = obj.getglobaloptions(operation, ttype, keys)
    return parseResult(ret)


def getgroupmembervalues(jobid, execid, groupid, membername):
    obj = OrchestrationForm()
    return parseResult(obj.get_group_member_values_api(jobid, execid, groupid, membername))


def getfieldvalue(jobid, execid, fieldname):
    obj = OrchestrationForm()
    return parseResult(obj.get_field_value_api(jobid, execid, fieldname))


def taskinputvalue(self, jid, taskid):
    obj = Orchestration()
    return parseResult(obj.taskinputvalue(self, jid, taskid))


def exportworkflow(wkflowlist):
    obj = Orchestration()
    ret = obj.exportworkflow(wkflowlist)
    return parseResult(ret)


def exportlog():
    obj = Orchestration()
    ret = obj.exportlog()
    return parseResult(ret)


def importworkflow(uploadfile):
    obj = Orchestration()
    ret = obj.importworkflow(uploadfile)
    return parseResult(ret)


def possiblefstypes(data):
    log(data)
    obj = Orchestration()
    ret = obj.possiblefstypes(data)
    return parseResult(ret)


def getglobals(stacktype, hidden=False):
    obj = Orchestration()
    ret = obj.getglobals(stacktype, hidden)
    return parseResult(ret)


def setglobals(stacktype, input_list):
    obj = Orchestration()
    ret = obj.setglobals(stacktype, input_list)
    return parseResult(ret)


def batchstatus(stacktype):
    obj = Orchestration()
    ret = obj.batchstatus(stacktype)
    return parseResult(ret)


def eulacontent():
    obj = Orchestration()
    ret = obj.eulacontent()
    return parseResult(ret)


def eulaagreement(isagree):
    obj = Orchestration()
    ret = obj.eulaagreement(isagree)
    return parseResult(ret)


def exportconfiguration(stacktype):
    ret = config_json.export_configuration(stacktype)
    return parseResult(ret)


def importconfiguration(uploadfile):
    ret = config_json.import_configuration(uploadfile)
    return parseResult(ret)


def jsonconfigdefaults(stacktype):
    ret = config_json.json_config_defaults(stacktype)
    return parseResult(ret)


# reports
def sc_report(stacktype):
    obj = SCReport()
    ret = obj.report(stacktype)
    return parseResult(ret)


def sc_report_info(method, args):
    obj = SCReport()
    ret = obj.report_info(method, args)
    return parseResult(ret)


def generate_report(stacktype):
    obj = SCReport()
    ret = obj.generate_report(stacktype)
    return parseResult(ret)


def report_status(tid):
    obj = SCReport()
    ret = obj.report_status(tid)
    return parseResult(ret)


def fs_connectivity():
    ret = topology.fs_connectivity()
    return parseResult(ret)


def release_handle(stacktype):
    ret1 = release_ucsm_handler()
    if 'fb' not in stacktype:
        return parseResult(ret1)
    ret2 = release_fb_handler()
    ret = result()
    if ret1.getStatus() != 0 and ret2.getStatus() != 0:
        ret.setResult(False, PTK_NOTEXIST, "Both UCS and FlashBlade Handles don't exist")
        return parseResult(ret)
    elif ret1.getStatus() != 0:
        return parseResult(ret1)
    elif ret2.getStatus() != 0:
        return parseResult(ret2)
    else:
        ret.setResult(True, PTK_OKAY, "Released both UCS and FlashBlade Handles")
        return parseResult(ret)


def devicereset(devices_list, force):
    ret = device_reset(devices_list, force)
    return parseResult(ret)


def resetstatus():
    ret = reset_status()
    return parseResult(ret)

def device_to_reset():
    ret = devices_to_reset()
    return parseResult(ret)


def backupconfig():
    ret = fs_config.config_download()
    return parseResult(ret)
