var dev_mode = '', api_type = '';
if(getParameterByName('dev')) {
	dev_mode = 'flashstacks/';
	api_type = '.json';
}
var settings, notificationCnt = 0, autoLoad, executingApis = 0;
$(document).ready(function() {
	// Include self content while using html() method
	jQuery.fn.outerHTML = function(s) {
		return s ? this.before(s).remove() : jQuery("<p>").append(this.eq(0).clone()).html();
	};

	// Case insensitive contains method
	$.extend($.expr[":"], {
		"containsIN": function(elem, i, match, array) {
			return (elem.textContent || elem.innerText || "").toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
		}
	});
	
	String.prototype.fileExists = function() {
		filename = this.trim();
		
		var response = jQuery.ajax({
			url: filename,
			type: 'HEAD',
			async: false
		}).status;
		
		return (response != "200") ? false : true;
	}

	/* Event register for closing a notification */
	$('body').delegate('.nn-alert', 'click', function(e) {
		hideAlert($(this), 100);
	});
	
	function bindAnimationEnd() {
		//listen to animation end, then hide the element definitely
		$('.nn-alert').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
			$(this).html('');
			$(this).addClass('hide');
		});
	}
	//one call for handwritten html alerts
	bindAnimationEnd();

	/* Generate a notification */
	createAlert = function(opts) {
		notificationCnt++;
		var icon, //any icon form fontawesome would fit		eg: 'paperclip', 'exclamation-triangle', 'exclamation-circle', 'info-circle', 'check', 'check-circle'
			title, text, alertTemplate, color;
		
		if(opts === undefined) {
			opts = {};
		}
        
		icon = opts.icon || 'exclamation-triangle';
		title = opts.title || localization['error'] + '!!!';
		text = opts.text || localization['unexpected-mgs'],
		color = opts.color || 'red';

		alertTemplate = '<div id="notification_' + notificationCnt + '" api="' + opts.api + '" class="nn-alert animated bounceInRight ' + color + '"><i class="fa fa-' + icon + '"></i><strong>' + title + '</strong><p>' + text + '</p></div>';
		$(alertTemplate).appendTo('.nn-alert-container');
		
		//Hide alerts after 5 sec
		hideAlert("#notification_" + notificationCnt, 5000);
	};

	/* Event register for closing the notification */
	$('body').delegate('.ns-close', 'click', function(e) {
		$('.ns-box').removeClass('ns-show');
		setTimeout(function() { $('.ns-box').addClass('ns-hide'); }, 500);
		setTimeout(function() { $('.ns-box').remove(); }, 900);
	});
	/* Notification scripts */
	
	/* Event register for closing a model popup */
	$('body').delegate('.closeModel', 'click', function(e) {
		$(this).closest('.modal').find('.form-footer').find('button').first().trigger('click');
	});
	$('body').delegate('.closePopup', 'click', function(e) {
		$('.modal-inset .dialog').remove();
	});
	
	/* Event register for checking the input for a numeric value */
	$('body').delegate('input.numeric', 'keypress', function(e) {
		if(e.keyCode != 8 && e.keyCode != 9 && e.keyCode != 16 && e.keyCode != 37 && e.keyCode != 39 && e.keyCode != 46) {
			var regex = new RegExp("^[0-9]+$");
			var str = String.fromCharCode(!e.charCode ? e.which : e.charCode);
			if (regex.test(str)) {
				return true;
			}

			e.preventDefault();
			return false;
		}
		return true;
	});
	$('body').delegate('input.numeric', 'keyup', function(e) {
		if(e.keyCode != 8 && e.keyCode != 9 && e.keyCode != 16 && e.keyCode != 37 && e.keyCode != 39 && e.keyCode != 46 && $(this).attr('maxlength')) {
			if($(this).val().length == $(this).attr('maxlength')) {
				$(this).closest('.field-group').nextAll('.field-group').first().find(':input').focus();
			}
		}
	});
});

/** only implement if no native implementation is available
	this method is used to identify whether the variable is a array or object
*/
if (typeof Array.isArray === 'undefined') {
	Array.isArray = function(obj) {
		return Object.prototype.toString.call(obj) === '[object Array]';
	}
};

