/**
  * @desc Render the html page.
*/
function loadPageContent() {
	clearTimeout(tout);
	eulaContent();

	doAjaxRequest({url: 'System', base_path: settings.base_path, notify: false}, function(response) {
		updateDeploymentSettings(response.data.deployment_settings);
		systemInfo.dhcp_status = response.data.dhcp_status;
		
		$('.content').html(wizardTemplate());
		var mode = true;
		if(typeof systemInfo.deployment_type != 'undefined' && systemInfo.deployment_type == 'advanced') mode = false;
		$('.toggle-select.deployment-type').toggles({type: 'select', on: mode, width: 'auto', height: '22px', text: {on: localization['basic'], off: localization['advanced']}});
		$('.toggle-select.deployment-type').on('toggle', function(e, active) {
			if(active) {
				loadWorkflow('basic');
			} else {
				loadWorkflow('advanced');
			}
		});

		$('.software-version').html('<span>' + localization['version'] + ': ' + response.data.version + '</span>');
		$('title').html(response.data.name);
		$('.copyright').html('<span>' + response.data.copyright + '</span>');
		if(typeof systemInfo.current_step != 'undefined') {
			skipValidation = 1;
			stage = parseInt(systemInfo.current_step);
		}

		// Create wizard by binding the object with the html dom.
		$('#wizard').smartWizard({
			selected: parseInt(stage) - 1,
			keyNavigation: false,
			transitionEffect: 'slideleft',
			onLeaveStep: leaveAStepCallback,
			onShowStep: onShowCallback,
			onFinish: onFinishCallback,
			contentCache: false,
			enableFinishButton: true,
			hideButtonsOnDisabled: false,
			buttonOrder: ['prev', 'next', 'finish'],
			labelFinish: localization['deploy']
		});
		var height = parseInt($(window).height()) - 140;
		$('.swMain .stepContainer').css('height', height + 'px');
		if(systemInfo.dhcp_status == "enabled") {
			$('.dhcp-settings').removeClass('hide');
			$('#enable-dhcp').prop('checked', true);
		}
	}, function(response) {
		$('.content').html('<div class="error-wall">\
			<div class="error-container">\
				<h3>' + localization['page_error_mgs'] + '</h3>\
				<p>' + localization['page_error_desc'] + '</p>\
			</div>\
		</div>');
		tout = setTimeout(function() {
			loadPageContent();
		}, 2000);
	});
	return false;
}

/**
  * @desc Render the eula agreement popup.
*/
function eulaContent() {
	doAjaxRequest({url: 'EulaContent', base_path: settings.base_path, notify: false}, function(response) {
		if(!response.data.isagree) {
			var str = '<div class="agreement-container">\
				<div class="agreement"></div>\
				<div class="checkbox checkbox-primary widget-subtitle">\
					<input id="terms_aggreement" class="styled" type="checkbox" value="1">\
					<label for="terms_aggreement" class="nopadding r-height"> ' + localization['i_agree'] + '</label>\
				</div>\
				<span class="help-block"></span>\
				<div class="center"><button type="button" class="agree-terms primary">' + localization['next'] + '</button></div>\
			</div>';
			openModel({title: localization['eula'], body: str, buttons: {}});
			$('.closeModel, .form-footer').hide();
			initScroller($('.agreement'));
			$('.modal-inset').addClass('big');
			var height = parseInt($('.modal-inset').height()) - 146;
			$('.agreement').css('height', height + 'px').css('max-height', height + 'px');
			$.ajax({
				url: 'static/' + response.data.url,
				success: function(data) {
					$('.agreement .mCSB_container').append(nl2br(data, true) + '<div class="clear"></div>');
				}
			});
		}
	}, doNothing);
}

