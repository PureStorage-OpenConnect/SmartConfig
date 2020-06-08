/**
  * @desc bind ajax uploader event with the given html dom container element
  * @param string $url - the api name to trigger when clicking on the upload button.
  * @param bool $limitToOne - the flag whether to restrict to a single file or not
  * @param string $basePath - the basepath/rest api route identifier
  * @param string $container - the parent container where to list the selected files & its uploading status
  * @param string $fileFormat - the file formats(pipe seperated) to be supported
*/
function uploadHandler(url, limitToOne, basePath, container, fileFormat, autoUpload, successCallback, errorCallback) {
	$('.' + container + ' .files').html('');
	var url = location.protocol + '//' + window.location.host + '/' + dev_mode + basePath + '/' + url + api_type,
	uploadButton = $('<button/>').on('click', function() {
		var $this = $(this).prop('disabled', true).text(localization['processing'] + '...'),
		data = $this.data();
		$this.off('click').text(localization['abort']).on('click', function () {
			$this.remove();
			data.abort();
		});
		data.submit().always(function () {
			$this.remove();
		});
	});
	$('#' + container).fileupload({
		url: url,
		dataType: 'json',
		autoUpload: autoUpload,
		acceptFileTypes: fileFormat,
		maxFileSize: 0,
		maxChunkSize: 1000000000,       //1000 MB
		// Enable image resizing, except for Android and Opera,
		// which actually support image resizing, but fail to
		// send Blob objects via XHR requests:
		disableImageResize: /Android(?!.*Chrome)|Opera/
		.test(window.navigator.userAgent),
		previewMaxWidth: 100,
		previewMaxHeight: 100,
		previewCrop: true
	}).on('fileuploadadd', function (e, data) {
		if(limitToOne) {
			$('.' + container + ' .files').html('');
		}
		data.context = $('<div/>').appendTo('.' + container + ' .files');
		$.each(data.files, function (index, file) {
			$('.files > div > p.' + createSlug(file.name)).parent().remove();
			var node = $('<p class="' + createSlug(file.name) + '"/>').append($('<span/>').text(file.name));
			if(!index) {
				node.append(uploadButton.clone(true).data(data));
			}
			node.appendTo(data.context);
		});
	}).on('fileuploadprocessalways', function (e, data) {
		var index = data.index,
		file = data.files[index],
		node = $(data.context.children()[index]);
		if(file.preview) {
			node.prepend('<br>').prepend(file.preview);
		}
		node.find('span.icon, span.message').remove();
		node.find('span').first().after($('<span class="icon pull-right red-text fa fa-trash-alt remove-file" title="' + localization['remove'] + '" alt="' + localization['remove'] + '" />'));
		if(file.error) {
			node.find('button').first().before($('<span class="message pull-right red-text"/>').text(file.error));
		} else $('.control-group.import_iso .files > .error-msg').remove();
		if(index + 1 === data.files.length) {
			data.context.find('button')
				.text(localization['upload'])
				.prop('disabled', !!data.files.error);
		}
		node.append('<div class="clear"></div>');
	}).on('fileuploadprogressall', function (e, data) {
		var progress = parseInt(data.loaded / data.total * 100, 10);
		$('.' + container + ' .progress .progress-bar').css('width', progress + '%');
	}).on('fileuploaddone', function (e, data) {
		$('.' + container + ' .files > div > p.' + createSlug(data.files[0].name)).find('span.message').remove();
		if(data.result.status.code == 0) {
			$('.' + container + ' .files > div > p.' + createSlug(data.files[0].name) + ' button').first().before($('<span class="message pull-right green-text"/>').text(localization['success-upload']));
			successCallback(data.result);
		} else {
			$('.' + container + ' .files > div > p.' + createSlug(data.files[0].name) + ' .red-text:not(.fa)').remove();
			$('.' + container + ' .files > div > p.' + createSlug(data.files[0].name) + ' button').first().before($('<span class="message pull-right red-text"/>').text(data.result.status.message));
			errorCallback(data.result);
		}
	}).on('fileuploadfail', function (e, data) {
		$.each(data.files, function (index) {
			$(data.context.children()[index]).find('span.message').remove();
			var error = $('<span class="message pull-right red-text"/>').text(localization['failed-upload']);
			$(data.context.children()[index]).find('button').first().before(error);
			$(data.context.children()[index]).find('button').attr('disabled', 'disabled');
		});
		errorCallback(data.result);
	}).prop('disabled', !$.support.fileInput)
		.parent().addClass($.support.fileInput ? undefined : 'disabled');
}