/**
  * @desc hide notification after a specified time interval
  * @param string $id - HTML dom id/class of the notification message
  * @return bool - success or failure
*/
var MyRequestsCompleted = (function() {
	var numRequestToComplete, requestsCompleted, callBacks, singleCallBack;
	return function(options) {
		if (!options) options = {};

		numRequestToComplete = options.numRequest || 0;
		requestsCompleted = options.requestsCompleted || 0;
		callBacks = [];
		var fireCallbacks = function() {
			for (var i = 0; i < callBacks.length; i++) callBacks[i]();
		};
		if (options.singleCallback) callBacks.push(options.singleCallback);

		this.addCallbackToQueue = function(isComplete, callback) {
			if (isComplete) requestsCompleted++;
			if (callback) callBacks.push(callback);
			if (requestsCompleted == numRequestToComplete) fireCallbacks();
		};
		this.requestComplete = function(isComplete) {
			if (isComplete) requestsCompleted++;
			if (requestsCompleted == numRequestToComplete) fireCallbacks();
		};
		this.setCallback = function(callback) {
			callBacks.push(callBack);
		};
	};
})();

/**
  * @desc it will generate a confirmation popup template
*/
function popupConfirmation(style, msg) {
	return '<div class="dialog">' +
		'<div class="dialog-overlay"></div>' +
		'<div class="dialog-content">' +
			'<div class="widget-title center">' + localization['confirmation'] + '</div>' +
			'<div class="dialog-body">' + msg + '</div>' +
			'<div class="dialog-footer">' +
				'<div class="form-group">' +
					'<div class="pull-left">' +
						'<button type="button" class="closePopup">' + localization['no'] + '</button>' +
					'</div>' +
					'<div class="pull-right">' +
						'<button type="button" class="' + style + ' primary">' + localization['yes'] + '</button>' +
					'</div>' +
				'</div>' +
			'</div>' +
		'</div>' +
	'</div>';
}

/**
  * @desc display the notification
  * @param string $msg - messaage string to display
*/
function showNotification(msg, sec) {
	$('body').prepend('<div class="ns-box ns-growl ns-effect-genie ns-type-notice ns-show">' +
		'<div class="ns-box-inner">' +
			'<p>' + msg + '.</p>' +
		'</div>' +
		'<span class="ns-close"></span>' +
	'</div>');
	hideNotification(sec);
}

/**
  * @desc hide notification after a specified time interval
*/
function hideNotification(sec) {
	setTimeout(function() {$('.ns-close').trigger('click');}, sec);
}

/**
  * @desc hide an alert after the specified time interval
  * @param string $id - HTML dom id/class of the alert message container
*/
function hideAlert(id, time) {
	setTimeout(function() {
		$(id).addClass('animated bounceOutRight');
		setTimeout(function() {
			$(id).addClass('hide');
		}, 500);
		setTimeout(function() {
			$(id).remove();
		}, 120000);
	}, time);
}

/**
  * @desc infra for file upload handler. It will validate the form before start uploading.
  * @param string $container - HTML dom id/class of container where to draw the loading animation.
  * @param string $formContainer - HTML dom id/class of the form to validate.
  * @param boolean $isValidate - flag - whether to validate the upload form or not.
  * @param string $successCallback - callback function to trigger upon successfull upload.
  * @param string $errorCallback - callback function to trigger upon failure upload.
*/
function doImport(container, formContainer, isValidate, successCallback, errorCallback) {
	var loaderCnt = addProcessingSpinner(container);
	if(isValidate) {	
		$(formContainer + ' .control-group').find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').removeClass('error');
		$(formContainer + ' .control-group').find('.help-block').html('');
	}
	$(formContainer + ' .files button').each(function(index) {
		data = $(this).data();
		if(!data.files.error) {
			$(this).next('span').remove();
			data.submit().always(function(response) {
				if(response.status.code == 0) {
					$(this).find('button').remove();
					if($(formContainer + ' .files button').length == 0)
						removeProcessingSpinner(container, loaderCnt);
					successCallback(response);
				} else {
					removeProcessingSpinner(container, loaderCnt);
					if(isValidate && typeof response.data == 'object' && response.data.length > 0) {
						$.each(response.data, function(i, value) {
							$(formContainer + ' .control-group.' + value.field).find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
							$(formContainer + ' .control-group.' + value.field).find('.help-block').show().html(ucfirst(value.msg));
						});
					}
					errorCallback(response);
				}
			});
		} else {
			$(this).remove();
			if($(formContainer + ' .files button').length == 0)
                                removeProcessingSpinner(container, loaderCnt);
		}
	});
	if($(formContainer + ' .files button').length == 0)
                removeProcessingSpinner(container, loaderCnt);
}