/**
  * @desc This method will give the HTML template string of the wizard.
  * @return string $str - the html string
*/
function wizardTemplate() {
	var str = '<div class="datacenter-wizard">\
		<div class="form-3 sf-wizard clearfix sf-t1 sf-slide sf-s-0 sf-nomob">\
			<input type="hidden" name="issubmit" value="1">\
			<div class="sf-nav-wrap clearfix sf-nav-smmob sf-nav-top">\
				<ul class="sf-nav clearfix" style="clear: both;">\
					<li class="sf-nav-step sf-li-number sf-active sf-nav-link">\
						<span class="sf-nav-subtext">' + localization['flashstacks'] + '</span>\
						<div class="sf-nav-number"><span class="sf-nav-number-inner">1</span></div>\
						<div></div>\
					</li>\
					<li class="sf-nav-step sf-li-number sf-active sf-nav-link">\
						<span class="sf-nav-subtext">' + localization['discovery'] + '</span>\
						<div class="sf-nav-number"><span class="sf-nav-number-inner">2</span></div>\
						<div></div>\
					</li>\
					<li class="sf-nav-step sf-li-number sf-nav-unlink">\
						<span class="sf-nav-subtext">' + localization['configuration'] + '</span>\
						<div class="sf-nav-number"><span class="sf-nav-number-inner">3</span></div>\
						<div></div>\
					</li>\
					<li class="sf-nav-step sf-li-number sf-nav-unlink">\
						<span class="sf-nav-subtext">' + localization['device-initialization'] + '</span>\
						<div class="sf-nav-number"><span class="sf-nav-number-inner">4</span></div>\
						<div></div>\
					</li>\
					<li class="sf-nav-step sf-li-number sf-nav-unlink">\
						<span class="sf-nav-subtext">' + localization['deployment'] + '</span>\
						<div class="sf-nav-number"><span class="sf-nav-number-inner">5</span></div>\
						<div></div>\
					</li>\
				</ul>\
			</div>\
			<div id="wizard" class="swMain">\
				<ul>\
					<li>\
						<a href="#step-1">\
							<label class="stepNumber">1</label>\
						</a>\
					</li>\
					<li>\
						<a href="#step-2">\
							<label class="stepNumber">2</label>\
						</a>\
					</li>\
					<li>\
						<a href="#step-3">\
							<label class="stepNumber">3</label>\
						</a>\
					</li>\
					<li>\
						<a href="#step-4">\
							<label class="stepNumber">4</label>\
						</a>\
					</li>\
					<li>\
						<a href="#step-5">\
							<label class="stepNumber">5</label>\
						</a>\
					</li>\
				</ul>\
				<div id="step-1" class="nopadding">\
					<div class="smartwidget">\
						<h5 class="StepTitle widget-title">' + localization['step'] + ' 1: ' + localization['flashstack-deployments'] + '</h5>\
						<div class="widget-content border">\
							<div class="flashstack_types scroller"></div>\
						</div>\
					</div>\
				</div>\
				<div id="step-2" class="nopadding">\
					<div class="smartwidget">\
						<h5 class="StepTitle widget-title">' + localization['step'] + ' 2: ' + localization['flashstack-discovery'] + '</h5>\
						<div class="">\
							<div class="col-lg-6 col-md-6 col-sm-12 col-xs-12 nopadding">\
								<div class="loader-msg"></div>\
							</div>\
							<div class="col-lg-6 col-md-6 col-sm-12 col-xs-12 nopadding">\
								<div class="dropdown pull-right">\
									<button class="dropbtn" type="button"><i class="fa fa-bars"></i></button>\
									<div class="dropdown-content">\
										<a href="javascript:;" class="add-device icon-with-link"><i class="fa fa-plus-circle"></i> ' + localization['add-device'] + '</a>\
										<a href="javascript:;" class="dhcp-settings hide icon-with-link"><i class="fa fa-cog"></i> ' + localization['dhcp-settings'] + '</a>\
										<a type="" href="javascript:;" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['iso-library'] + '</a>\
									</div>\
								</div>\
								<div class="pull-right title-label toggle-switch">\
									<label class="title pull-left">' + localization['enable-dhcp'] + ':</label>\
									<div class="controls pull-left">\
										<div class="slideThree pull-right">\
											<input type="checkbox" value="None" id="enable-dhcp" name="check" />\
											<label for="enable-dhcp"></label>\
										</div>\
									</div>\
								</div>\
							</div>\
						</div>\
						<div class="clear"></div>\
						<div class="networkList dataList table">\
							<table class="table border action-table" id="network_list">\
								<thead>\
									<tr>\
										<th colspan="3" class="widget-header">' + localization['devices'] + '</th>\
										<th colspan="4" class="widget-header">\
											<div class="pull-right required-hardwares-flash"></div>\
										</th>\
									</tr>\
									<tr>\
										<th width="50"></th>\
										<th width="50"></th>\
										<th width="20%">' + localization['device-type'] + '</th>\
										<th width="">' + localization['make'] + '/' + localization['model'] + '</th>\
										<th width="20%">' + localization['ip'] + '</th>\
										<th width="20%">' + localization['serial'] + '</th>\
										<th width="40"></th>\
									</tr>\
								</thead>\
							</table>\
							<div class="scroller"></div>\
						</div>\
					</div>\
				</div>\
				<div id="step-3" class="initial-setup nopadding">\
					<div class="smartwidget">\
						<h5 class="StepTitle widget-title">' + localization['step'] + ' 3: ' + localization['configuration'] + '</h5>\
						<div class="widget-content border"></div>\
					</div>\
				</div>\
				<div id="step-4" class="device-initialization nopadding">\
					<div class="smartwidget">\
						<h5 class="StepTitle widget-title">' + localization['step'] + ' 4: ' + localization['device-initialization'] + '</h5>\
						<div class="widget-content border"></div>\
					</div>\
				</div>\
				<div id="step-5" class="deployment nopadding">\
					<div class="smartwidget">\
						<h5 class="StepTitle widget-title">' + localization['step'] + ' 5: ' + localization['deployment'] + '</h5>\
						<div class="widget-content nopadding">\
							<div class="workflowsList dataList table">\
								<div class="list-workflows">\
									<table class="table border new action-table" id="workflows_list">\
										<thead>\
											<tr>\
												<th colspan="4" class="widget-header relative">\
													<span>' + localization['workflows'] + '</span>' +
													loadFormField({type: 'toggle', id: 'deployment-type pull-right dark'}) +
												'</th>\
											</tr>\
											<tr class="advanced hide">\
												<th width="50" align="center">#\
													<div class="hide checkbox checkbox-info pull-left">\
														<input id="all-workflow" type="checkbox">\
														<label for="all-workflow" class="nopadding"></label>\
													</div>\
												</th>\
												<th width="30%">' + localization['name'] + '</th>\
												<th width="">' + localization['desc'] + '</th>\
												<th width="150" align="center">&nbsp;</th>\
											</tr>\
										</thead>\
									</table>\
									<div class="scroller list-jobs"></div>\
									<div class="workflowsRollbackInfo scroller" style="display: none;"></div>\
								</div>\
							</div>\
							<div class="workflowsInfo">' + loadWorkflowInfoTemplate('Info') + '</div>\
						</div>\
					</div>\
				</div>\
			</div>\
		</div>\
	</div>';
	return str;
}

