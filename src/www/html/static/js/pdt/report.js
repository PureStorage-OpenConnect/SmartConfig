(function(API) {
    API.myText = function(txt, options, x, y) {
        options = options ||{};
        /* Use the options align property to specify desired text alignment
         * Param x will be ignored if desired text alignment is 'center'.
         * Usage of options can easily extend the function to apply different text 
         * styles and sizes 
        */
        if( options.align == "center" ){
            // Get current font size
            var fontSize = this.internal.getFontSize();

            // Get page width
            var pageWidth = this.internal.pageSize.width;

            // Get the actual text's width
            /* You multiply the unit width of your string by your font size and divide
             * by the internal scale factor. The division is necessary
             * for the case where you use units other than 'pt' in the constructor
             * of jsPDF.
            */
            txtWidth = this.getStringUnitWidth(txt)*fontSize/this.internal.scaleFactor;

            // Calculate text's x coordinate
            x = ( pageWidth - txtWidth ) / 2;
        }

        // Draw text at x,y
        this.text(txt,x,y);
    }
})(jsPDF.API);

var logoImg = null, logoWhiteImg = null, topologyImg = null, reportImg = null, margins = {
	top: 40,
	bottom: 10,
	left: 10,
	right: 10,
	a4_width: 297,
	a0_width: 841,
	a1_width: 594
},
pdfImageSize = {'a4': {'width': 185, 'height': 140}, 'a0': {'width': 185, 'height': 130}, 'a1': {'width': 500, 'height': 600}, 'a01': {'width': 500, 'height': 600}},
specialElementHandlers = {
	// element with id of "bypass" - jQuery style selector
	'#bypassme': function (element, renderer) {
		// true = "handled elsewhere, bypass text extraction"
		return true
	}
};

