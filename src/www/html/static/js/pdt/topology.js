var group, svg, svgLegend, links, markers, nodes;
var svgPaddingX = 20, svgPaddingY = 20;
var xP = svgPaddingX, yP = svgPaddingY, imageDistanceX = 750, imageDistanceY = 150, chassisHeight = 60, nodeDistanceX = 10, nodeDistanceY = 15;
var nodeRadius = 10, lineWidth = 2, animDuration = 2000;
var groupHPadding = 40, groupVPadding = 30, generalPadding = 20;
var labelColor = '#ABABAB';
var connColors = {'nexus-nexus': '#2196F3', 'ucs-ucs': '#F5CE0E', 'mds-mds': '#F5CE0E', 'chassis-ucs': '#D45AA9', 'nexus-ucs': '#C39787', 'mds-ucs': '#08A208', 'ucsB-mdsA': '#D45AA9', 'flasharray-mds': '#FB5000', 'flasharray-nexus': '#607D8B'};	//#F5CE0E
var imageSize = {'nexus': {'width': 300, 'height': 35}, 'ucs': {'width': 300, 'height': 35}, 'chassis': {'width': 300, 'height': 90}, 'mds': {'width': 300, 'height': 35}, 'flasharray': {'width': 300, 'height': 75}};
var connectionOffset = {
	'nexus': {'x': 5, 'y': 5, 'nodeDistX': 15, 'nodeDistY': 15}, 
	'ucs': {'x': 5, 'y': 10, 'nodeDistX': 15, 'nodeDistY': 15}, 
	'mds': {'x': 5, 'y': 15, 'nodeDistX': 15, 'nodeDistY': 15}, 
	'flasharray': {'x': 5, 'y': 20, 'nodeDistX': 15, 'nodeDistY': 45}, 
	'chassis': {'x': 5, 'y': 20, 'nodeDistX': 15, 'nodeDistY': 15}
};

function drawSmartConfigTopology(data) {
	svg = new SVG(document.querySelector(".graph")).size("100%", 100);
	svgLegend = new SVG(document.querySelector(".legend")).size("100%", 100);
	links = svg.group();
	markers = svg.group();
	nodes = svg.group();

	drawHardwares(data);
	drawConnections(data);
	drawLegend();
	
	setTimeout(function() {
		var el = document.querySelectorAll('.dashed');
		for (var i = 0; i < el.length; i++) {
			el[i].classList.add('active');
			el[i].setAttribute("style", "stroke-dasharray: 8");
		}
	}, animDuration);
}

function drawHardwares(data) {
	//console.log(data['components']);

	// Nexus
	if('nexus' in data['components']) {
		$.each(data['components']['nexus'], function(i, hardware) {
			plotShape('nexus', hardware['name'], hardware['vendor_model'], '(' + hardware['type'] + ')');
			if(i < (data['components']['nexus'].length - 1)) xP += imageDistanceX;
			else yP += imageDistanceY;
		});
	}

	// CHASSIS
	if('chassis' in data['components']) {
		xP = imageDistanceX / 2 + svgPaddingX;
		$.each(data['components']['chassis'], function(i, hardware) {
			plotShape('chassis', hardware['name'], hardware['vendor_model']);
			if(i < (data['components']['chassis'].length - 1)) xP += imageDistanceX;
			else yP += imageDistanceY + chassisHeight;
		});
	}

	// UCS
	if('ucs' in data['components']) {
		xP = svgPaddingX;
		$.each(data['components']['ucs'], function(i, hardware) {
			plotShape('ucs', hardware['name'], hardware['vendor_model'], '(' + hardware['type'] + ')');
			if(i < (data['components']['ucs'].length - 1)) xP += imageDistanceX;
			else yP += imageDistanceY;
		});
	}

	// MDS
	if('mds' in data['components']) {
		xP = svgPaddingX;
		$.each(data['components']['mds'], function(i, hardware) {
			plotShape('mds', hardware['name'], hardware['vendor_model']);
			if(i < (data['components']['mds'].length - 1)) xP += imageDistanceX;
			else yP += imageDistanceY;
		});
	}

	//Flasharray
	if('flasharray' in data['components']) {
		xP = imageDistanceX / 2 + svgPaddingX;
		$.each(data['components']['flasharray'], function(i, hardware) {
			plotShape('flasharray', hardware['name'], hardware['vendor_model']);
			if(i < (data['components']['flasharray'].length - 1)) xP += imageDistanceX;
			else yP += imageDistanceY + 80;
		});
	}
	// Set the height of the svg background
	$('.graph > svg').attr('height', (yP - 70) + 'px');
}

