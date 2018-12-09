/**
 * Very simple way to check if a file exists on this domain.
 * Use with the jQuery library.
 *
 * Important: 	Works only on the same domain. 
 * 		Cross-domain-requests have to be done in another way (see JSONP)!
 *
 * Use: console.log(   "/data/list.json".fileExists()  );
 */
String.prototype.fileExists = function() {
	filename = this.trim();
	
	var response = jQuery.ajax({
		url: filename,
		type: 'HEAD',
		async: false
	}).status;	
	
	return (response != "200") ? false : true;
}
