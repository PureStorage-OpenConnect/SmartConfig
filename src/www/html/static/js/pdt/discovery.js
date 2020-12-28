var NEXUSForConfigure = [], MDSForConfigure = [], UCSForConfigure = [], FAForConfigure = [];
$(document).ready(function() {
	/**
	  * @desc event registration for selecting/deselecting a device.
	*/
	$('body').delegate('.networkinfo.elementInfo:not(.non-selectable)', 'click', function(e) {
		if($(this).hasClass('In-progress')) return false;
		selectElement($(this));
		return false;
	});

	/**
	  * @desc event registration for opening the image library.
	*/
	$('body').delegate('.iso-library', 'click', function(e) {
		e.stopPropagation();
		var parentAttr = '', subtypes = {'UCSM': ['ESXi', 'ESXi-kickstart', 'RHEL', 'RHEL-kickstart', 'UCS-infra', 'UCS-blade'], 'MDS': ['MDS', 'MDS-kickstart'],'Nexus':['Nexus 5k','Nexus 9k','Nexus 5k-kickstart']};
		var buttons = {"close": closeModel}, file_format = {type: 'bin, gbin', format: /(\.|\/)(bin|gbin)$/i};
		var attr = $(this).attr('type'), file = $(this).attr('file');
		Object.keys(subtypes).some(function(key) {
			if($.inArray(attr, subtypes[key]) > -1) {
				parentAttr = key; return;
			}
		});
		if(parentAttr == '') parentAttr = attr;
		if(typeof attr !== typeof undefined && attr !== false && attr != '') {
			buttons['select'] = selectISO;
		} else attr = '';
		openModel({title: localization['iso-library'], body: loadISOLibraryForm(attr), buttons: buttons});
		$('.sub_hwtype').addClass('hide');
		loadImages('.tab-content', attr, file);
		attr = (attr == '') ? 'MDS-kickstart' : attr;
		var image_type = attr;
		if(attr == 'ESXi' || attr == 'RHEL') file_format = {type: 'iso', format: /(\.|\/)(iso)$/i};
		else if(attr == 'ESXi-kickstart' || attr == 'RHEL-kickstart') file_format = {type: 'cfg', format: /(\.|\/)(cfg)$/i};
		uploadHandler('ImportImage', false, settings.base_path, 'import_iso', file_format.format, false, doNothing, doNothing);
		$(".import_iso .file_format").html("(" + localization['allowed-format'] + ": <b>" + file_format.type + "</b>)");

		Object.keys(subtypes).some(function(key) {
			if($.inArray(attr, subtypes[key]) > -1) {
				attr = key; return;
			}
		});
		if($('.sub_hwtype .sub_image.' + attr).length > 0)
			$('.sub_hwtype').removeClass('hide');

		$('.toggle-select.image_mode').toggles({type: 'select', on: true, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['firmware'], off: localization['operating_system']}});
		$('.toggle-select.image_mode').on('toggle', function(e, active) {
			if(active) {
				$('#iso_image_mds').trigger('click');
				$('#import_form .firmware').removeClass('hide');
				$('.sub_image.MDS').parent().removeClass('hide');
				$('.sub_hwtype .radio.radio-inline.operating_system, .sub_ostype').addClass('hide');
				$('#iso_image_mds_kickstart').trigger('click');
				$('.os_sub_image').prop('checked', false);
			} else {
				$('#iso_image_ucsm').trigger('click');
				$('.sub_hwtype .radio.radio-inline').addClass('hide');
				$('#import_form .firmware').addClass('hide');
				$('.sub_hwtype .radio.radio-inline.operating_system, .sub_ostype').removeClass('hide');
				$('.sub_hwtype #iso_image_os').trigger('click');
				$('#iso_image_esxi_iso').trigger('click');
			}
		});
		$('[name="image_type"][value="' + parentAttr + '"]').addClass('active').trigger('click');
		$('.sub_image[value="' + image_type + '"]').addClass('active').trigger('click');
		if(image_type == 'ESXi' || image_type == 'ESXi-kickstart') {
			var myToggle = $('.toggle-select.image_mode').data('toggles');
			myToggle.toggle(false);
			$('#iso_image_os').trigger('click');
			if(image_type == 'ESXi')
				$('#iso_image_esxi_iso').trigger('click');
			else if(image_type == 'ESXi-kickstart')
				$('#iso_image_esxi_kickstart').trigger('click');
		} else if(image_type == 'RHEL' || image_type == 'RHEL-kickstart') {
			var myToggle = $('.toggle-select.image_mode').data('toggles');
			myToggle.toggle(false);
			$('#iso_image_os').trigger('click');
			if(image_type == 'RHEL')
				$('#iso_image_rhel_iso').trigger('click');
			else if(image_type == 'RHEL-kickstart')
				$('#iso_image_rhel_kickstart').trigger('click');
		}
		return false;
	});

	/**
	  * @desc event registration for selecting image type & sub type.
	*/
	$('body').delegate('.iso_image', 'change', function(e) {
		$('.sub_image').parent().addClass('hide');
		$('.sub_hwtype .sub_image').prop('checked', false);
		if($('.sub_hwtype .sub_image.' + this.value).length == 0)
			updateUploadEvent(this.value);
		$('.sub_hwtype .sub_image.' + this.value).first().trigger('click');
		$('.sub_image.' + this.value).parent().removeClass('hide');

		var myToggle = $('.toggle-select.image_mode').data('toggles');
		$('#import_form .operating_system').removeClass('hide');
		if(myToggle.active) {
			$('#import_form .operating_system').addClass('hide');
		}
	});
	$('body').delegate('.sub_image', 'change', function(e) {
		$('.os_sub_image').parent().addClass('hide');
		$('.os_sub_image.' + this.value).parent().removeClass('hide');
		if(this.value == 'ESXi')
			$('#iso_image_esxi_iso').trigger('click');
		else if(this.value == 'RHEL')
			$('#iso_image_rhel_iso').trigger('click');
		else
			$("[name='image_os_sub_type']").prop('checked', false);
		updateUploadEvent(this.value);
	});
	$('body').delegate('.os_sub_image', 'change', function(e) {
		updateUploadEvent(this.value);
	});

	/**
	  * @desc event registration for importing the selected image to library.
	*/
	$('body').delegate('#importBtn', 'click', function(e) {
		$('.control-group.import_iso .files > .error-msg').remove();
		if($('.control-group.import_iso .files button:not(:disabled)').length == 0) {
			$('.control-group.import_iso .files').prepend('<div class="red-text error-msg">Please select a file to upload</div>');
			return false;
		}
		doImport('.modal-inset', '.import_iso', true, function(response) {
			var attr = $('#list-images').attr('type');
			loadImages('.tab-content', attr, '');
		}, doNothing);
	});

	/**
	  * @desc event registration for selecting/deselecting an image from the library.
	*/
	$('body').delegate('.images-list tr:not(.head)', 'click', function(e) {
		$('.images-list tr').removeClass('selected');
		$(this).addClass('selected');
	});

	/**
	  * @desc event registration for opening a confirmation to delete an image.
	*/
	$('body').delegate('.delete-image', 'click', function(e) {
		$('.modal-inset').append(popupConfirmation('image_delete_confirm', localization['delete-image-confirm']));
	});

	/**
	  * @desc event registration for deleting an image.
	*/
	$('body').delegate('.image_delete_confirm', 'click', function(e) {
		var currentObj = $('.images-list tr.selected');
		doAjaxRequest({url: 'DeleteImage', base_path: settings.base_path, data: {imagename: currentObj.attr('primaryid')}, success_notify: true, container: '.modal-inset'}, function(response) {
			$('.closePopup').trigger('click');
			currentObj.addClass('animated bounceOutRight');
			setTimeout(function() {
				var attr = $('#list-images').attr('type');
				loadImages('.tab-content', attr, '');
			}, 500);
		}, doNothing);
	});

	/**
	  * @desc event registration for enabling/disabling the DHCP settings.
	*/
	$('body').delegate('#enable-dhcp', 'change', function(e) {
		$(this).attr("disabled", true);
		setTimeout(function() {
			$('#enable-dhcp').attr("disabled", false);
		}, 500);
		if(this.checked) {
			openModel({title: localization['dhcp-settings'], body: loadDHCPSettingsForm(), buttons: {
				"cancel": function() {
					$('#enable-dhcp').prop('checked', false);
					closeModel();
				},
				"submit": EnableDHCP
			}});
		} else {
			disableDHCP(true);
		}
	});

	/**
	  * @desc event registration for updating the DHCP settings.
	*/
	$('body').delegate('.dhcp-settings', 'click', function(e) {
		e.stopPropagation();
		openModel({title: localization['dhcp-settings'], body: loadDHCPSettingsForm(), buttons: {
			"cancel": closeModel,
			"submit": EnableDHCP
		}});
	});

	/**
	  * @desc event registration for adding a configured device to our components.
	*/
	$('body').delegate('.add-device', 'click', function(e) {
		e.stopPropagation();
		openModel({title: localization['add-device'], body: loadAddDeviceForm(), buttons: {
			"cancel": closeModel,
			"submit": function() {
				var data = {type: $('input[type="radio"][name="hardware_device"]:checked').val(), ip: $('#add_ip_address').val(), username: $('#add_user_name').val(), password: $('#add_password').val()};
				doAjaxRequest({url: 'AddDevice', base_path: settings.base_path, method: 'POST', data: data, container: '.modal-inset', success_notify: true, isValidate: true, formContainer: '.add_device'}, function(response) {
					closeModel();
					loadDiscovery('.content-container');
				}, doNothing);
			}
		}});
	});

	/**
	  * @desc event registration for deleting the configured devices from our components list.
	*/
	$('body').delegate('.delete-device, .delete-devices', 'click', function(e) {
		e.stopPropagation();
		var msg, data;
		if($(this).hasClass('delete-devices')) {
			msg = localization['delete-devices-confirm'];
			data = '';
		} else {
			msg = localization['delete-device-confirm'];
			$('#form_primaryid').val($(this).closest('.elementInfo').attr('primaryid'));
		}
		var str = '<div class="control-group">\
			<div class="title col-lg-12 col-md-12 col-sm-12"><h4>' + msg + '</h4></div>\
		</div>\
		<div class="clear"></div>';
		openModel({body: str, buttons: {
			"no": closeModel,
			"yes": function() {
				doAjaxRequest({url: 'DeleteDevice', base_path: settings.base_path, method: 'GET', data: {mac_list: $('#form_primaryid').val()}, success_notify: true, container: '.content-container'}, function(response) {
					loadDiscovery('.content-container');
					closeModel();
				}, doNothing);
			}
		}});
	});

	/**
	  * @desc event registration for re-initializating the device which got failure during initialization/flashing.
	*/
	$('body').delegate('.re-validate', 'click', function(e) {
		e.stopPropagation();
		var elem = $(this).closest('tr'), str = '';
		var obj, mac = elem.find('.mac_address').text();
		if(elem.find('.device-type').text() == 'UCSM' && $('.device-initialization tr.failed[type="UCSM"][mac!="' + mac + '"]').length > 0) {
			obj = $('.device-initialization tr.failed[type="UCSM"][mac!="' + mac + '"]');
			mac += ',' + $('.device-initialization tr.failed[type="UCSM"][mac!="' + mac + '"]').attr('mac');
		}
		doAjaxRequest({url: 'Reconfigure', base_path: settings.base_path, method: 'GET', query: {hwtype: elem.find('.device-type').text().replace(' ', '_'), mac: mac}, container: '.smartwidget'}, function(response) {
			$('.ucsm.ucsm-configure').remove();
			$('.mds.block.mds_0, .mds.block.mds_1').remove();
			$('.nexus.block.nexus_0, .nexus.block.nexus_1').remove();
			$('.flasharray.block.fa_0').remove();
			response.data = $.parseJSON(response.data);
			openModel({title: 'Re-initialize Confirmation', body: str, buttons: {
				"no": closeModel,
				"yes": function() {
					requestCallback = new MyRequestsCompleted({
						numRequest: 1,
						singleCallback: function() {
							if(callbackFlag) {
								saveConfig({hwtype: elem.find('.device-type').text().replace(' ', '_'), mac: mac});
							}
						}
					});
					callbackFlag = true;
					switch(elem.find('.device-type').text()) {
						case 'MDS':
							postMDSForm(0, 0);
							break;
						case 'Nexus 5k':
						case 'Nexus 9k':
							postNEXUSForm(0, 0);
							break;
						case 'UCSM':
							postUCSMForm();
							break;
						case 'PURE':
							isPUREConfigured = false;
							postFAForm(0, 0);
							break;
					}
				}
			}});
			UCSForConfigure = [];
			str = loadFormTemplate({id: 'common_netmask', label: localization['mgmt-netmask'], readonly: true, class: 'ipaddress', holder: 'netmask switch_netmask col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) + 
			loadFormTemplate({id: 'common_gateway', label: localization['default-gateway'], readonly: true, class: 'ipaddress', holder: 'gateway switch_gateway col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true});
			switch(elem.find('.device-type').text()) {
				case 'UCSM':
					UCSForConfigure.push({
						type: elem.find('.device-type').text(), 
						serial: elem.find('.serial_no').text(), 
						ip: elem.find('.ip_address').text(),
						mac: elem.find('.mac_address').text(),
						vendor: elem.find('.vendor').text()
					});
					if(elem.find('.device-type').text() == 'UCSM' && $('.device-initialization tr.failed[type="UCSM"][mac!="' + elem.find('.mac_address').text() + '"]').length > 0) {
						UCSForConfigure.push({
							type: obj.find('.device-type').text(), 
							serial: obj.find('.serial_no').text(), 
							ip: obj.find('.ip_address').text(),
							mac: obj.find('.mac_address').text(),
							vendor: obj.find('.vendor').text()
						});
					}
					str += loadFormTemplate({id: 'adminPasswd', type: 'password', label: localization['admin-password'], holder: 'ucsm-primary pri_passwd col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
					loadFormTemplate({id: 'adminPasswd1', type: 'password', label: localization['confirm-password'], holder: 'ucsm-primary conf_passwd col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
					loadFormTemplate({id: 'domainName', label: localization['domain'], holder: 'ucsm-primary domain_name col-lg-12 col-md-12 col-sm-12 col-xs-12'}) + 
					loadFormTemplate({id: 'ntp_server', label: localization['ntp-server'], readonly: true, class: 'ipaddress', holder: 'ntp_server col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
					'<div style="margin-bottom: 16px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
					loadFormTemplate({id: 'dns', label: localization['dns-ip'], class: 'ipaddress', holder: 'ucsm-primary dns nameserver col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
					'<div style="margin-bottom: 16px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
					loadUCSMForm(1);
					$('#form-body .mCSB_container').append(str);
					bindTagifyEvent('#ntp_server', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
					bindTagifyEvent('#dns', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
					break;
				case 'MDS':
					str += '<div class="basic-view">';
						str += loadFormTemplate({id: 'adminPasswd', type: 'password', label: localization['admin-password'], holder: 'ucsm-primary pri_passwd col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						loadFormTemplate({id: 'adminPasswd1', type: 'password', label: localization['confirm-password'], holder: 'ucsm-primary conf_passwd col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						loadFormTemplate({id: 'domainName', label: localization['domain'], holder: 'ucsm-primary domain_name col-lg-12 col-md-12 col-sm-12 col-xs-12'}) + 
						loadFormTemplate({id: 'ntp_server', label: localization['ntp-server'], readonly: true, class: 'ipaddress', holder: 'ntp_server col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						'<div style="margin-bottom: 16px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
						loadMDSForm({
							type: elem.find('.device-type').text(), 
							serial: elem.find('.serial_no').text(), 
							ip: elem.find('.ip_address').text(),
							mac: elem.find('.mac_address').text(),
							vendor: elem.find('.vendor').text()
						}, 0, true, 'col-lg-12 col-md-12 col-sm-12 col-xs-12');
						str += '<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding mds">' + 
							loadFormTemplate({type: 'dropdown', id: 'mds_switch_system_image', class: 'mds_switch_system_image', label: localization['system-image'], holder: 'switch_system_image', mandatory: true}) +
						'</div>\
						<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding mds">' +
							loadFormTemplate({type: 'dropdown', id: 'mds_switch_kickstart_image', class: 'mds_switch_kickstart_image', label: localization['kickstart-image'], holder: 'switch_kickstart_image', mandatory: true}) +
						'</div>';
					str += '</div>';
					$('#form-body .mCSB_container').append(str);
					bindTagifyEvent('#ntp_server', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
					break;
				case 'Nexus 5k':
				case 'Nexus 9k':
					str += '<div class="basic-view">';
						str += loadFormTemplate({id: 'adminPasswd', type: 'password', label: localization['admin-password'], holder: 'ucsm-primary pri_passwd col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						loadFormTemplate({id: 'adminPasswd1', type: 'password', label: localization['confirm-password'], holder: 'ucsm-primary conf_passwd col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						loadFormTemplate({id: 'domainName', label: localization['domain'], holder: 'ucsm-primary domain_name col-lg-12 col-md-12 col-sm-12 col-xs-12'}) + 
						loadFormTemplate({id: 'ntp_server', label: localization['ntp-server'], readonly: true, class: 'ipaddress', holder: 'ntp_server col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						'<div style="margin-bottom: 16px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
						loadNEXUSForm({
							type: elem.find('.device-type').text(), 
							serial: elem.find('.serial_no').text(), 
							ip: elem.find('.ip_address').text(),
							mac: elem.find('.mac_address').text(),
							vendor: elem.find('.vendor').text()
						}, 0, true, 'col-lg-12 col-md-12 col-sm-12 col-xs-12');
						if(elem.find('.device-type').text() == 'Nexus 9k') {
							str += '<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding nexus nexus_9k">' + 
								loadFormTemplate({type: 'dropdown', id: 'nexus_switch_image', class: 'nexus_switch_image', label: localization['switch-image'], holder: 'switch_image', mandatory: true}) +
							'</div>';
						} else {
							str += '<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding nexus nexus_5k">' + 
								loadFormTemplate({type: 'dropdown', id: 'nexus5k_system_image', class: 'nexus5k_system_image', label: localization['system-image'], holder: 'switch_system_image', mandatory: true}) +
							'</div>\
							<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding nexus nexus_5k">' + 
								loadFormTemplate({type: 'dropdown', id: 'nexus5k_kickstart_image', class: 'nexus5k_kickstart_image', label: localization['kickstart-image'], holder: 'switch_kickstart_image', mandatory: true}) +
							'</div>';
						}
					str += '</div>';
					$('#form-body .mCSB_container').append(str);
					bindTagifyEvent('#ntp_server', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
					break;
				case 'PURE':
					str += '<div class="basic-view">';
						str += loadFormTemplate({id: 'domainName', label: localization['domain'], holder: 'ucsm-primary domain_name col-lg-12 col-md-12 col-sm-12 col-xs-12'}) + 
						loadFormTemplate({id: 'workflow_host', label: 'SMTP Server Host', holder: 'relay_host col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) + 
						loadFormTemplate({id: 'ntp_server', label: localization['ntp-server'], readonly: true, class: 'ipaddress', holder: 'ntp_server col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						'<div style="margin-bottom: 16px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
						loadFormTemplate({id: 'dns', label: localization['dns-ip'], class: 'ipaddress', holder: 'ucsm-primary dns nameserver col-lg-12 col-md-12 col-sm-12 col-xs-12', mandatory: true}) +
						'<div style="margin-bottom: 16px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
						loadFAForm({
							type: elem.find('.device-type').text(), 
							serial: elem.find('.serial_no').text(), 
							ip: elem.find('.ip_address').text(),
							mac: elem.find('.mac_address').text(),
							vendor: elem.find('.vendor').text()
						}, 0, true, 'col-lg-12 col-md-12 col-sm-12 col-xs-12');
					str += '</div>';
					$('#form-body .mCSB_container').append(str);
					bindTagifyEvent('#fa_alert_emails_0', 'Add an email', /^[a-zA-Z0-9.!#$%&â€™*+/=?^_{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/);
					bindTagifyEvent('#ntp_server', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
					bindTagifyEvent('#dns', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
					break;
			}
			$('.modal-inset .help-txt').tipso({
				position: 'top',
				animationIn: 'bounceIn',
				animationOut: 'bounceOut',
				titleBackground: 'rgb(247, 124, 61)',
				background: '#FFF',
				color: '#454545',
				tooltipHover: true
			});
			$.when(
				loadImages('', '', '')
			).then(function() {
				setTimeout(function() {
					var flag = true, field, server_type = true;
					plotValuesByDom($('#form-body .switch_netmask'), response.data[0]['switch_netmask']);
					plotValuesByDom($('#form-body .switch_gateway'), response.data[0]['switch_gateway']);
					switch(elem.find('.device-type').text()) {
						case 'UCSM':
							$.each(response.data, function(index, val) {
								flag = true; field = 'pri_ip';
								if(val.mode == 'subordinate') {
									field = 'sec_ip'; flag = false;
								} else {
									$('#form-body .esxi_remote_file').val(val['esxi_file']);
									$('#form-body .esxi_kickstart_file').val(val['esxi_kickstart']);
								}
								$('#form-body #systemName').val(val['switch_name']);
								plotValuesByDom($('#form-body .virtual_ip'), val['virtual_ip']);
								if(typeof val['domain_name'] != 'undefined') $('#form-body #domainName').val(val['domain_name']);
								plotValuesByDom($('#form-body .' + field), val['switch_ip']);
								$('.toggle-select.switchFabric_' + index).toggles({type: 'select', on: flag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'A', off: 'B'}});
							});
							flag = true;
							$.each(response.data[0]['ntp_server'].split(","), function(i, value) {
								$('#form-body #ntp_server').tagsinput('add', trimChar(value, " "));
							});
							if(typeof response.data[0]['dns'] != 'undefined') {
								$.each(response.data[0]['dns'].split(","), function(i, value) {
									$('#form-body #dns').tagsinput('add', trimChar(value, " "));
								});
							}
							if(response.data[0]['server_type'] != 'Rack') server_type = false;
							if(UCSForConfigure.length == 1) {
								flag = false;
								$('.toggle-select.fabricSwitch').addClass('disabled');
								$('#form-body .ucsm-subordinate.pri_ip').removeClass('hide');
								plotValuesByDom($('#form-body .pri_ip'), response.data[0]['pri_ip']);
								$('#form-body .virtual_ip .task-input, #form-body .switch_name .task-input, #form-body .pri_ip .task-input').attr('readonly', 'readonly');
								$('#form-body .pri_passwd, #form-body .conf_passwd, #form-body .os_install, #form-body .esxi_file, #form-body .esxi_kickstart, #form-body .domain_name, #form-body .ucs_firmware, #form-body .ucs_upgrade, #form-body .dns.nameserver').remove();
							}
							$('.toggle-select.component_type').toggles({type: 'select', on: server_type, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'Rack Server', off: 'Blade Server'}}).toggleClass('disabled', true);
							$('.toggle-select.mode').toggles({type: 'select', on: false, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['standalone'], off: localization['cluster']}});
							$('.toggle-select.config_type').toggles({type: 'select', on: flag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['primary'], off: localization['subordinate']}});
							break;
						case 'MDS':
							$.each(response.data[0]['ntp_server'].split(","), function(i, value) {
								$('#form-body #ntp_server').tagsinput('add', trimChar(value, " "));
							});
							if(typeof response.data[0]['domain_name'] != 'undefined') $('#form-body #domainName').val(response.data[0]['domain_name']);
							$('#form-body #mds_switch_name_0').val(response.data[0]['switch_name']);
							$('#form-body #mds_switch_system_image').val(response.data[0]['switch_image']['switch_system_image']);
							$('#form-body #mds_switch_kickstart_image').val(response.data[0]['switch_image']['switch_kickstart_image']);
							plotValuesByDom($('#form-body .switch_ip'), response.data[0]['switch_ip']);
							if(response.data[0]['switch_tag'] == 'B') flag = false;
							$('.toggle-select.mdsSwitch_0').toggles({type: 'select', on: flag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'A', off: 'B'}}).addClass('disabled');
							break;
						case 'Nexus 5k':
						case 'Nexus 9k':
							$.each(response.data[0]['ntp_server'].split(","), function(i, value) {
								$('#form-body #ntp_server').tagsinput('add', trimChar(value, " "));
							});
							if(typeof response.data[0]['domain_name'] != 'undefined') $('#form-body #domainName').val(response.data[0]['domain_name']);
							if(response.data[0]['switch_tag'] == 'B') flag = false;
							$('#form-body #nexus_switch_name_0').val(response.data[0]['switch_name']);
							if(elem.find('.device-type').text() == 'Nexus 9k')
								$('#form-body #nexus_switch_image').val(response.data[0]['switch_image']['switch_system_image']);
							else {
								$('#form-body #nexus5k_system_image').val(response.data[0]['switch_image']['switch_system_image']);
								$('#form-body #nexus5k_kickstart_image').val(response.data[0]['switch_image']['switch_kickstart_image']);
							}
							plotValuesByDom($('#form-body .switch_ip'), response.data[0]['switch_ip']);
							$('.toggle-select.nexusSwitch_0').toggles({type: 'select', on: flag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'A', off: 'B'}}).addClass('disabled');
							break;
						case 'PURE':
							plotValuesByDom($('#form-body .domain_name'), response.data[0]['domain_name']);
							plotValuesByDom($('#form-body .switch_netmask'), response.data[0]['netmask']);
							plotValuesByDom($('#form-body .switch_gateway'), response.data[0]['gateway']);

							$('#form-body #fa_array_name_0').val(response.data[0]['array_name']);
							$('#form-body #fa_vir0_ip_0').val(response.data[0]['vir0_ip']);
							$('#form-body #fa_ct0_ip_0').val(response.data[0]['ct0_ip']);
							$('#form-body #fa_ct1_ip_0').val(response.data[0]['ct1_ip']);
							$('#form-body #workflow_host').val(response.data[0]['relay_host']);
							$('#form-body #sender_domain').val(response.data[0]['sender_domain']);
							$('#form-body #fa_organization_0').val(response.data[0]['organization']);
							$('#form-body #fa_full_name_0').val(response.data[0]['full_name']);
							$('#form-body #fa_job_title_0').val(response.data[0]['job_title']);
							$.each(response.data[0]['alert_emails'].split(","), function(i, value) {
								$('#form-body #fa_alert_emails_0').tagsinput('add', trimChar(value, " "));
							});
							$.each(response.data[0]['ntp_server'].split(","), function(i, value) {
								$('#form-body #ntp_server').tagsinput('add', trimChar(value, " "));
							});
							$.each(response.data[0]['dns'].split(","), function(i, value) {
								$('#form-body #dns').tagsinput('add', trimChar(value, " "));
							});
							break;
					}
					toggleSwitches();
				}, 500);
			});
		}, doNothing);
	});

	/**
	  * @desc event registration for selecting/deselecting the stack types for deployment.
	*/
	$('body').delegate('.boxes .box:not(.disabled)', 'click', function(e) {
		$('.boxes .box').removeClass('active');
		$(this).addClass('active');
	});

	/**
	  * @desc event registration for poping the notification while enabling the upgrade option.
	*/
	$('body').delegate('#ucs_upgrade', 'change', function(e) {
		$('.ucsm-configure .ucs_upgrade:not(#ucs_upgrade)').addClass('hide');
		if($(this).is(':checked')) {
			$('.ucsm-configure .ucs_upgrade.infra_image').removeClass('hide');
			var myToggle = $('.toggle-select.component_type').data('toggles');
			if(myToggle.active) $('.ucsm-configure .ucs_upgrade.rack_image').removeClass('hide');
			else $('.ucsm-configure .ucs_upgrade.blade_image').removeClass('hide');

			showNotification(localization['ucsm-upgrade-msg'], 10000);
		}
	});

	/**
	  * @desc event registration for poping the notification while enabling the upgrade option.
	*/
	$('body').delegate('#os_install', 'change', function(e) {
		$('.ucsm-configure .remote_file.os_install').addClass('hide');
		if($(this).val() == 'Yes') {
			$('.ucsm-configure .remote_file.os_install').removeClass('hide');
		}
	});

	/**
	  * @desc event registration for updating the form while changing the configuration type.
	*/
	$('body').delegate('[name="configuration-option"]', 'change', function(e) {
		$('.fs-configurations').removeClass('hide');
		$('.import-configurations').addClass('hide');
		$('.buttonNext').text(localization['next']).removeClass('buttonDisabled');
		$('.manual-config, .iso-library').removeClass('hide');
		$('.json-config').addClass('hide');
		$('#ucs_upgrade').prop('checked', false);
		$('.iso-library').html('<i class="fa fa-th-large"></i> ' + localization['select-iso-library']);
		$('.iso-library').closest('.control-group').find('.task-input').attr('disabled', false);
		if(this.value == 'JSON') {
			$('.fs-configurations').addClass('hide');
			$('.import-configurations').removeClass('hide');
			$('.manual-config').addClass('hide');
			$('.json-config').removeClass('hide');
			$('.import_config .files').html('');
			$('.buttonNext').text(localization['init_deploy']).addClass('buttonDisabled');
		} else {
			loadGlobalConfigForm();
		}
	});

	/**
	  * @desc event registration for mapping the hardwares with the existing configuration set.
	*/
	$('body').delegate('.nexus_mapping, .mds_mapping, .fabric_mapping', 'change', function(e) {
		if($(this).val() != '') {
			var type = 'mds', tmp;
			if($(this).attr('class').indexOf('nexus') > -1) type = 'nexus';
			if($(this).attr('class').indexOf('fabric') > -1) type = 'fabric';
			var objId = $(this).attr('id');
			$('.task-input.' + type + '_mapping').each(function(index) {
				tmp = $(this).closest('.control-group').prev().find('.' + type + 'Switch').data('toggles');
				tmp.toggle();
				if(objId != this.id) {
					var actualIndex = $(this).prop('selectedIndex');
					//var nextIndex = (actualIndex + 1 == $(this).children('option').length) ? 0 : actualIndex + 1;
					var nextIndex = (actualIndex <= 0) ? 1 : 0;
					var next = $(this).children('option').eq(nextIndex);
					next.prop('selected', true);
				}
			});
		}
	});

	/**
	  * @desc event registration for choosing the stack type.
	*/
	$('body').delegate('.possible_stacktypes div.box', 'click', function(e) {
		$('.networkinfo.elementInfo').removeClass('non-selectable');
		$('.possible_stacktypes div.box').removeClass('active');
		$(this).addClass('active');
		systemInfo.stacktype = $(this).attr('stacktype');
		systemInfo.subtype = $(this).attr('stacktype');
		flashStackSelection([]);
	});

	$('body').delegate('.regenerate', 'click', function(e) {
		var $this = $(this),
			config = $(this).data('config'),
			data = {},
			query = {operation: config.name, ttype: config.tasktype};
		$.each(config.args, function(key, value) {
			data[value.field] = value.value;
		});
		doAjaxRequest({url: 'GetGlobalOptions', base_path: settings.base_path, method: 'POST', query: query, data: data, success_notify: true, container: 'div.' + $(this).parent().attr('argname')}, function(response) {
			$this.parent().find('.task-input.reset').val(response.data[0].id);
		}, doNothing);
	});
});

/**
  * @desc this method is used to seleting/deseleting the devices from the discovered list.
  * @param object $elem - the dom object of the selected device.
*/
function selectElement(elem) {
	if(elem.hasClass('active')) {
		elem.removeClass('active');
		elem.find('.devices').prop('checked', false);
	} else {
		if(elem.attr('type') == 'PURE') {
			$('.networkinfo.elementInfo[type="PURE"]').removeClass('active');
			elem.addClass('active');
		} else if(elem.attr('type') == 'FlashBlade') {
			$('.networkinfo.elementInfo[type="FlashBlade"]').removeClass('active');
			elem.addClass('active');
		} else if(elem.hasClass('Unconfigured')) {
			$('.networkinfo.elementInfo.Configured').removeClass('active');
			elem.addClass('active');
			elem.find('.devices[disabled!="disabled"]').prop('checked', true);
		}
	}
	checkRequiredHardwares('');
}

/**
  * @desc this method will enable DHCP settings based on the values filled on the settings form.
*/
function EnableDHCP() {
	var slider = $('#dhcp_ranges').data("ionRangeSlider");
	var dhcp_range = $('#dhcp_ranges').val().split(";");
	var data = {};
	data.subnet = $('#dhcp_subnet').val();
	data.netmask = $('#dhcp_netmask').val();
	data.gateway = $('#dhcp_gateway').val();
	data.server_ip = $('#dhcp_ipaddress').val();
	var subnet = $('#dhcp_subnet').val().split(".");
	subnet.pop();
	subnet = subnet.join(".");
	data.dhcp_start = subnet + "." + dhcp_range[0];
	data.dhcp_end = subnet + "." + dhcp_range[1];
	var static_start = parseInt(dhcp_range[1]) + 1;
	data.start = subnet + "." + slider.options.min;
	data.end = subnet + "." + slider.options.max;
	doAjaxRequest({url: 'DHCPSettings', base_path: settings.base_path, method: 'POST', data: data, success_notify: true, container: '.modal-inset', isValidate: true, formContainer: '.modal-inset .dhcp_settings'}, function(response) {
		systemInfo.dhcp_status = 'enabled';
		$('#enable-dhcp').prop('checked', true);
		$('.dhcp-settings').removeClass('hide');
		loadDiscovery('.content-container');
		closeModel();
	}, function() {
		$('#enable-dhcp').prop('checked', false);
	});
}

/**
  * @desc this method will disable the DHCP settings.
*/
function disableDHCP(notify) {
	doAjaxRequest({url: 'DHCPSettings', base_path: settings.base_path, success_notify: notify, container: '.content-container'}, function(response) {
		systemInfo.dhcp_status = 'disabled';
		$('.dhcp-settings').addClass('hide');
	}, function() {
		$('#enable-dhcp').prop('checked', true);
	});
}

/**
  * @desc this method is used to update the handler of image uploader.
  * @param string $value - the type of the image to upload.
*/
function updateUploadEvent(value) {
	$('.iso_file').addClass('hide');
	$('#iso_file').val('');
	var file_format = {type: 'bin, gbin', format: /(\.|\/)(bin|gbin)$/i};
	if(value == 'ESXi' || value == 'RHEL') file_format = {type: 'iso', format: /(\.|\/)(iso)$/i};
	else if(value == 'ESXi-kickstart' || value == 'RHEL-kickstart') {
		file_format = {type: 'cfg', format: /(\.|\/)(cfg)$/i};
		$('.iso_file').removeClass('hide');
	}
	uploadHandler('ImportImage', false, settings.base_path, 'import_iso', file_format.format, false, doNothing, doNothing);
	$(".import_iso .file_format").html("(" + localization['allowed-format'] + ": <b>" + file_format.type + "</b>)");
}

/**
  * @desc this method is used to select a image from the image library.
*/
function selectISO() {
	var options = {
		'MDS': 'mds_switch_system_image', 'MDS-kickstart': 'mds_switch_kickstart_image', 'Nexus 9k': 'nexus_switch_image', 'Nexus 5k': 'nexus5k_system_image', 'Nexus 5k-kickstart': 'nexus5k_kickstart_image', 'kickstart': 'mds_switch_kickstart_image', 'ESXi': 'esxi_remote_file', 'ESXi-kickstart': 'esxi_kickstart_file', 'UCS-infra': 'ucs_infra_image', 'UCS-blade': 'ucs_blade_image', 'UCS-Rack': 'ucs_rack_image'};
	$('#list-images .error').remove();
	if($('.images-list tr.selected').length == 0) {
		$('.images-list').before('<div class="red-text error">Please select a file.</span>');
		return false;
	}
	$('.' + options[$('#list-images').attr('type')]).val($('.images-list tr.selected').attr('primaryid'));
	$('.' + options[$('#list-images').attr('type')]).closest('.control-group').find('.iso-library').html('<i class="fa fa-th-large"></i> ' + localization['select-iso-library']);
	closeModel();
}

/**
  * @desc .
*/
function loadFlashstackTypes() {
	doAjaxRequest({url: 'FlashStackTypes', base_path: settings.base_path}, function(response) {
		var str = '', enabled, stacktype = '';
		str += '<div class="boxes row">\
			<h4>' + localization['choose-flashstack'] + '</h4>';
		$.each(response.data, function(key, value) {
			hardwares[value.value] = value.req_hardwares;
			value.enabled = (value.enabled == true) ? '' : 'disabled';
			str += '<div class=""><div data-ripple="#FFF" class="box ' + value.enabled + ' material-ripple" hardware_id="' + value.value + '"><div class="tag ribbon ribbon-top-right"><span>' + value.tag + '</span></div><h4>' + value.label + '</h4></div></div>';
		});
		str += '</div>';
		$('.flashstack_types').html(str);
		initScroller($('.flashstack_types.scroller'));
		var height = parseInt($('.stepContainer').height()) - 76;
		$('.flashstack_types.scroller').css('height', height + 'px').css('max-height', height + 'px');
		$('.boxes .box[hardware_id="' + systemInfo.stacktype + '"]').addClass('active');
	}, doNothing);
}

/**
  * @desc this method is used load the discovered devices with its availability & configurable status.
  * @param string $container - the dom selector string in-which location to create the loading icon.
*/
function loadDiscovery(container) {
	clearTimeout(tout);
	var notify = true, obj = {'PURE': 0, 'FlashBlade': 0, 'UCSM': 0, 'MDS': 0, 'Nexus 5k': 0, 'Nexus 9k': 0};
	if(container == '') notify = false;
	var cb_status, checked, title, device_type, selectedHost = [], unSelectableDevices = [], device_state = {'Up': {'icon': 'online', 'title': localization['online']}, 'Down': {'icon': 'offline', 'title': localization['offline']}, 'Failed': {'icon': 'failed', 'title': localization['failed']}, 'Checking': {'icon': 'fa fa-circle faa-burst animated', 'title': localization['checking']}};
	if(systemInfo.dhcp_status == "enabled")
		$('.loader-msg').html('<i class="fa fa-sync faa-spin animated active"></i> ' + localization['searching-devices'] + '...');
	doAjaxRequest({url: 'FSComponents', base_path: settings.base_path, container: container, notify: notify}, function(response) {
		var str = '', style, icon;
		var action_icons = [];
		str += '<table>';
		if(response.data.length > 0) {
			$.each(response.data, function(key, value) {
				if($.inArray(value.config_state, ['Configured', 'Unconfigured']) > -1)
					obj[value.device_type] += 1;
				device_type = (value.device_type == 'UCSM') ? 'Fabric Interconnect' : value.device_type;
				device_type = (device_type == 'PURE') ? 'FlashArray' : device_type;
				if($.inArray(value.config_state, ['Configured', 'Unconfigured', 'In-progress', 'Failed', 'Re-validate']) > -1) {
					icon = 'fa-times';
					style = 'grey-text';
					title = '';
					switch(value.config_state) {
						case 'Configured':
							style = 'green-text';
							icon = 'fa-check';
							break;
						case 'In-progress':
							style = 'blue-text';
							icon = 'fa-sync faa-spin animated';
							break;
						case 'Failed':
						case 'Re-validate':
							style = 'red-text re-validate tipso tipso_style';
							icon = 'fa-exclamation-triangle';
							title = ' data-tipso-title="' + localization['info'] + '" data-tipso="' + value.reval_msg + '"';
							break;
					}
					value.reachability = (value.reachability == '') ? 'Checking' : value.reachability;
					str += '<tr class="networkinfo elementInfo ' + value.config_state + '" primaryid="' + value.mac_address + '" state="' + value.config_state + '" type="' + value.device_type + '">\
						<td width="50" class="hide">';
							cb_status = '';checked = ' checked = "checked"';
							if(systemInfo.stacktype != '' && (typeof hardwares[systemInfo.stacktype] != 'undefined') && (typeof hardwares[systemInfo.stacktype][value.device_type] == 'undefined' || hardwares[systemInfo.stacktype][value.device_type] == 0)) {
								checked = ' disabled="disabled"';
							}
							if($.inArray(value.config_state, ['Unconfigured', 'Failed']) == -1) {
								if((value.device_type == 'PURE' || value.device_type == 'FlashBlade') && value.config_state == 'Configured') {}
								else {
									cb_status = 'disabled';checked = '';
								}
							}
							str += '<div class="pull-left checkbox checkbox-primary">\
								<input id="device_' + key + '" class="styled devices" htype="' + value.device_type + '" ' + cb_status + ' ' + checked + ' type="checkbox" value="' + value.ip_address + '">\
								<label for="device_' + key + '" class="nopadding"></label>\
							</div>';
							str += '<div class="mac_address hide">' + value.mac_address + '</div>\
						</td>\
						<td width="50">';
							if($.inArray(value.config_state, ['Unconfigured', 'Failed']) == -1)
								str += '<div class="reachability_status ' + device_state[value.reachability].icon + '" alt="' + device_state[value.reachability].title + '" title="' + device_state[value.reachability].title + '"></div>';
						str += '</td>\
						<td width="20%" class="">\
							<span class="device_type hide">' + value.device_type + '</span>' + device_type +
						'</td>\
						<td width="" class="vendor_model">' + value.vendor_model + '</td>\
						<td width="20%" class="ip_address">' + value.ip_address + '</td>\
						<td width="20%" class="serial_number">' + value.serial_number + '</td>\
						<td width="40">';
							if(value.config_state == 'Configured')
								str += '<span class="text-center"><i class="fa fa-trash-alt red-text delete-device" alt="' + localization['delete-device'] + '" title="' + localization['delete-device'] + '"></i></span>';
						str += '</td>\
					</tr>';
				}
			});
		} else {
			str += '<tr><td><h4><span class="col-lg-12 col-md-12 col-sm-12 col-xs-12 widget-subtitle">' + localization['no-device'] + '.</span></h4></td></tr>';
		}
		str += '</table>\
		<div class="clear"></div>';
		if($('.networkinfo.elementInfo:not(.active)').length) {
			$('.networkinfo.elementInfo:not(.active)').each(function(index) {
				selectedHost.push($(this).attr('primaryId'));
			});
		}
		if($('.networkinfo.elementInfo:not(.non-selectable)').length) {
			$('.networkinfo.elementInfo:not(.non-selectable)').each(function(index) {
				unSelectableDevices.push($(this).attr('primaryId'));
			});
		}
		if($('.networkList .scroller .mCSB_container').length)
			$('.networkList .scroller').mCustomScrollbar("destroy");
		initScroller($('.networkList .scroller'));
		$('.networkList .scroller .mCSB_container').html(str);
		$('.devices[checked="checked"]').closest('.networkinfo.elementInfo').addClass('active');
		//initTooltip();
		if(selectedHost.length > 0) {
			$.each(selectedHost, function(index, value) {
				$('.networkinfo.elementInfo[primaryid="' + value + '"]').removeClass('active');
				$('.networkinfo.elementInfo[primaryid="' + value + '"]').find('.devices').prop('checked', false);
			});
		}
		$('.devices[disabled]').closest('.networkinfo.elementInfo').addClass('non-selectable');
		if(unSelectableDevices.length > 0) {
			$.each(unSelectableDevices, function(index, value) {
				$('.networkinfo.elementInfo[primaryid="' + value + '"]').removeClass('non-selectable');
			});
		}
		getStackTypesByHardwares(obj, container);
		var height = parseInt($('.networkList').closest('.smartwidget').height()) - 260;
		$('.networkList .scroller').css('height', height + 'px').css('max-height', height + 'px');
		tout = setTimeout(function () {
			loadDiscovery('');
		}, 10000);
	}, function() {
		tout = setTimeout(function () {
			loadDiscovery('');
		}, 10000);
	});
}

/**
  * @desc this method is used to get the posible stacktypes based on the hardwares discovered.
  * @param object $obj - the object contains the type of the hardware & its quantity.
*/
function getStackTypesByHardwares(obj, container) {
	var unSelectableDevices = [];
	doAjaxRequest({url: 'FlashStackTypes', base_path: settings.base_path, method: 'POST', data: obj}, function(response) {
		$('.possible_stacktypes').remove();
		if(response.data.length > 0) {
			var str = '', enabled, stacktype = '';
			str += '<fieldset class="possible_stacktypes">' +
				'<legend>' + localization['configuration_options'] + ':</legend>' +
				'<div class="boxes">';
				$.each(response.data, function(key, value) {
					hardwares[value.value] = value.req_hardwares;
					if(value.enabled) {
						str += '<div class=""><div data-ripple="#FFF" class="box ' + value.enabled + ' material-ripple" stacktype="' + value.value + '">';
							if(value.tag.length > 0)
								str += '<div class="tag ribbon ribbon-top-right"><span>' + value.tag + '</span></div>';
							str += '<h4>' + value.label + '</h4></div>';
						str += '</div>';
					}
				});
				str += '</div>' +
			'</fieldset>';
			$('.flashstack_types').html(str);

			$('.possible_stacktypes').remove();
			$('.networkList.dataList').before(str);
			$('.possible_stacktypes div.box[stacktype="' + systemInfo.stacktype + '"]').addClass('active');
			//$('.possible_stacktypes div.box[stacktype="' + systemInfo.stacktype + '"]').trigger('click');
			if($('.networkinfo.elementInfo:not(.active)').length) {
				$('.networkinfo.elementInfo:not(.active)').each(function(index) {
					unSelectableDevices.push($(this).attr('primaryId'));
				});
			}
			flashStackSelection(unSelectableDevices);
		}
		checkRequiredHardwares(container);
	}, doNothing);
}

function flashStackSelection(unSelectableDevices) {
	$('.networkinfo.elementInfo .devices').attr('disabled', true).prop('checked', false);
	$('.networkinfo.elementInfo').removeClass('active');
	if(typeof systemInfo.stacktype != 'undefined' && systemInfo.stacktype != '') {
		$.each(hardwares[systemInfo.stacktype], function(index, value) {
			if(value > 0) {
				$('.networkinfo.elementInfo .devices[htype="' + index + '"]').removeAttr('disabled').prop('checked', true);
				$('.networkinfo.elementInfo .devices[htype="' + index + '"]').closest('.networkinfo').addClass('active');
			}
		});
	}
	if(unSelectableDevices.length > 0) {
		$.each(unSelectableDevices, function(index, value) {
			$('.networkinfo.elementInfo[primaryid="' + value + '"]').removeClass('active');
			$('.networkinfo.elementInfo[primaryid="' + value + '"]').find('.devices').prop('checked', false);
		});
	}
	$('.devices[disabled]').closest('.networkinfo.elementInfo').addClass('non-selectable');
	checkRequiredHardwares('a');
}

/**
  * @desc this method is used to check the hardware requirements for the selected flashstack type and display the same on UI.
  * @param string $container - the dom selector string in-which location to create the loading icon.
*/
function checkRequiredHardwares(container) {
	if(systemInfo.stacktype != '') {
		var str = '', color, display_name, flag, status, selected;
		if(systemInfo.stacktype in hardwares) {
			Object.keys(hardwares[systemInfo.stacktype]).some(function(key) {
				display_name = (key == 'UCSM') ? 'Fabric Interconnect' : key;
				display_name = (display_name == 'PURE') ? 'FlashArray': display_name;
				flag = false; status = 0;
				color = 'red-text';

				if(key == 'PURE' || key == 'FlashBlade') {
					selected = $('.networkinfo.elementInfo.active[type="' + key + '"]').length;
					if(selected == 1) {
						color = 'green-text';status = 1;
					}
				} else if($('input[type="checkbox"].devices:checked').length == 0) {
					selected = $('.networkinfo.Configured').find('input[type="checkbox"].devices[htype="' + key + '"][disabled]').length;
					if(flag == true || $('.networkinfo.Configured').find('input[type="checkbox"].devices[htype="' + key + '"][disabled]').length == hardwares[systemInfo.stacktype][key]) {
				                color = 'green-text';status = 1;
				        }
				} else {
					selected = $('input[type="checkbox"].devices[htype="' + key + '"]:checked').length;
				        if(flag == true || $('input[type="checkbox"].devices[htype="' + key + '"]:checked').length == hardwares[systemInfo.stacktype][key]) {
				                color = 'green-text';status = 1;
				        }
				}

				str += '<div class="' + key.replace(/\s/g, "-") + ' tipso-content hardware-types" status="' + status + '" key="' + key + '" data-tipso-title="' + display_name + '" expected="' + hardwares[systemInfo.stacktype][key] + '" selected="' + selected + '"><i class="' + color + ' fa fa-circle"></i> ' + display_name + ' x ' + hardwares[systemInfo.stacktype][key] + '</div>';

				$('.tipso-content.hardware-types[key="' + key + '"]').find('i').removeClass('red-text green-text').addClass(color);
				if(container == '')
					$('.tipso-content.' + key.replace(/\s/g, "-")).attr('status', status);
			});
			if(container != '') {
				$('.required-hardwares-flash').html(str);
				$('.tipso-content').tipso({
				        position: 'bottom',
				        animationIn: 'bounceIn',
				        animationOut: 'bounceOut',
				        titleBackground: 'rgb(247, 124, 61)',
				        background: '#FFF',
				        color: '#454545',
				        tooltipHover: true,
				        onBeforeShow: function(ele, tipso) {
						var selected = $('input[type="checkbox"].devices[htype="' + ele.attr('key') + '"]:checked').length;
				                ele.tipso('update', 'content', selected + ' selected (' + localization['expected'] + ' ' + ele.attr('expected') + ')');
				        }
				});
			} else {
				Object.keys(hardwares[systemInfo.stacktype]).some(function(key) {
					var ele = $('.required-hardwares-flash .hardware-types.' + key.replace(/\s/g, "-"));
				        var selected = $('input[type="checkbox"].devices[htype="' + ele.attr('key') + '"]:checked').length;
				        $('.tipso-content.' + key.replace(/\s/g, "-")).tipso('update', 'content', selected + ' selected (' + localization['expected'] + ' ' + ele.attr('expected') + ')');
				});
			}
		}
	}
	$('.buttonNext').removeClass('disable buttonDisabled');
}

/**
  * @desc method for validating & configuring UCSM devices. It will collect all UCSM configuration values from the form & make a request.
*/
function postUCSMForm() {
	var data = {}, myToggle, type = 'cluster';
	if(UCSForConfigure.length == 1 && $('.toggle-select.config_type').length) {
		myToggle = $('.toggle-select.config_type').data('toggles');
		type = 'subordinate';
		if(myToggle.active)
			type = 'primary';
		else data.sec_cluster = "1";
	}

	data.pri_passwd = $('#adminPasswd').val();
	data.conf_passwd = $('#adminPasswd1').val();
	if($('#ucs_upgrade').length) {
		data.ucs_upgrade = ($('#ucs_upgrade').is(':checked')) ? "Yes" : "No";
		if(!$('#ucs_upgrade').is(':checked')) $('#infra_image, #rack_image, #blade_image').val('');
	}
	if($('#os_install').length) {
		data.os_install = ($('#os_install').val() == '') ? "No" : "Yes";
		if(data.os_install == 'No') $('#esxi_file, #esxi_kickstart').val('');
	}
	if($('#infra_image').length)
		data.infra_image = $('#infra_image').val();
	if($('#rack_image').length)
		data.blade_image = $('#rack_image').val();
	data.server_type = 'Rack';
	if($('.toggle-select.component_type').length) {
		myToggle = $('.toggle-select.component_type').data('toggles');
		if(!myToggle.active) {
			data.server_type = "Blade";
			data.blade_image = $('#blade_image').val();
		}
	}
	data.ntp_server = $('#ntp_server').val();
	data.virtual_ip = $('#virtualIP').val();
	if(type == 'subordinate') {
		data.pri_name = $('#systemName').val();
		data.pri_ip = $('#oobIP').val();
		data.sec_ip = $('#oobIP_0').val();
		data.sec_id = "2";
		data.sec_orig_ip = $('#ucsm_switch_ip_0').val();
		data.sec_switch_mac = $('#ucsm_switch_mac_0').val();
		data.sec_switch_serial_no = $('#ucsm_switch_serial_0').val();
		data.sec_switch_vendor = $('#ucsm_vendor_model_0').val();
	} else {
		data.pri_cluster = "1";
		if(type == 'cluster') data.sec_cluster = "1";
		if($('.toggle-select.mode').length) {
			myToggle = $('.toggle-select.mode').data('toggles');
			if(myToggle.active) {
				type = 'standalone';
				data.pri_cluster = "2";
			}
		}
		$.each(UCSForConfigure, function(index, value) {
			myToggle = $('.toggle-select.switchFabric_' + index).data('toggles');
			if(myToggle.active) {
				data.pri_switch_mac = $('#ucsm_switch_mac_' + index).val();
				data.pri_switch_serial_no = $('#ucsm_switch_serial_' + index).val();
				data.pri_switch_vendor = $('#ucsm_vendor_model_' + index).val();
				data.pri_orig_ip = $('#ucsm_switch_ip_' + index).val();
				data.pri_id = "1";
				data.pri_ip = $('#oobIP_' + index).val();
			} else {
				data.sec_switch_mac = $('#ucsm_switch_mac_' + index).val();
				data.sec_switch_serial_no = $('#ucsm_switch_serial_' + index).val();
				data.sec_switch_vendor = $('#ucsm_vendor_model_' + index).val();
				data.sec_orig_ip = $('#ucsm_switch_ip_' + index).val();
				data.sec_id = "2";
				data.sec_ip = $('#oobIP_' + index).val();
			}
		});
		data.pri_name = $('#systemName').val();
		data.ipformat = "1";
		data.pri_setup_mode = "1";
		data.netmask = $('#common_netmask').val();
		data.gateway = $('#common_gateway').val();
		data.dns = $('#dns').val();
		data.domain_name = $('#domainName').val();
		data.esxi_file = $('#esxi_file').val();
		data.esxi_kickstart = ($('#esxi_kickstart').val() == null) ? '' : $('#esxi_kickstart').val();
	}
	$('.ucsm.ucsm-configure').data('config', data);
	var formContainer = ['.initial-setup .common-inputs', '.initial-setup .ucsm-configure', '.modal-inset'];
	doAjaxRequest({url: 'UCSMFIValidate', base_path: settings.base_path, method: 'POST', query: {mode: type}, data: data, isValidate: true, notify: false, formContainer: formContainer}, function(response) {
		requestCallback.requestComplete(true);
	}, function(response) {
		callbackFlag = false;
		requestCallback.requestComplete(true);
		removeProcessingSpinner('.content-container', loaderCnt);
	});
}

/**
  * @desc method for validating & configuring MDS devices. It will collect all MDS configuration values from the form & make a request.
  * @param integer $index - .
  * @param boolean $isMDSPrimary - .
*/
function postMDSForm(index, isMDSPrimary) {
	var data = {}, n = index;
	data.tag = 'A';
	var myToggle = $('.toggle-select.mdsSwitch_' + index).data('toggles');
	if(!myToggle.active) {
		data.tag = 'B';
	}
	data.domain_name = $('#domainName').val();
	data.pri_passwd = $('#adminPasswd').val();
	data.conf_passwd = $('#adminPasswd1').val();
	data.switch_name = $('#mds_switch_name_' + index).val();
	data.switch_mac = $('#mds_switch_mac_' + index).val();
	data.switch_vendor = $('#mds_vendor_model_' + index).val();
	data.switch_serial_no = $('#mds_switch_serial_' + index).val();
	data.switch_ip =  $('#mds_ipaddress_' + index).val();
	var formContainer = ['.initial-setup .common-inputs', '.mds_' + index, '.modal-inset'];

	if(typeof isMDSPrimary == 'number') index = isMDSPrimary;
	data.ntp_server = $('#ntp_server').val();
	data.switch_gateway = $('#common_gateway').val();
	data.switch_netmask =  $('#common_netmask').val();
	data.switch_kickstart_image = $('#mds_switch_kickstart_image').val();
	data.switch_system_image = $('#mds_switch_system_image').val();
	$('.mds.mds_' + n).data('config', data);
	doAjaxRequest({url: 'MDSValidate', base_path: settings.base_path, method: 'POST', data: data, isValidate: true, notify: false, formContainer: formContainer}, function(response) {
		requestCallback.requestComplete(true);
	}, function(response) {
		$.each(response.data, function(i, value) {
			if($.inArray(value.field, ['switch_kickstart_image', 'switch_system_image']) >= 0) {
				$('.mds .control-group.' + value.field).find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
				$('.mds .control-group.' + value.field).find('.help-block').show().html(ucfirst(value.msg));
			}
		});
		callbackFlag = false;
		requestCallback.requestComplete(true);
		removeProcessingSpinner('.content-container', loaderCnt);
	});
}

/**
  * @desc method for validating & configuring NEXUS devices. It will collect all NEXUS configuration values from the form & make a request.
  * @param integer $index - .
  * @param boolean $isNexusPrimary - .
*/
function postNEXUSForm(index, isNexusPrimary) {
	var data = {}, n = index, model = 'n9k';
	data.tag = 'A';
	var myToggle = $('.toggle-select.nexusSwitch_' + index).data('toggles');
	if(!myToggle.active) {
		data.tag = 'B';
	}
	data.domain_name = $('#domainName').val();
	data.pri_passwd = $('#adminPasswd').val();
	data.conf_passwd = $('#adminPasswd1').val();
	data.switch_name = $('#nexus_switch_name_' + index).val();
	data.switch_mac = $('#nexus_switch_mac_' + index).val();
	data.switch_serial_no = $('#nexus_switch_serial_' + index).val();
	data.switch_vendor = $('#nexus_vendor_model_' + index).val();
	data.switch_ip =  $('#nexus_ipaddress_' + index).val();
	var formContainer = ['.initial-setup .common-inputs', '.nexus_' + index, '.modal-inset'];

	if(typeof isNexusPrimary == 'number') index = isNexusPrimary;
	data.ntp_server = $('#ntp_server').val();
	data.switch_gateway = $('#common_gateway').val();
	data.switch_netmask =  $('#common_netmask').val();
	if(systemInfo.stacktype.indexOf('-n5k-') > 0) {
		model = 'n5k';
		data.switch_system_image = $('#nexus5k_system_image').val();
		data.switch_kickstart_image = $('#nexus5k_kickstart_image').val();
	} else data.switch_image = $('#nexus_switch_image').val();

	$('.nexus.nexus_' + n).data('config', data);
	doAjaxRequest({url: 'NEXUSValidate', base_path: settings.base_path, method: 'POST', query: {model: model}, data: data, isValidate: true, notify: false, formContainer: formContainer}, function(response) {
		requestCallback.requestComplete(true);
	}, function(response) {
		$.each(response.data, function(i, value) {
			if($.inArray(value.field, ['switch_image', 'switch_system_image', 'switch_kickstart_image']) >= 0) {
				$('.nexus .control-group.' + value.field).find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
				$('.nexus .control-group.' + value.field).find('.help-block').show().html(ucfirst(value.msg));
			}
		});
		callbackFlag = false;
		requestCallback.requestComplete(true);
		removeProcessingSpinner('.content-container', loaderCnt);
	});
}

/**
  * @desc method for validating & configuring MDS devices. It will collect all MDS configuration values from the form & make a request.
  * @param integer $index - .
  * @param boolean $isMDSPrimary - .
*/
function postFAForm(index, isFAPrimary) {
	var data = {}, n = index;
	data.netmask = $('#common_netmask').val();
	data.gateway = $('#common_gateway').val();
	data.dns = $('#dns').val();
	data.domain_name = $('#domainName').val();
	data.ntp_server = $('#ntp_server').val();
	data.pri_passwd = ($('#adminPasswd').length) ? $('#adminPasswd').val() : '';

	data.array_name = $('#fa_array_name_' + index).val();
	data.mac = $('#fa_switch_mac_' + index).val();
	data.model = $('#fa_vendor_model_' + index).val();
	data.orig_ip =  $('#fa_switch_ip_' + index).val();
	data.serial_number = $('#fa_switch_serial_' + index).val();
	data.ct0_ip = $('#fa_ct0_ip_' + index).val();
	data.ct1_ip = $('#fa_ct1_ip_' + index).val();
	data.vir0_ip = $('#fa_vir0_ip_' + index).val();
	data.relay_host = $('#workflow_host').val();
	data.sender_domain = $('#sender_domain').val();
	data.organization = $('#fa_organization_' + index).val();
	data.full_name = $('#fa_full_name_' + index).val();
	data.job_title = $('#fa_job_title_' + index).val();
	data.alert_emails = $('#fa_alert_emails_' + index).val();
	var formContainer = ['.initial-setup .common-inputs', '.pure.fa_' + index, '.modal-inset'];
	if(typeof isFAPrimary == 'number') index = isFAPrimary;
	$('.pure.fa_' + n).data('config', data);
	doAjaxRequest({url: 'FAValidate', base_path: settings.base_path, method: 'POST', data: data, isValidate: true, notify: false, formContainer: formContainer}, function(response) {
		requestCallback.requestComplete(true);
	}, function(response) {
		callbackFlag = false;
		requestCallback.requestComplete(true);
		removeProcessingSpinner('.content-container', loaderCnt);
	});
}

/**
  * @desc 
*/
function validateConfiguration() {
	$('.control-group').find('.help-block').hide().html('');
	$('.control-group').find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').removeClass('error');
	
	var tmp, ips = [], dhcpIPs = [], arr, flag = true, dom, subnet = dhcpInfo.dhcp_start.split(".");
	subnet.pop();
	subnet = subnet.join(".");
	for(var i = parseInt(dhcpInfo.dhcp_start.split(".").pop()); i <= parseInt(dhcpInfo.dhcp_end.split(".").pop()); i++) {
		dhcpIPs.push(subnet + '.' + i);
	}
	$('.initial-setup .control-group.hostname-or-ip').each(function(index) {
		if(!isValidIP($(this).find('input.task-input').val()) && !isValidDomain($(this).find('input.task-input').val())) {
			flag = false;
			$(this).find('.help-block').show().html("Address must be a valid IP address or hostname.");
			$(this).find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
		}
	});
	
	$('.initial-setup .control-group.unique_ip').each(function(index) {
		tmp = '';
		if($(this)[0].hasAttribute("argtype") && $(this).attr("argtype") == 'ip-range') {
			arr = $(this).find('input.task-input').val().split('-');
			for(i = parseInt(arr[0]); i <= parseInt(arr[1]); i++) {
				tmp = $(this).find('input.task-input').attr("subnet") + '.' + i;
				ips.push(tmp);
			}
		} else {
			$(this).find('input.task-input').each(function(i) {
				tmp = $(this).val().split(',');
				$.each(tmp, function(i, v) {
					if(v.length > 0) ips.push(v);
				});
			});
		}
	});
	$('.initial-setup .control-group.unique_ip').each(function(index) {
		tmp = '';
		if($(this)[0].hasAttribute("argtype") && $(this).attr("argtype") == 'ip-range') {
			arr = $(this).find('input.task-input').val().split('-');
			for(i = arr[0]; i <= arr[1]; i++) {
				tmp = $(this).find('input.task-input').attr("subnet") + '.' + i;
				if(tmp.length > 0 && ips.filter(function(x){ return x === tmp; }).length > 1) {
					$(this).find('.help-block').show().html(localization['duplicate-ip']);
					$(this).find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
					flag = false;
				}
				if(tmp.length > 0 && dhcpIPs.filter(function(x){ return x === tmp; }).length > 0) {
					$('.ucsm-configure .control-group.kvm_console_ip').find('.help-block').show().html(localization['ip_overlap_dhcp']);
					$(this).find('.help-block').show().html(localization['ip_overlap_dhcp']);
					$(this).find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
					flag = false;
				}
			}
		} else {
			$(this).find('input.task-input').each(function(i) {
				tmp = $(this).val().split(',');
				dom = $(this);
				$.each(tmp, function(i, v) {
					if(v.length > 0) {
						if(ips.filter(function(x){ return x === v; }).length > 1) {
							dom.closest('.control-group').find('.help-block').show().html(localization['duplicate-ip']);
							dom.closest('.control-group').find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
							flag = false;
						}
						if(dhcpIPs.filter(function(x){ return x === v; }).length > 0) {
							$('.ucsm-configure .control-group.kvm_console_ip').find('.help-block').show().html(localization['ip_overlap_dhcp']);
							dom.closest('.control-group').find('.help-block').show().html(localization['ip_overlap_dhcp']);
							dom.closest('.control-group').find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
							flag = false;
						}
					}
				});
			});
		}
	});
	var slider = $('.ucsm-configure .control-group.kvm_console_ip').find('#workflow_kvm_console_ip.range-slider').val();
	slider = slider.split("-");
	if((slider[0] >= parseInt(dhcpInfo.dhcp_start.split(".").pop()) && slider[0] <= parseInt(dhcpInfo.dhcp_end.split(".").pop())) || 
		(slider[1] >= parseInt(dhcpInfo.dhcp_start.split(".").pop()) && slider[1] <= parseInt(dhcpInfo.dhcp_end.split(".").pop()))) {
		$('.ucsm-configure .control-group.kvm_console_ip').find('.help-block').show().html(localization['dhcp_kvm_overlap']);
	}

	response = checkIpAvailability($('#common_gateway').val());
	if(!response[0]) {
		$('#common_gateway').closest('.control-group').find('.help-block').show().html(response[1]);
		$('#common_gateway').closest('.control-group').find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
		flag = false;
	}

	if(!flag) return false;
	loaderCnt = addProcessingSpinner('.content-container');
	var requestCount = NEXUSForConfigure.length + MDSForConfigure.length + 1;
	if(!isPUREConfigured) {
		requestCount += FAForConfigure.length;
	}
	if(UCSForConfigure.length > 0) requestCount++;
	requestCallback = new MyRequestsCompleted({
		numRequest: requestCount,
		singleCallback: function() {
			if(callbackFlag) {
				saveConfig({});
			}
		}
	});
	
	callbackFlag = true;
	updateGlobalConfig();
	if(UCSForConfigure.length > 0)
		postUCSMForm();

	var isMDSPrimary = '', isNexusPrimary = '', isFAPrimary = '';
	$.each(NEXUSForConfigure, function(index, val) {
		postNEXUSForm(index, isNexusPrimary);
		isNexusPrimary = index;
	});
	$.each(MDSForConfigure, function(index, val) {
		postMDSForm(index, isMDSPrimary);
		isMDSPrimary = index;
	});
	if(!isPUREConfigured) {
		$.each(FAForConfigure, function(index, val) {
			postFAForm(index, isFAPrimary);
			isFAPrimary = index;
		});
	}
}

function checkIpAvailability(ip) {
	var dom, flag = true, msg = '';
	$('.initial-setup .control-group.unique_ip:not(.ntp_server)').each(function(index) {
		tmp = '';
		if($(this)[0].hasAttribute("argtype") && $(this).attr("argtype") == 'ip-range') {
			arr = $(this).find('input.task-input').val().split('-');
			for(i = parseInt(arr[0]); i <= parseInt(arr[1]); i++) {
				tmp = $(this).find('input.task-input').attr("subnet") + '.' + i;
				if(ip.length > 0 && tmp.length > 0 && ip === tmp) {
					msg = localization['duplicate-ip'];
					$(this).find('.help-block').show().html(msg);
					$(this).find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
					flag = false;
				}
			}
		} else {
			dom = $(this);
			$(this).find('input.task-input').each(function(i) {
				tmp = $(this).val().split(',');
				$.each(tmp, function(i, v) {
					if(ip.length > 0 && v.length > 0 && ip == v) {
						msg = localization['duplicate-ip'];
						dom.find('.help-block').show().html(msg);
						dom.find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
						flag = false;
					}
				});
			});
		}
	});
	if(parseInt(ip.split(".").pop()) > parseInt(dhcpInfo.dhcp_start.split(".").pop()) && parseInt(ip.split(".").pop()) < parseInt(dhcpInfo.dhcp_end.split(".").pop())) {
		msg = "Gateway IP should not be in DHCP range";
		$('.ucsm-configure .control-group.kvm_console_ip').find('.help-block').show().html(msg);
		flag = false;
	}
	return [flag, msg];
}
/**
  * @desc .
  * @param object $obj - .
*/
function saveConfig(obj) {
	var data = {}, mds = [], nexus = [], pure = [];
	data.ucsm = JSON.stringify($('.ucsm.ucsm-configure').data('config'));

	if(!isPUREConfigured) {
		$('.basic-view .pure.block').each(function(index) {
			pure.push($(this).data('config'));
		});
		data.pure = JSON.stringify(pure);
	}

	$('.basic-view .mds.block').each(function(index) {
		mds.push($(this).data('config'));
	});
	data.mds = JSON.stringify(mds);
       
	$('.basic-view .nexus.block').each(function(index) {
		nexus.push($(this).data('config'));
	});
	if(systemInfo.stacktype.indexOf('-n9k-') > 0) {
		data.nexus_9k = JSON.stringify(nexus);
	} else {
		data.nexus_5k = JSON.stringify(nexus);
	}
	var query = {stacktype: systemInfo.subtype};
	if($('.toggle-select.component_type').length) {
		query.stacktype = query.stacktype.replace("-rack", "");
		var myToggle = $('.toggle-select.component_type').data('toggles');
		if(myToggle.active && query.stacktype.indexOf('-rack') < 0) query.stacktype += '-rack';
	}
	
	var api = 'SaveConfiguration';
	if($('[name="configuration-option"]:checked').val() == 'JSON' && $('#wizard').smartWizard('currentStep') != 3)
		api = 'RestoreConfig';
	else {
		if($('#wizard').smartWizard('currentStep') == 3) query.update = 1;
	}
	doAjaxRequest({url: api, base_path: settings.base_path, method: 'POST', data: data, query: query, isValidate: true, notify: false, formContainer: '.fs-configurations'}, function(response) {
		if($('#wizard').smartWizard('currentStep') == 2) {
			var deploymentData = {config_mode: $('[name="configuration-option"]:checked').val().toLowerCase(), deployment_type: 'basic'};
			if($('[name="configuration-option"]:checked').val() == 'JSON')
				deploymentData.deployment_type = 'advanced';
			doAjaxRequest({url: 'DeploymentSettings', base_path: settings.base_path, method: 'POST', data: deploymentData, container: '.content-container'}, function(response) {
				doAjaxRequest({url: 'System', base_path: settings.base_path, notify: false}, function(response) {
					updateDeploymentSettings(response.data.deployment_settings);
					removeProcessingSpinner('.content-container', loaderCnt);
					navigateStep(3);
				}, doNothing);
			}, doNothing);
		} else {
			reConfigure(obj);
		}
		return true;
	}, function(response) {
		removeProcessingSpinner('.content-container', loaderCnt);
	});
}

/**
  * @desc .
  * @param object $obj - .
*/
function reConfigure(obj) {
	obj.force = 1;
	doAjaxRequest({url: 'Reconfigure', base_path: settings.base_path, method: 'GET', query: obj, container: '.modal-inset'}, function(response) {
		$('.buttonNext, .buttonPrevious').addClass('buttonDisabled');
		loadDevices('');
		closeModel();
	}, doNothing);
}

/**
  * @desc .
*/
function triggerInitialization() {
	doAjaxRequest({url: 'ConfigureDevices', base_path: settings.base_path, container: '.device-initialization'}, function(response) {
		$('.basic-view, .ucsm.ucsm-configure').remove();
		$('.buttonNext').addClass('buttonDisabled');
		$('.buttonPrevious').remove();
		loadDevices('.device-initialization');
	}, doNothing);
}

/**
  * @desc .
*/
var isPUREConfigured = true, dhcpInfo;
function loadInitialSetupForm() {
	clearTimeout(tout);
	var loadDynamicValues = {}, tmp, data_str, obj = {'UCSM': [], 'MDS': []};
	var passwordHelp = '<span><strong>Must contain:</strong><br>\
		Lowercase letters<br>\
		Uppercase letters<br>\
		Numbers<br>\
		Special Characters - &#33; &quot; &#37; &amp; &#39; &#40; &#41; &#92; &#42; &#43; &#44; &#45; &#46; &#47; &#58; &#59; &#60; &#62; &#64; &#91; &#93; &#94; &#95; &#96; &#123; &#124; &#125; &#126;<br><br>\
		<strong>Must meet the following complexity conditions:</strong><br>\
		Must not contain letters consecutively repeated more than 3 times: e.g. aaa bbb.<br>\
		Must not contain letters listed in alphabetical order: e.g. abcd efgh ijkl.<br>\
		Must not contain numbers consecutively repeated more than 3 times: e.g. 123 456.<br>\
		Must not contain the following special characters: $ (dollar), ? (question mark) or = (equals).<br>\
		Must not be blank.<br>\
		Must not be identical to the username (forward or reverse).<br>\
		Must not be based on a standard dictionary word.</span>';
	var fields = [], file_format = {type: 'json', format: /(\.|\/)(json)$/i};
        if(systemInfo.stacktype.indexOf('-n9k-') > 0)
             obj['NEXUS_9K'] = [];
        else
             obj['NEXUS_5K'] = []; 

	fields.push({type: 'radio', id: 'manual-configuration', optional_label: localization['manual_configuration'], value: 'Manual', name: 'configuration-option', checked: true});
	fields.push({type: 'radio', id: 'import-configuration', optional_label: localization['import_configuration'], value: 'JSON', name: 'configuration-option'});
	var string = '<div class="form scroller" style="margin-bottom: 100px;">\
		<fieldset class="row nomargin">\
			<legend>' + localization['configuration_type'] + '</legend>\
			<div class="row configuration-option col-lg-6 col-md-6 col-sm-12 col-xs-12">' +
				loadFormTemplate({type: 'group', label: localization['type'], fields: fields, mandatory: true}) + 
			'</div>\
			<div class="clear"></div>\
			<div class="row import-configurations col-lg-6 col-md-6 col-sm-12 col-xs-12 hide">' +
				loadFormTemplate({type: 'file', id: 'import_config', name: 'uploadfile', label: localization['import-file'], holder: 'import_config', mandatory: true}) + 
			'</div>\
		</fieldset>\
		<div class="fs-configurations">\
			<div class="controls mode-container addition-info col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding ">' +
				loadFormField({type: 'toggle', id: 'viewmode pull-right dark'}) +
				'<div class="clear"></div>\
			</div>\
			<div class="col-lg-12 col-md-12 col-sm-12 nopadding">\
				<div class="basic-view">\
					<div class="row common-inputs">\
						<div class="info-section col-lg-12 col-md-12 col-sm-12 col-xs-12">\
							<h3 class="hseperator widget-subtitle bold">' + localization['general-info'] + '</h3>\
						</div>\
						<div class="form col-lg-12 col-md-12 col-sm-12 col-xs-12">' +
							loadFormTemplate({id: 'common_netmask', label: localization['mgmt-netmask'], class: 'ipaddress', holder: 'netmask switch_netmask unique_ip col-lg-6 col-md-6 col-sm-6 col-xs-6', mandatory: true, readonly: true}) + 
							loadFormTemplate({id: 'common_gateway', label: localization['default-gateway'], class: 'ipaddress', holder: 'gateway switch_gateway col-lg-6 col-md-6 col-sm-6 col-xs-6', mandatory: true, readonly: true}) + 
							loadFormTemplate({id: 'ntp_server', label: localization['ntp-server'] + '(s)**', class: 'tags tagify', "dataRole": "tagsinput", holder: 'ntp ntp_server unique_ip col-lg-6 col-md-6 col-sm-6 col-xs-6', mandatory: true}) + 
							loadFormTemplate({id: 'dns', label: localization['dns-ip'] + '(s)**', class: 'tags tagify', "dataRole": "tagsinput", holder: 'ucsm-primary dns nameserver unique_ip col-lg-6 col-md-6 col-sm-6 col-xs-6', mandatory: true}) + 
							'<div style="margin-bottom: 10px;" class="clear col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>' +
							loadFormTemplate({id: 'adminPasswd', type: 'password', label: localization['admin-password'], holder: 'ucsm-primary pri_passwd col-lg-6 col-md-6 col-sm-6 col-xs-6', mandatory: true, helptext: passwordHelp}) +
							loadFormTemplate({id: 'adminPasswd1', type: 'password', label: localization['confirm-password'], holder: 'ucsm-primary conf_passwd col-lg-6 col-md-6 col-sm-6 col-xs-6', mandatory: true}) +
							loadFormTemplate({id: 'domainName', label: localization['domain'], holder: 'ucsm-primary domain_name col-lg-6 col-md-6 col-sm-6 col-xs-6'}) +
						'</div>\
					</div>';
					if(UCSForConfigure.length > 0) {
						string += loadUCSMForm(2);
						loadImages('', 'ESXi', '');
						$.each(UCSForConfigure, function(index, val) {
							obj['UCSM'].push(val.mac);
						});
					}
					var isMDSPrimary = true, isNexusPrimary = true, isFAPrimary = true;
					if(MDSForConfigure.length > 0) {
						string += '<div class="clear"></div>\
						<div class="row info-section mds-container col-lg-12 col-md-12 col-sm-12 col-xs-12">\
							<h3 class="hseperator widget-subtitle bold">MDS</h3>\
						</div>';
						$.each(MDSForConfigure, function(index, val) {
							string += loadMDSForm(val, index, isMDSPrimary, 'col-lg-6 col-md-6 col-sm-12 col-xs-12');
							obj['MDS'].push(val.mac);
							isMDSPrimary = false;
						});
						string += '<div class="col-lg-6 col-md-6 col-sm-6 col-xs-6 nopadding mds">' + 
							loadFormTemplate({type: 'dropdown', id: 'mds_switch_system_image', class: 'mds_switch_system_image', label: localization['system-image'], holder: 'switch_system_image', mandatory: true}) +
						'</div>\
						<div class="col-lg-6 col-md-6 col-sm-6 col-xs-6 nopadding mds">' +
							loadFormTemplate({type: 'dropdown', id: 'mds_switch_kickstart_image', class: 'mds_switch_kickstart_image', label: localization['kickstart-image'], holder: 'switch_kickstart_image', mandatory: true}) +
						'</div>';
					}
				
					if(NEXUSForConfigure.length > 0) {
						string += '<div class="clear"></div>\
						<div class="row info-section nexus-container col-lg-12 col-md-12 col-sm-12 col-xs-12">\
							<h3 class="hseperator widget-subtitle bold">Nexus</h3>\
						</div>';
						$.each(NEXUSForConfigure, function(index, val) {
							string += loadNEXUSForm(val, index, isNexusPrimary, 'col-lg-6 col-md-6 col-sm-12 col-xs-12');
							if(systemInfo.stacktype.indexOf('-n9k-') > 0)
		                                        obj['NEXUS_9K'].push(val.mac);
		                                        else
		                                        obj['NEXUS_5K'].push(val.mac); 
							isNexusPrimary = false;
						});
						if(systemInfo.stacktype.indexOf('-n9k-') > 0) {
							string += '<div class="col-lg-6 col-md-6 col-sm-6 col-xs-6 nopadding nexus nexus_9k">' + 
								loadFormTemplate({type: 'dropdown', id: 'nexus_switch_image', class: 'nexus_switch_image', label: localization['switch-image'], holder: 'switch_image switch_system_image', mandatory: true}) +
							'</div>';
						} else {
							string += '<div class="col-lg-6 col-md-6 col-sm-6 col-xs-6 nopadding nexus nexus_5k">' + 
								loadFormTemplate({type: 'dropdown', id: 'nexus5k_system_image', class: 'nexus5k_system_image', label: localization['system-image'], holder: 'switch_system_image', mandatory: true}) +
							'</div>\
							<div class="col-lg-6 col-md-6 col-sm-6 col-xs-6 nopadding nexus nexus_5k">' + 
								loadFormTemplate({type: 'dropdown', id: 'nexus5k_kickstart_image', class: 'nexus5k_kickstart_image', label: localization['kickstart-image'], holder: 'switch_kickstart_image', mandatory: true}) +
							'</div>';
						}
					}

					if(FAForConfigure.length > 0 && FAForConfigure[0]['state'] == 'Unconfigured') {
						obj['PURE'] = [];
						isPUREConfigured = false;
						string += '<div class="clear"></div>\
						<div class="row info-section flasharray-container col-lg-12 col-md-12 col-sm-12 col-xs-12">\
							<h3 class="hseperator widget-subtitle bold">FlashArray <span class="bold dark-text" style="font-size: 75%;">(' + FAForConfigure[0].serial + ')</span></h3>\
						</div>';
						$.each(FAForConfigure, function(index, val) {
							string += loadFAForm(val, index, isFAPrimary, 'col-lg-6 col-md-6 col-sm-12 col-xs-12');
		                                        obj['PURE'].push(val.mac);
							isFAPrimary = false;
						});
					}
					string += '<div class="clear"></div>\
				</div>\
				<div class="advanced-view hide">\
				</div>\
				<div class="clear"></div>\
				<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 text-right">**Comma separated</div>\
			</div>\
			<div class="clear"></div>\
		</div>\
	</div>';
	$('.initial-setup>.smartwidget>.widget-content').html(string).data('devices', obj);
	uploadHandler('ImportConfiguration', true, settings.base_path, 'import_config', file_format.format, true, loadImportedConfig, doNothing) +
	$(".import_config .file_format").html("(" + localization['allowed-format'] + ": <b>" + file_format.type + "</b>)");
	
	$('.mds_switch_kickstart_image').after('<div type="MDS-kickstart" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	$('.mds_switch_system_image').after('<div type="MDS" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	if(systemInfo.stacktype.indexOf('-n9k-') > 0)
		$('.nexus_switch_image').after('<div type="Nexus 9k" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	else {
		$('.nexus5k_system_image').after('<div type="Nexus 5k" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
		$('.nexus5k_kickstart_image').after('<div type="Nexus 5k-kickstart" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	}
	tmp = 'ESXi';
	if(systemInfo.stacktype.indexOf('fb-') > -1)
		tmp = 'RHEL';
	$('.esxi_remote_file').after('<div type="' + tmp + '" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	$('.esxi_kickstart_file').after('<div type="' + tmp + '-kickstart" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	$('.ucs_infra_image').after('<div type="UCS-infra" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	$('.ucs_blade_image').after('<div type="UCS-blade" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');
	$('.ucs_rack_image').after('<div type="UCS-Rack" class="iso-library icon-with-link"><i class="fa fa-th-large"></i> ' + localization['select-iso-library'] + '</div>');

	doAjaxRequest({url: 'DHCPInfo', base_path: settings.base_path}, function(response) {
		dhcpInfo = response.data;
		loadGlobalConfigForm();
	}, doNothing);
	initScroller($('.initial-setup>.smartwidget .scroller'));
	var height = parseInt($('.stepContainer').height()) - 100;
	$('.initial-setup>.smartwidget .scroller').css('height', height + 'px').css('max-height', height + 'px');
	height = parseInt($('.stepContainer').height()) - 40;
	$('.initial-setup .widget-content').css('height', height + 'px');

	if(typeof systemInfo.server_types != 'undefined' && typeof systemInfo.server_types.rack != 'undefined' && systemInfo.server_types.rack) $('.toggle-select.component_type').closest('.control-group').removeClass('hide');
	$('.toggle-select.component_type').toggles({type: 'select', on: false, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {off: 'Blade Server', on: 'Rack Server'}});
	$('.toggle-select.component_type').on('toggle', function(e, active) {
		$('.ucsm-configure .ucs_upgrade.blade_image, .ucsm-configure .ucs_upgrade.rack_image').addClass('hide');
		if($('#ucs_upgrade').is(':checked')) {
			if(active) {
				$('.ucsm-configure .ucs_upgrade.rack_image').removeClass('hide');
			} else {
				$('.ucsm-configure .ucs_upgrade.blade_image').removeClass('hide');
			}
		}
	});

	$('.toggle-select.viewmode').toggles({type: 'select', on: true, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['basic'], off: localization['advanced']}});
	$('.toggle-select.viewmode').on('toggle', function(e, active) {
		$('.initial-setup .basic-view, .initial-setup .advanced-view').addClass('hide');
		if(active) {
			$('.initial-setup .basic-view').removeClass('hide');
		} else {
			$('.initial-setup .advanced-view').removeClass('hide');
		}
	});

	bindTagifyEvent('#ntp_server', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
	bindTagifyEvent('#dns', 'Add IP Address', /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/);
	if(!isPUREConfigured) {
		bindTagifyEvent('#fa_alert_emails_0', 'Add an email', /^[a-zA-Z0-9.!#$%&â€™*+/=?^_{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/);
	}

	var flag = true, mdsflag = true, nexusflag = true;
	$.each(UCSForConfigure, function(index, val) {
		$('.toggle-select.switchFabric_' + index).toggles({type: 'select', on: flag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'A', off: 'B'}});
		flag = false;
	});
	$.each(NEXUSForConfigure, function(index, val) {
		$('.toggle-select.nexusSwitch_' + index).toggles({type: 'select', on: nexusflag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'A', off: 'B'}});
		nexusflag = false;
	});
	$.each(MDSForConfigure, function(index, val) {
		$('.toggle-select.mdsSwitch_' + index).toggles({type: 'select', on: mdsflag, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: 'A', off: 'B'}});
		mdsflag = false;
	});

	if(UCSForConfigure.length > 1) {
		$('.toggle-select.mode').addClass('disabled');
		$('.toggle-select.config_type').closest('.control-group').addClass('hide');
	}
	$('.toggle-select.mode').toggles({type: 'select', on: false, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['standalone'], off: localization['cluster']}});
	$('.toggle-select.config_type').toggles({type: 'select', on: true, animate: 250, easing: 'swing', width: 'auto', height: '22px', text: {on: localization['primary'], off: localization['subordinate']}});
	toggleSwitches();
}

/**
  * @desc .
  * @param object $response - .
*/
function loadImportedConfig(response) {
	var dom, tmp;
	$('.fs-configurations').removeClass('hide');
	$('.buttonNext').removeClass('buttonDisabled');
	var server_type = (response.data.server_type == 'Blade') ? false : true;
	$('.toggle-select.component_type').toggles(server_type);
	var stacktype = systemInfo.subtype;
	if(server_type) stacktype += '-rack';

	doAjaxRequest({url: 'JSONConfig', base_path: settings.base_path, query: {stacktype: stacktype}}, function(response) {
		$.each(response.data.global_config, function(index, value) {
			if(value.name == 'ntp') {
				$('#ntp_server').prev('.bootstrap-tagsinput').find('span').each(function() {
					$('#ntp_server').tagsinput('remove', $(this).text());
				});
				$.each(value.value.split(","), function(i, v) {
					$('#ntp_server').tagsinput('add', trimChar(v, " "));
				});
			} else {
				dom = $('.fs-configurations .control-group.' + value.name);
				plotValuesByDom(dom, value.value);
			}
		});
		loadConfigValues(response.data.devices);
		var mds_index = 0, nexus_index = 0, tag;
		$.each(response.data.devices, function(index, value) {
			value.device_type = value.device_type.toLowerCase().replace(' ', '_');
			var dom, slider, tmp;
			switch(value.device_type) {
				case 'ucsm':
					if('mode' in value && value.mode == 'primary') {
						$('.ucsm-configure #virtualIP.task-input').val(value.virtual_ip);
						$('.ucsm-configure .control-group.switch_ip #oobIP_0.task-input').val(value.switch_ip);
						$('.ucsm-configure .control-group #fabric_mapping_0.task-input option[tag="' + value.tag + '"]').attr("selected","selected");
						if($('#fabric_mapping_0').closest('.control-group').prev().find('.fabricSwitch').length > 0) {
							tmp = $('#fabric_mapping_0').closest('.control-group').prev().find('.fabricSwitch').data('toggles');
							tag = (tmp.active) ? 'A' : 'B';
							if(tag != value.tag)
								tmp.toggle();
						}
						dom = $('.ucsm-configure .control-group.kvm_console_ip').find('#workflow_kvm_console_ip.range-slider');
						tmp = value.kvm_console_ip.split('-');
						slider = dom.data("ionRangeSlider");
						slider.update({
							from: parseInt(tmp[0]),
							to: parseInt(tmp[1])
						});
						updateDHCPIPs($(".control-group.kvm_console_ip #workflow_kvm_console_ip.range-slider"));
						
						if((parseInt(tmp[0]) > parseInt(dhcpInfo.dhcp_start.split(".").pop()) && parseInt(tmp[0]) < parseInt(dhcpInfo.dhcp_end.split(".").pop())) || 
							(parseInt(tmp[1]) > parseInt(dhcpInfo.dhcp_start.split(".").pop()) && parseInt(tmp[1]) < parseInt(dhcpInfo.dhcp_end.split(".").pop()))) {
							$('.ucsm-configure .control-group.kvm_console_ip').find('.help-block').show().html(localization['dhcp_kvm_overlap']);
						}
					} else {
						$('.ucsm-configure .control-group.switch_ip #oobIP_1.task-input').val(value.switch_ip);
						$('.ucsm-configure .control-group #fabric_mapping_1.task-input option[tag="' + value.tag + '"]').attr("selected","selected");
						if($('#fabric_mapping_1').closest('.control-group').prev().find('.fabricSwitch').length > 0) {
							tmp = $('#fabric_mapping_1').closest('.control-group').prev().find('.fabricSwitch').data('toggles');
							tag = (tmp.active) ? 'A' : 'B';
							if(tag != value.tag)
								tmp.toggle();
						}
					}
					break;
				case 'mds':
					$('.block.mds.mds_' + mds_index + ' .control-group.switch_ip #mds_ipaddress_' + mds_index + '.task-input').val(value.switch_ip);
					mds_index++;
					break;
				case 'nexus_5k':
				case 'nexus_9k':
					$('.block.nexus.nexus_' + nexus_index + ' .control-group.switch_ip #nexus_ipaddress_' + nexus_index + '.task-input').val(value.switch_ip);
					nexus_index++;
					break;
				case 'pure':
					$('.block.pure.flasharray .control-group #fa_vir0_ip_0.task-input').val(value.vir0_ip);
					$('.block.pure.flasharray .control-group #fa_ct0_ip_0.task-input').val(value.ct0_ip);
					$('.block.pure.flasharray .control-group #fa_ct1_ip_0.task-input').val(value.ct1_ip);
					
					$('.block.pure.flasharray .control-group #fa_array_name_0.task-input').val(value.array_name);
					$('.block.pure.flasharray .control-group #fa_sender_domain_0.task-input').val(value.domain_name);
					$('.block.pure.flasharray .control-group #fa_full_name_0.task-input').val(value.full_name);
					$('.block.pure.flasharray .control-group #fa_job_title_0.task-input').val(value.job_title);
					$('.block.pure.flasharray .control-group #fa_organization_0.task-input').val(value.organization);
					break;
			}
		});

		var j, types = ['mds', 'nexus'];
		for(i = 0; i < 2; i++) {
			$.each(types, function(n, type) {
				$('#' + type + '_mapping_' + i).prop('selectedIndex', i);
				if($('#' + type + '_mapping_' + i).closest('.control-group').prev().find('.' + type + 'Switch').length > 0) {
					tmp = $('#' + type + '_mapping_' + i).closest('.control-group').prev().find('.' + type + 'Switch').data('toggles');
					if($('option:selected', $('#' + type + '_mapping_' + i)).attr('tag') == 'A') tmp.toggle(true);
					else tmp.toggle(false);
				}
			});
			$('#mds_switch_name_' + i).val($('#mds_mapping_' + i).val());
			$('#nexus_switch_name_' + i).val($('#nexus_mapping_' + i).val());
		}
	}, doNothing);
}

/**
  * @desc .
*/
function toggleSwitches() {
	$('.toggle-select.fabricSwitch').on('click', function(e) {
		e.stopPropagation();
		var toggle, current = $(this);
		$('.toggle-select.fabricSwitch').each(function(index) {
			if(!current.is($(this))) {
				toggle = $(this).data('toggles');
				toggle.toggle();
			}
		});
	});
	$('.toggle-select.nexusSwitch').on('click', function(e) {
		e.stopPropagation();
		var toggle, current = $(this);
		$('.toggle-select.nexusSwitch').each(function(index) {
			if(!current.is($(this))) {
				toggle = $(this).data('toggles');
				toggle.toggle();
			}
		});
	});
	$('.toggle-select.mdsSwitch').on('click', function(e) {
		e.stopPropagation();
		var toggle, current = $(this);
		$('.toggle-select.mdsSwitch').each(function(index) {
			if(!current.is($(this))) {
				toggle = $(this).data('toggles');
				toggle.toggle();
			}
		});
	});
}

/**
  * @desc .
*/
var counter = 0, formData = [];
function loadGlobalConfigForm() {
	var str = '<div class="row info-section col-lg-12 col-md-12 col-sm-12 col-xs-12">\
		<h3 class="hseperator widget-subtitle bold">' + localization['advanced_config'] + '</h3>\
	</div>';
	$('.initial-setup .advanced-view').html(str);
	$('.initial-setup .global.block').remove();
	loaderCnt = addProcessingSpinner('.content-container');
	return doAjaxRequest({url: 'GetGlobals', base_path: settings.base_path, query: {stacktype: systemInfo.subtype}}, function(response) {
		formData = response.data;
		loadGlobalFormFields();
	}, doNothing);
}

/**
  * @desc .
*/
function loadGlobalFormFields() {
	var container;
	if(counter < formData.length) {
		if(!formData[counter].hidden) {
			if(formData[counter].view == 'basic') {
				container = 'common-inputs';
				if(typeof formData[counter].hwtype != 'undefined' && formData[counter].hwtype.length > 0) {
					$.each(formData[counter].hwtype, function(i, v) {
						if(typeof v != 'undefined' && v.length > 0) {
							if($('.initial-setup .' + v + ' > .form').length) {
								container = v;
								return false;
							}
						}
					});
				}
				$('.initial-setup .' + container + ' > .form').first().append('<div class="col-lg-6 col-md-6 col-sm-12 col-xs-12 nopadding global block">' + loadWorkflowInputForm(formData[counter], 'global-config').advanced + '</div>');
			} else 
				$('.initial-setup .advanced-view').append('<div class="col-lg-6 col-md-6 col-sm-12 col-xs-12 nopadding global block">' + loadWorkflowInputForm(formData[counter], 'global-config').advanced + '</div>');
			
			populateFormData(formData[counter], 'global-config', 0, 1);
		} else {
			counter++;
			loadGlobalFormFields();
		}
	} else {
		$.each(formData, function(i, v) {
			if(v.reset) {
				$('div[argname="' + v.name + '"]').find('.regenerate').data('config', v.api);
			}
		});
		counter = 0; formData = [];
		$('.task-input[type="multiselect-dropdown"]').each(function(index) {
			initMultiSelect($(this), $(this).attr('label'), true, true, 1);
		});
		$('.task-input[dropdown-type="select-box"]').each(function(index) {
			$(this).select2();
		});
		$('.control-group .controls span.prefix').each(function(index) {
			var borderWidth = 15 + $(this).outerWidth();
			$(this).next('input.prefix').css('border-left-width', borderWidth + 'px');
		});

		$('.control-group .controls span.suffix').each(function(index) {
			var borderWidth = 15 + $(this).outerWidth();
			$(this).prev('input.suffix').css('border-right-width', borderWidth + 'px');
		});
		initTooltip('.fs-configurations');
		populateData();
	}
}

/**
  * @desc .
*/
function updateGlobalConfig() {
	var data = {};
	var obj = getFormData('.initial-setup .global .control-group');
	Object.keys(obj.task_input_api).some(function(key) {
		data[key] = obj.task_input_api[key].values;
	});
	if(!isPUREConfigured) {
		data["pure_id"] = $('#fa_switch_mac_0').val();
	}

	var stack = systemInfo.subtype;
	stack = stack.replace("-rack", "");
	var myToggle = $('.toggle-select.component_type').data('toggles');
	if(myToggle.active && stack.indexOf('-rack') < 0) stack += '-rack';
	doAjaxRequest({url: 'SetGlobals', base_path: settings.base_path, query: {stacktype: stack}, data: data, method: 'PUT', isValidate: true, formContainer: ['.initial-setup .basic-view', '.initial-setup .advanced-view']}, function(response) {
		requestCallback.requestComplete(true);
	}, function(response) {
		callbackFlag = false;
		requestCallback.requestComplete(true);
		removeProcessingSpinner('.content-container', loaderCnt);
	});
}

/**
  * @desc .
*/
function populateData() {
	$.when(
		loadImages('', '', '')
	).then(function() {
		setTimeout(function() {
			populateNetworkInfo();
			populateDefaults($('.initial-setup>.smartwidget>.widget-content').data('devices'));
		}, 500);
	});
}

function updateDHCPIPs(dom) {
	dom.closest('[type="range-picker"]').find('.showcase__mark').remove();
	let html = '<span class="showcase__mark help-txt tipso tipso_style" data-tipso-title="DHCP Range/Reserved IPs" data-tipso="These IP address ranges are used for device discovery." data-html="true" data-toggle="tooltip" style="left: ' + dhcpLeft + '; width: ' + dhcpWidth + ';">' + dhcpInfo.dhcp_start.split(".").pop() + '-' + dhcpInfo.dhcp_end.split(".").pop() + '</span>';
	dom.closest('[type="range-picker"]').find('span.irs').find('span.irs').after(html);
	
	$('.tipso_bubble').remove();
	initTooltip('[type="range-picker"]');
}

/**
  * @desc .
  * @param array $data - .
*/
var dhcpLeft, dhcpWidth;
function loadConfigValues(data) {
	var marks = [], dom, slider, tmp;
	marks.push(parseInt(dhcpInfo.dhcp_start.split(".").pop()));
	marks.push(parseInt(dhcpInfo.dhcp_end.split(".").pop()));
	$('.fabric_mapping, .mds_mapping, .nexus_mapping').html('');
	$('.ucsm-configure .ucs_upgrade:not(#ucs_upgrade)').addClass('hide');
	$.each(data, function(index, value) {
		value.device_type = value.device_type.toLowerCase().replace(' ', '_');
		Object.keys(value).some(function(key) {
			if(value.device_type == 'ucsm' && key == 'kvm_console_ip' && $('.' + value.device_type + ' input[value="' + value.switch_mac + '"]').length > 0) {
				dom = $('.' + value.device_type + ' input[value="' + value.switch_mac + '"]').closest('.' + value.device_type).find('.control-group.' + key).find('#workflow_' + key + '.range-slider');
				slider = dom.data("ionRangeSlider");
				value[key] = $.parseJSON(value[key]);
				tmp = value[key].kvm_range.split('-');
				diff = parseInt(tmp[1]) - parseInt(tmp[0]);
				dom.attr('subnet', value[key].subnet);
				dom.closest('[type="range-picker"]').find('.legend').find('.ip-subnet').html(value[key].subnet + '.');
				slider.update({
					min: parseInt(value[key].min_range),
					max: parseInt(value[key].max_range),
					from: parseInt(dhcpInfo.dhcp_start.split(".").pop()), 
					to: parseInt(dhcpInfo.dhcp_end.split(".").pop()),
					min_interval: (parseInt(value[key].min_interval) - 1),
					max_interval: (parseInt(value[key].max_interval) - 1)
				});
				dhcpLeft = $('.irs-bar').css('left');
				dhcpWidth = $('.irs-bar').css('width');
				
				var sliderInitFrom = parseInt(tmp[0]), sliderInitTo = parseInt(tmp[1]);
				slider.update({
					from: parseInt(tmp[0]),
					to: parseInt(tmp[1]),
					onChange: function(data) {
						if( (data.to <= marks[0] && ((marks[0] - data.min) < (parseInt(value[key].min_interval) - 1))) ||
							(data.from >= marks[1] && ((data.max - marks[1]) < (parseInt(value[key].min_interval) - 1))) ) {
							slider.update({from: sliderInitFrom, to: sliderInitTo});
							updateDHCPIPs($(".control-group.kvm_console_ip #workflow_kvm_console_ip.range-slider"));
							return false;
						}
						if(data.from >= marks[0] && data.from <= marks[1]) {
							slider.update({from: (marks[0] - diff - 1), to: (marks[0] - 1)});
							updateDHCPIPs($(".control-group.kvm_console_ip #workflow_kvm_console_ip.range-slider"));
							return false;
						} else if(data.to >= marks[0] && data.to <= marks[1]) {
							slider.update({from: (marks[1] + 1), to: (marks[1] + diff + 1)});
							updateDHCPIPs($(".control-group.kvm_console_ip #workflow_kvm_console_ip.range-slider"));
							return false;
						} else {
							diff = parseInt(data.to) - parseInt(data.from);
							if(diff < parseInt(value[key].min_interval)) diff = parseInt(value[key].min_interval);
							else if(diff > parseInt(value[key].max_interval)) diff = parseInt(value[key].max_interval);
						}
					},
					onFinish: function(data) {
						sliderInitFrom = data.from;
						sliderInitTo = data.to;
					}
				});
				updateDHCPIPs(dom, marks, dhcpLeft, dhcpWidth);
			} else if(key == 'switch_image') {
				try {
					value[key] = $.parseJSON(value[key]);
				} catch(err) {}
				if(typeof value[key] == 'object') {
					Object.keys(value[key]).some(function(key1) {
						dom = $('.' + value.device_type).find('.' + key1).closest('.control-group');
						plotValuesByDom(dom, value[key]);
						if($('[name="configuration-option"]:checked').val() == 'JSON') {
							dom.find('.iso-library').removeClass('hide').html('<i class="fa fa-th-large"></i> Select from ISO library');
							if(dom.find('.task-input').val() == null) {
								dom.find('.iso-library').attr("file", value[key][key1]).html('<i class="fa fa-th-large"></i> Image(' + value[key][key1] + ') is not available. Please upload.');
							}
						}
					});
				} else {}
			} else {
				if(value.device_type == 'pure')
					dom = $('.' + value.device_type + ' input[value="' + value.mac + '"]').closest('.' + value.device_type).find('.control-group.' + key);
				else
					dom = $('.' + value.device_type + ' input[value="' + value.switch_mac + '"]').closest('.' + value.device_type).find('.control-group.' + key);
				plotValuesByDom(dom, value[key]);
				if(value.device_type == 'pure' && !isPUREConfigured) {
					$('.control-group.pure_id[argname="pure_id"][execid="global-config"]').closest('.global.block').hide();
					if(key == 'alert_emails') {
						$('#fa_alert_emails_0').prev('.bootstrap-tagsinput').find('span').each(function() {
							$('#fa_alert_emails_0').tagsinput('remove', $(this).text());
						});
						$.each(value[key].split(","), function(i, value) {
							$('#fa_alert_emails_0').tagsinput('add', trimChar(value, " "));
						});
					} else if(key == 'sender_domain') {
						$('#sender_domain').val(value['sender_domain']);
					}
				}
				if(key == 'switch_name') {
					switch(value.device_type) {
						case 'ucsm':
							$('.fabric_mapping').append('<option value="' + value[key] + '" tag="' + value.tag + '">' + value[key] + '</option>');
							if('mode' in value && value.mode == 'primary') {
								dom = $('.control-group.ucsm-primary.switch_name');
								var switch_name = (value['switch_name'].lastIndexOf("-") > 0) ? value['switch_name'].substr(0, value['switch_name'].lastIndexOf("-")) : value['switch_name'];
								plotValuesByDom(dom, switch_name);
							}
							break;
						case 'nexus_9k':
						case 'nexus_5k':
							$('.nexus_mapping').append('<option value="' + value[key] + '" tag="' + value.tag + '">' + value[key] + '</option>');
							break;
						case 'mds':
							$('.mds_mapping').append('<option value="' + value[key] + '" tag="' + value.tag + '">' + value[key] + '</option>');
							break;
					}
				} else if('mode' in value && value.mode == 'primary' && (key == 'domain_name' || key == 'esxi_kickstart')) {
					dom = $('.control-group.' + key);
					plotValuesByDom(dom, value[key]);
				} else if('mode' in value && value.mode == 'primary' && (key == 'ntp_server' || key == 'dns')) {
					$('#' + key).prev('.bootstrap-tagsinput').find('span').each(function() {
						$('#' + key).tagsinput('remove', $(this).text());
					});
					$.each(value[key].split(","), function(i, value) {
						$('#' + key).tagsinput('add', trimChar(value, " "));
					});
				} else if('mode' in value && value.mode == 'primary' && key == 'server_type') {
					var server_type = (value[key] == 'Blade') ? false : true;
					$('.toggle-select.component_type').toggles(server_type);
				} else if(value[key] != '' && (key == 'esxi_file' || key == 'blade_image' || key == 'infra_image') && $('[name="configuration-option"]:checked').val() == 'JSON') {
					dom = $('.control-group.' + key);
					plotValuesByDom(dom, value[key]);
					dom.find('.iso-library').removeClass('hide').html('<i class="fa fa-th-large"></i> Select from ISO library');
					if(dom.find('.task-input').val() == null) {
						dom.find('.iso-library').attr("file", value[key]).html('<i class="fa fa-th-large"></i> Image(' + value[key] + ') is not available. Please upload.');
					}
					if((key == 'blade_image' || key == 'infra_image') && value[key] != '') {
						$('#ucs_upgrade').prop('checked', true);
						$('.ucsm-configure .ucs_upgrade.infra_image').removeClass('hide');
						if(key == 'blade_image') {
							var myToggle = $('.toggle-select.component_type').data('toggles');
							if(myToggle.active) $('.ucsm-configure .ucs_upgrade.rack_image').removeClass('hide');
							else $('.ucsm-configure .ucs_upgrade.blade_image').removeClass('hide');
						}
					}
					$('#os_install').val('');
					$('.ucsm-configure .os_install.remote_file').addClass('hide');
					if(key == 'esxi_file' && value[key] != '') {
						$('#os_install').val('Yes');
						$('.ucsm-configure .os_install.remote_file').removeClass('hide');
					}
				}
			}
		});
	});
}

/**
  * @desc .
  * @param object $data - .
*/
function populateDefaults(data) {
	doAjaxRequest({url: 'ConfigDefaults', base_path: settings.base_path, method: 'POST', data: data}, function(response) {
		loadConfigValues(response.data);
		var flag = true;
		$.each(response.data, function(index, value) {
			if(value.device_type == 'ucsm' && 'switch_name' in value === true) {
				dom = $('.' + value.device_type + ' input[value="' + value.switch_mac + '"]').closest('.' + value.device_type).find('.control-group.pri_ip');
				plotValuesByDom(dom, value.switch_ip);
			}
			if(value.device_type == 'ucsm') {
				if(value.mode == 'primary') flag = false;
				else if(value.mode == 'secondary' && flag)
					$('.toggle-select.config_type').toggles(false);
				else if(value.mode == 'standalone')
					$('.toggle-select.mode').toggles(true);
			}
		});
		removeProcessingSpinner(true);
	}, doNothing);
}

/**
  * @desc .
  * @param object $dom - .
  * @param array $value - .
*/
function plotValuesByDom(dom, value) {
	var tmp, j;
	if(dom.find('.task-input').hasClass('ip')) {
		tmp = value.split(".");
		for(i = 0; i < tmp.length; i++) {
			j = i + 1;
			dom.find('.field-group:nth-child(' + j + ')').find('.task-input').val(tmp[i]);
		}
	} else if(typeof value == 'object') {
		Object.keys(value).some(function(key) {
			plotValuesByDom(dom.parent().find('.control-group.' + key), value[key]);
		});
	} else dom.find('.task-input').val(value);
}

/**
  * @desc .
  * @param integer $column - .
*/
function loadUCSMForm(column) {
	var osArray = [];
	osArray.push({label: 'None', value: '', selected: 'selected'});
	if(systemInfo.stacktype.indexOf('fb-') > -1)
		osArray.push({label: 'RHEL', value: 'Yes', selected: ''});
	else
		osArray.push({label: 'ESXi', value: 'Yes', selected: ''});
	
	var widthCls = ' col-lg-12 col-md-12 col-sm-12 col-xs-12';
	$('.ucsm.ucsm-configure').remove();
	var str = '<div class="row ucsm ucsm-configure">';
		if(column == '2') {
			widthCls = ' col-lg-6 col-md-6 col-sm-6 col-xs-12';
			str += '<div class="info-section col-lg-12 col-md-12 col-sm-12 col-xs-12">\
				<h3 class="hseperator widget-subtitle bold">Fabric Interconnect</h3>\
			</div>';
		}
		str += '<div class="form col-lg-12 col-md-12 col-sm-12 col-xs-12">';
			str += loadFormTemplate({type: 'toggle', id: 'mode', label: localization['mode'], mandatory: true, 'holder': 'hide'}) + 
			loadFormTemplate({type: 'toggle', id: 'config_type', label: localization['type'], 'holder': 'hide'}) + 
			loadFormTemplate({type: 'toggle', id: 'component_type dark', label: 'Compute Type', mandatory: true, 'holder': 'hide ' + widthCls});
			str += '<div class="clear"></div>';
			$.each(UCSForConfigure, function(index, value) {
				str += '<div class="' + widthCls + ' nopadding">';
					var checked = false, class_name = 'sec_ip';
					if(index == 0 && UCSForConfigure.length > 1) {
						checked = true;
						class_name = 'pri_ip';
					}
					str += '<div class="seperator">' +
						loadFormField({type: 'hidden', id: 'ucsm_switch_serial_' + index, value: value.serial}) + 
						loadFormField({type: 'hidden', id: 'ucsm_switch_mac_' + index, value: value.mac}) + 
						loadFormField({type: 'hidden', id: 'ucsm_switch_ip_' + index, value: value.ip}) + 
						loadFormField({type: 'hidden', id: 'ucsm_vendor_model_' + index, value: value.vendor}) + 
						loadFormTemplate({type: 'toggle', id: 'fabricSwitch switchFabric_' + index, label: localization['fabric-setup'] + ' <span class="small bold dark-text">(' + value.serial + ')</span>', mandatory: true, holder: 'manual-config'}) + 
						loadFormTemplate({type: 'dropdown', id: 'fabric_mapping_' + index, label: 'Map Switch <span class="small bold dark-text">(' + value.serial + ')</span>', mandatory: true, class: 'fabric_mapping', holder: 'json-config hide'}) +
						loadFormTemplate({id: 'oobIP_' + index, value: value.ip, label: localization['mgmt-ip'], class: 'ipaddress', mandatory: true, holder: 'switch_ip mgmt_ip unique_ip ' + class_name}) +
					'</div>' +
				'</div>';
			});
			str += loadFormTemplate({id: 'virtualIP', label: localization['virtual-ip'], class: 'virtualIP ipaddress', holder: 'ucsm-primary virtual_ip unique_ip nopadding ' + widthCls, mandatory: true}) + 
			loadFormTemplate({id: 'primaryName', label: localization['primary-name'], holder: 'ucsm-subordinate pri_name switch_name hide nopadding ' + widthCls, mandatory: true}) +
			loadFormTemplate({id: 'oobIP', label: localization['primary-ip'], class: 'ipaddress', holder: 'ucsm-subordinate pri_ip hide nopadding ' + widthCls, mandatory: true}) + 
			loadFormTemplate({id: 'systemName', label: localization['system-name'], holder: 'ucsm-primary pri_name switch_name ' + widthCls, mandatory: true});
			str += '<div class="' + widthCls + ' nopadding">' +
				loadFormTemplate({type: 'dropdown', id: 'os_install', class: 'os_install', label: localization['operating_system'], holder: 'os_install nopadding', value: osArray}) +
				loadFormTemplate({type: 'dropdown', id: 'esxi_file', class: 'esxi_remote_file', label: 'ISO File', holder: 'esxi_file remote_file os_install hide nopadding', mandatory: true}) +
				loadFormTemplate({type: 'dropdown', id: 'esxi_kickstart', class: 'esxi_kickstart_file', label: localization['kickstart'], holder: 'esxi_kickstart remote_file os_install hide nopadding'}) +
			'</div>' +
			'<div class="' + widthCls + ' nopadding">' +
				loadFormTemplate({type: 'checkbox', id: 'ucs_upgrade', class: 'ucs_upgrade', label: localization['ucs_firmware'], holder: 'ucs_firmware nopadding'}) +
				loadFormTemplate({type: 'dropdown', id: 'infra_image', class: 'ucs_infra_image', label: localization['ucs-software-bundle'], holder: 'infra_image ucs_upgrade hide nopadding'}) + 
				loadFormTemplate({type: 'dropdown', id: 'blade_image', class: 'ucs_blade_image', label: localization['blade-software'], holder: 'blade_image ucs_upgrade hide nopadding'}) + 
				loadFormTemplate({type: 'dropdown', id: 'rack_image', class: 'ucs_rack_image', label: localization['rack-software'], holder: 'rack_image ucs_upgrade hide nopadding'}) +
			'</div>';
		str += '</div>\
		<div class="table-end"></div>\
	</div>\
	<div class="clear"></div>';
	return str;
}

/**
  * @desc .
  * @param object $options - .
  * @param number $index - .
  * @param boolean $isMDSPrimary - .
  * @param string $width - .
*/
function loadMDSForm(options, index, isMDSPrimary, width) {
	$('.mds.block.mds_' + index).remove();
	var str = '<div class="' + width + ' nopadding block mds mds_' + index + '">';
		str += '<div class="form ">' +
			loadFormTemplate({type: 'toggle', id: 'mdsSwitch mdsSwitch_' + index, label: localization['switch-selection'] + ' <span class="small bold dark-text">(' + options.serial + ')</span>', mandatory: true, holder: 'manual-config'}) + 
			loadFormTemplate({type: 'dropdown', id: 'mds_mapping_' + index, label: 'Map Switch <span class="small bold dark-text">(' + options.serial + ')</span>', mandatory: true, class: 'mds_mapping', holder: 'json-config hide'}) + 
			loadFormTemplate({id: 'mds_switch_name_' + index, label: localization['switch-name'], holder: 'switch_name', mandatory: true}) +
			loadFormTemplate({id: 'mds_ipaddress_' + index, label: localization['ip'], class: 'ipaddress', holder: 'switch_ip unique_ip', mandatory: true});
			str += loadFormField({type: 'hidden', id: 'mds_switch_serial_' + index, value: options.serial}) + 
			loadFormField({type: 'hidden', id: 'mds_switch_mac_' + index, value: options.mac}) + 
			loadFormField({type: 'hidden', id: 'mds_switch_ip_' + index, value: options.ip}) + 
			loadFormField({type: 'hidden', id: 'mds_vendor_model_' + index, value: options.vendor});
		str += '</div>\
		<div class="table-end"></div>\
	</div>';
	return str;
}

/**
  * @desc .
  * @param object $options - .
  * @param number $index - .
  * @param boolean $isNexusPrimary - .
  * @param string $width - .
*/
function loadNEXUSForm(options, index, isNexusPrimary, width) {
	var type = 'nexus_9k';
	if(systemInfo.stacktype.indexOf('-n5k-') > 0) type = 'nexus_5k';
	$('.nexus.block.nexus_' + index).remove();
	var str = '<div class="' + width + ' nopadding block nexus ' + type + ' nexus_' + index + '">';
		str += '<div class="form nopadding">' +
			loadFormTemplate({type: 'toggle', id: 'nexusSwitch nexusSwitch_' + index, label: localization['switch-selection'] + ' <span class="small bold dark-text">(' + options.serial + ')</span>', mandatory: true, holder: 'manual-config'}) + 
			loadFormTemplate({type: 'dropdown', id: 'nexus_mapping_' + index, label: 'Map Switch <span class="small bold dark-text">(' + options.serial + ')</span>', mandatory: true, class: 'nexus_mapping', holder: 'json-config hide'}) + 
			loadFormTemplate({id: 'nexus_switch_name_' + index, label: localization['switch-name'], holder: 'switch_name', mandatory: true}) + 
			loadFormTemplate({id: 'nexus_ipaddress_' + index, label: localization['ip'], class: 'ipaddress', holder: 'switch_ip unique_ip', mandatory: true}) + 
			loadFormField({type: 'hidden', id: 'nexus_switch_serial_' + index, value: options.serial}) + 
			loadFormField({type: 'hidden', id: 'nexus_switch_mac_' + index, value: options.mac}) + 
			loadFormField({type: 'hidden', id: 'nexus_switch_ip_' + index, value: options.ip}) + 
			loadFormField({type: 'hidden', id: 'nexus_vendor_model_' + index, value: options.vendor});
		str += '</div>\
		<div class="table-end"></div>\
	</div>';
	return str;
}


/**
  * @desc .
  * @param object $options - .
  * @param number $index - .
  * @param boolean $isNexusPrimary - .
  * @param string $width - .
*/
function loadFAForm(options, index, isFAPrimary, width) {
	$('.flasharray.block.fa_' + index).remove();
	var str = '<div class="col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding block pure flasharray fa_' + index + '">';
		str += '<div class="form nopadding">' +
			loadFormTemplate({id: 'fa_array_name_' + index, label: 'FlashArray Name', class: '', holder: 'array_name fa_name ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'fa_vir0_ip_' + index, label: localization['virtual-ip'], class: 'ipaddress', holder: 'vir0_ip fa_virtual_ip unique_ip ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'fa_ct0_ip_' + index, label: 'Controller 0 ' + localization['ip'], class: 'ipaddress', holder: 'ct0_ip fa_controller0_ip unique_ip ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'fa_ct1_ip_' + index, label: 'Controller 1 ' + localization['ip'], class: 'ipaddress', holder: 'ct1_ip fa_controller1_ip unique_ip ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'fa_organization_' + index, label: 'Organization Name', class: '', holder: 'fa_eula organization fa_organization ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'fa_full_name_' + index, label: 'Your Name', class: '', holder: 'fa_eula full_name fa_full_name ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'fa_job_title_' + index, label: 'Your Title', class: '', holder: 'fa_eula job_title fa_job_title ' + width, mandatory: true}) + 
			loadFormTemplate({id: 'sender_domain', label: 'Sender Domain', holder: 'sender_domain fa_sender_domain ' + width, mandatory: true, helptext: 'Email Domain Name (Example: flashstack.cisco.com)'}) + 
			loadFormTemplate({id: 'fa_alert_emails_' + index, label: 'Alert Email Address(s)**', class: 'tags tagify', "dataRole": "tagsinput", holder: 'alert_emails fa_alert_emails ' + width}) + 
			loadFormField({type: 'hidden', id: 'fa_switch_serial_' + index, value: options.serial}) + 
			loadFormField({type: 'hidden', id: 'fa_switch_mac_' + index, value: options.mac}) + 
			loadFormField({type: 'hidden', id: 'fa_switch_ip_' + index, value: options.ip}) + 
			loadFormField({type: 'hidden', id: 'fa_vendor_model_' + index, value: options.vendor});
		str += '</div>\
		<div class="table-end"></div>\
	</div>';
	return str;
}

/**
  * @desc .
*/
function populateNetworkInfo() {
	doAjaxRequest({url: 'NetworkInfo', base_path: settings.base_path}, function(response) {
		plotValuesByDom($('.control-group.gateway'), response.data.gateway, 'gateway');
		plotValuesByDom($('.control-group.netmask'), response.data.netmask, 'netmask');
	}, doNothing);
}

/**
  * @desc .
*/
function loadDHCPSettingsForm() {
	doAjaxRequest({url: 'DHCPInfo', base_path: settings.base_path, container: '.modal-inset', formContainer: '.modal-inset .dhcp_settings'}, function(response) {
		var str = '<div class="dhcp_settings">' +
			'<h5 class="notification info inline fixed"><i class="fa fa-info-circle"></i> ' + localization['dhcp-settings-msg'] + '.</h5>' +
			loadFormTemplate({id: 'dhcp_subnet', label: 'Network', value: response.data.subnet, readonly: true, class: 'disabled ipaddress', holder: 'dhcp subnet'}) +
			loadFormTemplate({id: 'dhcp_netmask', label: localization['netmask'], value: response.data.netmask, readonly: true, class: 'disabled ipaddress', holder: 'dhcp netmask'}) +
			loadFormTemplate({id: 'dhcp_gateway', label: localization['gateway'], value: response.data.gateway, readonly: true, class: 'disabled ipaddress', holder: 'dhcp gateway'}) +
			loadFormTemplate({id: 'dhcp_ipaddress', label: 'SmartConfig ' + localization['ip'], value: response.data.ip, readonly: true, class: 'disabled ipaddress', holder: 'dhcp server_ip'}) +
			loadFormTemplate({id: 'dhcp_ranges', label: localization['dhcp-static-range'], holder: 'dhcp ranges range-slider', helptext: localization['static-range-info']}) +
		'</div>';
		$('.modal-body #form-body .mCSB_container').html(str);
		$('#dhcp_ranges').after('<div class="legend">\
			<span><i class="orange-text fa fa-square"></i>' + localization['dhcp_range'] + '</span>\
			<span class="pull-right"><i class="light-grey-text fa fa-square"></i>' + localization['static_range'] + '</span>\
		</div>');
		var max = response.data.end.split(".").pop();
		$("#dhcp_ranges").ionRangeSlider({
			type: "double",
			grid: true,
			force_edges: true,
			min: response.data.start.split(".").pop(),
			max: max,
			from: parseInt(response.data.dhcp_start.split(".").pop()),
			//from_min: parseInt(response.data.dhcp_start.split(".").pop()),
			//from_fixed: true,
			//from_shadow: true,
			min_interval: 10,
			max_interval: 40,
			to: response.data.dhcp_end.split(".").pop(),
			//to_max: (max - 30),
			drag_interval: true
		});
		if(systemInfo.dhcp_status == "enabled") {
			$('#enable-dhcp').prop('checked', true);
			$('div.control-group.dhcp').removeClass('hide');
		}
		$('.modal-inset .help-txt').tipso({
			position: 'top',
			animationIn: 'bounceIn',
			animationOut: 'bounceOut',
			titleBackground: 'rgb(247, 124, 61)',
			background: '#FFF',
			color: '#454545',
			tooltipHover: true,
			onBeforeShow: function(ele, tipso) {
				
			}
		});
	}, doNothing);
}

/**
  * @desc .
*/
function loadAddDeviceForm() {
	var str = '<div class="add_device">';
		str += loadFormTemplate({type: 'group', label: 'Hardware Type', class: 'hardware_device', holder: 'hwtype', fields: [
			{type: 'radio', id: 'hardware_pure', optional_label: 'FlashArray', value: 'PURE', name: 'hardware_device', checked: true},
			{type: 'radio', id: 'hardware_fb', optional_label: 'FlashBlade', value: 'FlashBlade', name: 'hardware_device'}
		]}) + 
		loadFormTemplate({id: 'add_ip_address', label: localization['ip'], class: 'ipaddress', holder: 'ip ip_address', mandatory: true}) + 
		loadFormTemplate({id: 'add_user_name', label: localization['username'], holder: 'username', mandatory: true}) + 
		loadFormTemplate({type: 'password', id: 'add_password', label: localization['password'], holder: 'password', mandatory: true}) + 
	'</div>';
	return str;
}

/**
  * @desc .
  * @param string $attr - .
*/
function loadISOLibraryForm(attr) {
	var style = '', display = 'hide', fields = [], subtype = [], ossubtype = [];
	if(attr == '') {
		style = 'active'; display = '';
	}
	fields.push({type: 'radio', id: 'iso_image_mds', optional_label: 'NXOS MDS', value: 'MDS', name: 'image_type', class: 'iso_image ' + style, checked: true});
	subtype.push({type: 'radio', id: 'iso_image_mds_kickstart', optional_label: 'Kickstart', value: 'MDS-kickstart', class: 'sub_image MDS ' + style, name: 'image_sub_type', checked: true});
	subtype.push({type: 'radio', id: 'iso_image_mds_image', optional_label: 'System Software', value: 'MDS', name: 'image_sub_type', class: 'sub_image MDS ' + style});

	fields.push({type: 'radio', id: 'iso_image_nexus', optional_label: 'NXOS NEXUS', value: 'Nexus', name: 'image_type', class: 'iso_image ' + style});
	subtype.push({type: 'radio', id: 'iso_image_nexus9k_image', optional_label: 'Nexus 9k System Software', value: 'Nexus 9k', name: 'image_sub_type', class: 'sub_image Nexus ' + style, holder: 'hide'});
	subtype.push({type: 'radio', id: 'iso_image_nexus5k_image', optional_label: 'Nexus 5k System Software', value: 'Nexus 5k', name: 'image_sub_type', class: 'sub_image Nexus ' + style, holder: 'hide'});
	subtype.push({type: 'radio', id: 'iso_image_nexus5k_kickstart', optional_label: 'Nexus 5k Kickstart', value: 'Nexus 5k-kickstart', class: 'sub_image Nexus ' + style, name: 'image_sub_type', holder: 'hide'});

	fields.push({type: 'radio', id: 'iso_image_ucsm', optional_label: 'NXOS UCS', value: 'UCSM', name: 'image_type', class: 'iso_image ' + style});
	subtype.push({type: 'radio', id: 'iso_image_ucs_infra', optional_label: 'Infrastructure Image', value: 'UCS-infra', name: 'image_sub_type', class: 'sub_image UCSM ' + style, holder: 'hide'});
	subtype.push({type: 'radio', id: 'iso_image_ucs_blade', optional_label: 'B-Series Blade Image', value: 'UCS-blade', name: 'image_sub_type', class: 'sub_image UCSM ' + style, holder: 'hide'});
	subtype.push({type: 'radio', id: 'iso_image_ucs_rack', optional_label: 'C-Series Rack Image', value: 'UCS-Rack', name: 'image_sub_type', class: 'sub_image UCSM ' + style, holder: 'hide'});

	subtype.push({type: 'radio', id: 'iso_image_bare_metal', optional_label: 'Bare Metal', value: 'Bare-Metal', name: 'image_sub_type', class: 'sub_image UCSM ' + style, disabled: 'disabled', holder: 'operating_system hide disabled'});
	subtype.push({type: 'radio', id: 'iso_image_hyper_v', optional_label: 'Hyper-V', value: 'Hyper-v', name: 'image_sub_type', class: 'sub_image UCSM ' + style, disabled: 'disabled', holder: 'operating_system hide disabled'});
	subtype.push({type: 'radio', id: 'iso_image_kvm', optional_label: 'KVM', value: 'KVM', name: 'image_sub_type', class: 'sub_image UCSM ' + style, disabled: 'disabled', holder: 'operating_system hide disabled'});
	subtype.push({type: 'radio', id: 'iso_image_os', optional_label: 'vSphere ESXi', value: 'ESXi', name: 'image_sub_type', class: 'sub_image UCSM ' + style, holder: 'operating_system hide'});
	subtype.push({type: 'radio', id: 'iso_image_rhel', optional_label: 'RHEL', value: 'RHEL', name: 'image_sub_type', class: 'sub_image UCSM ' + style, holder: 'operating_system hide'});
	ossubtype.push({type: 'radio', id: 'iso_image_esxi_iso', optional_label: 'ISO', value: 'ESXi', name: 'image_os_sub_type', class: 'os_sub_image ESXi ' + style, holder: ''});
	ossubtype.push({type: 'radio', id: 'iso_image_esxi_kickstart', optional_label: localization['kickstart'], value: 'ESXi-kickstart', name: 'image_os_sub_type', class: 'os_sub_image ESXi ' + style, holder: ''});
	ossubtype.push({type: 'radio', id: 'iso_image_rhel_iso', optional_label: 'ISO', value: 'RHEL', name: 'image_os_sub_type', class: 'os_sub_image RHEL ' + style, holder: 'hide'});
	ossubtype.push({type: 'radio', id: 'iso_image_rhel_kickstart', optional_label: localization['kickstart'], value: 'RHEL-kickstart', name: 'image_os_sub_type', class: 'os_sub_image RHEL ' + style, holder: 'hide'});

	var str = '<div class="form-container nopadding">\
		<div class="">\
			<div>\
				<div id="list-images" type="' + attr + '">\
					<form id="import_form">' +
						'<div class="' + display + '">' +
							'<div class="controls mode-container addition-info col-lg-12 col-md-12 col-sm-12 col-xs-12 nopadding ">' +
								loadFormField({type: 'toggle', id: 'image_mode capitalize pull-right dark'}) +
								'<div class="clear"></div>\
							</div>' +
							'<div class="clear"></div>' +
							loadFormTemplate({type: 'group', label: localization['firmware'], class: 'hardware_device', holder: 'firmware hwtype', fields: fields, mandatory: true}) + 
							loadFormTemplate({type: 'group', label: localization['operating_system'], class: 'sub_hardware', holder: 'sub_hwtype', fields: subtype, mandatory: true}) + 
							loadFormTemplate({type: 'group', label: localization['type'], class: 'sub_hardware', holder: 'sub_ostype hide', fields: ossubtype, mandatory: true}) + 
						'</div>' + 
						loadFormTemplate({type: 'file', id: 'import_iso', name: 'uploadfile', label: localization['image-file'], holder: 'import_iso', mandatory: true}) +
						'<div class="control-group">\
							<label class="col-lg-5 col-md-5 col-sm-4 col-xs-4"></label>\
							<div class="controls col-lg-7 col-md-7 col-sm-8 col-xs-8">\
								<button type="button" class="primary nomargin" id="importBtn">' + localization['import'] + '</button>\
							</div>\
						</div>\
						<div class="clear"></div>\
					</form>\
					<div class="clear"></div>\
					<div class="images-list spadding"></div>\
					<div class="clear"></div>\
				</div>\
			</div>\
		</div>\
		<div class="clear"></div>\
	</div>';
	return str;
}

/**
  * @desc .
  * @param string $container - .
  * @param string $type - .
  * @param string $file - .
*/
function loadImages(container, type, file) {
	return doAjaxRequest({url: 'ListImages', base_path: settings.base_path, container: container}, function(response) {
		var action_icons = [], length = 0, str = '<div class="">';
		var arr = ['#iso_file', '#esxi_file', '#esxi_kickstart', '.nexus_switch_image', '.nexus5k_system_image', '.nexus5k_kickstart_image', '.mds_switch_kickstart_image', '.mds_switch_system_image', '.ucs_infra_image', '.ucs_blade_image', '.ucs_rack_image'];
		$.each(arr, function(key, val) {
			$(val).attr('data', $(val).val());
		});
		$('#iso_file, #esxi_file, #esxi_kickstart, .nexus_switch_image, .nexus5k_system_image, .nexus5k_kickstart_image, .mds_switch_kickstart_image, .mds_switch_system_image, .ucs_infra_image, .ucs_blade_image, .ucs_rack_image').html('<option value="">' + localization['select-file'] + '</option>');
		if(response.data.length > 0) {
			str += '<table>\
				<tr class="head">\
					<th>' + localization['file-name'] + '</th>\
					<th>' + localization['type'] + '</th>\
					<th>' + localization['action'] + '</th>\
				</tr>';
				$.each(response.data, function(key, value) {
					switch(value.type) {
						case 'ESXi':
							if(systemInfo.stacktype.indexOf('fb-') == -1)
								$('#iso_file, #esxi_file').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'ESXi-kickstart':
							if(systemInfo.stacktype.indexOf('fb-') == -1)
								$('#esxi_kickstart').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'RHEL':
							if(systemInfo.stacktype.indexOf('fb-') > -1)
								$('#iso_file, #esxi_file').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'RHEL-kickstart':
							if(systemInfo.stacktype.indexOf('fb-') > -1)
								$('#esxi_kickstart').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'Nexus 9k':
							$('.nexus_switch_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'Nexus 5k':
							$('.nexus5k_system_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'Nexus 5k-kickstart':
							$('.nexus5k_kickstart_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'MDS':
							$('.mds_switch_system_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'MDS-kickstart':
							$('.mds_switch_kickstart_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'UCS-infra':
							$('.ucs_infra_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'UCS-blade':
							$('.ucs_blade_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
						case 'UCS-Rack':
							$('.ucs_rack_image').append('<option value="' + value.name + '">' + value.name + '</option>');
							break;
					}
					if(type == '' || (type != '' && type == value.type)) {
						value.type = (value.type == 'UCS-infra') ? 'Infra Image' : value.type;
						value.type = (value.type == 'UCS-blade') ? 'Blade Image' : value.type;
						value.type = value.type.replace('-', ' ');
						length++;
						str += '<tr primaryid="' + value.name + '">\
							<td>' + value.name + '</td>\
							<td>' + value.type + '</td>\
							<td><i class="fa fa-trash-alt delete-image" alt="' + localization['delete-image'] + '" title="' + localization['delete-image'] + '"></i></td>\
						</tr>';
					}
				});
			str += '</table>';
		}
		if(length == 0) str += '<div class="widget-subtitle col-lg-12 col-md-12 col-sm-12 col-xs-12">' + localization['no-images-upload'] + '.</div>';
		str += '</div>\
		<div class="clear"></div>';
		$('.images-list').html(str);
		if(typeof file != 'undefined' && file != '')
			$('.images-list').before('<div class="red-text">Expected version - ' + file + '</span>');
		$.each(arr, function(key, val) {
			$(val).val($(val).attr('data'));
		});
	}, doNothing);
}

/**
  * @desc .
  * @param string $container - .
*/
function loadDevices(container) {
	clearTimeout(tout);
	var notify = true;
	if(container == '') notify = false;
	if(systemInfo.config_mode.toLowerCase() == 'json') {
		$('.buttonNext').text(localization['init_deploy']);
		$('.buttonNext').addClass('buttonDisabled');
		$('.buttonPrevious').remove();
	}
	var str = '', j = 1, style, icon, buttons, title, flag = false, callbackFlag = true, device_type;
	doAjaxRequest({url: 'FSComponents', base_path: settings.base_path, container: container, query: {initStage: true}, notify: notify}, function(response) {
		str += '<table class="table new">\
		    <thead>\
			<tr>\
			    <th>#</th>\
			    <th>' + localization['device-type'] + '</th>\
			    <th>' + localization['make'] + '/' + localization['model'] + '</th>\
			    <th>' + localization['serial'] + '</th>\
			    <th width="100"></th>\
			    <th width="200" class="center">' + localization['status'] + '</th>\
			</tr>\
		    </thead>\
		    <tbody>';
		
		$.each(response.data, function(key, value) {
			if(value.validated) {
				device_type = (value.device_type == 'UCSM') ? 'Fabric Interconnect' : value.device_type;
				device_type = (device_type == 'PURE') ? 'FlashArray' : device_type;
				icon = ''; buttons = ''; title = ''; style = 'grey-text';
				switch(value.config_state) {
					case 'Configured':
						style = 'green-text fa fa-check-circle medium';
						icon = '<span class="green-text fa fa-check-circle medium"></span>\
						<br><span class="medium">' + localization['success-configure'] + '</span>';
						break;
					case 'In-progress':
						if(value.config_state == 'In-progress') {
							icon += '<span class="small progress-bar orange-bar shine stripes">\
								<span style="width: 100%"></span>\
							</span>';
							if(value.device_type == 'UCSM' && (typeof value.infra_image != 'undefined' || typeof value.blade_image != 'undefined')) {
								icon += '<span class="medium">';
								if(typeof value.infra_image != 'undefined') icon += '<div class="center">' + localization['upgrading_firmware'] + ' <b>' + localization['version'] + ' ' + value.infra_image + '</b></div>';
								if(typeof value.blade_image != 'undefined') icon += '<div class="center">' + localization['upgrading_blade'] + ' <b>' + localization['version'] + ' ' + value.blade_image + '</b></div>';
								icon += '</span>';
							}
							else if(value.device_type == 'UCSM' || value.device_type == 'PURE') icon += '<span class="medium">' + localization['configure-inprogress'] + '</span>';
							else icon += '<span class="medium">' + localization['upgrading'] + ' <b>' + localization['version'] + ' ' + value.image_version + '</b></span>';
						}
						if(value.config_state == 'Configured')
							icon += '<br><span class="medium">' + localization['success-configure'] + '</b></span>';
						if(value.config_state == 'Re-validate')
							icon += '<br><span class="medium">' + localization['configure-failed'] + '</b></span>';
						break;
					case 'Failed':
					case 'Re-validate':
						title = ' class="failed"';
						buttons = '<a href="javascript:;" class="buttonCustom small re-validate" style="display: inline-block;">' + localization['retry'] + '</a>';
						icon = '<span class="red-text tipso tipso_style" data-tipso-title="' + localization['info'] + '" data-tipso="' + value.reval_msg + '">\
							<i class="fa fa-exclamation-triangle medium"></i>\
						</span>';
						break;
				}
				if(value.config_state != 'Configured') callbackFlag = false;
				if(value.config_state != 'Unconfigured') flag = true;
				str += '<tr mac="' + value.mac_address + '" type="' + value.device_type + '" ' + title + '>\
				    <th scope="row">' + j + '<span class="mac_address hide">' + value.mac_address + '</span><span class="ip_address hide">' + value.ip_address + '</span></th>\
				    <td><span class="device-type hide">' + value.device_type + '</span>' + device_type + '</td>\
				    <td class="vendor">' + value.vendor_model + '</td>\
				    <td class="serial_no">' + value.serial_number + '</td>\
				    <td class="action-buttons" align="right">' + buttons + '</td>\
				    <td align="center">' + icon + '</td>\
				</tr>';
				j++;
			}
		});
		str += '</tbody>\
		</table>';
		initScroller($('.device-initialization .widget-content'));
		$('.device-initialization .widget-content .mCSB_container').html(str);
		var height = parseInt($('.device-initialization').height()) - 50;
		$('.device-initialization .widget-content').css('height', height + 'px').css('max-height', height + 'px');
		
		initTooltip('.device-initialization');
		if(flag) {
			$('.buttonNext').addClass('buttonDisabled');
			$('.buttonPrevious').remove();
		}
		if(callbackFlag) {
			$('.buttonNext, .buttonPrevious').removeClass('buttonDisabled');
			disableDHCP(false);
			navigateStep(4);
		} else {
			tout = setTimeout(function () {
				loadDeviceStatus();
			}, 10000);
		}
	}, function() {
		tout = setTimeout(function () {
			loadDevices('');
		}, 10000);
	});
}

/**
  * @desc .
*/
function loadDeviceStatus() {
	clearTimeout(tout);
	var icon, buttons, flag = false, callbackFlag = true, exec_status = false;
	doAjaxRequest({url: 'FSComponents', base_path: settings.base_path, query: {initStage: true}, notify: false}, function(response) {
		$('.re-validate').remove();
		$.each(response.data, function(key, value) {
			if(value.validated) {
				exec_status = true;
				$('.device-initialization tr[mac="' + value.mac_address + '"]').removeClass('failed');
				icon = ''; buttons = '';
				switch(value.config_state) {
					case 'Configured':
						icon = '<span class="green-text fa fa-check-circle medium"></span>\
						<br><span class="medium">' + localization['success-configure'] + '</span>';
						break;
					case 'In-progress':
						if(value.config_state == 'In-progress') {
							icon += '<span class="small progress-bar orange-bar shine stripes">\
								<span style="width: 100%"></span>\
							</span>';
							if(value.device_type == 'UCSM' && (typeof value.infra_image != 'undefined' || typeof value.blade_image != 'undefined')) {
								icon += '<span class="medium">';
								if(typeof value.infra_image != 'undefined') icon += '<div class="center">' + localization['upgrading_firmware'] + ' <b>' + localization['version'] + ' ' + value.infra_image + '</b></div>';
								if(typeof value.blade_image != 'undefined') icon += '<div class="center">' + localization['upgrading_blade'] + ' <b>' + localization['version'] + ' ' + value.blade_image + '</b></div>';
								icon += '</span>';
							}
							else if(value.device_type == 'UCSM' || value.device_type == 'PURE') icon += '<span class="medium">' + localization['configure-inprogress'] + '</span>';
							else icon += '<span class="medium">' + localization['upgrading'] + ' <b>' + localization['version'] + ' ' + value.image_version + '</b></span>';
						}
						break;
					case 'Failed':
					case 'Re-validate':
						$('.device-initialization tr[mac="' + value.mac_address + '"]').addClass('failed');
						buttons = '<a href="javascript:;" class="buttonCustom small re-validate" style="display: inline-block;">' + localization['retry'] + '</a>';
						if($('.device-initialization tr[mac="' + value.mac_address + '"]').find('.tipso').length) {
							$('.device-initialization tr[mac="' + value.mac_address + '"]').find('.tipso').tipso('update', 'content', value.reval_msg);
						} else {
							icon = '<span class="red-text tipso tipso_style" data-tipso-title="' + localization['info'] + '" data-tipso="' + value.reval_msg + '">\
								<i class="fa fa-exclamation-triangle medium"></i>\
							</span>';
						}
						break;
				}
				if(value.config_state != 'Configured') callbackFlag = false;
				if(value.config_state != 'Unconfigured') flag = true;
				if(icon != '') $('.device-initialization tr[mac="' + value.mac_address + '"]').children(':last-child').html(icon);
				if(buttons != '')
					$('.device-initialization tr[mac="' + value.mac_address + '"]').children('.action-buttons').html(buttons);
			}
		});
		initTooltip('.device-initialization');
		if(systemInfo.config_mode.toLowerCase() == 'json') {
			$('.buttonNext').text('Initialize & Deploy');
			$('.buttonNext').addClass('buttonDisabled');
			$('.buttonPrevious').remove();
		} else
			$('.buttonNext, .buttonPrevious').removeClass('buttonDisabled');
		if(flag) {
			$('.buttonNext').addClass('buttonDisabled');
			$('.buttonPrevious').remove();
		}
		if(callbackFlag && exec_status) {
			$('.buttonNext, .buttonPrevious').removeClass('buttonDisabled');
			disableDHCP(false);
			navigateStep(4);
		} else {
			tout = setTimeout(function () {
				loadDeviceStatus();
			}, 10000);
		}
	}, function() {
		tout = setTimeout(function () {
			loadDeviceStatus();
		}, 10000);
	});
}
