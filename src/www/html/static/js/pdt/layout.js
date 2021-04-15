var stage = 0, tout, rout, no_steps = 4, systemInfo, localization, macs = [], hardwares = {}, hardwareStacks = {};
var current_step = 1, skipValidation = 0, goTo, loaderCnt, requestCallback, callbackFlag = false;
var resetTimeout, deviceToReset = [];
$(document).ready(function() {
	if(navigator.userAgent.indexOf('Firefox') > -1) $('body').addClass('firefox');
	var lang = navigator.language || navigator.userLanguage;

	/**
	  * @desc it will load the configuration from a settings json file such as ui theme, language and etc.
	*/
	$.getJSON("settings.json", function(json) {
		settings = json;
		$('body').addClass(settings.layout.theme);
		$.getJSON('static/localization/' + lang + '.json', {_: new Date().getTime()}, function() {
		}).done(function(json) {
			localization = json;
			loadPageContent();
		}).fail(function() {
			$.getJSON('static/localization/en-US.json', {_: new Date().getTime()}, function(json) {
				localization = json;
				loadPageContent();
			});
		});
	});
	
	/**
	  * @desc event registration for masking the ip address input fields.
	*/
	$('.ipaddress').mask('099.099.099.099');
	
	/**
	  * @desc event registration for moving back.
	*/
	$('body').delegate('.back.transition', 'click', function(e) {
		closeModel();
	});

	/**
	  * @desc event registration for closing/hiding a notification popup with certain animation.
	*/
	$('body').delegate('.close-notification', 'click', function(e) {
		$(this).closest('.notification').removeClass('bounceInRight').addClass('bounceOutRight');
	});
	
	/**
	  * @desc event registration for removing a file from the selected list.
	*/
	$('body').delegate('.remove-file', 'click', function(e) {
		$(this).closest('p').parent().remove();
	});

	/**
	  * @desc .
	*/
	$('body').delegate('.sf-done .sf-nav-subtext, .sf-done .sf-nav-number', 'click', function(e) {
		var step = $(this).parent().children("div.sf-nav-number").children("span.sf-nav-number-inner").text();
		$('#wizard li a.done[rel="' + step + '"]').trigger('click');
	});

	/**
	  * @desc event registration for accepting the terms and agreement option.
	*/
	$('body').delegate('.agree-terms', 'click', function(e) {
		if(!$('#terms_aggreement').is(':checked')) {
			$('.agreement-container').find('.help-block').show().html(ucfirst(localization['terms_cond_acceptance']));
			return false;
		}
		doAjaxRequest({url: 'EulaAgreement', base_path: settings.base_path, method: 'PUT', query: {isagree: true}, container: '.modal-inset'}, function(response) {
			closeModel();
		}, doNothing);
	});
	
	/**
	  * @desc event registration for opening a link in new window/tab.
	*/
	$('body').delegate('.external_link', 'click', function(e) {
		e.stopPropagation();
		window.open(settings[$(this).attr('name') + '_url'], '_blank');
	});

	/**
	  * @desc event registration for showing the software/tool information.
	*/
	$('body').delegate('.about-us', 'click', function(e) {
		e.stopPropagation();
		clearTimeout(resetTimeout);
		doAjaxRequest({url: 'System', base_path: settings.base_path, container: '.modal-body'}, function(response) {
			var str = '<div class="pull-right">\
				<label class="title title-label pointer icon-with-link pull-right">\
					<a href="javascript:;" class="system-log icon-with-link ml10"><i class="fa fas fa-clipboard-list"></i> <span class="">' + localization['system-log'] + '</span></a>';
					if(systemInfo.current_step >= 4)
						str+= '<a href="javascript:;" class="hardware_reset icon-with-link ml10"><i class="fa fa-sync red-text"></i> <span class="red-text">' + localization['hardware-reset'] + '</span></a>';
					str += '<a href="javascript:;" class="factory_reset icon-with-link ml10"><i class="fa fa-sync red-text"></i> <span class="red-text">' + localization['factory-reset'] + '</span></a>\
				</label>\
				<div class="clear"></div>\
			</div>\
			<div class="clear"></div>\
			<div class="warning-msg"></div>\
			<div class="about-us-info" style="overflow: auto;">\
				<div class="control-group">\
					<label class="title col-lg-3 col-md-4 col-sm-4 col-xs-4">' + localization['version'] + ':</label>\
					<label class="controls col-lg-9 col-md-8 col-sm-8 col-xs-8">' + response.data.version + '</label>\
					<div class="clear"></div>\
				</div>\
				<div class="clear"></div>\
				<div class="control-group">\
					<label class="title col-lg-3 col-md-4 col-sm-4 col-xs-4">' + localization['copyright'] + ':</label>\
					<label class="controls col-lg-9 col-md-8 col-sm-8 col-xs-8">' + response.data.copyright + '</label>\
					<div class="clear"></div>\
				</div>\
				<div class="clear"></div>';
				if(typeof response.data.report_logo != 'undefined' && response.data.report_logo != '') {
					var filename = 'static/images/' + response.data.report_logo;
					if(filename.fileExists()) {
						str += '<div class="control-group">\
							<label class="title col-lg-3 col-md-4 col-sm-4 col-xs-4"></label>\
							<label class="controls col-lg-9 col-md-8 col-sm-8 col-xs-8">\
								<img class="report_logo" src="static/images/' + response.data.report_logo + '" style="width: 200px; height: 52px;"></img>\
							</label>\
							<div class="clear"></div>\
						</div>';
					}
				}
				str += '<div class="control-group import_logo">\
					<label class="title col-lg-3 col-md-4 col-sm-4 col-xs-4">\
						<span class="">Logo:</span>\
					</label>\
					<div class="controls col-lg-9 col-md-8 col-sm-8 col-xs-8">' +
						loadFormField({type: 'file', id: 'import_logo', name: 'uploadfile', label: 'Logo', holder: 'import_logo', mandatory: true}) +
						'<div class="clear"></div>\
						<div class="help-block"></div>\
					</div>\
					<div class="clear"></div>\
				</div>\
				<div class="clear"></div>\
			</div>\
			<div class="reset-hardware-info"></div>\
			<div class="clear"></div>';
			openModel({title: localization['about'], body: str, buttons: {'close': closeModel}});
			var file_format = {type: 'png, jpg, jpeg', format: /(\.|\/)(png|jpg|jpeg)$/i};
			uploadHandler('ImportLogo', true, settings.base_path, 'import_logo', file_format.format, true, importLogo, doNothing) +
			$(".import_logo .file_format").html("(" + localization['allowed-format'] + ": <b>" + file_format.type + "</b>)");
			$(".import_logo .file_format").after("<div>Recommended size: 200 X 50 px</div>");
		}, doNothing);
	});
	
	/**
	  * @desc event registration for doing factory reset.
	*/
	$('body').delegate('.factory_reset', 'click', function(e) {
		$('.modal-inset').append(popupConfirmation('factory-reset-confirm', localization['confirmation'], localization['reset-confirm']));
	});
	$('body').delegate('.factory-reset-confirm', 'click', function(e) {
		resetTool();
	});
	
	/**
	  * @desc event registration for doing hardware reset.
	*/
	$('body').delegate('.hardware_reset', 'click', function(e) {
		e.stopPropagation();
		doAjaxRequest({url: 'ResetStatus', base_path: settings.base_path, container: '.model-inset'}, function(response) {
			if(response.data.length > 0) {
				loadResetHardwares(response);
				updateResetStatus();
			} else {
				doAjaxRequest({url: 'DevicesToReset', base_path: settings.base_path, container: '.model-inset', notifyContainer: '.modal-inset .warning-msg'}, function(response) {
					loadResetHardwares(response);
					if(!$('#hardware-reset-btn').length) {
						setTimeout(function() {
							$('.form-footer #hardware-reset-btn').remove();
							$('.form-footer').append('<div class="pull-right"><button type="button" id="hardware-reset-btn" class="primary">Reset</button></div>');
						}, 2000);
					}
				}, doNothing);
			}
		}, doNothing);
	});
	$('body').delegate('#hardware-reset-btn', 'click', function(e) {
		$(this).attr('disabled', true);
		resetHardwares(deviceToReset, {force: 0});
	});
	$('body').delegate('.hardware-reset-confirm', 'click', function(e) {
		$(this).attr('disabled', true);
		var obj = {force: 1};
		$("#confirmation_frm :input").each(function() {
			if($(this).attr('type') != 'button' && $(this).attr("name").length > 0) {
				obj[$(this).attr("name")] = this.checked;
			}
		});
		resetHardwares(deviceToReset, obj);
	});
	
	/**
	  * @desc event registration for downloading the logs from the server.
	*/
	$('body').delegate('.system-log', 'click', function(e) {
		e.stopPropagation();
		doAjaxRequest({url: 'ExportLog', base_path: settings.base_path}, function(response) {
			if(typeof response.data != 'undefined') {
				var url = location.protocol + '//' + window.location.host + '/static/downloads/' + response.data;
				if(url.fileExists()) {
					download(location.protocol + '//' + window.location.host + '/static/downloads/' + response.data);
				} else showError({message: localization['file_not_found']}, 'ExportLog');
			} else showError(response.status, 'ExportLog');
		}, doNothing);
		return false;
	});
});