/**
  * @desc it will check the status of the background operation triggered eariler.
  * @param object $api - parameters for the api call.
  * @param object $successCallback - set of commands to execute if the request got success
  * @param object $errorCallback - set of commands to execute incase of failure
  * @param object $backgroundCallback - set of commands to execute when background operation successfully triggered
*/	
function bgTaskInfo(api, bgSuccessCallback, bgErrorCallback, backgroundCallback) {
	clearTimeout(autoLoad);
	doAjaxRequest(api, bgSuccessCallback, bgErrorCallback, backgroundCallback);
}

/**
  * @desc wrapper for making a rest request 
  * @param object $api - parameters for the api call.
  * @param object $successCallback - set of commands to execute if the request got success
  * @param object $errorCallback - set of commands to execute incase of failure
  * @param object $backgroundCallback - set of commands to execute when background operation successfully triggered
*/
function doAjaxRequest(api, successCallback, errorCallback, backgroundCallback, completeCallback) {
	// Defaults for making a rest call
	var defaults = {
		url: 'System',
		alt_url: '',
		base_path: 'pure',
		method: 'GET',
		query: '',
		data: null,
		isAsync: true,
		container: '',
		isValidate: false,
		formContainer: '',
		notify: true,
		success_notify: false
	};
	var api = $.extend({}, defaults, api);

	// Clear all validation error messages before making a rest call.
	if(api.isValidate) {
		var container = '';
		if(typeof api.formContainer == 'object') {
			$.each(api.formContainer, function(i, elem) {
				container += elem + ' .control-group,';
			});
			container = trimChar(container, ',');
		} else {
			container = api.formContainer + ' .control-group';
		}
		$(container).find('.task-input, .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').removeClass('error');
		$(container).find('.help-block, .notification-block').html('');
		$(container).find('.notification-block').addClass('hide');
	}
	// Display a progressing spinner till the UI successfully receives the response.
	var spinner_cnt = addProcessingSpinner(api.container);
	// Form the request url and data
	if(api.method != 'GET') api.data = JSON.stringify(api.data);
	var sep, url = location.protocol + '//' + window.location.host + '/' + dev_mode + api.base_path + '/' + api.url + api_type;
	if(api.query != '') {
		Object.keys(api.query).some(function(key) {
			sep = (url.indexOf('?') > -1) ? '&' : '?';
			url += sep + key + '=' + api.query[key];
		});
	}
	//sep = (url.indexOf('?') > -1) ? '&' : '?';
	//url += sep + 't=' + $.now();
	var ajaxRequest = $.ajax({
		type: api.method,
		url: url,
		data: api.data,
		async: api.isAsync,
		contentType: "application/json; charset=utf-8",
		success: function(response) {
			if(typeof response == 'string')
				response = $.parseJSON(response);
			if(response.status.code == '2') {		// Status code is 2 for background operations
				successCallback(response);
				removeProcessingSpinner(api.container, spinner_cnt);
				if(response.data.tid) {
					api.container = '';
					api.notify = false;
					api.query = {'tid': response.data.tid};
					api.url = api.alt_url;
					autoLoad = setTimeout(function() {
						bgTaskInfo(api, backgroundCallback, errorCallback, backgroundCallback);
					}, settings.background_api_duration);
				}
			} else if(response.status.code == '1') {	// Status code is 1 to display a Confirmation popup
				removeProcessingSpinner(api.container, spinner_cnt);
				successCallback(response);		// To trigger success callback
			} else if(response.status.code == '0' || response.status.code == '5') {	// A successful response for server
				if(response.status.taskid) {
					if(response.status.progress != '100') {
						api.data = {id: response.status.taskid};
						autoLoad = setTimeout(function() {
							bgTaskInfo(api, backgroundCallback, errorCallback, backgroundCallback);
						}, settings.background_api_duration);
					}
				}
				if(response.info && response.info.taskid) {
					if(response.info.progress != '100') {
						api.data = {id: response.info.taskid};
						autoLoad = setTimeout(function() {
							bgTaskInfo(api, backgroundCallback, errorCallback, backgroundCallback);
						}, settings.background_api_duration);
					}
				}
				removeProcessingSpinner(api.container, spinner_cnt);	// Remove the progressing spinner since the request got successful response.
				if(api.success_notify) {		// To display a successful status notification.
					createAlert({icon:'check-circle', title: localization['success'] + '!', color: 'green success', text: response.status.message, api: api.url});
				}
				successCallback(response);		// To trigger success callback
				
				if(response.status.code == '5' && 'notifications' in response.data) {		// Handling the warning messages.
					$.each(response.data.notifications, function(i, value) {
						container = '';
						if(typeof api.formContainer == 'object') {
							$.each(api.formContainer, function(i, elem) {
								container += elem + ' .control-group.' + value.field + ',';
							});
							container = trimChar(container, ',');
						} else {
							container = api.formContainer + ' .control-group.' + value.field;
						}
						$(container).find('.notification-block').removeClass('hide').html('<i class="fa fa-warning"></i> ' + ucfirst(value.msg));
					});
				}
			} else if(response.status.code == '-20') {	// Authentification failure.
				$.removeCookie(settings.cookie_name);
				$(location).attr('href', 'login.html');
			} else {					// Other application errors.
				removeProcessingSpinner(api.container, spinner_cnt);
				if(api.url == 'TaskInfo') {
					backgroundCallback(response);
				} else {
					if(response.status.code == '-14') {
						$(api.formContainer).find('.notification.inline:not(.fixed)').remove();
						if($(api.formContainer).find('.notification.inline').length)
							$(api.formContainer).find('.notification.inline').after('<h5 class="notification danger inline"><i class="fa fa-warning"></i> ' + response.status.message + '</h5>');
						else $(api.formContainer).prepend('<h5 class="notification danger inline"><i class="fa fa-warning"></i> ' + response.status.message + '</h5>');
					} else if(api.notify) showError(response.status, api.url);	// To display a failure status notification.
					// Display the validation error occur on the forms
					if(api.isValidate && response.data) {
						$.each(response.data, function(i, value) {
							container = '';
							if(typeof api.formContainer == 'object') {
								$.each(api.formContainer, function(i, elem) {
									container += elem + ' .control-group.' + value.field + ',';
								});
								container = trimChar(container, ',');
							} else {
								container = api.formContainer + ' .control-group.' + value.field;
							}
							$(container).find('.task-input, .bootstrap-tagsinput > [type="text"], .ms-options-wrap > button, .multiple_emails-input, .checkbox, .radio').addClass('error');
							$(container).find('.help-block').show().html(ucfirst(value.msg));
						});
					}
					errorCallback(response);	// To trigger failure callback
				}
			}
		},
		error: function(response, status) {
			errorCallback(response);
			if(status == 'error') {
				//showError({title: localization['error'] + '!', text: response.statusText});
			}
		},
		complete: function(response, status) {
			if(typeof completeCallback != 'undefined')
				completeCallback(response);
		}
	});
	return ajaxRequest;
}

