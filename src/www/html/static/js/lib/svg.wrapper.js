$description = $(".description");
$(document).ready(function() {
	$('body').delegate('#connectivity-diagram path', 'click', function(e) {
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
	var startIndex = 20, lineLength = 70, lineTxtSpacing = 20, legendDistance = 420, k = 0;
	$.each(legendColorArr, function(txt, color) {
		svgLegend.path().attr({fill: 'none', stroke: color, 'stroke-width': lineWidth})
			.M((startIndex + (legendDistance * k)), 16).L((startIndex + (legendDistance * k) + lineLength), 16);
		svgLegend.text(txt).font({ size: 12.5, family: 'Verdana' }).fill(color).move((startIndex + (legendDistance * k) + lineLength + lineTxtSpacing), 10);	//.animate('2s');

		svgLegend.path().attr({fill: 'none', stroke: color, 'stroke-width': lineWidth}).style('stroke-dasharray', 8)
			.M((startIndex + (legendDistance * k)), 40).L((startIndex + (legendDistance * k) + lineLength), 40);
		svgLegend.text(txt).font({ size: 12.5, family: 'Verdana' }).fill(color).move((startIndex + (legendDistance * k) + lineLength + lineTxtSpacing), 34);
		k++;
	});
}

function plotNodes(position, nodeColor, x, y, port, helpTxt) {
	group = nodes.group().attr({"class": "enabled tipso tipso_style", "data-tipso-title": '&nbsp;&nbsp;' + port, "data-tipso": helpTxt});
	var nested = group.nested(), textAnchor = 'start', rotation = 0;
	nested.circle(nodeRadius).attr({'style': "fill: " + nodeColor + "; stroke: " + nodeColor + "; stroke-width: 1;"}).move(x, y);
	switch(position) {
		case 'top':
			y -= 10 + ((port.length - 1) * 3);
			x -= 5 + ((port.length - 1) * 2.5);
			rotation = 270;
			break;
		case 'bottom':
			y += 15 + ((port.length - 1) * 2.5);
			x += 8 - ((port.length - 1) * 2.5);
			rotation = 90;
			break;
		case 'left':
			textAnchor = 'end';
			x -= 10;
			y -= 7;
			break;
		case 'right':
		default:
			x += 15;
			y -= 7;
			break;
	}
	nested.text(function(add) {
		add.tspan(port).fill(nodeColor).attr({'text-anchor': textAnchor, 'font-size': '9px', 'letter-spacing': '0.8px'})
	}).move(x, y).transform({ rotation: rotation });
}

var group;
function plotShape(objType, objName, objLabel, subLabel, helpTxt) {
	var color;
	subLabel = (typeof subLabel == 'undefined') ? '' : subLabel;
	group = nodes.group().translate(xP, yP).attr({"name": objName, "class": "tipso tipso_style", "data-tipso-title": '&nbsp;&nbsp;' + ucfirst(objType), "data-tipso": helpTxt}).draggy();
	var nested = group.nested().attr({'width': (imageSize[objType].width + (groupHPadding * 2)) + 'px', 'height': (imageSize[objType].height + groupVPadding * 2) + 'px'});
	//nested.rect((imageSize[objType].width + (groupHPadding * 2)), (imageSize[objType].height + groupVPadding * 2)).radius(7).fill("#FFF").stroke("#EAEAEA");
	//group.image(objType + '.png', imageSize[objType].width, imageSize[objType].height).move(groupHPadding, 30);
	nested.rect(imageSize[objType].width, imageSize[objType].height).radius(4).fill('#DADADA').stroke('#A2A2A2').move(groupHPadding, groupVPadding);
	nested.text(function(add) {
		add.tspan(objLabel).fill(labelColor).attr({'font-size': '9px', 'font-family': 'ProximaNovaSemibold', 'letter-spacing': '0.8px'})
		add.tspan(subLabel).fill('#FB5000').attr({'font-size': '8px'}).dx(5).dy(-2)
	}).move((groupHPadding + 20), (groupVPadding + 10))
	.attr({'text-anchor': 'middle', 'dominant-baseline': 'middle', 'x': '50%', 'y': '50%'});
	/* $.each(connections[objType], function(index, value) {
		color = (typeof connColors[objType + '-' + value['to']] == 'undefined') ? connColors[value['to'] + '-' + objType] : connColors[objType + '-' + value['to']];
		plotNodes(color, (groupHPadding + value['x']), (groupVPadding + value['y']));
	}); */
}