/**
  * @desc it will update the systemInfo global variable based on the server response received via HTTP.
  * @param object $options - the object received from the server(Systems API).
*/
function updateDeploymentSettings(options) {
	systemInfo = {
		current_step: '1',
		config_mode: 'manual',
		stacktype: '',
		subtype: '',
		deployment_type: 'basic'
	};
	systemInfo = $.extend({}, systemInfo, options);
}

function importLogo(response) {
	systemInfo.report_logo = response.data;
	if($('.report_logo').length)
		$('.report_logo').attr('src', 'static/images/' + response.data + '?t=' + Math.random());
	else {
		var str = '<div class="control-group">\
			<label class="title col-lg-3 col-md-4 col-sm-4 col-xs-4"></label>\
			<label class="controls col-lg-9 col-md-8 col-sm-8 col-xs-8">\
				<img class="report_logo" src="static/images/' + response.data + '" style="width: 200px; height: 52px;"></img></div>\
			</label>\
			<div class="clear"></div>\
		</div>';
		$('.control-group.import_logo').before(str);
	}
}
/**
  * @desc this method will generate tooltip on the given input dom element.
  * @param string $container - the container selector, for which element tooltip event should bind with.
*/
function initTooltip(container, obj) {
	if(typeof obj == 'undefined') obj = {};
	var defaults = {
		animationIn: 'bounceIn',
		animationOut: 'bounceOut',
		titleBackground: 'rgb(247, 124, 61)',
		background: '#FFF',
		color: '#454545',
		tooltipHover: true,
		width: false,		// Dynamic width
		maxWidth: 600
	};
	var obj = $.extend({}, defaults, obj);
	$(container + ' .tipso').tipso(obj);
}