/**
  * @desc empty/do nothing function
*/
function doNothing() {return false;}

/**
  * @desc generate a processing spinner within the given dom element
  * @param string $container - the element selector where to create the spinner
  * @return int - return the currently running spinners count
*/
function addProcessingSpinner(container) {
	if(container.length > 0) {
		executingApis++;
		var str = '';
		str = '<div class="ajax-overlay executingApis_' + executingApis + '"></div>\
		<div class="ajax-spinner executingApis_' + executingApis + '">\
			<div class="cs-loader">\
				<h4>' + localization['loading'] + '...</h4>\
				<div class="cs-loader-inner">\
					<label>	●</label>\
					<label>	●</label>\
					<label>	●</label>\
					<label>	●</label>\
					<label>	●</label>\
					<label>	●</label>\
				</div>\
			</div>\
		</div>';
		$(container).prepend(str);
	}
	return executingApis;
}
/**
  * @desc will remove the processing spinner generated within the given parent element.
  * @param string $container - the parent container where to check/remove for the spinner
  * @param int $spinner_cnt - the identifier of the spinner
*/
function removeProcessingSpinner(container, spinner_cnt) {
	if(typeof container == 'boolean' && container) {
		$('.ajax-overlay, .ajax-spinner').remove();
	} else if(container.length > 0) {
		setTimeout(function() {$('.executingApis_' + spinner_cnt).remove();}, 500);
	}
}