/**
  * @desc method to navigate the wizard to a specific step.
  * @param number $step - the step number to move.
*/
function navigateStep(step) {
	goTo = step; skipValidation = 1; skipStep = true;
	$('#wizard').smartWizard('goToStep', step);
	return false;
}

/**
  * @desc set of commands to execute when a user leave from a step.
  * @param dom object $obj - the dom object which contains the current step element.
  * @param object $context - the object which contains the wizard navigation information.
*/
var skipStep = false;
function leaveAStepCallback(obj, context) {
	if(!skipStep) {
		if(parseInt(context.fromStep) > parseInt(context.toStep) && ($('.buttonPrevious').hasClass('buttonDisabled') || $('.buttonPrevious').hasClass('disable'))) {
			return false;
		} else if(parseInt(context.fromStep) < parseInt(context.toStep) && ($('.buttonNext').hasClass('buttonDisabled') || $('.buttonNext').hasClass('disable'))) {
			return false;
		}
	
		$('.buttonNext, .buttonPrevious, .buttonFinish').addClass('disable');
		setTimeout(function() {
			$('.buttonNext, .buttonPrevious, .buttonFinish').removeClass('disable');
		}, 1000);
	}

	var step_num = obj.attr('rel');
	if(typeof goTo != 'undefined' && goTo != null) {
		if(step_num == goTo)
			goTo = null;
		else
			return true;
	}
	if(context.fromStep == 5 && context.toStep == 4) {
		navigateStep(2);
	} else if(context.fromStep == 4 && context.toStep == 3) {
		doAjaxRequest({url: 'ClearConfiguration', base_path: settings.base_path, container: '.content-container'}, function(response) {
			if(MDSForConfigure.length == 0 && NEXUSForConfigure.length == 0 && UCSForConfigure.length == 0) {
				navigateStep(2);
			}
		}, doNothing);
	} else if((context.fromStep == 3 && context.toStep == 2) && goTo != 4) {
		var str = '<div class="control-group">\
			<div class="title col-lg-12 col-md-12 col-sm-12"><h4>' + localization['input-lost-msg'] + '</h4></div>\
		</div>\
		<div class="clear"></div>';
		openModel({body: str, buttons: {
			"no": closeModel,
			"yes": function() {
				goTo = 2;
				closeModel();
				$('#wizard').smartWizard('goToStep', 2);
			}
		}});
		return false;
	}
	if(parseInt(context.fromStep) > parseInt(context.toStep)) {
		skipValidation = 1;
		return true;
	}
	if(step_num == 1) {
		if($('.boxes .box.active').length == 0) {
			showNotification(localization['select-flashstack'], 5000);
			return false;
		}
		doAjaxRequest({url: 'DeploymentSettings', base_path: settings.base_path, method: 'POST', data: {stacktype: $('.boxes .box.active').attr('hardware_id'), subtype: $('.boxes .box.active').attr('hardware_id')}, container: '.content-container'}, function(response) {
			systemInfo.stacktype = $('.boxes .box.active').attr('hardware_id');
			systemInfo.subtype = $('.boxes .box.active').attr('hardware_id');
			navigateStep(2);
		}, doNothing);
	} else if(step_num == 2) {
		if($('input[type="checkbox"].devices:checked').length == 0) {
			var flag = true;
			Object.keys(hardwares[systemInfo.stacktype]).some(function(key) {
				if(hardwares[systemInfo.stacktype][key] > $('.networkinfo.Configured').find('.device_type:contains(' + key + ')').length) {
					flag = false;
				}
			});
			if(flag) {
				disableDHCP(false);
				navigateStep(5);
			} else {
				showNotification(localization['device-selection-cnf'], 5000);
				return false;
			}
		}
		if($('.required-hardwares-flash .hardware-types[status="0"]').length > 0) {
			showNotification(localization['device-selection-cnf'], 5000);
			return false;
		}
		MDSForConfigure = [], NEXUSForConfigure = [], UCSForConfigure = [];
		$('.networkinfo.elementInfo.active').each(function(index) {
			switch($(this).find('.device_type').text()) {
				case 'UCSM':
					UCSForConfigure.push({
						type: $(this).find('.device_type').text(), 
						serial: $(this).find('.serial_number').text(), 
						ip: $(this).find('.ip_address').text(),
						mac: $(this).find('.mac_address').text(),
						vendor: $(this).find('.vendor_model').text()
					});
					break;
				case 'Nexus 9k':
					NEXUSForConfigure.push({
						type: $(this).find('.device_type').text(), 
						serial: $(this).find('.serial_number').text(), 
						ip: $(this).find('.ip_address').text(),
						mac: $(this).find('.mac_address').text(),
						vendor: $(this).find('.vendor_model').text()
					});
					break;
				case 'Nexus 5k':
					NEXUSForConfigure.push({
						type: $(this).find('.device_type').text(), 
						serial: $(this).find('.serial_number').text(), 
						ip: $(this).find('.ip_address').text(),
						mac: $(this).find('.mac_address').text(),
						vendor: $(this).find('.vendor_model').text()
					});
					break;
				case 'MDS':
					MDSForConfigure.push({
						type: $(this).find('.device_type').text(), 
						serial: $(this).find('.serial_number').text(), 
						ip: $(this).find('.ip_address').text(),
						mac: $(this).find('.mac_address').text(),
						vendor: $(this).find('.vendor_model').text()
					});
					break;
			}	
		});
		if(MDSForConfigure.length > 0 || NEXUSForConfigure.length > 0 || UCSForConfigure.length > 0) {
			clearTimeout(tout);
			var data = [];
			$.each(UCSForConfigure, function(index, value) {
				data.push(value.vendor);
			});
			doAjaxRequest({url: 'FIGenValidate', base_path: settings.base_path, method: 'POST', data: data, query: {stacktype: systemInfo.subtype}}, function(response) {
				systemInfo.subtype = response.data;
				loadInitialSetupForm();
				navigateStep(3);
			}, function(response) {
				removeProcessingSpinner('.content-container', loaderCnt);
				showNotification(response.status.message, 5000);
			});
			return false;
		} else {
			disableDHCP(false);
			navigateStep(5);
		}
		return false;
	} else if(step_num == 3) {
		validateConfiguration();
		return false;
	} else if(step_num == 4) {
		triggerInitialization();
	}
	$('.sf-nav-step.sf-li-number.sf-nav-link.sf-active').addClass('sf-done');
}