function exportAsPDF(PDFSize) {
	var pageType = 'l';
	if(PDFSize.toLowerCase() != 'a4') pageType = 'p';

	var Y = 62, count = 1, totalPages = 0, maxCellWidth, doc = new jsPDF(pageType, 'mm', PDFSize);
	doc.autoTable.previous.finalY = 0;
	var totalPagesExp = "{total_pages_count_string}";

	var startY = 80;
	let styles = {cellPadding: 3, fontSize: 12, minCellWidth: 25}, columnStyles;
	let topPadding = 30;
	let logoSize = {'left': 10, 'right': 240, 'top': 10, 'width': 52, 'height': 14};
	let titleConf = {'fontSize': 34, 'left': 65, 'top': 60};
	let subTitleConf = {'fontSize': 16, 'left': 157, 'top': 75};
	let versionTxtConf = {'fontSize': 10, 'left': 212, 'top': 66};
	var contentPage = [], tmp = '', additionalPages = 1;

	$('.report-container .report-section').each(function(index) {
		if(Y >= 175) { additionalPages++; Y = 62; }
		if(tmp != $(this).closest('.tab-pane').data('menu-name')) {
			tmp = $(this).closest('.tab-pane').data('menu-name');
			Y += 15;
		}
		if($(this).find('h3.title').length || $(this).find('h4.title').length)
			Y += 8;
	});

	$('.report-container .report-section').each(function(index) {
		var $self = $(this);
		Y = doc.autoTable.previous.finalY || 0;
		Y += topPadding;
		if(PDFSize == 'a4' && Y > 150) { doc.addPage(); Y = topPadding; }
		else if(PDFSize == 'a0' && Y > 1000) { doc.addPage(); Y = topPadding; }
		doc.setTextColor(100);

		columnStyles = {text: {cellWidth: 'wrap'}};
		if($('#' + $(this).attr('id') + ' table.report-table > thead > tr > td').length > 0)
			maxCellWidth = 274 / $('#' + $(this).attr('id') + ' table.report-table > thead > tr > td').length;
		if(maxCellWidth < 45) maxCellWidth = 45;

		if($('#' + $(this).attr('id') + ' table.report-table > thead > tr > td[cellwidth]').length > 0) {
			maxCellWidth = 0;
			columnStyles = [];
			$('#' + $(this).attr('id') + ' table.report-table > thead > tr > td[cellwidth]').each(function(td) {
				columnStyles.push({cellWidth: (parseInt($(this).attr('cellWidth')) * 3)});
			});
		}

		if($(this).find('h3.title').length) {
			doc.setFontSize(18);
			doc.text(count + '. ' + $(this).find('h3.title').text(), 10, Y);

			contentPage.push({txt: count + '. ' + $(this).find('h3.title').text(), 
							category: $(this).closest('.tab-pane').data('menu-name'), 
							page: (doc.internal.getNumberOfPages() + additionalPages)});
		}
		if($(this).find('h4.title').length) {
			doc.setFontSize(15);
			doc.text(count + '. ' + $(this).find('h4.title').text(), 10, Y);

			contentPage.push({txt: count + '. ' + $(this).find('h4.title').text(), 
							category: $(this).closest('.tab-pane').data('menu-name'), 
							page: (doc.internal.getNumberOfPages() + additionalPages)});
		}
		if($(this).find('h3.title').length || $(this).find('h4.title').length) {
			Y += 7;
			count++;
		}
		if($(this).find('p').length) {
			doc.setFontSize(10);
			doc.setTextColor(100);
			var splitTitle = doc.splitTextToSize($(this).find('p').text(), (margins[PDFSize + '_width'] - 40));
			$.each(splitTitle, function(i, text) {
				doc.text(10, Y, text);
				Y += 7;
			});
		}

		doc.autoTable({
			didDrawCell: function (data) {
				if($self.find('table.report-table').hasClass('connection-table') && data.cell.section == 'body' && data.column.index === 5) {
					var td = data.cell.raw;
					var textPos = data.cell.textPos;
					/* var img = td.getElementsByTagName('img')[0];
					//var dim = data.cell.height - data.cell.padding('vertical');
					var stateImg = new Image();
					stateImg.src = img.src;
					doc.addImage(stateImg, textPos.x, textPos.y, 4, 4); */
					switch(td.innerHTML) {
						case 'Up':
							doc.setTextColor('#16961C');
							break;
						case 'Down':
							doc.setTextColor('#454545');
							break;
						default:
							doc.setTextColor('#FF0000');
							break;
					}
					doc.text(td.innerHTML, textPos.x, (textPos.y + 3.2));
				}
			},
			didDrawPage: function (data) {
				// Header
				doc.printingHeaderRow = true;
				doc.setFillColor(250, 80, 0);
				doc.rect(0, 0, margins[PDFSize + '_width'], 20, "F");
				if(logoWhiteImg != null)
					doc.addImage(logoWhiteImg, 'PNG', 5, 5, 0, 13);

				if(reportImg != null)
					doc.addImage(reportImg, 'PNG', (logoSize['right']), (logoSize['top'] - 6), 0, 13);
				else {
					doc.setFontSize(18);
					doc.setTextColor(255);
					doc.setFontStyle('normal');
					doc.text("SmartConfig - Report", margins[PDFSize + '_width'] - 65, 13);
				}

				// Footer
				totalPages = (doc.internal.getNumberOfPages() + additionalPages);
				var str = "Page " + (doc.internal.getNumberOfPages() + additionalPages);
				// Total page number plugin only available in jspdf v1.0+
				if (typeof doc.putTotalPages === 'function') {
					str = str + " of " + totalPagesExp;
				}
				doc.setFontSize(10);
				doc.setTextColor('#000');
				// jsPDF 1.4+ uses getWidth, <1.4 uses .width
				var pageSize = doc.internal.pageSize;
				var pageHeight = pageSize.height ? pageSize.height : pageSize.getHeight();
				doc.text(str, 10, pageHeight - 5);
			},
			startY: Y, 
			margin: margins,
			pageBreak: "auto", 
			rowPageBreak: 'auto',
			bodyStyles: {valign: 'top'},
			headStyles: {halign: 'center', fillColor: [241, 196, 15], fontSize: 15},
			styles: {fontSize: 9, overflow: 'linebreak', cellWidth: 'wrap', minCellWidth: 25, maxCellWidth: maxCellWidth},	//, cellWidth: 'wrap'
			columnStyles: columnStyles,
			html: '#' + $(this).attr('id') + ' table.report-table',
			tableWidth: "wrap",	//auto, wrap
			showHead: 'everyPage',	//everyPage, firstPage, never
			useCss: true
		});
		if($(this).find('div#topology-diagram').length && topologyImg != null) {
			doc.addImage(topologyImg, 'PNG', 10, (Y), 0, pdfImageSize[PDFSize]['height']);
			doc.autoTable.previous.finalY = 200;
		}
	});

	// Total page number plugin only available in jspdf v1.0+
	if (typeof doc.putTotalPages === 'function') {
		doc.putTotalPages(totalPagesExp, additionalPages);
	}

	var p = 1;
	doc.insertPage(p);
	// Footer
	pageSize = doc.internal.pageSize;
	pageHeight = pageSize.height ? pageSize.height : pageSize.getHeight();
	str = "Page " + p + " of " + totalPages;
	doc.setFontSize(10);	
	doc.setTextColor('#000');
	doc.text(str, 10, pageHeight - 5);

	if(logoImg != null)
		doc.addImage(logoImg, 'PNG', (reportImg != null)?logoSize['left']:124, (reportImg != null)?logoSize['top']:25, logoSize['width'], logoSize['height']);
	if(reportImg != null)
		doc.addImage(reportImg, 'PNG', logoSize['right'], logoSize['top'], logoSize['width'], logoSize['height']);
	var stack = systemInfo.stacktype.split("-");
	stack = (stack[stack.length-1].toLowerCase() == 'fc') ? 'FC' : 'iSCSI';

	doc.setFontSize(titleConf['fontSize']);
	doc.setTextColor('#FB5000');
	doc.myText('FlashStack SmartConfig Report', {align: "center"}, titleConf['left'], titleConf['top']);
	doc.setFontSize(versionTxtConf['fontSize']);
	doc.setTextColor('#8D8D8D');
	doc.myText('Tool Version: ' + systemInfo.version, {align: "center"}, versionTxtConf['left'], versionTxtConf['top']);
	doc.setFontSize(subTitleConf['fontSize']);
	doc.setTextColor('#8D8D8D');
	doc.myText(hardwareStacks[systemInfo.stacktype] + " [" + stack + "]", {align: "center"}, subTitleConf['left'], subTitleConf['top']);

	doc.autoTable({
		startY: startY,
		html: '#report-landing-info',
		columnStyles: {
			0: {cellWidth: 38},
			1: {cellWidth: 48},
			2: {cellWidth: 39},
			3: {cellWidth: 26},
			4: {cellWidth: 40},
			5: {cellWidth: 50},
			6: {cellWidth: 32}
		},
		styles: {fontSize: 9, overflow: 'linebreak', maxCellWidth: 55, cellPadding: 3},
		tableWidth: "wrap",
		useCss: true
	});
	p++;

	tmp = '', Y = 200;
	$.each(contentPage, function(i, content) {
		if(Y >= 175) {
			doc.insertPage(p);
			doc.printingHeaderRow = true;
			doc.setFillColor(250, 80, 0);
			doc.rect(0, 0, margins[PDFSize + '_width'], 20, "F");
			if(logoWhiteImg != null)
				doc.addImage(logoWhiteImg, 'PNG', 5, 5, 0, 13);

			if(reportImg != null)
				doc.addImage(reportImg, 'PNG', (logoSize['right']), (logoSize['top'] - 6), 0, 13);
			else {
				doc.setFontSize(18);
				doc.setTextColor(255);
				doc.setFontStyle('normal');
				doc.text("SmartConfig - Report", margins[PDFSize + '_width'] - 65, 13);
			}

			Y = 39;
			doc.setFontSize(24);
			doc.setTextColor('#FB5000');
			doc.myText('Contents', {align: "center"}, 0, Y);
			
			// Footer
			str = "Page " + p + " of " + totalPages;
			doc.setFontSize(10);
			doc.setTextColor('#000');
			doc.text(str, 10, pageHeight - 5);
			p++;
		}
		Y += 8;
		if(tmp != content.category) {
			tmp = content.category;
			doc.setFontSize(15);
			doc.setTextColor('#105EAB');
			Y += 5;
			doc.text(content.category, 25, Y);
			Y += 10;
		}
		doc.setFontSize(10);
		doc.setTextColor('#0360BC');
		doc.textWithLink(content.txt, 25, Y, {pageNumber: content.page});
		doc.text(' ' + content.page, 275, Y, {align: 'right'});
	});
	
	doc.setProperties({
		title: 'SmartConfig - Report',
		subject: 'SmartConfig - Report'
	});
	doc.save('SmartConfig-Report.pdf');
	return;
}

