/**
  * @desc it will take a object(form input options) as input and will generate a html template for it.
  * @param object $field - options object to display few placeholder (form labels, mandatory symbol, help icon end etc).
  * @return string - html template string which will contain the form input element.
*/
function loadFormTemplate(field) {
	var defaults = {
		label: '',
		mandatory: false,
		helptext: '',
		holder: ''
	};
	field = $.extend({}, defaults, field);
	field.mandatory = (typeof field.mandatory == 'undefined' || !field.mandatory) ? '' : 'required';
	var str = '<div class="control-group ' + field.holder + '">\
		<label class="title col-lg-5 col-md-5 col-sm-4 col-xs-4">\
			<span class="' + field.mandatory + '">' + field.label + ': ';
			if(field.helptext != '')
				str += '<i class="fa fa-question-circle help-txt tipso tipso_style" data-tipso-title="' + field.label + '" data-tipso="' + field.helptext + '" data-html="true" data-toggle="tooltip"></i>';
			str += '</span>\
		</label>\
		<div class="controls col-lg-7 col-md-7 col-sm-8 col-xs-8">';
			str += loadFormField(field);
			str += '<div class="clear"></div>\
			<div class="help-block"></div>\
		</div>\
		<div class="clear"></div>\
	</div>';
	return str;
}

/**
  * @desc it will dynamically create form input elements based on the options passed.
  * @param object $field - input type/attributes of the new form elements (label, text, dropdown end etc).
  * @return string - html template string of the newly created input element.
*/
function loadFormField(field) {
	// Default options of the field.
	var defaults = {
		type: 'text',
		id: '',
		name: '',
		disabled: '',
		class: '',
		label: '',
		optional_label: '',
		value: '',
		maxlength: '',
		dataRole: '',
		holder: '',
		checked: false,
		readonly: false,
		fields: []
	};
	field = $.extend({}, defaults, field);

	field.name = (field.name == '') ? field.id : field.name;
	field.readonly = (field.readonly == true) ? ' readonly=true' : '';
	field.maxlength = (field.maxlength == '') ? "" : ' maxlength="' + field.maxlength + '"';
	field.dataRole = (field.dataRole == '') ? "" : ' data-role="' + field.dataRole + '"';
	var str = '';
	switch(field.type) {
		case 'label':
			str += '<input type="text" readonly id="' + field.id + '" name="' + field.name + '" ' + field.disabled + ' placeholder="' + field.label + '" value="' + field.value + '" class="readonly task-input ' + field.class + '"></input>';
			break;
		case 'text':
		case 'hidden':
		case 'password':
			str += '<input type="' + field.type + '" id="' + field.id + '" name="' + field.name + '" ' + field.disabled + ' placeholder="' + field.label + '" ' + field.maxlength + ' value="' + field.value + '" class="task-input ' + field.class + '" ' + field.readonly + ' ' + field.dataRole + '></input>';
			break;
		case 'textarea':
			str += '<textarea id="' + field.id + '" name="' + field.name + '" ' + field.disabled + ' placeholder="' + field.label + '" value="' + field.value + '" class="task-input ' + field.class + '" ' + field.readonly + '></textarea>';
			break;
		case 'dropdown':
			str += '<select type="dropdown" id="' + field.id + '" name="' + field.name + '" class="task-input ' + field.class + '">\
				<option value="">' + localization['select'] + '</option>\
			</select>';
			break;
		case 'multiselect':
			str += '<select type="multiselect" label="' + field.label + '" id="' + field.id + '" name="' + field.name + '[]" multiple="multiple" class="task-input ' + field.class + '">';
			loadFormData(field);
			str += '</select>';
			break;
		case 'checkbox':
			field.checked = (field.checked) ? 'checked="checked"' : '';
			field.disabled = (field.disabled) ? 'disabled="disabled"' : '';
			str += '<div class="checkbox checkbox-primary checkbox-inline ' + field.holder + '">\
				<input id="' + field.id + '" name="' + field.name + '" type="checkbox" class="' + field.class + '" ' + field.checked + ' ' + field.disabled + ' value="' + field.value + '">\
				<label for="' + field.id + '" class="">' + field.optional_label + '</label>\
			</div>';
			break;
		case 'radio':
			field.checked = (field.checked) ? 'checked="checked"' : '';
			field.disabled = (field.disabled) ? 'disabled="disabled"' : '';
			str += '<div class="radio radio-primary radio-inline ' + field.holder + '">\
				<input id="' + field.id + '" name="' + field.name + '" type="radio" class="' + field.class + '" ' + field.checked + ' ' + field.disabled + ' value="' + field.value + '">\
				<label for="' + field.id + '" class="">' + field.optional_label + '</label>\
			</div>';
			break;
		case 'file':
			str += '<span class="btn btn-success fileinput-button">\
				<i class="fa fa-plus"></i>\
				<span>' + localization['choose-file'] + '</span>\
				<input id="' + field.id + '" type="file" name="' + field.name + '" multiple>\
			</span>\
			<span class="file_format"></span>\
			<div class="progress">\
				<div class="progress-bar progress-bar-success"></div>\
			</div>\
			<div class="files"></div>';
			break;
		case 'toggle':
			str += '<div class="toggle toggle-select toggle-modern ' + field.id + ' ' + field.class + '" data-type="select"></div>';
			break;
		case 'ipbox':
			if(typeof field.value == 'string')
				field.value = field.value.split(".");
			for(i = 0; i < 4; i++) {
				value = (typeof field.value[i] === 'undefined') ? '' : field.value[i];
				str += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3 field-group">\
					<input type="text" id="' + field.id + '_' + i + '" name="' + field.name + '_' + i + '" value="' + value + '" ' + field.maxlength + ' class="task-input ip numeric ' + field.class + '" ' + field.readonly + ' />\
				</div>';
			}
			break;
		case 'range-picker':
			str += '<input id="' + field.name + '" name="' + field.name + '" type="hidden" value="' + field.value + '" class="range-slider task-input ' + field.class + '">';
			break;
		case 'group':
			$.each(field.fields, function(key, value) {
				str += loadFormField(value);
			});
			break;
	}
	return str;
}