/**
  * @desc set of commands to execute when a user enter into a step.
  * @param dom object $obj - the dom object which contains the current step element.
*/
function onShowCallback(obj) {
	current_step = obj.attr('rel');
	$('.buttonFinish').hide();
	skipValidation = 0;
	if(current_step != 2) goTo = null;
	$('.buttonNext').text(localization['next']).removeClass('hide');
	if(current_step == 1) $('.networkinfo.elementInfo').addClass('active');
	if(current_step == 4) $('.buttonNext').text(localization['initialize']);
	if(current_step == no_steps) {
		$('.buttonFinish').show();
		$('.buttonPrevious').remove();
		$('.buttonNext').addClass('hide');
	}
	if(current_step == 3 && UCSForConfigure.length == 0 && NEXUSForConfigure.length == 0 && MDSForConfigure.length == 0) {
		goTo = 2;
		$('#wizard').smartWizard('goToStep', 2);
		return false;
	}
	if(current_step > 1) {
		if(!systemInfo.stacktype) {
			navigateStep(1);
		}
	}
	$('ul.sf-nav>li.sf-nav-step').removeClass('sf-done');
	for(i = 0; i < current_step; i++)
		$('ul.sf-nav>li.sf-nav-step:eq(' + i + ')').addClass('sf-done');
	triggerAPI();
	$('.sf-nav-step').removeClass('sf-active');
	$('li.sf-nav-step:nth-child(' + current_step + ')').addClass('sf-active sf-nav-link').removeClass('sf-done sf-error sf-nav-unlink');
	$('li.sf-nav-step:nth-child(2)').removeClass('.sf-nav-link').addClass('.sf-nav-unlink');
	if(skipStep) skipStep = false;
}