function getComponentInfoByName(components, name) {
	var comp;
	$.each(components, function(i, v) {
		comp = $.grep(components[i], function(obj){return obj.name === name})[0];
		if(typeof comp != 'undefined') return false;
	});
	return comp;
}

function loadReportTemplate(downloadFlag, size) {
	var n = 0;
	$('.hidden-content').html('<div id="html-2-pdfwrapper" class="report-container">' +
		'<ul class="nav nav-tabs">' +
			'<li class="active"><a data-toggle="tab" href="#cabling-info">Cabling Information</a></li>' +
		'</ul>' +
		'<div class="tab-content">' +
			'<div id="cabling-info" data-menu-name="Cabling Information" class="tab-pane fade in active">' +
				'<div class="report-section cabling" id="report-cabling-section-' + n + '">' +
					'<h3 class="title">FlashStack Cabling Information</h3>' +
					'<p>This section details a cabling example for a FlashStack environment. To make connectivity clear in this example, the tables include both the local and remote port locations.</p>' +
					'<table class="report-table"></table>' +
					'<div id="topology-diagram">' + 
						'<div class="graph"></div>' +
						'<div class="legend"></div>' +
						'<div class="description"></div>' +
					'</div>' +
				'</div>' +
			'</div>' +
		'</div>' +
	'</div>');
	if(!downloadFlag) initScroller($('.hidden-content'));

	doAjaxRequest({url: 'System', base_path: settings.base_path}, function(response) {
		updateDeploymentSettings(response.data.deployment_settings);
		systemInfo.report_logo = response.data.report_logo;
		systemInfo.version = response.data.version;

		logoImg = new Image();
		logoImg.src = 'static/images/logo.png';

		logoWhiteImg = new Image();
		logoWhiteImg.src = 'static/images/fslogo.png';

		var filename = 'static/images/topologies/' + systemInfo.subtype.replace('-rack', '') + '.png';
		if(filename.fileExists()) {
			topologyImg = new Image();
			topologyImg.src = filename;
		}
		if(typeof systemInfo.report_logo != 'undefined') {
			filename = 'static/images/' + systemInfo.report_logo;
			if(filename.fileExists()) {
				reportImg = new Image();
				reportImg.src = filename;
			}
		}
	}, doNothing);
	
	doAjaxRequest({url: 'FlashStackTypes', base_path: settings.base_path}, function(response) {
		$.each(response.data, function(key, value) {
			hardwareStacks[value.value] = value.label;
		});
	}, doNothing);

	var comp, tmp, str;
	doAjaxRequest({url: 'FSConnectivity', base_path: settings.base_path, container: '.content-container'}, function(response) {
		try {
			str = '<table id="report-landing-info" class="hide1">' +
				'<thead>' +
					'<tr style="background: #D85214; color: #FFF;">\
						<td colspan="7" style="text-align: center;">GENERIC INFORMATION</td>\
					</tr>' +
					'<tr style="background: #FB5000; color: #FFF;">' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">Name</td>' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">Serial Number</td>' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">MAC Address</td>' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">Leadership</td>' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">Virtual IP Address</td>' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">Model</td>' +
						'<td style="padding: 12px; text-align: center; vertical-align: middle;">IP address</td>' +
					'</tr>' +
				'</thead>' +
				'<tbody>';
					$.each(response.data.components, function(dType, components) {
						$.each(components, function(i, info) {
							if($.inArray(dType, ['MDS', 'PURE', 'UCSM', 'Nexus 5k', 'Nexus 9k']) !== -1) {
								info['vipaddress'] = (typeof info['vipaddress'] != 'undefined') ? info['vipaddress'] : '-';
								info['leadership'] = (typeof info['leadership'] != 'undefined') ? info['leadership'] : '-';
								str += '<tr>' +
									'<td style="padding: 12px;">' + info['name'] + '</td>' +
									'<td style="padding: 12px;">' + info['serial_no'] + '</td>' +
									'<td style="padding: 12px;">' + info['mac'] + '</td>' +
									'<td style="padding: 12px;">' + info['leadership'] + '</td>' +
									'<td style="padding: 12px;">' + info['vipaddress'] + '</td>' +
									'<td style="padding: 12px;">' + info['model'] + '</td>' +
									'<td style="padding: 12px;">' + info['ipaddress'] + '</td>' +
								'</tr>';
							}
						});
					});
				str += '</tbody>' +
			'</table>';
			$('#cabling-info').append(str);

			n++;
			$.each(response.data.connections, function(index, value) {
				comp = getComponentInfoByName(response.data.components, index);
				str = '<div class="report-section cabling" id="report-cabling-section-' + n + '">' +
					'<h4 class="title">' + comp['model'] + ' ' + index + ' Cabling Information</h4>' +
					'<div class="report-table-container">' +
						'<table class="report-table connection-table">' +
							'<thead>' +
								'<tr style="background: #FB5000; color: #FFF;">' +
									'<td style="text-align: center; vertical-align: middle;">Local Device</td>' +
									'<td style="text-align: center; vertical-align: middle;">Local Port</td>' +
									'<td style="text-align: center; vertical-align: middle;">Connection</td>' +
									'<td style="text-align: center; vertical-align: middle;">Remote Device</td>' +
									'<td style="text-align: center; vertical-align: middle;">Remote Port</td>' +
									'<td style="text-align: center; vertical-align: middle;">Port State</td>' +
								'</tr>' +
							'</thead>' +
							'<tbody>';
								$.each(value, function(i, info) {
									tmp = getComponentInfoByName(response.data.components, info['remote_device']);
									state = (info['state'].toLowerCase() == 'up') ? 'success' : 'm_xicon-1';
									var string = '';
									if(typeof info['local_ports'] != 'undefined') {
										console.log(info['local_ports']);
										$.each(info['local_ports'], function(p, port) {
											if(port['state'] == 'up') {
												string += port['name'] + ',';
											}
										});
										string = trimChar(string, ',');
										string = ' (' + string.replace(/,/g, ', ') + ')';
									}
									str += '<tr>';
										if(i == 0)
											str += '<td>' + comp['model'] + ' ' + index + '</td>';
										else str += '<td></td>';
										str += '<td>' + info['local_interface'].replace("|", ", ") + string + '</td>' +
										'<td>' + info['connection'] + '</td>' +
										'<td>' + tmp['model'] + ' ' + info['remote_device'] + '</td>' +
										'<td>' + info['remote_interface'].replace("|", ", ") + '</td>' +
										'<td>' +
											//'<img src="static/images/' + state + '.png" height="24px" width="24px"></img>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' +
											ucfirst(info['state']) + 
										'</td>' +
									'</tr>';
								});
							str += '</tbody>' +
						'</table>' +
					'</div>' +
				'</div>';
				$('#cabling-info').append(str);
				n++;
			});
			//drawSmartConfigTopology(response.data);
			reportAPIs(downloadFlag, size);
		} catch(err) {
			reportAPIs(downloadFlag, size);
		}
	}, function(response) {
		reportAPIs(downloadFlag, size);
	});
}