/**
  * @desc this method will throw the given error message as a notification bar on the screen top right corner.
  * @param object $error - the object will have error code and actual error message.
*/
function showError(error, api) {
	createAlert({icon:'exclamation-triangle', title: localization['error'] + '!', color: 'red failed', text: error.message, api: api});
	elementID = null;
	return false;
}

/**
  * @desc will sort an array of objects based on the key passed
  * @param array $array - the array to be sorted
  * @param string $key - the key/attribute for sorting the base array of object
  * @return bool - final sorted array
*/
function sortArrayofObjectByKey(array, key) {
	if(array.length > 0) {
		array = array.sort(function (a, b) {
			if(typeof array[0][key] == 'string') return a[key].localeCompare(b[key]);
			else return parseFloat(a[key]) - parseFloat(b[key]);
		});
	}
	return array;
}

/**
  * @desc delete an element from an array if its empty
  * @param array $array - the array to check for empty
*/
function removeEmptyElementFromArray(array) {
	array = array.filter(function(element) {
		return (element !== undefined && element !== null);
	});
	return array;
}

/**
  * @desc filter a object with the given key-value pair
  * @param object $array - the message to be displayed
  * @param string $value - the message to be displayed
  * @param string $base_key - the message to be displayed
  * @param string $field - the message to be displayed
*/
function getObjectByKeyValue(array, value, base_key, field) {
	var index = array.findIndex(function(element) {
		if(typeof field != 'undefined')
			return element[base_key][field] == value;
		else
			return element[base_key] == value;
	});
	return array[index];
}

function findObjectByKeyValue(array, key, value) {
	return result = array.filter(function (obj) {
		return obj[key].toLowerCase() == value.toLowerCase();
	})[0];
}

/**
  * @desc converts the given string to uppercase.
  * @param string $str - the string to be made uppercase
  * @return string - Uppercase string
*/
function stringToUpper(str) {
	str = str.toLowerCase().replace(/\b[a-z]/g, function(letter) {
		return letter.toUpperCase();
	});
	return str;
}

/**
  * @desc split the given string into multiple chunk with the given length
  * @param string $str - the string to be chuncked
  * @param int $n - the length of each chunk
  * @return array - array of chunked strings
*/
function chunk(str, n) {
    var ret = [];
    var i;
    var len;

    for(i = 0, len = str.length; i < len; i += n) {
       ret.push(str.substr(i, n))
    }

    return ret
}

/**
  * @desc to find a given data is a stringified or not
  * @param string $data - the string to be checked
  * @return bool - true if the given data is a string, false if not.
*/
function isStringify(data) {
	try {
		return JSON.parse(data);
	} catch(e) {
		return data;
	}
}

