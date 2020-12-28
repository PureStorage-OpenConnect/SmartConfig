var group, svg, svgLegend, links, markers, nodes;
var svgPaddingX = 20, svgPaddingY = 20;
var xP, yP, imageDistanceX = 750, imageDistanceY = 100, distBetChassis = 20, extraDist = 0, nodeDistanceX = 10, nodeDistanceY = 15;
var nodeRadius = 10, lineWidth = 2, animDuration = 2000;
var groupHPadding = 40, groupVPadding = 30, generalPadding = 20;
var labelColor = '#646464';
var connColors = {'nexus-nexus': '#2196F3', 'ucs-ucs': '#F5CE0E', 'mds-mds': '#F5CE0E', 'chassis-ucs': '#D45AA9', 'nexus-ucs': '#C39787', 'mds-ucs': '#08A208', 'ucsB-mdsA': '#D45AA9', 'flasharray-mds': '#FB5000', 'flasharray-nexus': '#607D8B', 'ucs-rack': '#D45AA9'};	//#F5CE0E
var imageSize = {'nexus': {'width': 300, 'height': 55}, 'ucs': {'width': 300, 'height': 55}, 'chassis': {'width': 300, 'height': 90}, 'mds': {'width': 300, 'height': 55}, 'flasharray': {'width': 300, 'height': 75}, 'rack': {'width': 300, 'height': 30}};
var colorArr = ['#54B36E', '#607D8B', '#B77A64', '#F5CE0E', '#2196F3', '#D45AA9'];

var connectionOffset = {
	'nexus': {'x': 5, 'y': 5, 'nodeDistX': 15, 'nodeDistY': 15, 'posIndex': 0}, 
	'ucs': {'x': 5, 'y': 10, 'nodeDistX': 15, 'nodeDistY': 15, 'posIndex': 1}, 
	'chassis': {'x': 5, 'y': 20, 'nodeDistX': 15, 'nodeDistY': 15, 'posIndex': 2},
	'rack': {'x': 5, 'y': 10, 'nodeDistX': 15, 'nodeDistY': 10, 'posIndex': 3},
	'mds': {'x': 5, 'y': 15, 'nodeDistX': 15, 'nodeDistY': 15, 'posIndex': 4}, 
	'flasharray': {'x': 5, 'y': 20, 'nodeDistX': 15, 'nodeDistY': 45, 'posIndex': 5}
};
var FSDevices = {};

function drawSmartConfigTopology(data) {
	svg = new SVG(document.querySelector(".graph")).size("100%", 100);
	svgLegend = new SVG(document.querySelector(".legend")).size("100%", 100);
	links = svg.group();
	markers = svg.group();
	nodes = svg.group();

	drawHardwares(data);
	drawConnections(data);
	drawPortChannel();
	drawLegend();
	
	setTimeout(function() {
		var el = document.querySelectorAll('.dashed');
		for (var i = 0; i < el.length; i++) {
			el[i].classList.add('active');
			el[i].setAttribute("style", "stroke-dasharray: 8");
		}
		initTooltip('#topology-diagram');
		
		/* setTimeout(function() {
			console.log(svg);
			svg.exportSvg({ whitespace: true });
		}, animDuration*3); */
	}, animDuration);
}