function reportAPIs(downloadFlag, size) {
	var n = 0, cellWidth, rowMerge;
	doAjaxRequest({url: 'Report', base_path: settings.base_path, query: {"stacktype": systemInfo.subtype}, container: '.content-container'}, function(response) {
		requestCount = 0;
		$.each(response['data'], function(index, value) {
			if(value.api.length > 0) requestCount++;
		});
		requestCallback = new MyRequestsCompleted({
			numRequest: requestCount,
			singleCallback: function() {
				if(downloadFlag) {
					exportAsPDF(size);
					doAjaxRequest({url: 'ReleaseHandle', base_path: settings.base_path, query: {"stacktype": systemInfo.stacktype}}, doNothing, doNothing);
					$('.export-report').closest('.buttonCustom').find('.dropdown-toggle').html('Export Report');
					$('.export-report').closest('.buttonCustom').removeClass('buttonDisabled');
				}
			}
		});
		n++;
		var data, str, $row, tmp_index, tmp = '', tmpArray = [], differenceArray = [], container = '';
		$.each(response['data'], function(index, value) {
			tmp_index = createSlug(value.belongsTo);
			data = {'keys': {}};
			$.each(value['args'], function(i, arg) {
				data['keys'][arg['name']] = arg['value'];
			});
			str = '<div class="report-section" id="report-section-' + index + '">' +
				'<h3 class="title">' + value['header']['title'] + '</h3>';
				if(typeof value['header']['desc'] != 'undefined' && value['header']['desc'] != '')
					str += '<p>' + value['header']['desc'] + '</p>';
			str += '</div>';
		
			if(!$('#html-2-pdfwrapper > .tab-content > #menu-' + tmp_index).length) {
				$('#html-2-pdfwrapper > ul.nav-tabs').append('<li><a data-toggle="tab" href="#menu-' + tmp_index + '">' + value.belongsTo + '</a></li>');
				$('#html-2-pdfwrapper > div.tab-content').append('<div id="menu-' + tmp_index + '" data-menu-name="' + value.belongsTo + '" class="tab-pane fade">' + str + '</div>');
			} else {
				$('#html-2-pdfwrapper > div.tab-content > #menu-' + tmp_index).append(str);
			}
		
			if(value.api.length > 0) {
				container = (container.length > 0) ? ' ': '#report-section-' + index;
				container = '#report-section-' + index;
				doAjaxRequest({url: 'ReportInfo', base_path: settings.base_path, method: 'POST', data: data, query: {'method': value.api}, container: container}, function(reportInfo) {
					try {
						tmpArray = [], differenceArray = [];
						str = '<div class="report-table-container">' +
							'<table class="report-table">' +
								'<thead><tr>';
									$.each(reportInfo['data']['labels'], function(i, info) {
										cellWidth = '', rowMerge = '';
										if(typeof info['cellWidth'] != 'undefined') cellWidth = ' cellWidth="' + info['cellWidth'] + '"';
										if(typeof info['rowMerge'] != 'undefined') rowMerge = ' rowMerge';
										tmpArray.push(info['key']);
										str += '<td ' + cellWidth + ' key="' + info['key'] + '" ' + rowMerge + '>' + info['label'] + '</td>';
									});
								str += '</tr></thead>' +
								'<tbody></tbody>' +
							'</table>' +
						'</div>';
						$('#report-section-' + index).append(str);
						if(!downloadFlag) $('#report-section-' + index + ' .report-table-container').mCustomScrollbar({axis: 'x', theme: "minimal-dark"});

						$.each(reportInfo['data']['list'], function(i, list) {
							if(i == 0) {
								jQuery.grep(tmpArray, function(el) {
									if (jQuery.inArray(el, Object.keys(list)) == -1) differenceArray.push(el);
								});
								$.each(differenceArray, function(i, diff) {
									$('#report-section-' + index + ' table.report-table > thead td[key="' + diff + '"]').remove();
								});
							}

							$row = $('#report-section-' + index + ' table.report-table > thead > tr').clone();
							if($row.find('td[rowmerge]').length) {
								$row.find('td[rowmerge]').each(function() {
									if(i == 0) {
										//$(this).attr('rowspan', reportInfo['data']['list'].length);
									} else {
										//$(this).remove();
										$(this).html('').removeAttr('key');
									}
								});
							}
							$.each(reportInfo['data']['labels'], function(i, label) {
								$('td[key="' + label['key'] + '"]', $row).html(translateJsonToHtml(list[label['key']]));
							});
							$row.appendTo('#report-section-' + index + ' table.report-table > tbody');
						});
						$('#report-section-' + index + ' table.report-table > thead > tr').css({'background': '#FB5000', 'color': '#FFF'});
						$('#report-section-' + index + ' table.report-table > thead > tr > td').css({'text-align': 'center', 'vertical-align': 'middle'});
						requestCallback.requestComplete(true);
					} catch(err) {
						requestCallback.requestComplete(true);
					}
				}, function(response) {
					requestCallback.requestComplete(true);
				});
			}
			if(!downloadFlag) initScroller($('.report-section:not(#report-section-cabling)'));
		});
	}, doNothing);
}

function translateJsonToHtml(data) {
	var str;
	if(data == null) return '';
	switch (typeof data) {
		case 'object':
			if($.isPlainObject(data)) {
				str = '';
				if(typeof data.label != 'undefined') {
					str += '<span style="font-weight: 700;">' + data.label + ': </span><span>' + data.value + '</span>';
				} else {
					$.each(data, function(i, info) {
						str += '<span style="font-weight: 700;">' + translateJsonToHtml(info) + '</span><br>';
					});
				}
			} else if(Array.isArray(data)) {
				str = '';
				$.each(data, function(i, info) {
					str += translateJsonToHtml(info) + '<br>';
				});
			} else {
				str = '';
				$.each(data, function(i, info) {
					str += '<span style="font-weight: 700;">' + info['label'] + ':</span>\t' + translateJsonToHtml(info['value']) + '<br>';
				});
			}
			break;
		default:
			str = data;
			break;

	}
	return (typeof str != 'undefined') ? str : '-';
}