/**
  * @desc replace all special character or spaces with hypens on a given string
  * @param string $string - the string to be parsed
  * @return string - the slugified string which will not have any special characters or spaces.
*/
function createSlug(string) {
	return string.replace(/[^a-z0-9\s]/gi, '').replace(/[\.\,\!\@\#\$\%\^\&\*\(\)\+\{\}\[\]\;\'\"_<\>\?\s]/g, '-');
}

/**
  * @desc remove a specified character from start and end of an another string
  * @param string $string - the string to be parsed
  * @param string $charToRemove - the character to be removed
  * @return string - trimed string
*/
function trimChar(string, charToRemove) {
	while(string.charAt(0) == charToRemove) {
		string = string.substring(1);
	}
	while(string.charAt(string.length-1) == charToRemove) {
		string = string.substring(0,string.length-1);
	}
	return string;
}

/**
  * @desc get a capacity string based on a large number
  * @param float $size - the size to be formated
  * @return float - formated size
*/
function sizeStr(size) {
	var sizes = [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB'];
	for (var i = 1; i < sizes.length; i++) {
		if (size < Math.pow(1024, i)) return (Math.round((size/Math.pow(1024, i-1))*100)/100) + sizes[i-1];
	}
	return size;
}

/**
  * @desc remove the specified attribute from a key-value pair of an object
  * @param object $object - the object to be parsed
  * @param string $str - the attribute name to be removed from an object.
  * @return object - final object without the specified attribute.
*/
function removeAttributeByKey(object, str) {
	Object.keys(object).some(function(key) {
		if(key.indexOf(str) == 0)
			delete object[key];
		//else if(key.match(/^prev_api_/) != null)
			//delete object[key];
	});
	return object;
}

/**
  * @desc this will take a HTML dom as a argument and generate a file with the content inside the HTML container.
  * @param string $filename - the name of the file to download
  * @param object $dom - the HTML container dom from where to get the content
  * @param string $mimeType - the mime type of the file
*/
function downloadInnerHtml(filename, dom, mimeType) {
	var elHtml = dom.text();
	var link = document.createElement('a');
	mimeType = mimeType || 'text/plain';
	//link.setAttribute('download', filename);
	//link.setAttribute('href', 'data:' + mimeType + ';charset=utf-8,' + encodeURIComponent(elHtml));
	//link.click();
	download(elHtml, filename, mimeType);
}

/**
  * @desc it will populate the dropdown options based on the given range.
  * @param int $start - the dropdown option value to start with.
  * @param int $end - the dropdown option value to end to.
  * @param string $title - the defalt option title to show on the dropdown
  * @return string - 
*/
function populateDropdownData(start, end, title) {
	var str = '<option value="">' + title + '</option>';
	for(i = start; i <= end; i++) {
		if(i < 10) i = '0' + i;
		str += '<option value="' + i + '">' + i + '</option>';
	}
	return str;
}

/**
  * @desc Make all first character of each word as capital
  * @param string $string - string to capitalize
  * @return string - converted string.
*/
function ucfirst(string) {
	if(typeof string == 'undefined')
		return;
	return string.charAt(0).toUpperCase() + string.slice(1);
}

/**
  * @desc replace all new line character with html break tag
  * @param string $str - the string contains new line character.
  * @param bool $is_xhtml - whether to support html or not.
  * @return string - return the replaced string
*/
function nl2br(str, is_xhtml) {
	var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';    
	return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1'+ breakTag +'$2');
}

/**
  * @desc fetch the query string parameter value by its key
  * @param string $name - name of the query string key
  * @param string $url - url from where to fetch the data, if url is not passed, it will take the current browser url
  * @return string - return the query string value for the given key
*/
function getParameterByName(name, url) {
	if (!url) url = window.location.href;
	name = name.replace(/[\[\]]/g, "\\$&");
	var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
	results = regex.exec(url);
	if (!results) return null;
	if (!results[2]) return '';
	return decodeURIComponent(results[2].replace(/\+/g, " "));
}

/**
  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
  * @param array $array - the initial array of objects with duplicate entries.
  * @param string $field - attribute name by which attribute to check the duplicate entry.
  * @return array - unique array of objects(attribute based).
*/
function getUniqueFromArrayObject(array, field) {
	var flags = [], output = [];
	for(var i = 0; i < array.length; i++) {
		if( flags[array[i][field]]) continue;
		flags[array[i][field]] = true;
		output.push(array[i][field]);
	}
	return output;
}

function isValidIP(ipaddress) {
	if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress)) {
		return (true)
	}
	return (false)
}

function isValidDomain(domain) {
	if (!domain) return false;
	//var re = /^(?!:\/\/)([a-zA-Z0-9-]+\.){0,5}[a-zA-Z0-9-][a-zA-Z0-9-]+\.[a-zA-Z]{2,64}?$/gi;
	var re = /^([a-zA-Z0-9]+)([a-zA-Z0-9-]+\.){0,5}[a-zA-Z0-9-][a-zA-Z0-9-]+\.[a-zA-Z]{2,64}?$/gi;
	return re.test(domain);
}