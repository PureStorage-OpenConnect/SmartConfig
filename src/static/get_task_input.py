
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
g_flash_stack_types = [
    {'label': 'FA//FI ', 'value': 'fs-mini','tag':'FC','enabled':False},
    {'label': 'FA//FI ', 'value': 'fa-fi-iscsi','tag':'iSCSI','enabled':False},
    {'label': 'FA//MDS//Nexus 9K//FI', 'value': 'fa-n9k-fi-mds-fc','tag':'FC','enabled':True},
    {'label': 'FA//MDS//FI ', 'value': 'fa-mds-fi-fc','tag':'FC','enabled':False},
    {'label': 'FA//MDS//Nexus 5K//FI', 'value': 'fa-mds-n5k-fi-fc','tag':'FC','enabled':False},
    {'label': 'FA//Nexus 5K//FI ', 'value': 'fa-n5k-fi','tag':'FC','enabled':False},
    {'label': 'FA//Nexus 5K//FI', 'value': 'fa-n5k-fi-iscsi','tag':'iSCSI','enabled':False},
    {'label': 'FA//Nexus 9K//FI ', 'value': 'fa-n9k-fi-iscsi','tag':'iSCSI','enabled':True},
]
import glob
import xmltodict
from pure_dir.services.apps.pdt.core.tasks.main.ucs import*
from pure_dir.services.apps.pdt.core.tasks.test.ucs import*
from pure_dir.services.apps.pdt.core.tasks.main.pure import *
from pure_dir.services.apps.pdt.core.tasks.test.pure import *
from pure_dir.services.apps.pdt.core.tasks.main.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.main.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.main.mds import*
from pure_dir.services.apps.pdt.core.tasks.test.mds import*

from xml.dom.minidom import *
def get_label_type(tid,argname):
    try:
       exec("%s = %s" % ("input_obj", tid +"." + tid + "Inputs" + "()"))
       exec("%s = %s.%s" % ("field", "input_obj", argname))
       return field.ip_type,field.label
    except:
       return None,None

def get_all_workflows():
    wfs = []
    for stack_type in g_flash_stack_types:
        wfs = wfs + glob.glob(get_workflow_files_pattern(stack_type['value']))
    return wfs

def get_task_data():
    wfs = get_all_workflows()
    global_file =get_global_wf_config_file()
    gl_file =parse(global_file)
    with open("text.csv", "a") as fh:
        fh.write("Task Name,label,value,type"+'\n')
    for wf in wfs:
        fd = open(wf, 'r')
        doc = xmltodict.parse(fd.read())
        xmldoc =parse(wf)
        with open("text.csv", "a") as fh:
            fh.write(doc['workflow']['@name']+'\n')
        if '@wtype' in doc['workflow'] and doc['workflow']['@wtype'] == 'wgroup':    
           pass
        else:
            for task in xmldoc.getElementsByTagName('task'):
                for arg in task.getElementsByTagName('arg'):
                    if arg.getAttribute('mapval') == "3":
                        for htype in gl_file.getElementsByTagName('htype'):
                             if htype.getAttribute('stacktype') == doc['workflow']['@htype']:
                                  for inpt in htype.getElementsByTagName('input'):
                                     if inpt.getAttribute('name') == arg.getAttribute('value') :
                                         val = get_label_type(task.getAttribute('id'),arg.getAttribute('name'))
                                         with open("text.csv", "a") as fh:
                                            fh.write(task.getAttribute('name')+","+val[1]+","+inpt.getAttribute('value')+","+val[0]+'\n')
                                  break
                    else:
                        # arg.getAttribute('mapval') == "0" or arg.getAttribute('mapval') == "1" or arg.getAttribute('mapval') == "":
                         val = get_label_type(task.getAttribute('id'),arg.getAttribute('name'))
                         with open("text.csv", "a") as fh:
                            fh.write(task.getAttribute('name')+","+val[1]+","+arg.getAttribute('value')+","+val[0]+'\n')