function drawConnections(data) {
	/* NEXUS Connections */
	createConnection('nexusA-nexusB', 1);
	createConnection('nexusA-nexusB', 2);
	/* NEXUS Connections */


	createConnection('ucsA-ucsB', 1);
	createConnection('ucsB-ucsA', 2);


	/* MDS Connections */
	//createConnection('mdsB-mdsA', 1);
	//createConnection('mdsB-mdsA', 2);
	/* MDS Connections */


	createConnection('nexusA-ucsA', 1);
	createConnection('nexusA-ucsA', 2);

	createConnection('nexusB-ucsB', 1, 'dashed');
	createConnection('nexusB-ucsB', 2, 'dashed');


	createConnection('nexusA-ucsB', 3);
	createConnection('nexusA-ucsB', 4);

	createConnection('nexusB-ucsA', 3, 'dashed');
	createConnection('nexusB-ucsA', 4, 'dashed');


	createConnection('ucsA-chassis', 1);
	createConnection('ucsA-chassis', 2);
					//createConnection('ucsA-chassis', 3);
					//createConnection('ucsA-chassis', 4);

	createConnection('ucsB-chassis', 1, 'dashed');
	createConnection('ucsB-chassis', 2, 'dashed');
					//createConnection('ucsB-chassis', 3, 'dashed');
					//createConnection('ucsB-chassis', 4, 'dashed');


	//createConnection('ucsA-mdsA', 1);
	//createConnection('ucsA-mdsA', 2);

	//createConnection('ucsB-mdsB', 1, 'dashed');
	//createConnection('ucsB-mdsB', 2, 'dashed');


	//createConnection('ucsA-mdsB', 3);
	//createConnection('ucsA-mdsB', 4);

	//createConnection('ucsB-mdsA', 3, 'dashed');
	//createConnection('ucsB-mdsA', 4, 'dashed');


	//createConnection('mdsA-flasharray', 1);
	//createConnection('mdsA-flasharray', 2);
					//createConnection('mdsA-flasharray', 3);
					//createConnection('mdsA-flasharray', 4);

	//createConnection('mdsB-flasharray', 1, 'dashed');
	//createConnection('mdsB-flasharray', 2, 'dashed');
					//createConnection('mdsB-flasharray', 3, 'dashed');
					//createConnection('mdsB-flasharray', 4, 'dashed');


	createConnection('nexusA-flasharray', 1);
	createConnection('nexusA-flasharray', 2);
					//createConnection('nexusA-flasharray', 3);
					//createConnection('nexusA-flasharray', 4);

	createConnection('nexusB-flasharray', 1, 'dashed');
	createConnection('nexusB-flasharray', 2, 'dashed');
					//createConnection('nexusB-flasharray', 3, 'dashed');
					//createConnection('nexusB-flasharray', 4, 'dashed');


	Object.keys(data['connections']).some(function(key) {
		//console.log(data['connections'][key]);
		$.each(data['connections'][key], function(index, value) {
			//console.log(key + '   >>>   ' + value['remote_device']);
		});
	});
}