var chassisHeight = 0, rackHeight = 0;
function drawHardwares(data) {
	var helpTxt, nType;
	chassisHeight = 0;
	rackHeight = 0;
	xP = svgPaddingX;
	yP = svgPaddingY;

	// Nexus
	if('Nexus 9k' in data['components'] || 'Nexus 5k' in data['components']) {
		extraDist = 90;
		if('Nexus 9k' in data['components']) nType = 'Nexus 9k';
		else if('Nexus 5k' in data['components']) nType = 'Nexus 5k';
			
		$.each(data['components'][nType], function(i, hardware) {
			FSDevices[hardware['name']] = (i == 0) ? 'nexusA' : 'nexusB';
			helpTxt = '<span><strong>Name:</strong> ' + hardware['name'] + '<br>\
				<strong>IP Address:</strong> ' + hardware['ipaddress'] + '<br>\
				<strong>MAC:</strong> ' + hardware['mac'] + '<br>\
				<strong>Serial No:</strong> ' + hardware['serial_no'] + '<br>\
				<strong>Model:</strong> ' + hardware['model'] + '</span>';
			plotShape('nexus', hardware['name'], hardware['model'], '', helpTxt);
			if(i < (data['components'][nType].length - 1)) xP += imageDistanceX;
		});
		yP += imageDistanceY + extraDist;
	} else {
		adjustHardwarePositionIndex(connectionOffset['nexus']['posIndex']);
	}

	// UCS
	if('UCSM' in data['components']) {
		xP = svgPaddingX;
		$.each(data['components']['UCSM'], function(i, hardware) {
			FSDevices[hardware['name']] = (i == 0) ? 'ucsA' : 'ucsB';
			helpTxt = '<span><strong>Name:</strong> ' + hardware['name'] + '<br>\
				<strong>IP Address:</strong> ' + hardware['ipaddress'] + '<br>\
				<strong>MAC:</strong> ' + hardware['mac'] + '<br>\
				<strong>Serial No:</strong> ' + hardware['serial_no'] + '<br>\
				<strong>Model:</strong> ' + hardware['model'] + '</span>';
			plotShape('ucs', hardware['name'], hardware['model'], '(' + ucfirst(hardware['leadership']) + ')', helpTxt);
			if(i < (data['components']['UCSM'].length - 1)) xP += imageDistanceX;
		});
		yP += imageDistanceY;
	} else {
		adjustHardwarePositionIndex(connectionOffset['ucs']['posIndex']);
	}

	// CHASSIS
	if('CHASSIS' in data['components']) {
		xP = imageDistanceX / 2 + svgPaddingX;
		$.each(data['components']['CHASSIS'], function(i, hardware) {
			FSDevices[hardware['name']] = 'chassis';
			helpTxt = '<span><strong>Name:</strong> ' + hardware['name'] + '<br>\
				<strong>IP Address:</strong> ' + hardware['ipaddress'] + '<br>\
				<strong>MAC:</strong> ' + hardware['mac'] + '<br>\
				<strong>Serial No:</strong> ' + hardware['serial_no'] + '<br>\
				<strong>Model:</strong> ' + hardware['model'] + '</span>';
			plotShape('chassis', hardware['name'], hardware['model'], '', helpTxt);
			if(i < (data['components']['CHASSIS'].length - 1)) {
				yP += imageSize['chassis']['height'] + distBetChassis;
				chassisHeight += imageSize['chassis']['height'] + distBetChassis;
			}
		});
		chassisHeight += 40;
		yP += imageDistanceY + 40;
	} else {
		adjustHardwarePositionIndex(connectionOffset['chassis']['posIndex']);
	}

	// RACK-SERVER
	if('RACK-SERVER' in data['components'] && data['components']['RACK-SERVER'].length > 0) {
		xP = imageDistanceX / 2 + svgPaddingX;
		$.each(data['components']['RACK-SERVER'], function(i, hardware) {
			FSDevices[hardware['name']] = 'rack';
			helpTxt = '<span><strong>Name:</strong> ' + hardware['name'] + '<br>\
				<strong>Serial No:</strong> ' + hardware['serial_no'] + '<br>\
				<strong>Model:</strong> ' + hardware['model'] + '</span>';
			plotShape('rack', hardware['name'], hardware['model'], '', helpTxt);
			if(i < (data['components']['RACK-SERVER'].length - 1)) {
				yP += imageSize['rack']['height'] + 10;
				rackHeight += imageSize['rack']['height'] + 10;
			}
		});
		rackHeight += 50;
		yP += imageDistanceY + 50;
	} else {
		adjustHardwarePositionIndex(connectionOffset['rack']['posIndex']);
	}

	// MDS
	if('MDS' in data['components']) {
		xP = svgPaddingX;
		$.each(data['components']['MDS'], function(i, hardware) {
			FSDevices[hardware['name']] = (i == 0) ? 'mdsA' : 'mdsB';
			helpTxt = '<span><strong>Name:</strong> ' + hardware['name'] + '<br>\
				<strong>IP Address:</strong> ' + hardware['ipaddress'] + '<br>\
				<strong>MAC:</strong> ' + hardware['mac'] + '<br>\
				<strong>Serial No:</strong> ' + hardware['serial_no'] + '<br>\
				<strong>Model:</strong> ' + hardware['model'] + '</span>';
			plotShape('mds', hardware['name'], hardware['model'], '', helpTxt);
			if(i < (data['components']['MDS'].length - 1)) xP += imageDistanceX;
		});
		yP += imageDistanceY;
	} else {
		adjustHardwarePositionIndex(connectionOffset['mds']['posIndex']);
	}

	//Flasharray
	if('PURE' in data['components']) {
		xP = imageDistanceX / 2 + svgPaddingX;
		$.each(data['components']['PURE'], function(i, hardware) {
			FSDevices[hardware['name']] = 'flasharray';
			helpTxt = '<span><strong>Name:</strong> ' + hardware['name'] + '<br>\
				<strong>IP Address:</strong> ' + hardware['ipaddress'] + '<br>\
				<strong>MAC:</strong> ' + hardware['mac'] + '<br>\
				<strong>Serial No:</strong> ' + hardware['serial_no'] + '<br>\
				<strong>Model:</strong> ' + hardware['model'] + '</span>';
			plotShape('flasharray', hardware['name'], hardware['model'], '', helpTxt);
			if(i < (data['components']['PURE'].length - 1)) xP += imageDistanceX;
		});
		yP += imageDistanceY + 80;
	}
	// Set the height of the svg background
	$('.graph > svg').attr('height', (yP - 70) + 'px');
}