/**
  * @desc it is used to reset the tool to initial state.
*/
function resetTool() {
	doAjaxRequest({url: 'PDTReset', base_path: settings.base_path, container: '.model-inset'}, function(response) {
		closeModel();
		systemInfo = null;
		$.removeCookie(settings.cookie_name + "-jobinfo", {path: '/'});
		setTimeout(function() {
			location.reload();
		}, 1000);
	}, doNothing);
}

function loadResetHardwares(response) {
	var str = '<div class="control-group">\
		<div class="title col-lg-12 col-md-12 col-sm-12">\
			<h4>List of Devices:</h4>\
			<table>';
				$.each(response.data, function(key, value) {
					deviceToReset.push(value['serial_no']);
					value['device_type'] = (value['device_type'] == 'PURE') ? 'FlashArray': value['device_type'];
					str += '<tr class="" serial_no="' + value['serial_no'] + '">\
						<td>' + value['device_name'] + '</td>\
						<td>' + value['serial_no'] + '</td>\
						<td>' + value['ipaddress'] + '</td>\
						<td>' + value['device_type'] + '</td>\
						<td width="50" class="hardware-reset-status"></td>\
					</tr>';
					if(value['reset_status'] == 'in-progress') flag = false;
				});
			str += '</table>';
	$('.about-us-info').animate({opacity: '0', height: '0px'});
	$('.reset-hardware-info').html(str).show(2000);
}

/**
  * @desc it is used to reset the tool as well as hardware to its initial state.
*/
function resetHardwares(obj, query) {
	doAjaxRequest({url: 'DeviceReset', base_path: settings.base_path, method: 'POST', data: obj, query: query, container: '.model-inset', formContainer: 'hardware-reset-confirm', notifyContainer: '.modal-inset .warning-msg', confirm_title: '<span class="red-text">' + localization['continue-confirm'] + '</span>'}, function(response) {
		$('.modal-inset .dialog').remove();
		$('#hardware-reset-btn').hide();
		updateResetStatus();
	}, function(){
		$('#hardware-reset-btn, .hardware-reset-confirm').attr('disabled', false);
		$('.modal-inset .dialog').remove();
	});
}