/**
  * @desc this method will prepare the post data for an API(GetOptions) based on the dynamic form generated.
  * @param object $value - the options fetched from the server for the dynamic form fields.
  * @param string $execid - the unique identifier of the task.
  * @param boolean $isEventBound - a flag, indicates weather events(change/click) were already bound to the html dom or not.
  * @return object - post data object for the API.
*/
var seperator = "@", tmp = '';
function generateAPIargs(value, execid, isEventBound) {
	var data = {"keyvalues": []}, arg_value, field, ismapped;
        if(value.api.args) {
                $.each(value.api.args, function(x, arg) {
                        arg_value = '', ismapped = '0';
                        if(!arg.isdynamic) arg_value = arg.value;
                        else {
                                arg.value = arg.value.replace(".value", "");
                                var dom = $('[name="workflow_' + arg.value + '"], [name="workflow_' + arg.value + '[]"]');
                                if(dom.closest('.field-group').length) dom = dom.closest('.field-group');
                                else dom = dom.closest('.controls');

                                if(dom.find('.map-global-input').is(':checked')) {
					ismapped = '3';
					field = dom.find('.global-config-input');
				} else if(dom.find('.map-prev-api').is(':checked')) {
					ismapped = '1';
					field = dom.find('.prev-task-input');
                                } else field = dom.find('.task-input');

                                var field_type = field.attr('type');
				if(field_type == 'text' || field_type == 'dropdown' || field_type == 'multiselect-dropdown') {
					arg_value = (field.val() == null) ? '' : field.val();
                                } else if(field_type == 'radio-button')
                                        arg_value = $('input[name="workflow_' + arg.value + '"]:checked').val();
                                else if(field_type == 'checkbox') {
                                        arg_value = [];
                                        $('input[name="workflow_' + arg.value + '"]:checked').each(function() {
                                                arg_value.push(this.value);
                                        });
                                } else if(field_type == 'multi-select' || field_type == 'multi-select-text') {
                                        arg_value = [];
                                        $('#workflow_' + arg.value + '_input_list > li.active').each(function(index) {
                                                arg_value.push($(this).attr('primaryid'));
                                        });
                                } else if(field_type == 'multi-drag') {
                                        arg_value = [];
                                        $('#workflow_' + arg.value + '_selected_list > li:not(.header)').each(function(index) {
                                                arg_value.push($(this).attr('primaryid'));
                                        });
                                }
                                if(!isEventBound) {
					//AddEventListner('[execid="' + execid + '"]', '[name="workflow_' + arg.value + '"]', value, execid);
					AddEventListner('[execid="' + execid + '"]', '#workflow_' + arg.value, value, execid);
                                }
                        }
                        if(typeof arg_value == 'object') arg_value = JSON.stringify(arg_value);
                        data.keyvalues.push({"key": arg.field, "ismapped": ismapped, "value": arg_value});
                });
        }
        return data;
}