/**
  * @desc method to execute on finish button.
*/
function onFinishCallback() {
	if(validateAllSteps()) {
		triggerExecute();
	}
}

/**
  * @desc this will validate the entire form before executing the finsh method
  * @return boolean - validation status for entire wizard success or failure.
*/
function validateAllSteps() {
	var isStepValid = true;
	for(i = parseInt(stage)+1; i <= 5; i++) {
		$('#wizard').smartWizard('setError',{stepnum:i,iserror:false});		// Dispaly the validation failure message
		if(validateStep(i) == false) {
			isStepValid = false;
			$('#wizard').smartWizard('setError',{stepnum:i,iserror:true});
		}
	}
	$('.swMain .msgBox .close').hide();
	if(!isStepValid) {
		showNotification(localization['single-row-validation'], 5000);		// Dispaly the validation failure message in a notification popup
		$('.swMain .msgBox .close').show();
	}
	return isStepValid;
}

/**
  * @desc used to validate the given step of the wizard.
  * @param number $step - step number to validate.
  * @return boolean - validation status for the given step success or failure.
*/
function validateSteps(step) {
	var isStepValid = true;
	$('#wizard').smartWizard('setError',{stepnum:step, iserror:false});
	$('.swMain .msgBox .close').hide();
	$('.sf-active.sf-nav-link').addClass('sf-done').removeClass('sf-error');
	$('#wizard').smartWizard('hideMessage');
	if(validateStep(step) == false) {
		isStepValid = false; 
		$('#wizard').smartWizard('setError',{stepnum:step,iserror:true});
		$('.sf-active.sf-nav-link').addClass('sf-error').removeClass('sf-done');
		$('.swMain .msgBox .close').show();
	}
	return isStepValid;
}

/**
  * @desc used to byepass the validation.
  * @param number $step - step number to validate.
  * @return boolean - validation status of the given step success or failure.
*/
function validateStep(step) {
	var isValid = true;
	return isValid;
}

/**
  * @desc it will save the step to the server and trigger the appropriate method based on the wizard movement.
*/
function triggerAPI() {
	$('#wizard').smartWizard('hideMessage');
	doAjaxRequest({url: 'DeploymentSettings', base_path: settings.base_path, method: 'POST', data: {current_step: current_step}, container: '.content-container'}, function(response) {
		systemInfo.current_step = current_step;
		clearTimeout(tout);
		switch(current_step) {
			case "1":
				loadFlashstackTypes();
				break;
			case "2":
				loadDiscovery('.content-container');
				break;
			case "3":
				break;
			case "4":
				loadDevices('.device-initialization');
				break;
			case "5":
				var mode = (typeof systemInfo.deployment_type != 'undefined') ? systemInfo.deployment_type : 'basic';
				loadWorkflow(mode);
				break;
		}
	}, doNothing);
}