function adjustHardwarePositionIndex(index) {
	$.each(connectionOffset, function(i, hardware) {
		if(hardware['posIndex'] > index) {
			connectionOffset[i]['posIndex']--;
		}
	});
}

var legendColorArr = {}, crossConnArray = [];
function drawConnections(data) {
	legendColorArr = {};
	crossConnArray = [];
	portChannels = {};
	var deviceType, tmp, count, color, clrCount = 0, connectionArray = [], obj, cCount = 0;

	$.each(data['components'], function(type, components) {
		deviceType = type.toLowerCase();
		deviceType = deviceType.replace(' 9k', '');
		deviceType = deviceType.replace(' 5k', '');
		if($.inArray(deviceType, ['ucsm', 'mds', 'nexus']) > -1) {
			$.each(components, function(i, component) {
				if(data['connections'][component['name']]) {
					$.each(data['connections'][component['name']], function(k, connections) {
						tmp = FSDevices[component['name']] + '-' + FSDevices[connections['remote_device']];
						if(tmp.indexOf('nexusB-nexusA') > -1)
							return;
						if(tmp.indexOf('nexusA-ucs') > -1 || tmp.indexOf('nexusB-ucs') > -1 || tmp.indexOf('ucsA-mds') > -1 || tmp.indexOf('ucsB-mds') > -1)
							tmp = FSDevices[component['name']].slice(0, -1) + '-' + FSDevices[connections['remote_device']].slice(0, -1);
						
						if(typeof connections['connection'] != 'undefined') {
							if(!(connections['connection'] in legendColorArr)) {
								legendColorArr[connections['connection']] = colorArr[clrCount];
								clrCount++;
							}
						}
						occurrence = 1;
						if(FSDevices[connections['remote_device']] == 'chassis') {
							if($.inArray(connections['remote_device'], chassisArray) < 0)
								chassisArray.push(connections['remote_device']);
							occurrence = chassisArray.indexOf(connections['remote_device']) + 1;
						} else if(FSDevices[connections['remote_device']] == 'rack') {
							if($.inArray(connections['remote_device'], rackArray) < 0)
								rackArray.push(connections['remote_device']);
							occurrence = rackArray.indexOf(connections['remote_device']) + 1;
						}

						color = (typeof legendColorArr[connections['connection']] != 'undefined') ? legendColorArr[connections['connection']] : '#FB5000';
						if((FSDevices[component['name']] == 'nexusA' && FSDevices[connections['remote_device']] == 'ucsB') ||
							(FSDevices[component['name']] == 'nexusB' && FSDevices[connections['remote_device']] == 'ucsA') ||
							(FSDevices[component['name']] == 'ucsA' && FSDevices[connections['remote_device']] == 'mdsB') ||
							(FSDevices[component['name']] == 'ucsB' && FSDevices[connections['remote_device']] == 'mdsA')) {
							obj = {'from': FSDevices[component['name']],
								'to': FSDevices[connections['remote_device']],
								'color': color,
								'info': {"local_device": component['name'], "connection": connections['connection'], "local_interface": connections['local_interface'], "remote_device": connections['remote_device'], "remote_interface": connections['remote_interface'], "speed": connections['speed'], "state": connections['state'], "type": connections['type']}
							};
							crossConnArray.push(obj);
						} else {
							connectionArray.push(FSDevices[component['name']] + '-' + FSDevices[connections['remote_device']]);
							cCount = connectionArray.filter(function(x){ return x === FSDevices[component['name']] + '-' + FSDevices[connections['remote_device']]; }).length;
							drawConnection(FSDevices[component['name']] + '-' + FSDevices[connections['remote_device']], color, cCount, cCount, occurrence, '', {"local_device": component['name'], "connection": connections['connection'], "local_interface": connections['local_interface'], "remote_device": connections['remote_device'], "remote_interface": connections['remote_interface'], "speed": connections['speed'], "state": connections['state'], "type": connections['type']});
						}
						if(tmp.indexOf('mdsA-ucs') > -1 || tmp.indexOf('mdsB-ucs') > -1 || tmp.indexOf('nexusA-ucs') > -1 || tmp.indexOf('nexusB-ucs') > -1 || tmp.indexOf('ucsA-nexus') > -1 || tmp.indexOf('ucsB-nexus') > -1) return;
						if('pc' in connections) {
							if(typeof portChannels[connections['pc']['id']] == 'undefined' || typeof portChannels[connections['pc']['id']]['connection'] == 'undefined')
								portChannels[connections['pc']['id']] = {'name': connections['pc']['type'], 'type': FSDevices[component['name']] + '-' + FSDevices[connections['remote_device']], 'connection': []};
							
							portChannels[connections['pc']['id']]['connection'].push(FSDevices[component['name']] + '-' + FSDevices[connections['remote_device']]);
						}
					});
				}
			});
		}
	});

	$.each(crossConnArray, function(i, conn) {
		var tmp, connArray = [], cCount;
		connectionArray.push(conn['from'] + '-' + conn['to']);
		tmp = conn['from'] + '-' + conn['to'];
		if(tmp.indexOf('nexusA-ucs') > -1 || tmp.indexOf('nexusB-ucs') > -1 || tmp.indexOf('ucsA-mds') > -1 || tmp.indexOf('ucsB-mds') > -1)
			tmp = conn['from'] + '-' + conn['to'].slice(0, -1);
		cCount = connectionArray.filter(function(x){ return x.indexOf(tmp) >= 0; }).length;
		drawConnection(conn['from'] + '-' + conn['to'], conn['color'], cCount, cCount, 1, '', conn['info']);
	});
}

