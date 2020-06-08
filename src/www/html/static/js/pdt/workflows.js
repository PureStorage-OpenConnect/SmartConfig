var jobTasks, tabIndex = 10, workflowTasks = [], overallflag = true, workflow_mode = 'Info', global_inputs = {};
var mimeType = {'xml': 'text/xml', 'zip': 'application/zip, application/octet-stream'};
$(document).ready(function() {
	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('.content-container').delegate('#all-workflow', 'click', function(e) {
		$('.workflowinfo.elementInfo .workflows').prop('checked', false);
		$('.workflowinfo.elementInfo').removeClass('active');
		if(this.checked) {
			$('.workflowinfo.elementInfo .workflows').prop('checked', true);
			$('.workflowinfo.elementInfo').addClass('active');
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('.content-container').delegate('.workflowinfo.elementInfo', 'click', function(e) {
		if($(this).find('.workflows').is(':checked')) {
			$(this).find('.workflows').prop('checked', false);
			$(this).removeClass('active');
		} else {
			$(this).find('.workflows').prop('checked', true);
			$(this).addClass('active');
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('.content-container').delegate('.workflowinfo.elementInfo .workflows', 'click', function(e) {
		e.stopPropagation();
		$(this).closest('.workflowinfo').removeClass('active');
		if(this.checked) {
			$(this).closest('.workflowinfo').addClass('active');
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.execute-workflow', 'click', function(e) {
		$(this).removeClass('fa-play execute-workflow').addClass('fa-spinner faa-spin animated');
		var wid = $(this).closest('.workflowinfo.elementInfo').attr('primaryid');
		executeJob(wid);
		return false;
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.modify-workflow, .info-workflow, .completed-workflow', 'click', function(e) {
		e.stopPropagation();
		if(systemInfo.deployment_type == 'advanced') {
			var obj = $(this).closest('.workflowinfo');
			$('.buttonCustom.close-workflow').remove();
			$('.buttonFinish').after('<a href="javascript:;" class="buttonCustom close-workflow" style="display: inline-block;">' + localization['back'] + '</a>');
			if(obj.hasClass('ROLLBACK') || obj.hasClass('ROLLBACK_COMPLETED') || obj.hasClass('ROLLBACK_FAILED')) {
				toggleWorkflows();
				var query = {jobid: obj.attr('jobid')};
				initScroller($('.workflow-log'));
				var height = parseInt($('.workflow-container .workshop').height()) - 75;
				$('.workflow-log').css('height', height + 'px').css('max-height', height + 'px');
				$(".workflow-log .mCSB_container").html('');
				$('.workflow-container>.widget-header>.info>.workflow-title').html(localization['revert'] + ' - ' + obj.find('.workflow-name').text());
				$(".workflow-log .mCSB_container").html('<div class="no-logs"><h5>' + localization['no-logs'] + '<h5></div>\n\n');
				$('.gridview').removeClass('active');
				loadServiceRequestInfo(query);
			} else {
				$('.gridview').addClass('active');
				if(obj.hasClass('EXECUTING') && (obj.attr('jobid') == "None" || obj.attr('jobid') == "")) {
					$('.buttonCustom.close-workflow').remove();
				} else {
					prepareJob($(this).closest('.workflowinfo.elementInfo').attr('primaryid'));
					toggleWorkflows();
				}
			}
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.close-workflow', 'click', function(e) {
		$('.reset-workshop').trigger('click');
		$('.buttonCustom.close-workflow').remove();
		$('.buttonFinish, .buttonPrevious').removeClass('hide');
		$('.workflow-container .gridview .workflow-info').html('');
		getBatchStatus(true);
		toggleWorkflows();
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.back-workflow', 'click', function(e) {
		$('.buttonCustom.back-workflow').remove();
		toggleWorkflowRollback();
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.download-log', 'click', function(e) {
		downloadInnerHtml('eventlog.log', $(this).closest('.log-container, .workflow-log-container').find('.workflow-log').find('.mCSB_container'), 'text/html');
	});
	
	$('body').delegate('ul.multi-select > li:not(.header)', 'click', function(e) {
		if($(this).hasClass('active'))
			$(this).removeClass('active');
		else $(this).addClass('active');
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('ul.multi-select > li:not(.header) > span > input', 'click', function(e) {
		e.stopPropagation();
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.ms-options-wrap > button', 'click', function() {
		$(this).parent().find('ul').children('li:first-child').find('[type="checkbox"]').focus();
		return false;
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.add-more-row', 'click', function(e) {
		if($(this).closest('.control-group').attr('argtype') == 'group') {
			$(this).closest('.controls').find('.group-row').last().after($(this).closest('.controls').find('.group-row').last().clone());

			var tmp;
			$(this).closest('.controls').find('.group-row').last().find('.checkbox-info').find('input[type="checkbox"], label').each(function(index) {
				switch($(this).prop("tagName").toLowerCase()) {
					case 'label':
						tmp = $(this).attr('for');
						$(this).attr('for', $(this).attr('for') + '_1');
						break;
					case 'input':
						tmp = $(this).attr('id');
						$(this).attr('id', $(this).attr('id') + '_1').attr('name', $(this).attr('id') + '_1');
						break;
				}
			});

			if($(this).closest('.controls').find('.group-row').last().find('.remove-row').length == 0)
				$(this).closest('.controls').find('.group-row').last().find('.action-icons').prepend('<i class="fa fa-minus-circle orange-text remove-row" alt="' + localization['remove'] + '" title="' + localization['remove'] + '"></i>');
			$(this).closest('.controls').find('.group-row').last().find('.field-group').each(function(index) {
				if($(this).find('[type="multiselect-dropdown"]').next('.ms-options-wrap').length) {
					$(this).find('.ms-options-wrap').remove();
					$(this).find('select[type="multiselect-dropdown"]').removeClass('jqmsLoaded').show();
					initMultiSelect($(this).find('select[type="multiselect-dropdown"]'), $(this).find('select[type="multiselect-dropdown"]').attr('label'), true, true, 1);
				} else {
					$(this).find('[type="dropdown"]').val('');
					$(this).find('[type="text"]').val('');
				}
			});
			$(this).closest('.controls').find('.group-row:nth-last-child(2)').find('.add-more-row').remove();
		} else {
			
		}
		return false;
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.remove-row', 'click', function(e) {
		if($(this).closest('.control-group').attr('argtype') == 'group') {
			if($(this).closest('.group-row').find('.add-more-row').length > 0 && $(this).closest('.group-row').prev('.group-row').length > 0) {
				$(this).closest('.group-row').prev('.group-row').find('.action-icons').append('<i class="fa fa-plus-circle orange-text add-more-row" alt="' + localization['add-more'] + '" title="' + localization['add-more'] + '"></i>');
			}
			$(this).closest('.group-row').remove();
		} else {
			
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.reset-config', 'click', function(e) {
		e.stopPropagation();
		var str = '<div class="control-group">\
			<div class="title col-lg-12 col-md-12 col-sm-12"><h4>' + localization['reset-config-confirm'] + '</h4></div>\
		</div>\
		<div class="clear"></div>';
		openModel({body: str, buttons: {
			"no": closeModel,
			"yes": function() {
				resetTool();
			}
		}});
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.export-config', 'click', function(e) {
		e.stopPropagation();
		doAjaxRequest({url: 'ExportConfiguration', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}, container: '.workflowsList'}, function(response) {
			download(location.protocol + '//' + window.location.host + '/static/downloads/' + response.data.url);
		}, doNothing);
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.export-report', 'click', function(e) {
		$(this).closest('.buttonCustom').find('.dropdown-toggle').html('<i class="blue-text fa-progress"></i> Generating...');
		$('.export-report').closest('.buttonCustom').addClass('buttonDisabled');
		$(this).closest('.buttonCustom').find('.dropdown-toggle').trigger('click');
		e.stopPropagation();
		if($(this).hasClass('excel')) {
			doAjaxRequest({url: 'GenerateReport', alt_url: 'ReportState', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}, container: '.workflowsList'}, function(response) {
				downloadReport(response.data);
			}, function() {
				$('.export-report').closest('.buttonCustom').find('.dropdown-toggle').html('Export Report');
				$('.export-report').closest('.buttonCustom').removeClass('buttonDisabled');
			}, function(response) {
				downloadReport(response.data);
			});
		} else if($(this).hasClass('pdf')) {
			if($(this).hasClass('a0'))
				loadReportTemplate(true, 'a0');
			else
				loadReportTemplate(true, 'a4');
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.job-resume', 'click', function(e) {
		e.stopPropagation();
		var query = {stacktype: systemInfo.subtype};
		if($(this)[0].hasAttribute('jobid'))
			query = {jobid: $(this).attr('jobid')};
		doAjaxRequest({url: 'JobResume', base_path: settings.base_path, query: query, container: '.workflowsList'}, function(response) {
			getBatchStatus(true);
		}, doNothing);
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.job-rollback', 'click', function(e) {
		e.stopPropagation();
		var query = {stacktype: systemInfo.subtype};
		if($(this)[0].hasAttribute('jobid'))
			query = {jobid: $(this).attr('jobid')};
		var str = '<div class="control-group">\
			<div class="title col-lg-12 col-md-12 col-sm-12"><h4>' + localization['rollback-confirm'] + '</h4></div>\
		</div>\
		<div class="clear"></div>';
		openModel({body: str, buttons: {
			"no": closeModel,
			"yes": function() {
				doAjaxRequest({url: 'JobRevert', base_path: settings.base_path, query: query, container: '.workflowsList'}, function(response) {
					closeModel();
					if(systemInfo.deployment_type != 'basic') {
						//$('.buttonCustom.back-workflow').remove();
					}
					getBatchStatus(true);
				}, doNothing);
			}
		}});
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.workflowlog', 'click', function(e) {
                autoScroll = false;
                $(".workflow-log").mCustomScrollbar('scrollTo', $('.workflowsList a[name="log_' + $(this).closest('.workflowinfo').attr('jobid') + '"]').last()[0].offsetTop);
        });

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.workflow-log', 'click', function(e) {
		autoScroll = false;
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.basic-config-details', 'click', function(e) {
		var tmp, name = $(this).closest('.workflowinfo').find('.workflow-name').text(),
		id = $(this).closest('.workflowinfo').attr('primaryid');
		$.when(
			doAjaxRequest({url: 'GetGlobals', base_path: settings.base_path, query: {stacktype: systemInfo.subtype, hidden: true}}, function(response) {
				global_inputs = {};
				$.each(response.data, function(key, value) {
					global_inputs[value.name] = {label: value.label, value: value.svalue};
				});
			})
		).then(function() {
			setTimeout(function() {
				doAjaxRequest({url: 'WorkflowInputs', base_path: settings.base_path, query: {id: id, stacktype: systemInfo.subtype}, container: '.model-inset'}, function(response) {
					var str = '<div class="configurations">\
					</div>';
					openModel({title: localization['configuration'] + ' - ' + name, body: str, buttons: {
						"cancel": closeModel
					}});
					tmpStr = '';
					if(response.data.length > 0) {
						$.each(response.data, function(key, value) {
							if(!value.hidden) {
								if(tmpStr != value.execid && value.execid != '') {
									if(tmpStr != '') {
										str += '</table></fieldset>';
										$('.configurations').append(str);
									}
									str = '<fieldset><legend>' + value.desc + '</legend>\
									<table>';
									tmpStr = value.execid;
								}
								str += '<tr class="control-group" execid="' + value.execid + '">\
									<td class="title col-lg-4 col-md-4 col-sm-4">' + value.label + ': </td>\
									<td class="controls col-lg-8 col-md-8 col-sm-8" field="' + value.name + '">' +
										workflowInputBasicTemplate('.configurations', value, '', 'readonly') + 
									'</td>\
								</tr>';
							}
						});
						str += '</table></fieldset>';
						$('.configurations').append(str);
					}
				}, doNothing);
			}, 500);
		});
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.workflow-group > h2', 'click', function(e) {
		if($(this).closest('.workflow-group').find('dl.sub-worflows').hasClass('expand')) {
			$(this).closest('.workflow-group').find('dl.sub-worflows').removeClass('expand');
		} else {
			$('.rollback-container .sub-worflows').removeClass('expand');
			$(this).closest('.workflow-group').find('dl.sub-worflows').addClass('expand');
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.sub-workflow-name', 'click', function(e) {
		if($(this).next('dd.workflow-tasks-list').hasClass('expand')) {
			$(this).next('dd.workflow-tasks-list').removeClass('expand');
		} else {
			$('.rollback-container dd.workflow-tasks-list').removeClass('expand');
			$(this).next('dd.workflow-tasks-list').addClass('expand');
		}
	});

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	$('body').delegate('.workflow-group li', 'click', function(e) {
		var pjobid = $(this).closest('.workflow-group').attr('jobid');
		var arr = $(this).attr('taskid').split('_');
		var name = $(this).text();
		doAjaxRequest({url: 'RollBackTaskData', base_path: settings.base_path, query: {pjobid: pjobid, jobid: arr[0], tid: arr[1]}, container: '.model-inset'}, function(response) {
			var str = '<div class="configurations">\
			</div>';
			openModel({title: localization['configuration'] + ' - ' + name, body: str, buttons: {
				"cancel": closeModel
			}});
			if(response.data.inputlist.length > 0) {
				str += '<table class="basic">';
				$.each(response.data.inputlist, function(key, value) {
					str += '<tr class="control-group" key="' + value.key + '">\
						<td class="title col-lg-4 col-md-4 col-sm-4">' + value.label + ': </td>';
						var data = value.value.split('|');
						if(data.length > 1 && (!value.hasOwnProperty("gmembers") || ("gmembers" in value && value.gmembers.length == 0))) {
							str += '<td class="controls col-lg-8 col-md-8 col-sm-8">';
							$.each(data, function(i, member) {
								str += '<span class="badge">' + member + '</span>';
							});
							str = str.substring(0, str.length - 2) + '</td>';
						} else if(data.length > 1 || ("gmembers" in value && value.gmembers.length > 0)) {
							str += '<td class="controls col-lg-8 col-md-8 col-sm-8">\
								<table>';
								$.each(data, function(key1, value1) {
									value1 = value1.replace(/\'/g, '"').replace(/: u/g, ": ");
									try {
										value1 = $.parseJSON(value1);
									} catch(err) {}
									if(typeof value1 == 'string')
										str += '';
									else {
										if(key1 == 0) {
											str += '<tr class="control-group">';
											if("gmembers" in value && value.gmembers.length > 0) {
												$.each(value.gmembers, function(i, members) {
													str += '<th class="title">' + members['label'] + '</th>';
												});
											} else {
												Object.keys(value1).some(function(index) {
													str += '<th class="title upper">' + index + '</th>';
												});
											}
											str += '</tr>';
										}
										str += '<tr class="control-group">';
										if("gmembers" in value && value.gmembers.length > 0) {
											$.each(value.gmembers, function(i, members) {
												str += '<td class="title">' + value1[members['name']].value + '</td>';
											});
										} else {
											Object.keys(value1).some(function(index) {
												str += '<td class="controls col-lg-8 col-md-8 col-sm-8">' + value1[index].value + '</td>';
											});
										}
										str += '</tr>';
									}
									
								});
								str += '</table>\
							</td>';
						} else if(typeof value.value == 'string') {
							str += '<td class="controls col-lg-8 col-md-8 col-sm-8">' + value.value + '</td>';
						}
					str += '</tr>';
				});
				str += '</table>';
				$('.configurations').append(str);
			}
		}, doNothing);
	});
});

function downloadReport(data) {
	if(data.report_status.toLowerCase() == 'completed') {
		$('.export-report').closest('.buttonCustom').find('.dropdown-toggle').html('Export Report');
		$('.export-report').closest('.buttonCustom').removeClass('buttonDisabled');
		download(location.protocol + '//' + window.location.host + '/static/downloads/' + data.tid);
	}
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
var autoScroll = true;
function triggerExecute() {
	if(systemInfo.deployment_type == 'basic') {
		autoScroll = true;
		JobExecute();
	} else {
		$('.execute-workflow').first().trigger('click');
	}
}

function JobExecute() {
	doAjaxRequest({url: 'BatchExecute', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}, container: '.deployment'}, function(response) {
		$('.workflowsList .scroller').addClass('shrink');
		$('.log-container').addClass('expand').removeClass('hide');
		setTimeout(function() {
			getBatchStatus(true);
		}, 2000);
	}, doNothing);
}
/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function toggleWorkflows() {
	$('.workflowsList').toggle('slide', {direction: 'left'}, 'slow');
	$('.workflowsInfo').toggle('slide', {direction: 'right'}, 'slow');
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function toggleWorkflowRollback() {
	$('.list-workflows table .advanced').toggle();
	$('.list-jobs').toggle('slide', {direction: 'left'}, 'slow');
	$('.workflowsRollbackInfo').toggle('slide', {direction: 'right'}, 'slow');
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function showGlobalInputs(dom, checked, svalue) {
	var currentDom;
	if(dom.closest('.field-group').length) currentDom = dom.closest('.field-group');
	else currentDom = dom.closest('.controls');
	currentDom.find('.global-config-input').addClass('hide');
	currentDom.find('.map-global-input').prop("checked", checked);
	if(checked) {
		currentDom.find('.task_ismapped').val("3");
		currentDom.find('.map-prev-api').prop("checked", false);
		currentDom.find('.task-input, .prev-task-input').addClass('hide');
		currentDom.find('.task-input').next('.ms-options-wrap').addClass('hide');
		currentDom.find('.prev-task-input').next('.ms-options-wrap').addClass('hide');
		var str = '<option value="">' + localization['select'] + '</option>';
		$.each(global_inputs, function(key, value) {
			str += '<option value="' + key + '">' + value.label + '</option>';
		});
		currentDom.find('.global-config-input').html(str).removeClass('hide');
		currentDom.find('.global-config-input').val(svalue);
	} else {
		currentDom.find('.task_ismapped').val("0");
		currentDom.find('.task-input').removeClass('hide');
		currentDom.find('.task-input').next('.ms-options-wrap').removeClass('hide');
	}
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function showPrevTaskOutputs(dom, checked, svalue) {
	var currentDom;
	if(dom.closest('.field-group').length) currentDom = dom.closest('.field-group');
	else currentDom = dom.closest('.controls');
	currentDom.find('.map-prev-api').prop("checked", checked);
	var execid = $('#form_primaryid').val();
	if($('.modal-body #form-body').attr('taskType') == 'wgroup') execid = currentDom.closest('.control-group').attr('execid');
	if(checked) {
		currentDom.find('.task_ismapped').val("1");
		currentDom.find('.map-global-input').prop("checked", false);
		currentDom.find('.global-config-input').addClass('hide');
		currentDom.find('.task-input').next('.ms-options-wrap').addClass('hide');
		currentDom.find('.task-input').addClass('hide');
		currentDom.find('.prev-task-input').removeClass('hide');
		currentDom.find('.prev-task-input').next('.ms-options-wrap').removeClass('hide');
		loadPrevTaskOption(currentDom, execid, svalue);
	} else {
		currentDom.find('.task_ismapped').val("0");
		currentDom.find('.prev-task-input').addClass('hide');
		currentDom.find('.prev-task-input').next('.ms-options-wrap').addClass('hide');
		if(dom.closest('.field-group').length) {
			currentDom.find('.task-input').removeClass('hide');
			currentDom.find('.task-input').next('.ms-options-wrap').removeClass('hide');
		} else {
			currentDom.find('.task-input').removeClass('hide');
			currentDom.find('.task-input').next('.ms-options-wrap').removeClass('hide');
		}
	}
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadPrevTaskOption(dom, execid, dfvalue) {
	var query = {id: $('.modal-body #form-body').attr('workflowJobId'), execid: execid};
	if(workflow_mode == 'Edit') query.ttype = 'workflow';
	else if(workflow_mode == 'Info') query.ttype = 'job';
	doAjaxRequest({url: 'TaskSuggestedInputs', base_path: settings.base_path, query: query, isAsync: false, container: '.modal-body'}, function(response) {
		var str = '';
		if(dom.find('.prev-task-input').get(0)) {
			if(!dom.find('.prev-task-input').get(0).hasAttribute('multiple')) str += '<option value="">' + localization['select'] + '</option>';
			$.each(response.data, function(key, value) {
				str += '<option value="' + value.input + '">' + value.input + '</option>';
			});
			dom.find('.prev-task-input').html(str);
			dfvalue = isStringify(dfvalue);
			dom.find('.prev-task-input').val(dfvalue);
			if(dom.find('.prev-task-input').get(0).hasAttribute('multiple'))
				initMultiSelect(dom.find('.prev-task-input'), localization['field'], true, true, 1);
		}
	}, doNothing);
}

function resetWorkflowInfo() {
	//$.removeCookie(settings.cookie_name + "-jobinfo", { path: '/' });
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadWorkflow(mode) {
	mode = (mode == '' || typeof mode == 'undefined') ? 'basic': mode;
	doAjaxRequest({url: 'DeploymentSettings', base_path: settings.base_path, method: 'POST', data: {deployment_type: mode}, container: '.content-container'}, function(response) {
		systemInfo.deployment_type = mode;
		//resetWorkflowInfo();
		$('table#workflows_list .basic, table#workflows_list .advanced').addClass('hide');
		$('table#workflows_list .' + mode).removeClass('hide');
		var selectedWorkflow;
		if($('.workflowinfo.elementInfo.active').length) {
			selectedWorkflow = $('.workflowinfo.elementInfo.active').attr('primaryId');
		}
		$('.buttonPrevious').addClass('buttonDisabled');
		loadWorkflows('.deployment .widget-content');
	}, doNothing);
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadWorkflows(container) {
	var j = 1, str = '', query = '';
	doAjaxRequest({url: 'Workflows', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}, container: container}, function(response) {
		str += '<table class="new table">';
		if(systemInfo.deployment_type == 'basic') {
			str += '<tr class="basic">\
				<th colspan="2">\
					<div class="pull-left progress-bar-container">\
						<div class="pull-left"><h4>' + localization['deployment-progress'] + '</h4></div>\
						<div class="pull-right"><h4 class="percentage">0%</h4></div>\
						<div class="clear"></div>\
						<div class="progress-bar orange-bar shine stripes small">\
							<span class="orange-background" style="width: 0%"></span>\
						</div>\
					</div>\
				</th>\
				<th width="150" align="center">\
				</th>\
			</tr>';
		}
		if(response.data.length > 0) {
			$.each(response.data, function(key, value) {
				var alt = "";
				if( key % 2 == 0 ) alt = "alt";
				str += '<tr class="' + alt + ' workflowinfo elementInfo" primaryid="' + value.id + '">';
					if(systemInfo.deployment_type == 'advanced') {
						str += '<td width="50">' +
							+ j + 
							'<div class="hide checkbox checkbox-info">\
								<input id="workflow_' + key + '" type="checkbox" class="workflows" value="' + value.id + '">\
								<label for="workflow_' + key + '" class="nopadding">\</label>\
							</div>\
						</td>\
						<td width="30%" class="workflow-name" status="READY">' + value.name + '</td>\
						<td width="">' + value.desc + '</td>\
						<td width="150" align="center" class="workflow-action-icons">\
							<div class="actions"></div>\
						</td>';
					} else {
						str += '<th width="50">' + j + '</th>\
						<td width="" class="workflow-name" status="READY">' + value.name + '</td>\
						<td width="150" align="center" class="workflow-action-icons"><a href="javascript:;" class="basic-config-details icon-with-link" alt="' + localization['basic_config'] + '" title="' + localization['basic_config'] + '"><i class="fa fa-info-circle medium grey-text"></i></a></td>';
					}
				str += '</tr>';
				j++;
			});
		} else {
			str += '<tr><td><h4><span class="col-lg-12 col-md-12 col-sm-12 col-xs-12 widget-subtitle">' + localization['no-workflow'] + '.</span></h4></td></tr>';
		}
		str += '</table>';

		if($('.workflowsList .list-jobs .mCSB_container').length)
			$('.workflowsList .list-jobs').mCustomScrollbar("destroy");
		initScroller($('.workflowsList .scroller'));
		$('.workflowsList .list-jobs .mCSB_container').html(str);
		
		str = '<div class="log-container nopadding pull-right">\
			<div class="sub-title logs">\
				<div class="pull-left"><h4>' + localization['progress-log'] + '</h4></div>\
				<div class="pull-right hide nopadding nomargin">\
					<div class="download-log pointer pull-right nomargin" alt="' + localization['download-log'] + '" title="' + localization['download-log'] + '"><i class="fa fa-download"></i></div>\
				</div>\
				<div class="clear"></div>\
			</div>\
			<div class="workflow-log logs"><span class="no-logs">' + localization['no-logs'] + '.</span></div>\
		</div>';
		$('.workflowsList .list-workflows').after(str);
		initScroller($('.workflow-log'));

		var height = parseInt($('.workflowsList').closest('.smartwidget').height()) - 100;
		$('.workflowsList .scroller').css('height', height + 'px').css('max-height', height + 'px');
		$('.log-container').css('height', height + 'px').css('max-height', height + 'px').addClass('hide');
		height -= 52;
		$('.log-container .workflow-log').css('height', height + 'px').css('max-height', height + 'px');
		getBatchStatus(true);
	}, doNothing);
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function getBatchStatus(notify) {
	clearTimeout(tout);clearTimeout(rout);
	var ccount = 0, fcount = 0, ecount = 0, rfcount = 0, tmp;
	var icon, flag = true, state = true, jobid;
	doAjaxRequest({url: 'BatchStatus', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}, notify: notify}, function(response) {
		if(systemInfo.config_mode.toLowerCase() == 'json') {
			$('.buttonNext').text(localization['init_deploy']).removeClass('hide');
			$('.buttonNext, .buttonPrevious').addClass('buttonDisabled');
			$('.toggle.deployment-type').addClass('hide');
		} else 
			$('.buttonFinish, .buttonPrevious').removeClass('hide');
		if(systemInfo.deployment_type == 'advanced')
			$('.buttonFinish').addClass('hide');
		$('tr.workflowinfo').removeClass('failed');
		$('.deployment-type').toggleClass('disabled', true);
		$('.buttonFinish, .buttonPrevious, .buttonCustom.export-report').addClass('buttonDisabled');
		$('.buttonCustom.job-rollback, .buttonCustom.job-resume').remove();

		if(response.data.length == 0) {
			if(systemInfo.deployment_type == 'advanced') {
				icon = '<span class="workflow-icons blue-text fa fa-play medium execute-workflow" alt="' + localization['exec-wf'] + '" title="' + localization['exec-wf'] + '"> </span>\
				<span class="workflow-icons grey-text fa fa-edit modify-workflow" alt="' + localization['info_modify'] + '" title="' + localization['info_modify'] + '"> </span>';
				$('.workflowsList .workflowinfo').children(':last-child').first().html(icon);
			}
			if(systemInfo.config_mode.toLowerCase() == 'json') {
				JobExecute();
				$('.execute-workflow, .modify-workflow').remove();
			} else 
				$('.buttonFinish, .buttonPrevious').removeClass('buttonDisabled');
			$('.deployment-type').toggleClass('disabled', false);
			return false;
		}
		
		$('.workflowsList .scroller').addClass('shrink');
		$('.log-container').addClass('expand').removeClass('hide');
		loadDeploymentLogs();
		$.each(response.data, function(key, value) {
			icon = '';
			if(systemInfo.deployment_type == 'basic')
				icon = '<span class="basic-config-details icon-with-link"><i class="fa faa fa-info-circle medium grey-text" alt="' + localization['basic_config'] + '" title="' + localization['basic_config'] + '"></i></span>';
			switch(value.status) {
				case 'COMPLETED':
				case 'ROLLBACK_COMPLETED':
					ccount++;
					icon += '<span class="workflow-icons green-text fa fa-check-circle medium completed-workflow" title="' + localization['already-executed'] + '"> </span>\
					<span class="workflow-icons workflowlog fa fas fa-clipboard-list medium grey-text" title="' + localization['progress-log'] + '"></span>';
					$(".workflow-log .mCSB_container .log_" + value.jid).remove();
					break;
				case 'EXECUTING':
				case 'ROLLBACK':
					ecount++;
					flag = false; state = false;
					icon += '<span class="blue-text fa-progress info-workflow" title="' + localization[value.status.toLowerCase()] + '"> </span>\
					<span class="workflow-icons workflowlog fa fas fa-clipboard-list medium grey-text" title="' + localization['progress-log'] + '"></span>';
					loadJobLogs(value.jid, 'basic', notify);
					break;
				case 'FAILED':
				case 'ROLLBACK_FAILED':
					fcount++;
					if(value.status == 'ROLLBACK_FAILED') rfcount++;
					state = false;
					icon += '<span class="workflow-icons info-workflow fa fa-exclamation-triangle medium red-text tipso tipso_style" data-tipso-title="' + localization['info'] + '" data-tipso="' + value.msg + '"> </span>';
					if(systemInfo.deployment_type == 'advanced') {
						$('tr.workflowinfo[primaryid="' + value.wid + '"]').addClass('failed');
						if(value.status != 'ROLLBACK_FAILED') {
							tmp = '<div class="pull-right">';
								if(systemInfo.config_mode.toLowerCase() != 'json')
									tmp += '<a href="javascript:;" jobid="' + value.jid + '" class="buttonCustom small job-rollback pull-right" style="display: inline-block;">' + localization['revert'] + '</a>';
								tmp += '<a href="javascript:;" jobid="' + value.jid + '" class="buttonCustom small job-resume pull-right" style="display: inline-block;">' + localization['retry'] + '</a>\
								<div class="clear"></div>\
							</div>';
							$('tr.workflowinfo[primaryid="' + value.wid + '"]').find('td:nth-last-child(2)').append(tmp);
						}
					}
					icon += '<span class="workflow-icons workflowlog fa fas fa-clipboard-list medium grey-text" title="' + localization['progress-log'] + '"></span>';
					$(".workflow-log .mCSB_container .log_" + value.jid).remove();
					break;
				default:
					if(state && systemInfo.deployment_type == 'advanced') {
						state = false;
						icon += '<span class="workflow-icons blue-text fa fa-play medium execute-workflow" title="' + localization['exec-wf'] + '"> </span>\
						<span class="workflow-icons grey-text fa fa-edit modify-workflow" title="' + localization['info_modify'] + '"> </span>';
					}
					flag = false;
					$(".workflow-log .mCSB_container .log_" + value.jid).remove();
					break;
			}
			$('tr.workflowinfo[primaryid="' + value.wid + '"]').children(':last-child').html(icon);
			$('tr.workflowinfo[primaryid="' + value.wid + '"]').attr('jobid', value.jid).removeClass('READY EXECUTING COMPLETED FAILED ROLLBACK ROLLBACK_COMPLETED ROLLBACK_FAILED').addClass(value.status);
			$('tr.workflowinfo[primaryid="' + value.wid + '"]').find('.workflow-name').attr('status', value.status);
		});
		initTooltip('.list-jobs');
		var percentage = (ccount / response.data.length) * 100;
		percentage = percentage.toFixed(2);
		$('.progress-bar-container .percentage').html(percentage + '%');
		$('.progress-bar-container .progress-bar > span').css('width', percentage + '%');
		if(systemInfo.deployment_type == 'advanced' && systemInfo.config_mode.toLowerCase() != 'json' && $('.job-rollback, .workflowinfo.EXECUTING, .workflowinfo.ROLLBACK').length == 0) {
			jobid = $('.workflow-icons.completed-workflow').last().closest('tr.workflowinfo').attr('jobid');
			$('.workflow-icons.completed-workflow').last().closest('tr.workflowinfo').find('td:nth-last-child(2)').append('<a href="javascript:;" jobid="' + jobid + '" class="buttonCustom small job-rollback pull-right" style="display: inline-block;">' + localization['revert'] + '</a>');
		}

		if(ccount == 0 && fcount == 0 && ecount == 0) {
			$('.buttonFinish, .buttonPrevious').removeClass('buttonDisabled');
			$('.deployment-type').toggleClass('disabled', false);
		}
		$('.reset-config, .export-config, .buttonCustom.reports').remove();
		if(state) {
			$('.buttonNext').addClass('hide');
		}
		if(flag || fcount > 0) {
			$('.progress-bar-container .progress-bar').removeClass('orange-bar shine stripes');
			if(fcount > 0) {
				if(systemInfo.deployment_type != 'advanced') {
					if(rfcount == 0) {
						$('.job-rollback, .job-resume').remove();
						$('.buttonFinish').after('<a href="javascript:;" class="buttonCustom job-resume" style="display: inline-block;">' + localization['retry'] + '</a>');
					}
				}
				if(rfcount > 0) {
					$('.job-rollback, .job-resume').remove();
					$('.buttonFinish').after('<a href="javascript:;" class="buttonCustom reset-config" style="display: inline-block;">' + localization['finish'] + '</a>');
				}
			} else {
				$('.buttonPrevious, .buttonFinish').addClass('hide');
				$('.buttonFinish').before('<a href="javascript:;" class="buttonCustom reset-config" style="display: inline-block;">' + localization['finish'] + '</a>');
				$('.reset-config').before('<a href="javascript:;" class="buttonCustom export-config" style="display: inline-block;">' + localization['export-devices'] + '</a>');
				//$('.reset-config').before('<a href="javascript:;" class="buttonCustom export-report" style="display: inline-block;">' + localization['export-report'] + '</a>');
				$('.reset-config').before('<div class="buttonCustom dropup reports">' +
					'<span type="button" class="dropdown-toggle" data-toggle="dropdown">' + localization['export-report'] + '</span>' +
					'<div class="dropdown-menu">' +
						'<a class="dropdown-item export-report pdf a4" href="javascript:;"><i class="fa fa-file-pdf-o"></i> PDF (A4 Size)</a>' +
						'<a class="dropdown-item export-report excel" href="javascript:;"><i class="fa fa-file-excel-o"></i> XLS</a>' +
					'</div>' +
				'</div>');
			}
		} else {
			tout = setTimeout(function() {
				getBatchStatus(false);
			}, 10000);
		}
	}, function() {
		tout = setTimeout(function() {
			getBatchStatus(false);
		}, 10000);
	});
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadWorkflowInfoTemplate(mode) {
	workflow_mode = mode;
	$('.workflow-container').remove();
	$('#wizard').addClass('full-screen');
	var str = '<div class="workflow-container">\
		<div class="widget-header">\
			<div class="widget-title pull-left info"><span class="workflow-title"></span><span class="clear"></span></div>\
			<div class="widget-subtitle pull-right action-icons">';
				str += '<i class="fa fa-times close-workflow pull-right" alt="' + localization['close'] + '" title="' + localization['close'] + '"></i>';
			str += '</div>\
		</div>';
		if(mode != 'Info') {
			str += '<div class="left-panel col-lg-4 col-md-4 col-sm-4 col-xs-4"></div>';
		}
		str += '<div class="gridview col-lg-8 col-md-8 col-sm-8 col-xs-8 nopadding">';
			str += '<div id="map-ctl">\
				<div id="zoomin-ctl">\
					<i title="' + localization['zoom-in'] + '" alt="' + localization['zoom-in'] + '" class="fa fa-plus-circle zoomin"></i>\
				</div>\
				<div id="zoomout-ctl">\
					<i title="' + localization['zoom-out'] + '" alt="' + localization['zoom-out'] + '" class="fa fa-minus-circle zoomout"></i>\
				</div>\
				<div id="reset-ctl">\
					<i title="' + localization['reset'] + '" alt="' + localization['reset'] + '" id="pan-reset" class="fa fa-stop-circle ctl-reset"></i>\
				</div>\
			</div>';
			str += '<div class="workshop">\
				<div class="scroller">\
					<div class="workflow-info workflow"></div>\
				</div>\
			</div>\
		</div>';
		if(mode == 'Info') {
			str += '<div class="right-panel workflow-log-container nopadding col-lg-4 col-md-4 col-sm-4 col-xs-4">\
				<div class="sub-title logs">\
					<div class="pull-left widget-subtitle">' + localization['progress-log'] + '</div>\
					<div class="pull-right hide nopadding nomargin">\
						<div class="download-log pointer pull-right nomargin" alt="' + localization['download-log'] + '" title="' + localization['download-log'] + '"><i class="fa fa-download"></i></div>\
					</div>\
					<div class="clear"></div>\
				</div>\
				<div class="workflow-log logs"><span class="no-logs">' + localization['no-logs'] + '.</span></div>\
			</div>';
		}
	str += '</section>';
	return str;
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function prepareJob(wid) {
	doAjaxRequest({url: 'WorkflowPrepare', base_path: settings.base_path, data: {id: wid}, container: '.workflowsInfo'}, function(response) {
		var obj = {workflowid: wid, jobid: response.data.jobid};
		$.cookie(settings.cookie_name + "-jobinfo", JSON.stringify(obj), {path: '/', expires: 7});
		$('.workflow-info').attr('id', response.data.jobid);
		$('.workflow-info').closest('.workshop').attr('jobid', response.data.jobid);
		loadWorkflowInfo(wid);
	}, doNothing);
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
var workflowTypes = {};
function loadWorkflowInfo(wid) {
	workflowTasks = [];
	initScroller($('.workflow-log'));
	var height = parseInt($('.workflow-container .workshop').height()) - 75;
	$('.workflow-log').css('height', height + 'px').css('max-height', height + 'px');
	$(".workflow-log .mCSB_container").html('');

	doAjaxRequest({url: 'WorkflowInfo', base_path: settings.base_path, data: {wid: wid}, container: '.workflowsInfo'}, function(response) {
		workflowTypes[JSON.parse($.cookie(settings.cookie_name + "-jobinfo")).jobid] = response.data.wtype;
		//str = '<h2>' + response.data.name + '</h2><small>' + response.data.desc + '</small>';
		$('.workflow-container>.widget-header>.info>.workflow-title').html(response.data.name);
		loadJobTasks(JSON.parse($.cookie(settings.cookie_name + "-jobinfo")).jobid);
		$(".workflow-log .mCSB_container").html('<div class="no-logs"><h5>' + localization['no-logs'] + '<h5></div>\n\n');
		loadJobLogs(JSON.parse($.cookie(settings.cookie_name + "-jobinfo")).jobid, 'advanced', false);
	}, doNothing);
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadJobTasks(jobid) {
	jobTasks = [];
	activeObj = jobid;
	initScroller($('#' + jobid).closest('.workshop > .scroller'));
	var height = parseInt($('.gridview').height()) - 5;
	$('#' + jobid).closest('.workshop > .scroller').css('height', height + 'px').css('max-height', height + 'px');

	initFlowchart(jobid, false, true);
	createShape('ellipse', localization['start'], 'start', jobid);
	var api = 'JobTasks';
	$('.workshop.fresh').attr('jobId', jobid).removeClass('fresh');
	if(workflowTypes[jobid] == 'wgroup') api = 'WorkflowGroupTasks';
	var data = {id: jobid};
	if(workflow_mode == 'Edit') data.ttype = 'workflow';
	else if(workflow_mode == 'Info') data.ttype = 'job';
	doAjaxRequest({url: api, base_path: settings.base_path, data: data, container: '.workflowsInfo'}, function(response) {
		$.each(response.data, function(key, value) {
			if(workflowTypes[jobid] != 'wgroup')
				jobTasks.push(value.execid);
			value.jobid = (typeof value.jobid == 'undefined') ? '' : value.jobid;
			workflowTasks.push(value.jobid);
			createShape('rect', value.name, value.execid, jobid, value.jobid, workflowTypes[jobid]);
		});
		createShape('ellipse', localization['end'], 'end', jobid);
		
		$.each(response.data, function(key, value) {
			if(key == 0)
				createConnection(paper[activeObj].getById('s_out_start'), paper[activeObj].getById('input_' + value.execid));

			if((parseInt(key) + 1) == response.data.length) {
				createConnection(paper[activeObj].getById('s_out_' + value.execid), paper[activeObj].getById('input_end'));
				createConnection(paper[activeObj].getById('f_out_' + value.execid), paper[activeObj].getById('input_end'));
			} else {
				if(value.onsuccess != 'None')
					createConnection(paper[activeObj].getById('s_out_' + value.execid), paper[activeObj].getById('input_' + value.onsuccess));
				if(value.onfailure != 'None')
					createConnection(paper[activeObj].getById('f_out_' + value.execid), paper[activeObj].getById('input_' + value.onfailure));
			}
		});
		getJobStatus(true);
	}, function() {
		createShape('ellipse', localization['end'], 'end', jobid);
	});
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function saveWorkflowTask(type) {
	var obj = getFormData('#form-body .control-group');
	var api = 'JobTaskInputSave';
	var query = {id: $('.modal-body #form-body').attr('workflowJobId')};
	query.execid = $('#form_primaryid').val();
	if(workflow_mode == 'Edit') query.ttype = 'workflow';
	else if(workflow_mode == 'Info') query.ttype = 'job';
	$('body').find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').removeClass('error');
	$('body').find('.help-block').html('');

	doAjaxRequest({url: api, base_path: settings.base_path, method: 'POST', query: query, data: obj.task_input_api, success_notify: true, container: '.modal-inset', formContainer: '.modal-inset'}, function(response) {
		$('svg>#' + $('#form_primaryid').val()).data('input', obj.form_data);
		if(paper[activeObj].getById($('#form_primaryid').val()) != null)
			paper[activeObj].getById($('#form_primaryid').val()).node.setAttribute('style', 'fill: ' + colorCodes['fill-input'] + '; stroke: ' + colorCodes['stroke-input']);

		var title = $('#form_primaryid').val() + ' - ' + $('rect#' + $('#form_primaryid').val()).next('text').text();
		$('rect#' + $('#form_primaryid').val()).find('title').html(title);
		closeModel();
	}, function(response) {
		if(response.data) {
			var container;
			$.each(response.data, function(i, value) {
				if("group_field" in value)
					container = '.modal-inset [argname="' + value.field + '"] .group-row:eq(' + value.order + ') .field-group[argname="' + value.group_field + '"]';
				else
					container = '.modal-inset .control-group.' + value.field + '[argname="' + value.field + '"]';
				$(container).find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
				$(container).find('.help-block').show().html(ucfirst(value.msg));
			});
			//$(api.formContainer).find('.task-input.error').first().focus();
		}
	});
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
var validate = false, group_row_count = 1;
Hook.register(
	'workflowInput',
	function(args) {
		var str, obj, title, type = 'row';//column/row
		var execid = args[0];
		var jobid = args[1];
		var taskJobId = args[2];
		var taskType = args[3];
		var api = 'JobTaskInputs';
		var query = {execid: execid, id: jobid};
		group_row_count = 1;
		if(workflow_mode == 'Edit') query.ttype = 'workflow';
		else if(workflow_mode == 'Info') query.ttype = 'job';
		if(taskType == 'wgroup') {
			jobid = taskJobId;
			api = 'JobTaskMandatoryInputs';
			query = {id: jobid};
		}
		if($('#label_' + execid).length)
			title = ' - ' + $('#label_' + execid).text();
		
		openModel({title: localization['wf-inputs'] + title, body: '', buttons: {
			"close": closeModel,
			"save": saveWorkflowTask
		}});
		if(taskType != 'wgroup') {
			str = '<div class="controls mode-container addition-info col-lg-12 col-md-12 col-sm-12 col-xs-12">' +
				loadFormField({type: 'toggle', id: 'mode pull-right'}) +
				'<div class="clear"></div>\
			</div>';
			$('.modal-body .mode-container').remove();
			$('.modal-body #form-body').before(str);
			$('.toggle-select.mode').toggles({type: 'select', on: true, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['basic'], off: localization['advanced']}});
			$('.toggle-select.mode').on('toggle', function(e, active) {
				$('.modal-body #form-body .basic, .modal-body #form-body .advanced').addClass('hide');
				$('.form-footer #saveBtn').addClass('hide');
				if(active) {
					$('.modal-body #form-body .basic').removeClass('hide');
				} else {
					$('.form-footer #saveBtn').removeClass('hide');
					$('.modal-body #form-body .advanced').removeClass('hide');
					$('.control-group .controls span.prefix').each(function(index) {
						var borderWidth = 15 + $(this).outerWidth();
						$(this).next('input.prefix').css('border-left-width', borderWidth + 'px');
					});
					$('.control-group .controls span.suffix').each(function(index) {
						var borderWidth = 15 + $(this).outerWidth();
						$(this).prev('input.suffix').css('border-right-width', borderWidth + 'px');
					});
				}
			});
		}

		$.when(
			doAjaxRequest({url: 'GetGlobals', base_path: settings.base_path, query: {stacktype: systemInfo.subtype, hidden: true}}, function(response) {
				global_inputs = {};
				$.each(response.data, function(key, value) {
					global_inputs[value.name] = {label: value.label, value: value.svalue};
				});
			})
		).then(function() {
			setTimeout(function() {
				doAjaxRequest({url: api, base_path: settings.base_path, query: query, container: '.modal-inset'}, function(response) {
					formData = response.data; n = -1;
					var workflow_input = $('svg>#' + execid).data('input');
					$('.modal-body #form-body').attr('taskExecId', execid).attr('workflowJobId', jobid).attr('taskType', taskType).attr('alignType', type);
					$('.form-footer #saveBtn').addClass('hide');
					tabIndex++;
					$('#form_primaryid').val(execid);
					if(response.data.length > 0) {
						tmpStr = '';
						$('.modal-body #form-body .mCSB_container').first().append('<div class="basic configurations"></div><div class="advanced hide"></div>');
						loadWorkflowFormFields();
					} else {
						$('.modal-body #form-body .mCSB_container').first().append('<h4 class="title empty_msg">' + localization['no-input-field'] + '.</h4>');
						$('.save-workflow-task-btn').addClass('hide');
					}
				}, doNothing);
			}, 500);
		});
		return true;
	}
);

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadWorkflowFormFields() {
	var tmp, execid = $('.modal-body #form-body').attr('taskExecId'),
	type = $('.modal-body #form-body').attr('alignType'),
	taskType = $('.modal-body #form-body').attr('taskType');

	if(counter < formData.length) {
		obj = loadWorkflowInputForm(formData[counter], execid, type);
		tmpStr += obj.basic;
		if(taskType != 'wgroup')
			$('.modal-body #form-body .mCSB_container .advanced').append(obj.advanced);

		tabIndex++;
		if($('.modal-body #form-body').attr('taskType') == 'wgroup') execid = formData[counter].execid;
		tmp = formData[counter];
		populateFormData(formData[counter], execid, 0, 1);
		if(tmp.iptype == 'group' && tmp.svalue != '' && tmp.svalue.length > 0) {
			var dom;
			$.each(tmp.svalue, function(i, val) {
				if(typeof val == 'string') val = $.parseJSON(val);
				Object.keys(val).some(function(key) {
					dom = $('div[argname="' + tmp.name + '"][argtype="group"]').find('.group-row').eq(i).find('div.field-group[argname="' + key + '"]');
					if(dom.find('.task-input').attr('type') == 'multiselect-dropdown')
						dom.find('.task-input').multiselect('reload');
					if(val[key].ismapped == "1") showPrevTaskOutputs(dom, true, val[key].value);
					else if(val[key].ismapped == "3") {
						showGlobalInputs(dom.find('.map-global-input'), true, val[key].value);
					}
				});
			});
		} else {
			if(tmp.ismapped == "1") {
				if(typeof tmp.svalue == 'string')
					tmp.svalue = tmp.svalue.split("|");
				showPrevTaskOutputs($('#prev_api_' + tmp.name + '.map-prev-api'), true, tmp.svalue);
			} else if(tmp.ismapped == "3") {
				showGlobalInputs($('#map_global_' + tmp.name + '.map-global-input'), true, tmp.svalue);
			}
		}
	} else {
		counter = 0; formData = [];
		tmpStr += '</table>';
		if($('#form-body').attr('tasktype') != 'wgroup') tmpStr += '</fieldset>';
		$('.modal-body #form-body .mCSB_container .basic').append(tmpStr);
		$('.modal-body #form-body .mCSB_container > div').addClass('loaded');
		tmpStr = '';

		$('.task-input[type="multiselect-dropdown"]').each(function(index) {
			initMultiSelect($(this), $(this).attr('label'), true, true, 1);
		});
		bindInputOptionEvent();
		initTooltip('.modal-inset');
		if(validate) validateTask(execid);
	}
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function bindInputOptionEvent() {
	$('#form-body').delegate('.map-prev-api', 'click', function(e) {
		showPrevTaskOutputs($(this), this.checked, '');
	});
	$('#form-body').delegate('.map-global-input', 'click', function(e) {
		showGlobalInputs($(this), this.checked, '');
	});
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function validateTask(execid) {
	doAjaxRequest({url: 'JobValidate', base_path: settings.base_path, data: {jobid: activeObj, execid: execid}, container: '.modal-inset'}, function(response) {
		if(!response.data.isvalid) {
			$.each(response.data.task[0].error, function(index, value) {
				$('#popupFrm .control-group[argname="' + value.field + '"], #popupFrm .field-group[argname="' + value.field + '"]').find('.task-input, .prev-task-input, .global-config-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
				$('#popupFrm .control-group[argname="' + value.field + '"], #popupFrm .field-group[argname="' + value.field + '"]').find('.help-block').show().html(ucfirst(value.msg));
			});
			var dom = $('#popupFrm .task-input.error, #popupFrm .prev-task-input.error, #popupFrm .global-config-input.error').first();
			if(dom.closest('.field-group').length) dom = dom.closest('.field-group');
			else dom = dom.closest('.controls');
			if(dom.find('.map-global-input').is(':checked')) dom.find('.global-config-input.error').focus();
			else if(dom.find('.map-prev-api').is(':checked')) dom.find('.prev-task-input.error').focus();
			else dom.find('.task-input.error').focus();
		}
	}, doNothing);
}

/**
  * @desc it will execute(internally generate a job for each workflows and trigger the execution) a set of workflows.
  * @param string $wid - the unique identifier of the workflow
*/
function executeJob(wid) {
	autoScroll = true;
	doAjaxRequest({url: 'BatchExecute', base_path: settings.base_path, query: {stacktype: systemInfo.subtype, wid: wid}, container: '.modal-inset'}, function(response) {
		currentTask = 0;
		getBatchStatus(true);
	}, function() {
		setTimeout(function() {
			$('.workflow-icons.fa-spinner.faa-spin').removeClass('fa-spinner faa-spin animated').addClass('fa-play execute-workflow');
		}, 500);
	});
}

/**
  * @desc this will collect/update the status of the job for every 5 sec for a specified stacktype(saved on cookie)
*/
function getJobStatus(notify) {
	clearTimeout(tout);
	var api = 'JobStatus';
	if(workflowTypes[activeObj] == 'wgroup') api = 'GroupJobStatus';
	$('.buttonFinish, .buttonPrevious').addClass('hide');
	doAjaxRequest({url: api, base_path: settings.base_path, data: {jobid: activeObj}, notify: notify, container: '.modal-inset'}, function(response) {
		var flag = false, job_status = 'success';
		$.each(response.data.taskstatus, function(key, value) {
			if(value.status != 'READY') flag = true;
		});
		if(response.data.taskstatus.length == 0 || !flag) return false;
		flag = false;
		$('text.shape-icons.task-input').remove();
		$.each(response.data.taskstatus, function(key, value) {
			if(value.status == 'FAILED') job_status = 'failed';
			else if(job_status != 'failed' && (value.status == 'EXECUTING' || value.status == 'READY')) flag = true;
			//else if(value.status == 'SUCCESS' || value.status == 'COMPLETED')
			addForiegnObject(activeObj, value.execid, value.status);
		});
		loadJobLogs(JSON.parse($.cookie(settings.cookie_name + "-jobinfo")).jobid, 'advanced', notify);
		if(flag) {
			tout = setTimeout(function() {getJobStatus(false)}, 5000);
		} else if(JSON.parse($.cookie(settings.cookie_name + "-jobinfo")).jobid != activeObj) {
			tout = setTimeout(function() {getJobStatus(false)}, 5000);
		} else {
			if(job_status == 'failed') {
				$('.fa-sync.faa-spin.animated').after('<i class="fa fa-warning faa-flash animated red-text pull-right" alt="' + localization['exec-wf'] + '" title="' + localization['exec-wf'] + '"></i>');
				$('.fa-sync.faa-spin.animated').remove();
			} else {
				$('.fa-sync.faa-spin.animated').after('<i class="fa fa-check-circle faa-flash animated green-text pull-right" alt="' + localization['exec-wf'] + '" title="' + localization['exec-wf'] + '"></i>');
				$('.fa-sync.faa-spin.animated').remove();
			}
		}
	}, function() {
		tout = setTimeout(function() {getJobStatus(false)}, 5000);
	});	
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadDeploymentLogs(mode) {
	doAjaxRequest({url: 'DeploymentLogs', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}}, function(response) {
		if(response.data.logs.length > 0) {
			$('.download-log').parent().removeClass('hide');
			$('.workflow-log .no-logs, .workflow-log-container .logs .no-logs').remove();
		}
		if(mode == 'basic') $('.log-container .logs').show();
		if(!$(".workflow-log .mCSB_container .deployment-log-collection").length)
			$(".workflow-log .mCSB_container").prepend('<div class="deployment-log-collection"></div>');

		$(".workflow-log .mCSB_container .deployment-log-collection").html(response.data.logs);
		if(autoScroll)
			setTimeout(function () {$(".workflow-log").mCustomScrollbar('scrollTo', 'bottom');}, 500);
	}, doNothing);
}

/**
  * @desc this will collect the log for a specified workflow using the unique identifier and place it on a log container
  * @param string $jobid - the unique identifier of the workflow
  * @param string $mode - the deployment mode (basic/advanced)
*/
function loadJobLogs(jobid, mode, notify) {
	if(jobid == '' || jobid == 'None') return;
	doAjaxRequest({url: 'Logs', base_path: settings.base_path, data: {jobid: jobid}, notify: notify}, function(response) {
		if(mode == 'basic') $('.log-container .logs').show();
		else $('.workshop #' + jobid + ' + .right-panel .logs').show();
		if(response.data.logs.length > 0) {
			$('.download-log').parent().removeClass('hide');
			$('.workflow-log .no-logs, .workflow-log-container .logs .no-logs').remove();

			if(!$(".workflow-log .mCSB_container .log_" + jobid).length) {
				$(".workflow-log .mCSB_container").append('<div class="log_' + jobid + '"></div>\n\n');
			}
		}
		var str = '<a name="log_' + jobid + '"></a><h5>' + $('tr.workflowinfo[jobid="' + jobid + '"]').find('.workflow-name').text() + ':</h5>\n' + response.data.logs;
		$(".workflow-log .mCSB_container .log_" + jobid).html(str);
		if(autoScroll)
			setTimeout(function () {$(".workflow-log").mCustomScrollbar('scrollTo', 'bottom');}, 500);
	}, doNothing);
}

/**
  * @desc this will generate a template/placeholder for child workflows
  * @param string $jobid - the unique identifier of the parent workflow
  * @param string $taskType - the type of the workflow whether its a group workflow with some child or not
  * @param string $uniqueid - the unique identifier of the child workflow
  * @param string $label - the name of the workflow
*/
function addWorkshop(jobid, taskType, uniqueid, label) {
	$('.workshop[jobId="' + uniqueid + '"]').removeClass(toggleEffect[effect]['in']).addClass('magictime ' + toggleEffect[effect]['out']);
	$('.subworkflow-title').remove();
	$('.workflow-container .widget-header .widget-title .workflow-title').after('<span class="subworkflow-title"> - ' + label + '</span>');
	var str = '<div class="workshop fresh" jobId="' + jobid + '" groupId="' + uniqueid + '">\
		<i class="fa fa-times-circle reset-workshop"></i>\
		<div class="scroller">\
			<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 pull-right nopadding">\
				<div id="' + jobid + '" class=""></div>\
			</div>\
		</div>\
	</div>';
	$('.gridview').append(str);

	workflowTypes[jobid] = 'standalone';
	setTimeout(function() {
		$('.workshop[jobId="' + uniqueid + '"]').hide();
		var leftPosition = parseInt($('.gridview').offset().left) + parseInt($('.gridview').width()) - 30;
		$('.reset-workshop').css({top: $('.gridview').offset().top + 10, left: leftPosition});
	}, 1100);
	loadJobTasks(jobid);
}

/**
  * @desc template form for adding a new workflow
  * @return bool - will return the html form for new workflow functionality
*/
function loadWorkflowForm() {
	var str = loadFormTemplate({id: 'workflow_name', label: localization['wf-name']}) + 
	loadFormTemplate({type: 'textarea', id: 'workflow_description', label: localization['description']});
	return str;
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadServiceRequestInfo(query) {
	clearTimeout(tout);
	doAjaxRequest({url: 'ServiceRequestInfo', base_path: settings.base_path, query: query}, function(response) {
		var str = '<div class="rollback-container">';
		$.each(response.data, function(key, value) {
			str += '<div class="workflow-group" jobid="' + value.jobid + '">\
				<h2 class="group-workflow-name"><span>' + value.name + '</span></h2>';
				if(value.subwflist.length > 0) {
					str += '<dl class="sub-worflows expand">';
					$.each(value.subwflist, function(key, workflow) {
						str += '<dt id="sub-' + workflow.jobid + '" class="sub-workflow-name"><a>' + workflow.wname + '</a></dt>';
						if(workflow.tasklist.length > 0) {
							str += '<dd class="workflow-tasks-list" id="sub-' + workflow.jobid + 'EX">\
								<ul class="">';
								$.each(workflow.tasklist, function(key, task) {
									str += '<li taskid="' + workflow.jobid + '_' + task.task_id + '"><span id="label_' + task.task_id + '">' + task.name + '</span></li>';
								});
								str += '</ul>\
							</dd>';
						}
					});
					str += '</dl>';
				}
			str += '</div>';
		});
		str += '<br class="clear">\
		</div>';
		initScroller($('.workflow-container .workshop .scroller'));
		$('.workflow-info').html(str);
		var height = parseInt($('.workflow-container').height()) - 75;
		$('.workflow-container .workshop .scroller').css('height', height + 'px').css('max-height', height + 'px');
		loadJobRevertStatus(query, true);
	}, doNothing);
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function loadJobRevertStatus(query, notify) {
	clearTimeout(rout);
	var state, flag = false, jid;
	loadJobLogs(query.jobid, 'basic', notify);
	doAjaxRequest({url: 'RollbackStatus', base_path: settings.base_path, query: query, notify: notify}, function(response) {
		$.each(response.data.rbstatus, function(key, value) {
			state = ''; state1 = '';
			$.each(value.status, function(key, status) {
				jid = status.execid.split('_');
				switch(status.status) {
					case 'READY':
						//state = '';
						state1 = ''; flag = true;
						$(".workflow-log .mCSB_container .log_" + jid[0]).remove();
						break;
					case 'EXECUTING':
						state = 'active'; state1 = 'active'; flag = true;
						break;
					case 'FAILED':
						state = 'failed'; state1 = 'failed';
						break;
					case 'COMPLETED':
						state = 'done'; state1 = 'done';
						break;
				}
				$('.workflow-group[jobid="' + value.jid + '"]').find('.workflow-tasks-list').find('li[taskid="' + status.execid + '"]').removeClass('active done failed').addClass(state1);
			});
			$('.workflow-group[jobid="' + value.jid + '"]').children('h2.group-workflow-name').removeClass('active done failed').addClass(state);
		});
		$('dd.workflow-tasks-list').each(function(index) {
			if($(this).find('li.done').length > 0) $(this).prev('dt').removeClass('active done failed').addClass('done');
			if($(this).find('li.active').length > 0) $(this).prev('dt').removeClass('active done failed').addClass('active');
			else if($(this).find('li.failed').length > 0) $(this).prev('dt').removeClass('active done failed').addClass('failed');
		});
		if(flag)
			rout = setTimeout(function() {loadJobRevertStatus(query, false);}, 3000);
	}, function() {
		rout = setTimeout(function() {loadJobRevertStatus(query, false);}, 3000);
	});
}