function createConnection(connB, n, cls) {
	var xP = svgPaddingX, yP = svgPaddingY, components;
	var strokeDA = (typeof cls == 'undefined') ? '': '';
	cls = (typeof cls == 'undefined') ? '': cls;
	hardwares = connB.replace(/A/g, "").replace(/B/g, "").split("-");
	components = connB.replace(/A/g, "").replace(/B/g, "").split("-");
	components = components.sort().join("-");
//console.log(components);
	connColors[connB] = (typeof connColors[components] == 'undefined') ? '#FB5000' : connColors[components];

//console.log(hardwares);
	switch(connB) {
		case 'nexusA-nexusB':
		case 'nexusB-nexusA':
			plotNodes(connColors[connB], (xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius), (yP + groupVPadding - nodeRadius + connectionOffset[hardwares[0]]['nodeDistY'] * n));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius/2), (yP + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + imageDistanceX + groupHPadding + nodeRadius/2), (yP + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + groupHPadding), (yP + groupVPadding - nodeRadius + connectionOffset[hardwares[1]]['nodeDistY'] * n));
			break;


		case 'ucsA-ucsB':
		case 'ucsB-ucsA':
			plotNodes(connColors[connB], (xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - nodeRadius + connectionOffset[hardwares[0]]['nodeDistY'] * n));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + imageDistanceX + groupHPadding + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + groupHPadding), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - nodeRadius + connectionOffset[hardwares[1]]['nodeDistY'] * n));
			break;


		case 'mdsA-mdsB':
		case 'mdsB-mdsA':
			plotNodes(connColors[connB], (xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius), (yP + imageDistanceY*3 + chassisHeight + groupVPadding - nodeRadius + connectionOffset[hardwares[0]]['nodeDistY'] * n));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageSize[hardwares[0]]['width'] + groupHPadding - nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + imageDistanceX + groupHPadding + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding - nodeRadius/2 + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + groupHPadding), (yP + imageDistanceY*3 + chassisHeight + groupVPadding - nodeRadius + connectionOffset[hardwares[1]]['nodeDistY'] * n));
			break;


		case 'nexusA-ucsA':
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y'] - nodeRadius/2));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2 - nodeRadius), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y']))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2 - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius/2))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius));
			break;

		case 'nexusB-ucsB':
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y'] - nodeRadius/2));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius/2))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius));
			break;


		case 'nexusA-ucsB':
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - nodeRadius));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + groupVPadding))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + imageDistanceY/1.5 - 10 * n))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + imageDistanceY/1.5 - 10 * n))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius/2))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius));
			break;

		case 'nexusB-ucsA':
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y'] - nodeRadius/2));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + groupVPadding - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + imageDistanceY/1.25 - 10 * n))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageSize[hardwares[0]]['height'] + imageDistanceY/1.25 - 10 * n))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y']))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + connectionOffset[hardwares[1]]['y'] - nodeRadius));
			break;


		case 'ucsA-chassis':
			plotNodes(connColors[connB], (xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageDistanceY*2 + chassisHeight + groupVPadding));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding))
				.L((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - imageDistanceY - chassisHeight + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.L((xP + imageDistanceX/2 + groupHPadding + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - imageDistanceY - chassisHeight + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX/2 + groupHPadding), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - imageDistanceY - chassisHeight + connectionOffset[hardwares[1]]['nodeDistY'] * n - nodeRadius/2));
			break;

		case 'ucsB-chassis':
			plotNodes(connColors[connB], (xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageDistanceY*2 + chassisHeight + groupVPadding));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding))
				.L((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - imageDistanceY - chassisHeight + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.L((xP + imageDistanceX/2 + imageSize[hardwares[1]]['width'] + groupHPadding - nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - imageDistanceY - chassisHeight + connectionOffset[hardwares[1]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX/2 + imageSize[hardwares[1]]['width'] + groupHPadding - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding - imageDistanceY - chassisHeight + connectionOffset[hardwares[1]]['nodeDistY'] * n - nodeRadius/2));
			break;


		case 'ucsA-mdsA':
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageDistanceY*3 + chassisHeight + groupVPadding));
			break;

		case 'ucsB-mdsB':
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n), (yP + imageDistanceY*3 + chassisHeight + groupVPadding));
			break;


		case 'ucsA-mdsB':
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - nodeRadius));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - imageDistanceY/2 - 10 * n))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - imageDistanceY/2 - 10 * n))
				.L((xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[1]]['width'] + groupHPadding - connectionOffset[hardwares[1]]['nodeDistX'] * n), (yP + imageDistanceY*3 + chassisHeight + groupVPadding));
			break;

		case 'ucsB-mdsA':
			plotNodes(connColors[connB], (xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*2 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - connectionOffset[hardwares[0]]['y']))
				.L((xP + imageDistanceX + imageSize[hardwares[0]]['width'] + groupHPadding - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - groupHPadding - 10 * n))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height']  - groupHPadding - 10 * n))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding))
				.drawAnimated({delay: 200, duration: animDuration});

			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + imageDistanceY*3 + chassisHeight + groupVPadding));
			break;


		case 'mdsA-flasharray':
			plotNodes(connColors[connB], (xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - nodeRadius));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + groupHPadding + imageDistanceX/2 + nodeRadius/2), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + groupHPadding + imageDistanceX/2), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n - nodeRadius/2));
			break;

		case 'mdsB-flasharray':
			plotNodes(connColors[connB], (xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height'] - nodeRadius));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*3 + chassisHeight + groupVPadding + imageSize[hardwares[0]]['height']))
				.L((xP + groupHPadding + imageDistanceX + imageSize[hardwares[0]]['width']/3 + connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + groupHPadding + imageDistanceX/2 + imageSize[hardwares[0]]['width']), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + groupHPadding + imageDistanceX/2 + imageSize[hardwares[0]]['width'] - nodeRadius), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n - nodeRadius/2));
			break;


		case 'nexusA-flasharray':
			plotNodes(connColors[connB], (xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius), (yP + groupVPadding));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + groupVPadding))
				.L((xP + groupHPadding + connectionOffset[hardwares[0]]['nodeDistX'] * n - nodeRadius/2), (yP + groupVPadding - 10 * n))
				.L((xP + groupHPadding - nodeRadius/2 - 10 * n), (yP + groupVPadding - 10 * n))
				.L((xP + groupHPadding - nodeRadius/2 - 10 * n), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + imageDistanceX/2 + groupHPadding + nodeRadius/2), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX/2 + groupHPadding), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n - nodeRadius/2));
			break;

		case 'nexusB-flasharray':
			plotNodes(connColors[connB], (xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * n), (yP + groupVPadding));
			svg.path().attr({fill: 'none', stroke: connColors[connB], 'stroke-width': lineWidth, 'class': cls}).style('stroke-dasharray', strokeDA)
				.M((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + groupVPadding))
				.L((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] - connectionOffset[hardwares[0]]['nodeDistX'] * n + nodeRadius/2), (yP + groupVPadding - 10 * n))
				.L((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] + nodeRadius/2 + 10 * n), (yP + groupVPadding - 10 * n))
				.L((xP + imageDistanceX + groupHPadding + imageSize[hardwares[0]]['width'] + nodeRadius/2 + 10 * n), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.L((xP + imageDistanceX/2 + groupHPadding + imageSize[hardwares[0]]['width'] - nodeRadius/2), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n))
				.drawAnimated({delay: 200, duration: animDuration});
			plotNodes(connColors[connB], (xP + imageDistanceX/2 + groupHPadding + imageSize[hardwares[0]]['width'] - nodeRadius), (yP + imageDistanceY*4 + chassisHeight + groupVPadding + connectionOffset[hardwares[0]]['nodeDistY'] * n - nodeRadius/2));
			break;
	}
}