var chassisArray = [], rackArray = [];
function drawConnection(connB, connColor, fromConn, toConn, deviceRow, cls, obj) {
	var helpTxt, helpTxt1, xP = svgPaddingX, yP = svgPaddingY, components;
	var strokeDA = (typeof cls == 'undefined') ? '': '';
	cls = (typeof cls == 'undefined') ? '': cls;
	hardwares = connB.replace(/A/g, "").replace(/B/g, "").split("-");
	components = connB.replace(/A/g, "").replace(/B/g, "").split("-");
	components = components.sort().join("-");
	
	//connColors[connB] = (typeof connColors[components] == 'undefined') ? '#FB5000' : connColors[components];
	if(typeof obj['state'] != 'undefined' && obj['state'].toLowerCase() == 'down') connColor = '#E43E3E';

	helpTxt = '<span><strong>Connected To:</strong> ' + obj['remote_device'] + '<br>\
				<strong>Remote Interface:</strong> ' + obj['remote_interface'] + '<br>\
				<strong>Speed:</strong> ' + obj['connection'] + '<br>\
				<strong>State:</strong> ' + obj['state'].toUpperCase() + '</span>';
	helpTxt1 = '<span><strong>Connected To:</strong> ' + obj['local_device'] + '<br>\
				<strong>Remote Interface:</strong> ' + obj['local_interface'] + '<br>\
				<strong>Speed:</strong> ' + obj['connection'] + '<br>\
				<strong>State:</strong> ' + obj['state'].toUpperCase() + '</span>';
					
	switch(connB) {
		case 'nexusA-nexusB':
		case 'nexusB-nexusA':
			plotNodes('right', connColor, (xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius), (yP + groupVPadding - nodeRadius + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius/2), (yP + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX + groupHPadding + nodeRadius/2), (yP + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + imageDistanceX + groupHPadding), (yP + groupVPadding - nodeRadius + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn), obj['remote_interface'], helpTxt1);
			break;


		case 'ucsA-ucsB':
		case 'ucsB-ucsA':
			plotNodes('right', connColor, (xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist - nodeRadius + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist - nodeRadius/2 + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX + groupHPadding + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist - nodeRadius/2 + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + imageDistanceX + groupHPadding), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist - nodeRadius + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn), obj['remote_interface'], helpTxt1);
			break;


		case 'mdsA-mdsB':
		case 'mdsB-mdsA':
			plotNodes('right', connColor, (xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + chassisHeight + groupVPadding + extraDist - nodeRadius + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + chassisHeight + groupVPadding + extraDist - nodeRadius/2 + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX + groupHPadding + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist - nodeRadius/2 + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + imageDistanceX + groupHPadding), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist - nodeRadius + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn), obj['remote_interface'], helpTxt1);
			break;


		case 'nexusA-ucsA':
			plotNodes('bottom', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y'] - nodeRadius/2), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2 - nodeRadius), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y']))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2 - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius/2))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius), obj['remote_interface'], helpTxt1);
			break;

		case 'nexusB-ucsB':
			plotNodes('bottom', connColor, (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y'] - nodeRadius/2), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius/2))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius), obj['remote_interface'], helpTxt1);
			break;


		case 'nexusA-ucsB':
			plotNodes('bottom', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + groupVPadding))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + (imageDistanceY)/1.25 - 10 * fromConn))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * toConn + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + (imageDistanceY)/1.25 - 10 * fromConn))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * toConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius/2))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * toConn), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius), obj['remote_interface'], helpTxt1);
			break;

		case 'nexusB-ucsA':
			plotNodes('bottom', connColor, (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y'] - nodeRadius/2), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + (imageDistanceY)/0.85 - 10 * fromConn))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * toConn - nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + (imageDistanceY)/0.85 - 10 * toConn))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * toConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y']))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * toConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + connectionOffset[hardwares[1]]['y'] - nodeRadius), obj['remote_interface'], helpTxt1);
			break;


		case 'ucsA-chassis':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius))
				.L((xP + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + ((deviceRow - 1) * distBetChassis) + connectionOffset[hardwares[1]]['nodeDistY'] * toConn))
				.L((xP + imageDistanceX/2 + groupHPadding + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + ((deviceRow - 1) * distBetChassis) + connectionOffset[hardwares[1]]['nodeDistY'] * toConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + imageDistanceX/2 + groupHPadding), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + ((deviceRow - 1) * distBetChassis) + connectionOffset[hardwares[1]]['nodeDistY'] * toConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;

		case 'ucsB-chassis':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageDistanceX + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageDistanceX + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageDistanceX + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + ((deviceRow - 1) * distBetChassis) + connectionOffset[hardwares[1]]['nodeDistY'] * toConn))
				.L((xP + imageDistanceX/2 + imageSize[hardwares[1]]['width'] + groupHPadding - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + ((deviceRow - 1) * distBetChassis) + connectionOffset[hardwares[1]]['nodeDistY'] * toConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('right', connColor, (xP + imageDistanceX/2 + imageSize[hardwares[1]]['width'] + groupHPadding - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + ((deviceRow - 1) * distBetChassis) + connectionOffset[hardwares[1]]['nodeDistY'] * toConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;
			

		case 'ucsA-rack':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius))
				.L((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX/2 + groupHPadding + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + imageDistanceX/2 + groupHPadding), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;
			
		case 'ucsB-rack':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX/2 + imageSize[hardwares[1]]['width'] + groupHPadding - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('right', connColor, (xP + imageDistanceX/2 + imageSize[hardwares[1]]['width'] + groupHPadding - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + groupVPadding + extraDist + (imageSize[hardwares[1]]['height'] * (deviceRow - 1)) + connectionOffset[hardwares[1]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;


		case 'ucsA-mdsA':
			plotNodes('bottom', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist), obj['remote_interface'], helpTxt1);
			break;

		case 'ucsB-mdsB':
			plotNodes('bottom', connColor, (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist), obj['remote_interface'], helpTxt1);
			break;


		case 'ucsA-mdsB':
			plotNodes('bottom', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - 110 - 10 * fromConn))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - 110 - 10 * fromConn))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist), obj['remote_interface'], helpTxt1);
			break;

		case 'ucsB-mdsA':
			plotNodes('bottom', connColor, (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - 60 - 10 * fromConn))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - 60 - 10 * fromConn))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('top', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist), obj['remote_interface'], helpTxt1);
			break;


		case 'mdsA-flasharray':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + groupHPadding + imageDistanceX/2 + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + groupHPadding + imageDistanceX/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;

		case 'mdsB-flasharray':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + groupHPadding + imageDistanceX/2 + imageSize[hardwares[0]]['width']), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('right', connColor, (xP + groupHPadding + imageDistanceX/2 + imageSize[hardwares[0]]['width'] - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;


		case 'nexusA-flasharray':
			plotNodes('top', connColor, (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius), (yP + groupVPadding), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + groupVPadding))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn - nodeRadius/2), (yP + groupVPadding - 10 * fromConn))
				.L((xP + groupHPadding - nodeRadius/2 - 10 * fromConn), (yP + groupVPadding - 10 * fromConn))
				.L((xP + groupHPadding - nodeRadius/2 - 10 * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX/2 + groupHPadding + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + imageDistanceX/2 + groupHPadding), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;

		case 'nexusB-flasharray':
			plotNodes('top', connColor, (xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + groupVPadding), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + groupVPadding))
				.L((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + groupVPadding - 10 * fromConn))
				.L((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] + nodeRadius/2 + 10 * fromConn), (yP + groupVPadding - 10 * fromConn))
				.L((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] + nodeRadius/2 + 10 * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + imageDistanceX/2 + groupHPadding + imageSize[hardwares[0]]['width'] - nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('right', connColor, (xP + imageDistanceX/2 + groupHPadding + imageSize[hardwares[0]]['width'] - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;


		case 'ucsA-flasharray':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius))
				.L((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + groupHPadding + imageDistanceX/2 + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('left', connColor, (xP + groupHPadding + imageDistanceX/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;

		case 'ucsB-flasharray':
			plotNodes('bottom', connColor, (xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height'] - nodeRadius), obj['local_interface'], helpTxt);
			svg.path().attr({fill: 'none', stroke: connColor, 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[0]]['posIndex']) + groupVPadding + extraDist + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * fromConn + nodeRadius/2), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.L((xP + groupHPadding + imageDistanceX/2 + imageSize[hardwares[0]]['width']), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes('right', connColor, (xP + groupHPadding + imageDistanceX/2 + imageSize[hardwares[0]]['width'] - nodeRadius), (yP + (imageDistanceY*connectionOffset[hardwares[1]]['posIndex']) + chassisHeight + rackHeight + groupVPadding + extraDist + connectionOffset[hardwares[0]]['nodeDistY'] * fromConn - nodeRadius/2), obj['remote_interface'], helpTxt1);
			break;
	}
}

var portChannels = {};
function drawPortChannel() {
	var g = nodes.group(), nested, width, height, x, y, tmp, labelDistanceX = 15, labelDistanceY = 15;

	$.each(portChannels, function(key, pc) {
		width = 15; height = 8;
		
		group = nodes.group();
		nested = group.nested();
		
		switch(pc['type']) {
			case 'nexusA-nexusB':
			case 'nexusB-nexusA':
				tmp = width;
				width = height;
				height = tmp;
				x = ((svgPaddingX*2 + groupHPadding*2 + imageSize['nexus']['width'] + imageDistanceX)/2);
				y = (svgPaddingY + groupVPadding + 2);
				break;
			case 'nexusA-ucsA':
			case 'nexusB-ucsA':
				x = (svgPaddingX + groupHPadding + 2);
				y = (svgPaddingY + imageDistanceY + extraDist - 25);
				break;
			case 'nexusA-ucsB':
			case 'nexusB-ucsB':
				x = (svgPaddingX + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - 2 - width * pc['connection'].length);
				y = (svgPaddingY + imageDistanceY + extraDist - 25);
				labelDistanceX = -(width * pc['connection'].length);
				break;
			case 'ucsA-mdsA':
			case 'ucsA-mdsB':
				x = (svgPaddingX + groupHPadding + 2);
				y = ((svgPaddingY*2 + imageDistanceY*5 + groupVPadding*2 + imageSize['ucs']['height'] + chassisHeight + rackHeight)/2);
				break;
			case 'ucsB-mdsB':
			case 'ucsB-mdsA':
				x = (svgPaddingX + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - 2 - width * pc['connection'].length);
				y = ((svgPaddingY*2 + imageDistanceY*5 + groupVPadding*2 + imageSize['ucs']['height'] + chassisHeight + rackHeight)/2);
				labelDistanceX = -(width * pc['connection'].length);
				break;
		}
		nested.ellipse((width * pc['connection'].length), (height * pc['connection'].length))
			.move(x, y)
			.attr({'fill': 'transparent', 'stroke': '#FF0000', 'stroke-width': 2, 'stroke-dasharray': '3 3 1 3'});
		nested.text(pc['name']).move((x - labelDistanceX), (y - labelDistanceY))
			.fill('#FB5000').font({ size: 10, family: 'Verdana' });
	});
}