/**
  * @desc this method will bind the events with the html dom based on the server response.
  * @param object $parentDom - the parent element of the dom object where to bind the new event.
  * @param object $dom - the html dom object where to bind the event.
  * @param object $value - the options fetched from the server for the dynamic form fields.
  * @param string $execid - the unique identifier of the task.
*/
function AddEventListner(parentDom, dom, value, execid) {
	var event = 'change';
	if($(dom).attr('type') == 'checkbox' || $(dom).attr('type') == 'radio')
		event = 'click';
	var elements = parentDom + ' ' + dom;
	elements += ', ' + parentDom + ' ' + dom.replace('#workflow_', '#global_input_');
	elements += ', ' + parentDom + ' ' + dom.replace('#workflow_', '#prev_task_');
	$('#form-body').on(event, elements, function () {
		$(parentDom + ' .workflow-input-' + value.name).html('<div class="clear"></div>');
		if($(parentDom + ' .workflow-input-' + value.name).attr('type') == 'dropdown')
			$(parentDom + ' .workflow-input-' + value.name).html('<option value="">' + localization['select'] + ' ' + value.label + '</option>');
		else if($(parentDom + ' .workflow-input-' + value.name).attr('type') == 'range-picker')
			$(parentDom + ' .workflow-input-' + value.name).html('<input id="workflow_' + value.name + '" name="workflow_' + value.name + '" class="range-slider task-input" type="hidden" value="' + value.svalue + '">');
		populateFormData(value, execid, 1, 0);
		if($(parentDom + ' .workflow-input-' + value.name).attr('type') == 'multiselect-dropdown') {
			$(parentDom + ' .workflow-input-' + value.name).multiselect('reload');
		}
	});
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function populateFormData(value, execid, bind, flag) {
	var j, label;
	var selected, data = [];
	if(value.ismapped == '2') {
		$('[execid="' + execid + '"] .task-input.workflow-input-' + value.dfvalues[0].label).each(function() {
			if(this.value.length > 0)
				data.push({id: $(this).val(), label: $(this).val()});
		});
		getOptionsCallback(value, data, execid, bind, flag);
	} else if(value.isstatic) {
		data = value.dfvalues;
		getOptionsCallback(value, data, execid, bind, flag);
	} else if(value.iptype != 'label' && value.iptype != 'ipbox') {
		if(typeof value.api.name == 'string' && value.api.name.length > 0) {
			value.api.name = value.api.name.replace("()", "");
			var api = 'GetOptions', query = {operation: value.api.name}, args = {}, container = '.modal-inset';
			args = generateAPIargs(value, execid, bind);		
			if(execid == 'global-config') {
				api = 'GetGlobalOptions';
				container = '.global-configuration';
				query.ttype = value.api.tasktype;
			} else {
				query.jobid = $('.modal-body #form-body').attr('workflowJobId');
				query.execid = execid;
				if(value.iptype == 'group') query.isGroup = true;
				if(workflow_mode == 'Edit') query.ttype = 'workflow';
				else if(workflow_mode == 'Info') query.ttype = 'job';
			}
			doAjaxRequest({url: api, base_path: settings.base_path, method: 'POST', query: query, data: args, container: container}, function(response) {
				data = response.data;
				getOptionsCallback(value, data, execid, bind, flag);
			}, function() {
				removeProcessingSpinner(true);
			});
		} else {
			getOptionsCallback(value, data, execid, bind, flag);
		}
	} else if(flag) {
		counter++;
		if(execid == 'global-config')
			loadGlobalFormFields();
		else loadWorkflowFormFields();
	}
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function getOptionsCallback(value, data, execid, bind, flag) {
	var str = '', tmp;
	if(value.iptype == 'range-picker' || value.iptype == 'ip-range') {
		var slider = value.dfvalues[0], tmp;
		if(!value.isstatic && typeof value.api.name == 'string' && data.length > 0) {
			slider = $.extend({}, slider, JSON.parse(data[0].extrafields));
			tmp = data[0].selected.split("-");
			slider.from = tmp[0];
			slider.to = tmp[1];
		}
		var obj = {};
		if(typeof slider != 'undefined') {
			if(value.svalue != '') {
				tmp = value.svalue.split("-");
				slider.from = tmp[0];
				slider.to = tmp[1];
			}
			if(typeof slider.min_range != 'undefined') obj.min = parseInt(slider.min_range);
			if(typeof slider.max_range != 'undefined') obj.max = parseInt(slider.max_range);
			if(typeof slider.min_interval != 'undefined') obj.min_interval = (parseInt(slider.min_interval) - 1);
			if(typeof slider.max_interval != 'undefined') obj.max_interval = (parseInt(slider.max_interval) - 1);
			if(typeof slider.min_fixed != 'undefined') obj.from_fixed = slider.min_fixed;
			if(typeof slider.max_fixed != 'undefined') obj.to_fixed = slider.max_fixed;
			if(typeof slider.from != 'undefined') obj.from = slider.from;
			if(typeof slider.to != 'undefined') obj.to = slider.to;
		}

		initRangeSlider($('#workflow_' + value.name + '.range-slider'), obj);
		if(value.iptype == 'ip-range') {
			$('#workflow_' + value.name + '.range-slider').next('.legend').remove();
			$('#workflow_' + value.name + '.range-slider').after('<div class="legend">\
				<div class="pull-left">Range <span><span class="ip-subnet"></span><span class="start-range">' + slider.from + '</span></div>\
				<div class="pull-left"> - <span><span class="ip-subnet"></span></span><span class="end-range">' + slider.to + '</span></div>\
			</div>');
			$('#workflow_' + value.name + '.range-slider').on("change", function() {
				var from = $(this).data("from"), to = $(this).data("to");
				$(this).closest('.controls').find('.legend').find('.start-range').html(from);
				$(this).closest('.controls').find('.legend').find('.end-range').html(to);
			});
		}
	} else if(value.iptype == 'ip-picker') {
		
	} else if(value.iptype == 'multi-select' || value.iptype == 'multi-select-text')
		initMultiSelector(value, data);
	else if(value.iptype == 'multi-drag')
		initDragableSelector(value, data);
	else if(value.iptype == 'group' && value.api != 'None') {
		if(value.svalue != '') {
			if(typeof value.svalue == 'string')
				value.svalue = value.svalue.split("|");
			$.each(value.group_fields, function(index, val) {
				var exec_id = ($('.modal-body #form-body').attr('taskType') == 'wgroup') ? execid = value.execid : execid;
				populateFormData(val, exec_id, 0, 0);
			});

			$.each(value.svalue, function(index, val) {
				if(typeof val == 'string') val = $.parseJSON(val);
				j = index + 1;
				$.each(value.group_fields, function(i, field) {
					if(field.name in val) {
						if(typeof val[field.name].value == 'string') val[field.name].value = val[field.name].value.split("|");
						if(field.iptype == 'drop-down' || field.iptype == 'text-box')
							val[field.name].value = val[field.name].value[0];
						$('.control-group[argname="' + value.name + '"]').find('[argname="' + value.name + '"]').children('.group-row').eq(index).find('.field-group[argname="' + field.name + '"]').find('.task-input.workflow-input-' + field.name).val(val[field.name].value);
					}
				});
			});
		} else {
			if(data.length > 0)
				$('.control-group[argname="' + value.name + '"]').find('[argname="' + value.name + '"]').html('');

			$.each(data, function(index, val) {
				str = '<div class="group-row">\
					<div class="workflow-input-' + value.name + ' col-lg-11 col-md-11 col-sm-11 col-xs-11 task-input">';
						$.each(value.group_fields, function(i, arg) {
							tmp = (value.group_fields.length > 3) ? 'col-lg-3 col-md-3 col-sm-3 col-xs-3' : (value.group_fields.length == 3) ? 'col-lg-4 col-md-4 col-sm-4 col-xs-4' : 'col-lg-6 col-md-6 col-sm-6 col-xs-6';
							str += loadFields(arg, true, execid, tmp);
						});
					str += '</div>';
					if(value.addmore) {
						str += '<div class="col-lg-1 col-md-1 col-sm-1 col-xs-1 nopadding nomargin action-icons">\
							<i class="fa fa-plus-circle orange-text add-more-row" alt="' + localization['add-more'] + '" title="' + localization['add-more'] + '"></i>\
						</div>';
					}
					str += '<div class="clear"></div>\
				</div>';
				$('.control-group[argname="' + value.name + '"]').find('[argname="' + value.name + '"]').append(str);
				
				$.each(value.group_fields, function(i, arg) {
					if(arg.name in val)
						$('.control-group[argname="' + value.name + '"]').find('[argname="' + value.name + '"]').children().eq(index).find('.task-input.workflow-input-' + arg.name).val(val[arg.name]);
				});
			});
			$.each(value.group_fields, function(i, arg) {
				populateFormData(arg, execid, 0, 0);
			});
		}
	} else if(typeof value.api.name != 'undefined' && value.api.name.length > 0 && (value.iptype == 'label' || value.iptype == 'text-box')) {
		if(typeof data[0] != 'undefined' && typeof data[0]['id'] != 'undefined')
			$('#workflow_' + value.name).val(data[0]['id']);
	} else if(value.iptype != 'label' && value.iptype != 'text-box') {
		$.each(data, function(index, val) {
			selected = '';
			switch(value.iptype) {
				case 'drop-down':
				case 'multiselect-dropdown':
					if(value.svalue == '' && val.selected == '1') {
						value.svalue = val.id;
					}
					str += '<option value="' + val.id + '" ' + selected + '>' + val.label + '</option>';
					break;
				case 'radio-button':
					if(value.svalue != '') {
						if(value.svalue == val.id) selected = 'checked="checked"';
					} else if(val.selected == '1') selected = 'checked="checked"';
					str += '<div class="radio radio-info">\
						<input id="workflow_' + value.name + '_' + index + '" name="workflow_' + value.name + '" type="radio" ' + selected + ' class="workflows" value="' + val.id + '">\
						<label for="workflow_' + value.name + '_' + index + '" class="nopadding">' + val.label + '</label>\
					</div>';
					if(selected != '') {
						str += '<div class="optional_label">' + val.label + '</div>';
					}
					break;
				case 'check-box':
					if(value.svalue != '') {
						if(data.length == 1) {
							if(value.svalue == val.id.split(seperator)[0]) selected = 'checked="checked"';
						} else {
							if(typeof value.svalue == 'string' || typeof value.svalue == 'number') {
								if(value.svalue.indexOf("|") > -1) {
									if($.inArray(val.id, value.svalue.split("|")) > -1) selected = 'checked="checked"';
								} else
									if(val.id == value.svalue) selected = 'checked="checked"';
							} else if(typeof value.svalue == 'object') {
								if($.inArray(val.id, value.svalue) > -1) selected = 'checked="checked"';
							}
						}
					} else if(val.selected == '1') selected = 'checked="checked"';
					str += '<div class="checkbox checkbox-info">\
						<input id="workflow_' + value.name + '_' + index + '" name="workflow_' + value.name + '" type="checkbox" ' + selected + ' class="workflows" value="' + val.id + '">\
						<label for="workflow_' + value.name + '_' + index + '" class="nopadding">' + val.label + '</label>\
					</div>';
					if(selected != '') {
						str += '<div class="optional_label">' + val.label + '</div>';
					}
					break;
			}
		});
		$('[execid="' + execid + '"] .workflow-input-' + value.name).append(str);
		if(value.iptype == 'multiselect-dropdown' || value.iptype == 'drop-down') {
			$('[execid="' + execid + '"] #workflow_' + value.name).each(function() {
				tmp = $(this).attr('value');
				if(tmp.indexOf(",") >= 0 && value.iptype == 'multiselect-dropdown') tmp = tmp.split(",");
				$(this).val(tmp);
			});
			$('[execid="' + execid + '"] .workflow-input-' + value.name).multiselect('reload');
		}
	}
	if(value.ismapped == '2' && !bind)
		AddEventListner('div.control-group[execid="' + execid + '"]', '.task-input.workflow-input-' + value.dfvalues[0].label, value, execid);
	if(flag) {
		counter++;
		if(execid == 'global-config')
			loadGlobalFormFields();
		else loadWorkflowFormFields();
	}
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @return string - .
*/
function loadPrevTaskTemplate(args, execid) {
	var str = '';
	if(jobTasks.indexOf(execid) > 0) {
		tabIndex++;
		if(typeof args.allow_multiple_values != 'undefined' && args.allow_multiple_values)
			str += '<select type="multiselect-dropdown" id="prev_task_' + args.name + '" name="prev_task_' + args.name + '[]" tabindex="' + tabIndex + '" multiple="multiple" class="prev-task-input hide">';
		else str += '<select type="dropdown" id="prev_task_' + args.name + '" name="prev_task_' + args.name + '" tabindex="' + tabIndex + '" class="prev-task-input hide">';
			str += '<option value="">' + localization['select'] + '</option>\
		</select>';
	}
	return str;
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @return string - .
*/
function loadGlobalInputTemplate(args) {
	tabIndex++;
	var str = '<select type="dropdown" id="global_input_' + args.name + '" name="global_input_' + args.name + '" tabindex="' + tabIndex + '" class="global-config-input hide">';
		str += '<option value="">' + localization['select'] + '</option>\
	</select>';
	return str;
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function workflowInputBasicTemplate(container, args, execid, mode) {
	var str = '', tmp;
	if(args.iptype == 'group') {
		str += '<table>\
			<tr>';
			$.each(args.group_fields, function(index, value) {
				str += '<th class="title">' + value.label + '</th>';
			});
			str += '</tr>';
				if(args.svalue == '' || args.svalue.length == 0) {
					str += '<tr>';
					$.each(args.group_fields, function(index, value) {
						str += '<td class="title">' + loadFields(value, true, execid, '', mode) + '</td>';
					});
					str += '</tr>';
				} else {
					if(typeof args.svalue == 'string')
						args.svalue = args.svalue.split("|");
					$.each(args.svalue, function(index, val) {
						str += '<tr>';
						if(typeof val == 'string') val = $.parseJSON(val);
						$.each(args.group_fields, function(i, value) {
							tmp = '';
							if(value.name in val) {
								value.svalue = val[value.name].value;
								value.ismapped = val[value.name].ismapped;
								tmp = loadFields(value, true, execid, '', mode);
							}
							str += '<td class="title">' + tmp + '</td>';
						});
						str += '</tr>';
					});
				}
			str += '</tr>\
		</table>';
	} else {
		if(args.ismapped == "3") {
			str += (typeof global_inputs[args.svalue] === 'undefined') ? '' : global_inputs[args.svalue].value;
		} else if(args.ismapped == "1") {
			tmp = args.svalue.replace("__", "").split(".");
			tmp = $(container + ' tr[execid="' + tmp[0] + '"] td[field="' + tmp[tmp.length - 1] + '"]').html();
			str += (typeof tmp === 'undefined') ? args.svalue : tmp;
		} else {
			if(typeof args.svalue == 'object') {
				$.each(args.svalue, function(index, val) {
					str += val + "<br>";
				});
			} else {
				args.svalue = args.svalue.replace(/@/g, "<br>");
				str += args.svalue.replace(/\|/g, "<br>");
			}
			if(args.val_prefix) str = args.val_prefix + '' + str;
			if(args.val_suffix) str += args.val_suffix;
		}
	}
	return str;
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function loadFields(args, isGroup, execid, width, mode) {
	var str = '', obj = {}, tmp;
	args.additional = '';
	if(args.reset) args.additional += ' reset';
	if(args.prefix || args.val_prefix) args.additional += ' prefix';
	if(args.suffix || args.val_suffix) args.additional += ' suffix';
	if(args.iptype == 'ipbox') args.additional += ' ipaddress';
	if(args.iptype != 'group') {
		args.label = args.label.replace(/(<([^>]+)>)/ig, "");
	}

	if(isGroup) width += ' field-group';
	if(mode == 'readonly') {
		str += workflowInputBasicTemplate('.configurations', args, execid, mode);
	} else {
		switch(args.iptype) {
			case 'label':
			case 'text-box':
			case 'ipbox':
				var tmp = (args.iptype == 'label') ? 'disabled' : '';
				args.maxlength = (typeof args.maxlength != 'undefined') ? args.maxlength : 100;
				str += '<div class="' + width + '" argname="' + args.name + '">';
					if(args.additional.indexOf('prefix') > -1) str += '<span class="prefix">' + (args.prefix || args.val_prefix) + '</span>';
					str += '<input type="text" id="workflow_' + args.name + '" name="workflow_' + args.name + '" tabindex="' + tabIndex + '" ' + tmp + ' placeholder="' + args.label + '" value="' + args.svalue + '" autocomplete="off" class="task-input workflow-input-' + args.name + ' ' + args.additional + '" maxlength="' + args.maxlength + '"></input>';
					if(args.additional.indexOf('reset') > -1) str += '<i class="fa fa-recycle regenerate" alt="Regenerate" title="Regenerate"></i>';
					if(args.additional.indexOf('suffix') > -1) str += '<span class="suffix">' + (args.suffix || args.val_suffix) + '</span>';
				break;
			case 'drop-down':
				str += '<div class="' + width + '" argname="' + args.name + '">\
					<select type="dropdown" id="workflow_' + args.name + '" name="workflow_' + args.name + '" value="' + args.svalue + '" tabindex="' + tabIndex + '" class="task-input workflow-input-' + args.name + '">\
						<option value="">' + localization['select'] + ' ' + args.label + '</option>\
					</select>';
				break;
			case 'ipbox1':
				if(typeof args.svalue == 'string')
					args.svalue = args.svalue.split(".");
				for(i = 0; i < 4; i++) {
					value = (typeof args.svalue[i] === 'undefined') ? '' : args.svalue[i];
					str += '<div class="col-lg-3 col-md-3 col-sm-3 col-xs-3 field-group">\
						<input type="text" id="workflow_' + args.name + '_' + i + '" name="workflow_' + args.name + '_' + i + '" tabindex="' + tabIndex + '" value="' + value + '"  class="task-input ip numeric workflow-input-' + args.name + '" maxlength="3" />\
					</div>';
				}
				break;
			case 'multiselect-dropdown':
				str += '<div class="' + width + '" argname="' + args.name + '">\
					<select type="multiselect-dropdown" value="' + args.svalue + '" label="' + args.label + '" id="workflow_' + args.name + '" name="workflow_' + args.name + '[]" tabindex="' + tabIndex + '" multiple="multiple" class="task-input workflow-input-' + args.name + '"></select>';
				break;
			case 'ip-picker':
				str += '<div class="' + width + '" argname="' + args.name + '">\
					<div class="task-input workflow-input-' + args.name + '" type="ip-picker">\
						<input id="workflow_' + args.name + '" name="workflow_' + args.name + '" class="ip-picker task-input" type="hidden" value="' + args.svalue + '">\
					</div>';
				break;
				break;
			case 'range-picker':
			case 'ip-range':
				str += '<div class="' + width + '" argname="' + args.name + '">\
					<div class="task-input workflow-input-' + args.name + '" type="range-picker">\
						<input id="workflow_' + args.name + '" name="workflow_' + args.name + '" class="range-slider task-input" type="hidden" value="' + args.svalue + '">\
					</div>';
				break;
			case 'group':
				str += '<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12" argname="' + args.name + '">';
					str += '<div class="col-lg-11 col-md-11 col-sm-11 col-xs-11 nopadding group-header">';
					$.each(args.group_fields, function(index, value) {
						tmp = (args.group_fields.length > 3) ? 'col-lg-3 col-md-3 col-sm-3 col-xs-3' : (args.group_fields.length == 3) ? 'col-lg-4 col-md-4 col-sm-4 col-xs-4' : 'col-lg-6 col-md-6 col-sm-6 col-xs-6';
						str += '<div class="noleftpadding borderbottom title bold ' + tmp + '">' + value.label + '</div>';
					});
					str += '</div>\
					<div class="clear"></div>';
					if(args.svalue == '' || args.svalue.length == 0) {
						str += '<div class="group-row">\
							<div class="workflow-input-' + args.name + ' col-lg-11 col-md-11 col-sm-11 col-xs-11 task-input">';
								$.each(args.group_fields, function(index, value) {
									tmp = (args.group_fields.length > 3) ? 'col-lg-3 col-md-3 col-sm-3 col-xs-3' : (args.group_fields.length == 3) ? 'col-lg-4 col-md-4 col-sm-4 col-xs-4' : 'col-lg-6 col-md-6 col-sm-6 col-xs-6';
									str += loadFields(value, true, execid, tmp, mode);
								});
								str += '<div class="clear"></div>\
								<div class="help-block"></div>\
							</div>';
							if(args.addmore) {
								str += '<div class="col-lg-1 col-md-1 col-sm-1 col-xs-1 nopadding nomargin action-icons">\
									<i class="fa fa-plus-circle orange-text add-more-row" alt="' + localization['add-more'] + '" title="' + localization['add-more'] + '"></i>\
								</div>';
							}
							str += '<div class="clear"></div>\
						</div>';
					} else {
						if(typeof args.svalue == 'string')
							args.svalue = args.svalue.split("|");
						$.each(args.svalue, function(index, val) {
							if(typeof val == 'string') val = $.parseJSON(val);
							str += '<div class="group-row">\
								<div class="workflow-input-' + args.name + ' col-lg-11 col-md-11 col-sm-11 col-xs-11 task-input">';
									$.each(args.group_fields, function(i, value) {
										if(value.name in val) {
											obj = {};
											obj.api = value.api;
											obj.dfvalues = value.dfvalues;
											obj.iptype = value.iptype;
											obj.isstatic = value.isstatic;
											obj.ismapped = value.ismapped;
											obj.label = value.label;
											obj.name = value.name;
											obj.svalue = val[value.name].value;
											tmp = (args.group_fields.length > 3) ? 'col-lg-3 col-md-3 col-sm-3 col-xs-3' : (args.group_fields.length == 3) ? 'col-lg-4 col-md-4 col-sm-4 col-xs-4' : 'col-lg-6 col-md-6 col-sm-6 col-xs-6';
											str += loadFields(obj, true, execid, tmp, mode);
										}
									});
									str += '<div class="clear"></div>\
								</div>';
								if(args.addmore) {
									str += '<div class="col-lg-1 col-md-1 col-sm-1 col-xs-1 nopadding nomargin action-icons">';
										if(index > 0)
											str += '<i class="fa fa-minus-circle orange-text remove-row" alt="' + localization['remove'] + '" title="' + localization['remove'] + '"></i>';
										if(index == parseInt(args.svalue.length - 1))
											str += '<i class="fa fa-plus-circle orange-text add-more-row" alt="' + localization['add-more'] + '" title="' + localization['add-more'] + '"></i>';
									str += '</div>';
								}
								str += '<div class="clear"></div>\
							</div>';
						});
					}
				str += '</div>';
				break;
			default:
				str += '<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12" argname="' + args.name + '">\
					<div type="' + args.iptype  + '" class="workflow-input-' + args.name + ' col-lg-12 col-md-12 col-sm-12 col-xs-12 task-input">\
						<div class="clear"></div>\
					</div>';
				break;
		}
		if(args.iptype != 'group' && args.iptype != 'label' && execid != 'global-config') {
			str += loadPrevTaskTemplate(args, execid);
			str += loadGlobalInputTemplate(args, execid);
			str += loadTaskFormInputOptions(args, isGroup, execid);
		}
			str += '<div class="clear"></div>\
			<div class="help-block"></div>\
		</div>';
	}
	return str;
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function loadTaskFormInputOptions(args, isGroup, execid) {
	tabIndex++;
	var gchkbox_label = 'map_global_';
	if(isGroup) {
		gchkbox_label = 'map_global_' + group_row_count + '_';
	}

	var str = '<div class="clear"></div>';
	str += '<div class="group-input pull-left">\
		<div class="checkbox checkbox-info">\
			<input type="checkbox" id="' + gchkbox_label + args.name + '" name="' + gchkbox_label + args.name + '" tabindex="' + tabIndex + '" class="map-global-input">\
			<label for="' + gchkbox_label + args.name + '"><div class="small title previous-task-label">' + localization['map-global'] + '</div></label>\
		</div>\
	</div>\
	<input id="ismapped_' + args.name + '" class="task_ismapped" value="' + args.ismapped + '" type="hidden">';
	if($('#form-body').attr('tasktype') != 'wgroup' && jobTasks.indexOf(execid) > 0) {
		var chkbox_label = 'prev_api_';
		if(isGroup) {
			chkbox_label = 'prev_api_' + group_row_count + '_';
		}
		str += '<div class="group-input pull-left">\
			<div class="checkbox checkbox-info">\
				<input type="checkbox" id="' + chkbox_label + args.name + '" name="' + chkbox_label + args.name + '" tabindex="' + tabIndex + '" class="map-prev-api">\
				<label for="' + chkbox_label + args.name + '"><div class="small title previous-task-label">' + localization['map-prev-output'] + '</div></label>\
			</div>\
		</div>';
	}
	group_row_count++;
	return str;
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
var tmpStr;
function loadWorkflowInputForm(args, execid, type) {
	type = (typeof type == 'undefined') ? 'row' : type;
	var str = '', obj = {}, isHidden, additional, width = (execid == 'global-config') ? 'col-lg-5 col-md-5 col-sm-5 col-xs-5' : 'col-lg-3 col-md-3 col-sm-3 col-xs-3',
	width1 = (execid == 'global-config') ? 'col-lg-7 col-md-7 col-sm-7 col-xs-7' : 'col-lg-9 col-md-9 col-sm-9 col-xs-9 nopadding',
	width2 = (execid == 'global-config') ? '' : 'col-lg-8 col-md-9 col-sm-12 col-xs-12';
	args.execid = (typeof args.execid == 'undefined') ? execid : args.execid;
	args.mandatory = (typeof args.mandatory == 'undefined') ? '' : 'required';

	if($('#form-body').attr('tasktype') == 'wgroup' && tmpStr != args.execid && args.execid != '') {
		if(tmpStr != '') str += '</table></fieldset>';
		str += '<fieldset><legend>' + args.desc + '</legend>\
		<table>';
		tmpStr = args.execid;
	}
	if(tmpStr == '') {
		str = '<table>';
	}
	isHidden = (args.hidden) ? 'hide' : '';
	additional = (args.additional) ? args.additional : '';
	if(type == 'row') {
		str += '<tr class="' + isHidden + '" execid="' + args.execid + '">\
			<td class="title col-lg-3 col-md-3 col-sm-3 col-xs-3">' + args.label + ':</td>\
			<td class="title col-lg-9 col-md-9 col-sm-9 col-xs-9" field="' + args.name + '">' + loadFields(args, false, execid, 'col-lg-8 col-md-9 col-sm-12 col-xs-12', 'readonly') + '</td>\
		</tr>';
	} else if(!args.hidden)
		str += '<td class="title">' + loadFields(args, false, execid, 'col-lg-8 col-md-9 col-sm-12 col-xs-12', 'readonly') + '</td>';
	obj.basic = str;
	if($('#form-body').attr('tasktype') != 'wgroup') {
		str = '<div class="control-group ' + args.name + ' ' + isHidden + ' ' + additional + '" argname="' + args.name + '" argtype="' + args.iptype + '" execid="' + args.execid + '">\
			<label class="title ' + width + '">\
				<span class="' + args.mandatory + '">' + args.label + ': ';
				if(typeof args.helptext != 'undefined')
					str += '<i class="fa fa-question-circle help-txt tipso tipso_style" data-tipso-title="' + args.label + '" data-tipso="' + args.helptext + '" data-html="true" data-toggle="tooltip"></i>';
				str += '</span>\
			</label>\
			<div class="controls ' + width1 + '">';
				str += loadFields(args, false, execid, width2, 'editable');
				str += '<div class="clear"></div>\
			</div>\
			<div class="clear"></div>\
		</div>';
		obj.advanced = str;
	}
	return obj;
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function initMultiSelector(value, data) {
	try {
		var str = '<div class="scroller nopadding col-lg-12 col-md-12 col-sm-12 col-xs-12">\
			<ul id="workflow_' + value.name + '_input_list" name="workflow_' + value.name + '" class="multi-select" type="' + value.iptype + '">\
				<li class="ui-state-default header ui-state-disabled">\
					<span class="">' + localization['select-avail-list'] + '</span>\
				</li>\
			</ul>\
		</div>';
		$('.workflow-input-' + value.name).prepend(str);
		$('.workflow-input-' + value.name + ' .scroller').css('height', 'auto').css('min-height', '80px').css('max-height', '200px');
		initScroller($('.workflow-input-' + value.name + ' .scroller'));

		var selected = '';
		$.each(data, function(x, val) {
			selected = '';
			if(val.selected == '1' && !value.svalue) selected = 'active';
			str = '<li class="ui-state-default primaryid_' + val["id"].replace(/\//g, '--') + ' ' + selected + '" primaryId="' + val["id"] + '" alt="' + val["label"] + '" title="' + val["label"] + '">';
				str += '<i class="pull-left fa fa-check"></i>';
				str += '<span class="hide">' + val["id"] + '</span>';
				str += '<span>' + val["label"] + '</span>';
				if(value.iptype == 'multi-select-text')
					str += '<span class="pull-right"><input type="text" id="workflow_' + value.name + '_text" class="" value="' + val["id"] + '"></input></span>';
			str += '</li>';
			$('#workflow_' + value.name + '_input_list').append(str);
		});
		if(value.svalue) {
			switch(typeof value.svalue) {
				case 'string':
				case 'number':
					if(value.svalue.indexOf("|") > -1) {
						makeSValueActive(value.svalue.split("|"), value.name, value.iptype);
					} else {
						$('#workflow_' + value.name + '_input_list > li[primaryid="' + value.svalue + '"]').addClass('active');
					}
					break;
				case 'object':
					makeSValueActive(value.svalue, value.name, value.iptype);
					break;
			}
		}
	} catch(err) {
		loadWorkflowFormFields();
	}
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function makeSValueActive(value, arg_name, type) {
	$.each(value, function(index, obj) {
		var cond = '';
		if(typeof obj == 'object') {
			if(type == 'multi-select' || type == 'multi-select-text') {
				$('#workflow_' + arg_name + '_input_list > li.primaryid_' + obj.key.replace(/\//g, '--')).addClass('active');
			} else 
				$('#workflow_' + arg_name + '_input_list > li.primaryid_' + obj.key.replace(/\//g, '--')).appendTo('#workflow_' + arg_name + '_selected_list');
		} else {
			if(type == 'multi-select' || type == 'multi-select-text')
				$('#workflow_' + arg_name + '_input_list > li.primaryid_' + obj.replace(/\//g, '--')).addClass('active');
			else
				$('#workflow_' + arg_name + '_input_list > li.primaryid_' + obj.replace(/\//g, '--')).appendTo('#workflow_' + arg_name + '_selected_list');
		}
	});
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function initDragableSelector(value, data) {
	var str = '<div class="scroller nopadding col-lg-6 col-md-6 col-sm-6 col-xs-6">\
		<ul id="workflow_' + value.name + '_input_list" class="draggable">\
			<li class="ui-state-default header ui-state-disabled">\
				<span class="">' + localization['select-avail-list'] + '</span>\
			</li>\
		</ul>\
	</div>\
	<div class="scroller nopadding col-lg-6 col-md-6 col-sm-6 col-xs-6">\
		<ul id="workflow_' + value.name + '_selected_list" name="workflow_' + value.name + '" type="multi-drag" class="draggable">\
			<li class="ui-state-default header ui-state-disabled">\
				<span class="">' + localization['selected-list'] + '</span>\
			</li>\
		</ul>\
	</div>';
	$('.workflow-input-' + value.name).prepend(str);
	$('.workflow-input-' + value.name + ' .scroller').css('height', 'auto').css('min-height', '80px').css('max-height', '200px');
	initScroller($('.workflow-input-' + value.name + ' .scroller'));
	$('#workflow_' + value.name + '_input_list, #workflow_' + value.name + '_selected_list').sortable({
		connectWith: ".draggable",
		placeholder: "ui-state-highlight",
		items: "li:not(.ui-state-disabled)"
	}).disableSelection();

	$.each(data, function(x, val) {
		if(val.selected == '1' && !value.svalue)
			$('#workflow_' + value.name + '_selected_list').append('<li class="ui-state-default primaryid_' + val["id"].replace(/\//g, '--') + '" primaryId="' + val["id"] + '" alt="' + val["label"] + '" title="' + val["label"] + '"><span>' + val["id"] + '</span><span>' + val["label"] + '</span></li>');
		else
			$('#workflow_' + value.name + '_input_list').append('<li class="ui-state-default primaryid_' + val["id"].replace(/\//g, '--') + '" primaryId="' + val["id"] + '" alt="' + val["label"] + '" title="' + val["label"] + '"><span>' + val["id"] + '</span><span>' + val["label"] + '</span></li>');
	});

	if(value.svalue) {
		switch(typeof value.svalue) {
			case 'string':
			case 'number':
				if(value.svalue.indexOf("|") > -1) {
					makeSValueActive(value.svalue.split("|"), value.name, 'drag-select');
				} else {
					$('#workflow_' + value.name + '_input_list > li.primaryid_' + value.svalue.replace(/\//g, '--')).appendTo('#workflow_' + value.name + '_selected_list');
				}
				break;
			case 'object':
				makeSValueActive(value.svalue, value.name, 'drag-select');
				break;
		}
	}
}

/**
  * @desc .
  * @param array $array - .
  * @param string $field - .
  * @param array $array - .
  * @param string $field - .
*/
function getFormData(selector) {
	var task_input = {}, task_input_api = {}, tmp, obj;
	var value, ismapped, execid, arg_name;
	$(selector).each(function(index) {
		value = ''; ismapped = "0";
		execid = $(this).attr('execid');
		arg_name = 'workflow_' + $(this).attr('argname');
		if($(this).attr('argtype') == 'group') {
			tmp = [];
			$(this).find('div[argname="' + $(this).attr('argname') + '"]').find('.group-row').each(function(i) {
				obj = {};
				$(this).find('.field-group').each(function(i) {
					if($(this).find('.map-prev-api').is(':checked'))
						obj[$(this).attr('argname')] = {'ismapped': "1", 'value': $(this).find('.prev-task-input').val()};
					else if($(this).find('.map-global-input').is(':checked'))
						obj[$(this).attr('argname')] = {'ismapped': "3", 'value': $(this).find('.global-config-input').val()};
					else {
						ismapped = ($(this).find('.task_ismapped').length == 0) ? "0" : ($(this).find('.task_ismapped').val() == '') ? '0' : $(this).find('.task_ismapped').val();
                                                value = '';
                                                if($(this).find('.task-input').attr('type') == 'multiselect-dropdown') {
                                                        value = $(this).find('.task-input').val();
                                                        if($(this).find('.task-input').val() != null) {
                                                                if($(this).find('.task-input').val().length > 1) value = $(this).find('.task-input').val();
                                                                else value = $(this).find('.task-input').val()[0];
                                                        } else value = "";
                                                } else {
                                                        value = (typeof $(this).find('.task-input').val() != 'undefined' && $(this).find('.task-input').val() != null) ? $(this).find('.task-input').val() : '';
                                                }
                                                obj[$(this).attr('argname')] = {'ismapped': ismapped, 'value': value};
                                        }
				});
				tmp.push(obj);
			});
			ismapped = "0";
			value = tmp;
		} else {
			if($('#prev_api_' + $(this).attr('argname')).length && $('#prev_api_' + $(this).attr('argname')).is(':checked')) {
				value = $('#prev_task_' + $(this).attr('argname')).val();
				if($('#prev_task_' + $(this).attr('argname')).val() != null) {
					if($('#prev_task_' + $(this).attr('argname')).val().length > 1) value = $('#prev_task_' + $(this).attr('argname')).val();
					else value = $('#prev_task_' + $(this).attr('argname')).val()[0];
				}
				task_input['prev_task_' + $(this).attr('argname')] = true;
				ismapped = "1";
			} else if($('#map_global_' + $(this).attr('argname')).length && $('#map_global_' + $(this).attr('argname')).is(':checked')) {
				value = $('#global_input_' + $(this).attr('argname')).val();
				task_input['global_input_' + $(this).attr('argname')] = true;
				ismapped = "3";
			} else {
				if($('[name="' + arg_name + '[]"]').attr('type') == 'multiselect-dropdown') {
					value = $('#workflow_' + $(this).attr('argname')).val();
					if($('#workflow_' + $(this).attr('argname')).val() != null) {
						if($('#workflow_' + $(this).attr('argname')).val().length > 1) value = $('#workflow_' + $(this).attr('argname')).val();
						else value = $('#workflow_' + $(this).attr('argname')).val()[0];
					}
				} else if($(this).attr('argtype') == 'ipbox') {
					value = ($('[name="' + arg_name + '_0"]').val() == '') ? '' : $('[name="' + arg_name + '_0"]').val() + '.' + $('[name="' + arg_name + '_1"]').val() + '.' + $('[name="' + arg_name + '_2"]').val() + '.' + $('[name="' + arg_name + '_3"]').val();
				} else if($('[name="' + arg_name + '"]').attr('type') == 'text') {
					value = (typeof $('[name="' + arg_name + '"]').val() != 'undefined' && $('[name="' + arg_name + '"]').val() != null) ? $('[name="' + arg_name + '"]').val() : '';
					if($('[name="' + arg_name + '"].prefix').length) {
						value = $('[name="' + arg_name + '"].prefix').parent().find('span.prefix').text() + value;
					}
					if($('[name="' + arg_name + '"].suffix').length) {
						value += $('[name="' + arg_name + '"].suffix').parent().find('span.suffix').text()
					}
				} else if($('[name="' + arg_name + '"]').attr('type') == 'hidden' || $('[name="' + arg_name + '"]').attr('type') == 'dropdown') {
					value = (typeof $('[name="' + arg_name + '"]').val() != 'undefined' && $('[name="' + arg_name + '"]').val() != null) ? $('[name="' + arg_name + '"]').val() : '';
				} else if($('[name="' + arg_name + '"]').attr('type') == 'radio') {
					value = $('input[name="' + arg_name + '"]:checked').val();
				} else if($('[name="' + arg_name + '"]').attr('type') == 'checkbox') {
					value = '';
					if($('input[name="' + arg_name + '"]').length == 1) {
						if($('input[name="' + arg_name + '"]').is(':checked')) value = $('input[name="' + arg_name + '"]').val().split(seperator)[0];
						else if(typeof $('input[name="' + arg_name + '"]').val().split(seperator)[1] != 'undefined') value = $('input[name="' + arg_name + '"]').val().split(seperator)[1];
					} else {
						var array = [];
						$('input[name="' + arg_name + '"]:checked').each(function() {
							array.push(this.value);
						});
						value = array;
					}
				} else if($('[name="' + arg_name + '"]').attr('type') == 'multi-drag') {
					var array = [];
					$('#' + arg_name + '_selected_list > li:not(.header)').each(function(index) {
						array.push($(this).attr('primaryid'));
					});
					value = array;
				} else if($('[name="' + arg_name + '"]').attr('type') == 'multi-select') {
					var array = [];
					$('#' + arg_name + '_input_list > li.active').each(function(index) {
						array.push($(this).attr('primaryid'));
					});
					value = array;
				} else if($('[name="' + arg_name + '"]').attr('type') == 'multi-select-text') {
					var array = [];
					$('#' + arg_name + '_input_list > li.active').each(function(index) {
						array.push({'id': $(this).attr('primaryid'), 'value': $(this).find('input[type="text"]').val()});
					});
					value = array;
				}
			}
		}
		value = (typeof value == 'undefined') ? '' : value;
		task_input_api[$(this).attr('argname')] = {"ismapped": ismapped, "values": value};
		if(execid != '') task_input_api[$(this).attr('argname')].execid = execid;
	});
	return {form_data: task_input, task_input_api: task_input_api};
}

function loadFormData(field) {
	
}

/**
  * @desc it will open the model popup with content & button passed as args.
  * @param object $options - args contains popup title, body, size & button list.
*/
function openModel(options) {
	var defaults = {
		size: '',
		title: localization['confirmation'],
		body: '',
		buttons: {
			No: closeModel
		}
	};
	options = $.extend({}, defaults, options);
	
	$('.ajax-overlay, .ajax-spinner').remove();
	$("#submitBtn").removeAttr("disabled");
	$('.form-footer, .help-block').html('');
	$('.closeModel, .form-footer').show();
	if($('#form-body .mCSB_container').length)
		$('#form-body').mCustomScrollbar("destroy");
	
	$('.modal-inset').removeClass('big').addClass(options.size);
	$('.modal-head .widget-title').html(options.title);
	$('.modal-body #form-body').html(options.body);
	var str = '';
	Object.keys(options.buttons).some(function(key) {
		$('.form-footer').append('<div class="pull-left">\
			<button type="button" id="' + key + 'Btn">' + localization[key] + '</button>\
		</div>');
		$('.form-footer #' + key + 'Btn').click(function(e) {
			e.stopPropagation();
			$(this).attr('disabled', 'disabled');
			setTimeout(function() {$('.form-footer #' + key + 'Btn').removeAttr('disabled').prop("disabled", false);}, 1000);
			options.buttons[key]();
		});
	});
	
	$('.form-footer > div:not(:first-child)').addClass('pull-right');
	$('.form-footer > div:not(:first-child)').find('button').addClass('primary');
	$('.modal-overlay').addClass('state-show');
	$('.modal-frame').removeClass('state-leave bounceOutUp bounceOutDown').addClass('state-appear animated bounceInDown');
	var height = parseInt($(document).height()) - 300;
	//if(options.size == 'big') height += 100;
	$('#form-body').css('min-height', '50px').css('height', 'auto').css('max-height', height + 'px');
	initScroller($('#form-body'));
}

/**
  * @desc it will close/hide the model popup and clear its content.
*/
function closeModel() {
	$('.modal-overlay').removeClass('state-show');
	$('.modal-frame').removeClass('bounceInDown').addClass('bounceOutUp');
	$('.modal-body .addition-info').remove();
	setTimeout(function() {
		$('.modal-frame').removeClass('state-appear').addClass('state-leave');
		$('.modal-body.widget-content').removeClass('nopadding');
		$('.modal-body #form-body .mCSB_container').html('');
		$('.modal-body #form-body').off('change click');
	}, 500);
}
