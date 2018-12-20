"""
    Orchestration_form_data
    ~~~~~~~~~~~~~~~~~~~~~~~

    Helps to fill form data for tasks

"""

from pure_dir.infra.logging.logmanager import *
from pure_dir.infra.apiresults import *
from pure_dir.services.apps.pdt.core.tasks.main.pure import*
from pure_dir.services.apps.pdt.core.tasks.test.pure import*
from pure_dir.services.apps.pdt.core.tasks.main.ucs import*
from pure_dir.services.apps.pdt.core.tasks.test.ucs import*
from pure_dir.services.apps.pdt.core.tasks.main.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_5k import*
from pure_dir.services.apps.pdt.core.tasks.main.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.test.nexus_9k import*
from pure_dir.services.apps.pdt.core.tasks.main.mds import*
from pure_dir.services.apps.pdt.core.tasks.test.mds import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_config import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_task_data import*
from pure_dir.services.apps.pdt.core.orchestration.orchestration_job_executor import*

from xml.dom.minidom import *
import xmltodict


class OrchestrationForm:
    def __init__(self):
        pass

    def _check_if_simulated(self, doc, texecid):
        """
        Returns True if the job is simulated

        :param doc: XML document object
        :param texecid: Task execution ID 
        """
        if '@simulate' in doc['workflow'].keys(
        ) and doc['workflow']['@simulate'] == "1":
            return True

        for task in doc['workflow']['tasks']['task']:
            if type(task) is unicode:
                if '@simulate' in doc['workflow']['tasks']['task'] and doc['workflow']['tasks']['task']['@simulate'] == "1":
                    return True
            elif task['@texecid'] == texecid:
                if '@simulate' in task.keys() and task['@simulate'] == "1":
                    return True
        return False

    def _get_class_from_texecid(self, doc, texecid):
        """
        Returns class ID/ task ID from task execution ID

        :param doc: XML document object
        :param texecid: Task execution ID 
        """
        for task in doc['workflow']['tasks']['task']:
            if type(task) is unicode:
                return doc['workflow']['tasks']['task']['@id']
            if task['@texecid'] == texecid:
                return task['@id']
        return None

    def _get_field_value_from_texecid(self, doc, texecid, field_name):
        """
        Returns value of a field from task execution ID

        :param doc: XML document object
        :param texecid: Task execution ID
        :param field_name: field name 
        """

        for task in doc['workflow']['tasks']['task']:
            if task['@texecid'] == texecid:
                for arg in task['args']['arg']:
                    if arg['@name'] == field_name:
                        return arg['@value']

        return None

    def _get_hw_type(self, doc):
        """
        Returns hardware type from Job document

        :param doc: XML document object
        :param texecid: Task execution ID
        :param field_name: field name 
        """

        if '@htype' in doc['workflow'].keys():
            return doc['workflow']['@htype']
        return None

    def _get_group_value_from_texecid(self, doc, texecid, group_name):
        """
        Returns value for a group of fields from Job document

        :param doc: XML document object
        :param texecid: Task execution ID
        :param field_name: field name 
        """

        for task in doc['workflow']['tasks']['task']:
            if task['@texecid'] == texecid:
                for arg in task['args']['arg']:
                    if arg['@ip_type'] == "group" and arg['@name'] == group_name:
                        return eval(arg['@value'])
        return None

    def _get_group_member_values(self, doc, group_value, member_name):
        """
        Returns value for a group member from Job document

        :param doc: XML document object
        :param texecid: Task execution ID
        :param field_name: field name 
        """

        grp_mbr_vals = []
        for grp in group_value:
            if member_name in grp.keys():
                grp_mbr_vals.append(grp[member_name]['value'])
        return grp_mbr_vals

    def get_options_api(self, jobid, texecid, operation, keys, isGroup=False, ttype=''):
        """
        Returns the option values to be filled in listbox, dropbox, radio button etc.
        Method invokes the helper method in specfic task to get the values

        :param jobid: Job ID
        :param operation: Method to be executed
        :param keys: key values passed from UI, based on the values in TaskInputs API
        :param isGroup: represents if this is a group field
        """
        ret = result()

        keys['keyvalues'].append({'value': jobid, 'key': 'jobid'})
        keys['keyvalues'].append({'value': texecid, 'key': 'texecid'})

        path = get_file_location(execid=texecid, ttype=ttype, id=jobid)
        if not path:
            loginfo("No such instance")
            ret.setResult(None, PTK_NOTEXIST,  _(
                "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
            return ret

        with open(path) as td:
            doc = xmltodict.parse(td.read())

        class_name = self._get_class_from_texecid(doc, texecid)
        hw_type = self._get_hw_type(doc)
        if class_name is not None:
            realm = class_name

        try:
            if self._check_if_simulated(doc, texecid):
                exec("%s = %s" % ("obj", "Test_" + realm + ".Test_" + realm + "()"))
            else:
                exec("%s = %s" % ("obj", realm + "." + realm + "()"))

        except Exception as e:
            loginfo(str(e))
            ret.setResult(None, PTK_INTERNALERROR, _(
                "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
            return ret

        try:
            method = getattr(obj, operation)
            if keys:
                for key_pair in keys['keyvalues']:
                    if 'ismapped' in key_pair and key_pair['ismapped'] == '3':
                        key_pair['value'] = get_value_from_global_list(
                            hw_type, key_pair['value'])
                        # Its a global mapped value, Get the value
            if isGroup == True:
                tmp_args = keys.values()[0]
                tmp_args.append({"key": "group", "value": "1"})
                keys['keyvalues'] = tmp_args
            return method(keys)
        except Exception as e:
            ret = result()
            loginfo("exception" + str(e))
            ret.setResult([], PTK_INTERNALERROR, _(
                "PDT_UNEXPECTED_INTERNAL_ERR_MSG"))
            return ret

    def get_group_member_values_api(self, jobid, texecid, group_id, member_name):
        """
        Returns list of group member values

        :param jobid: Job ID
        :param texecid: task execution ID
        :param group_id: Group ID
        :param member_name: field member name
        """
        ret = result()
        grp_member_values = []

        try:
            with open(get_job_file(jobid)) as td:
                doc = xmltodict.parse(td.read())
        except IOError:
            loginfo("Job does not exist")
            ret.setResult(None, PTK_NOTEXIST, _(
                "PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
            return ret

        grp_value = self._get_group_value_from_texecid(doc, texecid, group_id)
        if grp_value:
            grp_member_values = self._get_group_member_values(
                doc, grp_value, member_name)

        ret.setResult(grp_member_values, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret

    def get_field_value_api(self, jobid, texecid, field_name):
        """
        Returns value for specified field

        :param jobid: Job ID
        :param texecid: task execution ID
        :param field_name: Field Name
        """

        ret = result()
        field_values = []

        try:
            with open(get_job_file(jobid)) as td:
                doc = xmltodict.parse(td.read())
        except IOError:
            loginfo("Job does not exist")
            ret.setResult(None, PTK_NOTEXIST, _(
                "PDT_RESOURCE_UNAVAILABLE_ERR_MSG"))
            return ret

        fvalue = self._get_field_value_from_texecid(doc, texecid, field_name)
        if fvalue:
            try:
                fvalue = eval(fvalue)
                if type(fvalue) == list:
                    field_values = fvalue
            except (TypeError, NameError):
                if '|' in fvalue:
                    field_values = fvalue.split('|')
                else:
                    field_values = fvalue

        ret.setResult(field_values, PTK_OKAY, _("PDT_SUCCESS_MSG"))
        return ret
