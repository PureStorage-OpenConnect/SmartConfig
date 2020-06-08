$description = $(".description");
$(document).ready(function() {
	$('path').click(function(e) {
		e.stopPropagation();
		$('path.move').removeAttr('class');
		$(this).attr('class', 'move');
		return false;
	});

	$('circle').click(function(e) {
		e.stopPropagation();
		$('path.move').removeAttr('class');
		console.log($(this).data('connection'));
		return false;
	});

	$('.enabled').hover(function() {
		$(this).attr("class", "enabled active");
		$description.addClass('active');
		$description.html($(this).attr('id'));
	}, function() {
		$description.removeClass('active');
	});

	$(document).on('click', function(e) {
		$('path.move').removeAttr('class');
	});

	$(document).on('mousemove', function(e) {
		$description.css({
			left:  e.pageX - 65,
			top:   e.pageY - 55
		});
	});
});

function drawLegend() {
	svgLegend.path().attr({fill: 'none', stroke: connColors['nexus-nexus'], 'stroke-width': lineWidth})
		.M(10, 16).L(80, 16);
	svgLegend.text('10 GbE (LAN Fabric A)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['nexus-nexus']).move(100, 10);	//.animate('2s');

	svgLegend.path().attr({fill: 'none', stroke: connColors['nexus-nexus'], 'stroke-width': lineWidth}).style('stroke-dasharray', 8)
		.M(10, 40).L(80, 40);
	svgLegend.text('10 GbE (LAN Fabric B)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['nexus-nexus']).move(100, 34);

	
	svgLegend.path().attr({fill: 'none', stroke: connColors['chassis-ucs'], 'stroke-width': lineWidth})
		.M(300, 16).L(380, 16);
	svgLegend.text('10 GbE (Unified Fabric A)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['chassis-ucs']).move(400, 10);

	svgLegend.path().attr({fill: 'none', stroke: connColors['chassis-ucs'], 'stroke-width': lineWidth}).style('stroke-dasharray', 8)
		.M(300, 40).L(380, 40);
	svgLegend.text('10 GbE (Unified Fabric B)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['chassis-ucs']).move(400, 34);


	svgLegend.path().attr({fill: 'none', stroke: connColors['mds-ucs'], 'stroke-width': lineWidth})
		.M(600, 16).L(680, 16);
	svgLegend.text('8G FC (SAN Fabric A)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['mds-ucs']).move(700, 10);

	svgLegend.path().attr({fill: 'none', stroke: connColors['mds-ucs'], 'stroke-width': lineWidth}).style('stroke-dasharray', 8)
		.M(600, 40).L(680, 40);
	svgLegend.text('8G FC (SAN Fabric B)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['mds-ucs']).move(700, 34);


	svgLegend.path().attr({fill: 'none', stroke: connColors['flasharray-mds'], 'stroke-width': lineWidth})
		.M(900, 16).L(980, 16);
	svgLegend.text('16G FC (SAN Fabric A)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['flasharray-mds']).move(1000, 10);

	svgLegend.path().attr({fill: 'none', stroke: connColors['flasharray-mds'], 'stroke-width': lineWidth}).style('stroke-dasharray', 8)
		.M(900, 40).L(980, 40);
	svgLegend.text('16G FC (SAN Fabric B)').font({ size: 12.5, family: 'Verdana' }).fill(connColors['flasharray-mds']).move(1000, 34);
}

function drawPortChannelConnections() {
	var g = nodes.group();

	g.ellipse(20, 65).fill('transparent').stroke("#000").move(580, 25).attr('class', 'enabled');
	g.ellipse(28, 70).fill('transparent').stroke("#FF0000").move(576, 22).attr('class', 'enabled');
	g.text('vPC Peer').move(610, 50).fill('#FB5000').font({ size: 13.5, family: 'Verdana' });

	g.ellipse(50, 20).fill('transparent').stroke("#000").move(20, 140).attr('class', 'enabled');
	g.ellipse(60, 26).fill('transparent').stroke("#FF0000").move(15, 137).attr('class', 'enabled');
	g.text('vPC').move(85, 143).fill('#FB5000').font({ size: 13.5, family: 'Verdana' });

	g.ellipse(50, 20).fill('transparent').stroke("#000").move(1170, 140).attr('class', 'enabled');
	g.ellipse(60, 26).fill('transparent').stroke("#FF0000").move(1165, 137).attr('class', 'enabled');
	g.text('vPC').move(1135, 143).fill('#FB5000').font({ size: 13.5, family: 'Verdana' });

	g.ellipse(50, 20).fill('transparent').stroke("#000").move(60, 350).attr('class', 'enabled');
	g.ellipse(60, 26).fill('transparent').stroke("#FF0000").move(55, 347).attr('class', 'enabled');

	g.ellipse(50, 20).fill('transparent').stroke("#000").move(810, 350).attr('class', 'enabled');
	g.ellipse(60, 26).fill('transparent').stroke("#FF0000").move(805, 347).attr('class', 'enabled');
}

function plotNodes(nodeColor, x, y) {
	//console.log(nodeColor + '  ::  ' + x + '   >>>   ' + y);
	//group.circle(nodeRadius).fill(nodeColor).move(x, y).attr('class', 'enabled');
	svg.circle(nodeRadius).fill(nodeColor).move(x, y).attr('class', 'enabled');
}

var group;
function plotShape(objType, objName, objLabel, subLabel) {
	var color;
	subLabel = (typeof subLabel == 'undefined') ? '' : subLabel;
	group = nodes.group().translate(xP, yP).attr("name", objName).draggy();
	group.rect((imageSize[objType].width + (groupHPadding * 2)), (imageSize[objType].height + groupVPadding * 2)).radius(7).fill("#FFF").stroke("#EAEAEA");
	//group.image(objType + '.png', imageSize[objType].width, imageSize[objType].height).move(groupHPadding, 30);
	group.rect(imageSize[objType].width, imageSize[objType].height).radius(4).fill('#DADADA').stroke('#A2A2A2').move(groupHPadding, groupVPadding);
	group.text(function(add) {
		add.tspan(objLabel).fill(labelColor)
		add.tspan(subLabel).fill('#FB5000').attr({'font-size': '10px'}).dx(5).dy(-2)
	}).move((groupHPadding + 20), (groupVPadding + 10));

	/* $.each(connections[objType], function(index, value) {
		color = (typeof connColors[objType + '-' + value['to']] == 'undefined') ? connColors[value['to'] + '-' + objType] : connColors[objType + '-' + value['to']];
		plotNodes(color, (groupHPadding + value['x']), (groupVPadding + value['y']));
	}); */
}