function updateResetStatus() {
	var str = '', flag = true, notifyContainer = '.modal-inset .warning-msg';
	doAjaxRequest({url: 'ResetStatus', base_path: settings.base_path, notifyContainer: notifyContainer}, function(response) {
		$.each(response.data, function(key, value) {
			switch(value['reset_status']) {
				case 'completed':
					str = '<span class="green-text fa fa-check-circle medium"></span>';
					break;
				case 'in-progress':
					flag = false;
					str = '<span class="blue-text fa fa-progress medium"></span>';
					break;
				case 'failed':
					flag = false;
					$(notifyContainer).find('.notification.inline:not(.fixed)').remove();
					if($(notifyContainer).find('.notification.inline').length)
						$(notifyContainer).find('.notification.inline').after('<h5 class="notification danger inline"><i class="fa fa-warning"></i> Unable to reset the hardware. Please reset it manually.</h5>');
					else $(notifyContainer).prepend('<h5 class="notification danger inline"><i class="fa fa-warning"></i> Unable to reset the hardware. Please reset it manually.</h5>');
					
					$('.form-footer #hardware-reset-btn').after('<button type="button" class="factory_reset primary">' + localization['factory-reset'] + '</button>');
					$('.form-footer #hardware-reset-btn').remove();
					
					str = '<span class="red-text fa fa-exclamation-triangle medium tipso tipso_style" data-tipso-title="Failed" data-tipso="' + value['error'] + '"></span>';
					break;
			}
			if(!$('.reset-hardware-info tr[serial_no="' + value['serial_no'] + '"] .hardware-reset-status .tipso').length) {
				$('.reset-hardware-info tr[serial_no="' + value['serial_no'] + '"] .hardware-reset-status').html(str).attr('reset_status', value['reset_status']);
				initTooltip('.reset-hardware-info tr[serial_no="' + value['serial_no'] + '"] .hardware-reset-status');
			}
		});
		if(flag) {
			//resetTool();
			closeModel();
			systemInfo = null;
			$.removeCookie(settings.cookie_name + "-jobinfo", {path: '/'});
			setTimeout(function() {
				location.reload();
			}, 1000);
		} else {
			resetTimeout = setTimeout(function() {
				updateResetStatus();
			}, 5000);
		}
	}, doNothing);
}
/**
  * @desc initiate/bind scrollbar(vertical/horizandal) inside a given html dom element
  * @param object $dom - the html dom element where to create the scrollbar
*/
function initScroller(dom) {
	dom.mCustomScrollbar({axis: 'xy', theme:"minimal-dark", scrollbarPosition: "outside"});
}

/**
  * @desc initiate/bind range slider event to the given html dom element
  * @param object $dom - the html dom element to be displayed as range slider
  * @param int $from - the minimum value of the slider
  * @param int $to - the max value of the slider
*/
function initRangeSlider(dom, options) {
	var defaults = {
		type: 'double',
		grid: true,
		force_edges: true,
		drag_interval: true,
		input_values_separator: '-',
		min: 0,
		max: 100
	};
	var options = $.extend({}, defaults, options);
	dom.ionRangeSlider(options);
	/* {
		min: options.from,
		max: options.to,
		from: options.from,
		to: parseInt(options.from) + options.min_limit,
		min_interval: options.min_limit,
		max_interval: options.max_limit
	}); */
}
function convertToPercent(num, min, max) {
	return (num - min) / (max - min) * 100;
}

/**
  * @desc initiate/bind multiselect dropdown event on the given html dom element
  * @param object $dom - the html dom element to be displayed as multiselect dropdown
  * @param string $label - the label to be displayed on the multiselect dropdown
  * @param bool $isSearch - the flag whether to show search option or not
  * @param bool $isSelectAll - the flag to have show select all option or not
  * @param int $column - the no of columns to to displayed on each row
*/
function initMultiSelect(dom, label, isSearch, isSelectAll, column) {
	dom.multiselect({
		columns: column,
		placeholder: localization['select'] + ' ' + label,
		search: isSearch,
		searchOptions: {
			'default': localization['search'] + ' ' + label
		},
		selectAll: isSelectAll
	});
	if(dom.hasClass('hide')) {
		dom.next('.ms-options-wrap').addClass('hide');
	}
}

/**
  * @desc .
  * @param object $response - .
*/
function bindTagifyEvent(selector, label, pattern) {
	$(selector).tagsinput();
	$(selector).on('beforeItemAdd', function(event) {
		if(!pattern.test(event.item)) event.cancel = true;
	});
}