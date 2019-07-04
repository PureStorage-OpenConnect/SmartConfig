var paper = {}, connections = [], shapeSets = {};
var xCenter, sourceObj = null, currentShape = null, activeObj;
var TRANSITION_TIME = 500; PAN_DISTANCE = 200, FLOWCHART_START = 20, ISEDITABLE = false, ISDRAGGABLE = false;

// Shape sizes, colors & font icon declarations
var shapeSizes = {'rect': '250', 'rect-height': '50', 'ellipse': '40', 'triangle': '65', 'diamond': '40', 'port': '5'};
var colorCodes = {'fill': '#929292', 'stroke': '#DEDEDE', 'workflow-fill': '#3C87C2', 'workflow-stroke': '#CEDAE2', 'fill-input': '#83B98A', 'stroke-input': '#D0DECD', 'shape-fill': '#F17C22', 'shape-stroke': '#DADADA', 'EXECUTING-fill': '#096FB8', 'COMPLETED-fill': '#83B98A', 'FAILED-fill': '#CE5151', 'success-conn': '#52BF52', 'failure-conn': '#EA4747', 'success-port': '#55AD38', 'failure-port': '#CE6868', 'input-port': '#AFAFAF', 'port-stroke': '#A9A9A9', 'label': '#FFF'};
var fontIconList = {
	'task-input': {'icon': '\uf044', 'color': '#555', 'font': '16'}, 
	'task-success-input': {'icon': '\uf058', 'color': '#5EA25E', 'font': '16'}, 
	'delete-element': {'icon': '\uf057', 'color': '#BC0001', 'font': '16'}, 
	'task-expand': {'icon': '\uf0b2', 'color': '#555', 'font': '14'}
};//'clear-connections': {'icon': '\uf074', 'color': '#555', 'font': '16'}, 
// Animation declarations
var toggleEffect = {'puff': {'in': 'puffIn', 'out': 'puffOut'}, 'vanish': {'in': 'vanishIn', 'out': 'vanishOut'}, 'slide': {'in': 'slideLeftReturn', 'out': 'slideLeft'}}, effect = 'vanish';

/**
  * @desc this method will create connection path between two shapes passed as argument.
  * @param object $obj1 - rapheal shape object from where to start the connection.
  * @param object $obj2 - rapheal shape object from where to end the connection.
  * @param object $line - raphael path object for the line.
  * @param object $bg - raphael path object for the line background.
*/
Raphael.fn.connection = function (obj1, obj2, line, bg) {
    if (obj1.line && obj1.from && obj1.to) {
        line = obj1;
        obj1 = line.from;
        obj2 = line.to;
    }
    var bb1 = obj1.getBBox(),
        bb2 = obj2.getBBox(),
        p = [{x: bb1.x + bb1.width / 2, y: bb1.y - 1},
        {x: bb1.x + bb1.width / 2, y: bb1.y + bb1.height + 1},
        {x: bb1.x - 1, y: bb1.y + bb1.height / 2},
        {x: bb1.x + bb1.width + 1, y: bb1.y + bb1.height / 2},
        {x: bb2.x + bb2.width / 2, y: bb2.y - 1},
        {x: bb2.x + bb2.width / 2, y: bb2.y + bb2.height + 1},
        {x: bb2.x - 1, y: bb2.y + bb2.height / 2},
        {x: bb2.x + bb2.width + 1, y: bb2.y + bb2.height / 2}],
        d = {}, dis = [];
    for (var i = 0; i < 4; i++) {
        for (var j = 4; j < 8; j++) {
            var dx = Math.abs(p[i].x - p[j].x),
                dy = Math.abs(p[i].y - p[j].y);
            if ((i == j - 4) || (((i != 3 && j != 6) || p[i].x < p[j].x) && ((i != 2 && j != 7) || p[i].x > p[j].x) && ((i != 0 && j != 5) || p[i].y > p[j].y) && ((i != 1 && j != 4) || p[i].y < p[j].y))) {
                dis.push(dx + dy);
                d[dis[dis.length - 1]] = [i, j];
            }
        }
    }
    if (dis.length == 0) {
        var res = [0, 4];
    } else {
        res = d[Math.min.apply(Math, dis)];
    }
    var x1 = p[res[0]].x,
        y1 = p[res[0]].y,
        x4 = p[res[1]].x,
        y4 = p[res[1]].y;
    dx = Math.max(Math.abs(x1 - x4) / 2, 10);
    dy = Math.max(Math.abs(y1 - y4) / 2, 10);
    var x2 = [x1, x1, x1 - dx, x1 + dx][res[0]].toFixed(3),
        y2 = [y1 - dy, y1 + dy, y1, y1][res[0]].toFixed(3),
        x3 = [0, 0, 0, 0, x4, x4, x4 - dx, x4 + dx][res[1]].toFixed(3),
        y3 = [0, 0, 0, 0, y1 + dy, y1 - dy, y4, y4][res[1]].toFixed(3);
    var path = ["M", x1.toFixed(3), y1.toFixed(3), "C", x2, y2, x3, y3, x4.toFixed(3), y4.toFixed(3)].join(",");
    if (line && line.line) {
        line.bg && line.bg.attr({path: path});
        line.line.attr({path: path});
    } else {
        var color = typeof line == "string" ? line : "#000";
        return {
            bg: bg && bg.split && this.path(path).attr({stroke: bg.split("|")[0], "arrow-end": "block-midium-midium", "stroke-width": bg.split("|")[1] || 3}),
            line: this.path(path).attr({stroke: color, fill: "none"}),
            from: obj1,
            to: obj2
        };
    }
};

/**
  * @desc initialize the flow chart on the given dom element.
  * @param string $domID - the id string of the element where to bind the raphael workspace object.
  * @param boolean $isEditable - flag weather the chart element is a editable or not.
  * @param boolean $isDraggable - flag weather the chart element is a draggable or not.
*/
function initFlowchart(domID, isEditable, isDraggable) {
	FLOWCHART_START = 40;
	ISEDITABLE = isEditable;
	ISDRAGGABLE = isDraggable;
	$('#' + domID).html('');
	paper[domID] = Raphael(domID, '100%', '100%');
	//var color = Raphael.getColor();
	bindPanZoom(domID);

	var position = $('#' + domID).position();
	xCenter = parseInt($('#' + domID).width()) / 2;
}

/**
  * @desc bind zoom object with the raphael container element.
  * @param string $domID - the id string of the element where to bind the zoom object.
*/
window.zoomWorkflow = [];
function bindPanZoom(domID) {
	window.zoomWorkflow[domID] = $('#' + domID).panzoom({
		maxScale: 2,
		disablePan: true,
		contain: 'automatic'
		//contain: 'invert'
		//contain: false
	});
}

/**
  * @desc this method will create a triangle shape on the workspace using the rapheal path object.
  * @param integer $x - the position (x - axis) to create the shape.
  * @param integer $y - the position (y - axis) to create the shape.
  * @param integer $sl - length of the shape on each side.
*/
function createTrianglePath(x, y, sl) {
	var path = 'M' + x + ',' + y + 'L' + (parseInt(x) - parseInt(sl)) + ',' + (parseInt(y) + parseInt(sl)) + 'L' + (parseInt(x) + parseInt(sl)) + ',' + (parseInt(y) + parseInt(sl)) + 'Z';
	return path;
}

/**
  * @desc this method will create a diamond shape on the workspace using the rapheal path object.
  * @param integer $x - the position (x - axis) to create the shape.
  * @param integer $y - the position (y - axis) to create the shape.
  * @param integer $sl - length of the shape on each side.
*/
function createDiamondPath(x, y, sl) {	// x,y = center location, sl = length of the side
	var path = 'M' + x + ',' + y + 'L' + (parseInt(x) - (parseInt(sl) * 2)) + ',' + (parseInt(y) + parseInt(sl)) + 'L' + x + ',' + (parseInt(y) + (parseInt(sl) * 2)) + 'L' + (parseInt(x) + (parseInt(sl) * 2)) + ',' + (parseInt(y) + parseInt(sl)) + 'Z';
	return path;
}

$(document).ready(function() {
	hoverIn = function() {
		this.attr({"opacity": 0.6});
	};
	hoverOut = function() {
		this.attr({"opacity": 1});
	}

	/**
	  * @desc event registration for zooming the workspace area.
	*/
	$('body').delegate('.zoomin', 'click', function(e) {
		e.preventDefault();
		zoomWorkflow[activeObj].panzoom('zoom');
		return false;
	});
	
	/**
	  * @desc event registration for zooming out the workspace area.
	*/
	$('body').delegate('.zoomout', 'click', function(e) {
		e.preventDefault();
		zoomWorkflow[activeObj].panzoom('zoom', true);
		return false;
	});

	/**
	  * @desc event registration for reset zoom of workspace area.
	*/
	$('body').delegate('#pan-reset', 'click', function(e) {
		zoomWorkflow[activeObj].panzoom("reset");
		$('.workshop[jobId="' + activeObj + '"]').css({top: 0, left: 0});
		return false;
	});

	/**
	  * @desc event registration for removing an element/shape from the workspace.
	*/
	$('body').delegate('.delete-element', 'click', function(e) {
		var api, query = {};
		query.wid = activeObj;
		query.execid = currentShape.id;
		if(currentShape.type != 'path' || (currentShape.type == 'path' && (currentShape.node.className.baseVal == 'diamond' || currentShape.node.className.baseVal == 'triangle')))
			api = 'DeleteTask';
		else {
			var connection = getObjectByKeyValue(connections, currentShape.id, 'bg', 'id');
			api = 'DeleteConnection';
			query.ttype = 'onsuccess';
			query.execid = connection.from.id.replace('s_out_', '');
			if(connection.from.id.indexOf('f_out_') == 0) {
				query.execid = connection.from.id.replace('f_out_', '');
				query.ttype = 'onfailure';
			}
		}
		doAjaxRequest({url: api, base_path: settings.base_path, method: 'DELETE', query: query, container: '.workshop > .workflow'}, function(response) {
			deleteItem(currentShape);
			currentShape = null;
		}, doNothing);
		return false;
	});

	/**
	  @desc event registration for clearing the workspace area.
	*/
	$('body').delegate('.clear-connections', 'click', function(e) {
		//clearConnectionsByShape(currentShape, ['s_out', 'f_out', 'input']);
		return false;
	});

	/**
	  * @desc event registration for reset the flow chart of the current workspace.
	*/
	$('body').delegate('.reset-workshop', 'click', function(e) {
		var obj = $(this);
		$('.workshop[jobId="' + obj.closest('.workshop').attr('groupId') + '"]').show().removeClass(toggleEffect[effect]['out']).addClass('magictime ' + toggleEffect[effect]['in']);
		$('.subworkflow-title').remove();
		activeObj = obj.closest('.workshop').attr('groupId');
		$('foreignObject.' + obj.closest('.workshop').attr('jobId')).remove();
		obj.closest('.workshop').remove();
		return false;
	});

	/**
	  * @desc method for making an element/shape as draggable.
	*/
	Raphael.st.draggable = function() {
		var me = this, lx = 0, ly = 0, ox = 0, oy = 0,
		moveFnc = function(dx, dy) {
			lx = dx + ox;
			ly = dy + oy;
			if(lx < me.min_x) {
				lx = me.min_x;
			} else if ( lx > me.max_x) {
				lx = me.max_x;
			}

			if(ly < me.min_y) {
				ly = me.min_y;
			} else if(ly > me.max_y) {
				ly = me.max_y;
			}

			me.transform('t' + lx + ',' + ly);
			for(var i = connections.length; i--;) {
				paper[activeObj].connection(connections[i]);
			}
		},
		startFnc = function() {},
		endFnc = function() {
			ox = lx;
			oy = ly;
		};

		this.drag(moveFnc, startFnc, endFnc);
	};

	/**
	  * @desc this will clear/reset the current workspace.
	*/
	clearPaper = function() {
		paper[activeObj].clear();
	};

	/**
	  * @desc this will create the given shape over workspace in the given location.
	  * @param string $type - the shape - rect or ellipse or triangle or diamond.
	  * @param string $label - the text to write on the shape.
	  * @param string $execid - .
	  * @param string $uniqueid - .
	  * @param string $jobid - .
	  * @param string $taskType - .
	  * @param array $position - .
	*/
	createShape = function(type, label, execid, uniqueid, jobid, taskType, position) {
		var display_label = chunk(label, 30).join('\n');
		if(display_label.length > 60)
			display_label = display_label.substring(0, 57) + '...';

		var y = FLOWCHART_START;
		if(execid == 'end') y += 20;
		var bgcolor = colorCodes['shape-fill'], bgstroke = colorCodes['shape-stroke'];
		if(typeof taskType != 'undefined' && (taskType == 'wgroup' || taskType.toLowerCase() == 'workflows')) bgcolor = colorCodes['workflow-fill'];
		var mySet = paper[activeObj].set();
		var xTmp = xCenter;
		var glowObj = [], glowOptions = [{width: '16px', opacity: '0.2'}, {width: '10px', opacity: '0.3'}, {width: '6px', opacity: '0.4'}];
		switch(type) {
			case "ellipse":
				var bgcolor = colorCodes['fill'], bgstroke = colorCodes['stroke'];
				for(i = 0; i < 3; i++)
					glowObj.push(paper[activeObj].ellipse(xCenter, y, shapeSizes[type], parseInt(shapeSizes[type]) / 2));
				shapeObj = paper[activeObj].ellipse(xCenter, y, shapeSizes[type], parseInt(shapeSizes[type]) / 2);
				FLOWCHART_START += 80;
				break;
			case "rect":
				x = parseInt(xTmp) - (parseInt(shapeSizes[type]) / 2);
				/* if(position != 'undefined') {
					x = position.left; y = position.top;
					xTmp = x + (shapeSizes[type] / 2);
				} */
				for(i = 0; i < 3; i++)
					glowObj.push(paper[activeObj].rect(x, y, shapeSizes[type], shapeSizes[type + '-height'], 10));
				shapeObj = paper[activeObj].rect(x, y, shapeSizes[type], shapeSizes[type + '-height'], 10);
				if(taskType == 'wgroup')
					shapeObj.node.setAttribute('class', 'group_box');
				else shapeObj.node.setAttribute('class', 'task_box');
				y += (parseInt(shapeSizes[type + '-height']) / 2);
				FLOWCHART_START += 100;
				break;
			case "triangle":
				shapeObj = paper[activeObj].path(createTrianglePath(xTmp, y, shapeSizes[type]));
				shapeObj.node.setAttribute('class', 'triangle');
				y += (parseInt(shapeSizes[type]) - 20);
				FLOWCHART_START += 100;
				break;
			case "diamond":
				shapeObj = paper[activeObj].path(createDiamondPath(xTmp, y, shapeSizes[type]));
				shapeObj.node.setAttribute('class', 'diamond');
				y += parseInt(shapeSizes[type]);
				FLOWCHART_START += 100;
				break;
		}
		shapeObj.node.id = execid;
		shapeObj.id = execid;
		shapeObj.node.setAttribute('style', 'fill: ' + bgcolor + '; stroke: ' + bgstroke);
		$.each(glowObj, function(i, obj) {
			obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #A9A9A9; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
		});
		
		var shapeLabel = paper[activeObj].text(xTmp, y, display_label).attr({fill: colorCodes['label'], 'font-size': '12', 'letter-spacing': '0.4'});
		shapeLabel.node.setAttribute('id', 'label_' + execid);
		$('#' + execid).html('<title>' + execid + ' - ' + label + '</title>');

		mySet.push(shapeObj, shapeLabel);
		$.each(glowObj, function(i, obj) {mySet.push(obj);});
		var inputPort, successOut, failureOut;
		if(execid == 'start') {
			for(i = 0; i < 3; i++) {
				obj = paper[activeObj].circle(xTmp, parseInt(y) + (parseInt(shapeSizes[type]) / 2), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);
			}
			successOut = paper[activeObj].circle(xTmp, parseInt(y) + (parseInt(shapeSizes[type]) / 2), shapeSizes['port']).attr({fill: colorCodes['input-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			successOut.click(function() {
				if(!this.data('output-line') && ISEDITABLE) {
					sourceObj = this;
					highlightPorts(successOut);
				}
			});
			successOut.id = 's_out_' + execid;
			successOut.node.setAttribute('id', 's_out_' + execid);
			successOut.node.setAttribute('type', 's_out');
			mySet.push(successOut);
		} else if(execid == 'end') {
			for(i = 0; i < 3; i++) {
				obj = paper[activeObj].circle(xTmp, parseInt(y) - (parseInt(shapeSizes[type]) / 2), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);
			}
			inputPort = paper[activeObj].circle(xTmp, parseInt(y) - (parseInt(shapeSizes[type]) / 2), shapeSizes['port']).attr({fill: colorCodes['input-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			inputPort.click(function() {
				if(ISEDITABLE && sourceObj)
					connectionCallback(sourceObj, this);
			});
			inputPort.id = 'input_' + execid;
			inputPort.node.setAttribute('id', 'input_' + execid);
			inputPort.node.setAttribute('type', 'input');
			mySet.push(inputPort);
		} else if(type == 'rect') {
			for(i = 0; i < 3; i++) {
				obj = paper[activeObj].circle(x + (parseInt(shapeSizes[type]) / 2) + (parseInt(shapeSizes[type]) / 2) - 20, parseInt(y) + (parseInt(shapeSizes[type + '-height']) / 2), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);

				obj = paper[activeObj].circle(x + (parseInt(shapeSizes[type]) / 2) - (parseInt(shapeSizes[type]) / 2) + 20, parseInt(y) + (parseInt(shapeSizes[type + '-height']) / 2), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);

				obj = paper[activeObj].circle(x + (parseInt(shapeSizes[type]) / 2), parseInt(y) - (parseInt(shapeSizes[type + '-height']) / 2), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);
			}
			successOut = paper[activeObj].circle(x + (parseInt(shapeSizes[type]) / 2) + (parseInt(shapeSizes[type]) / 2) - 20, parseInt(y) + (parseInt(shapeSizes[type + '-height']) / 2), shapeSizes['port']).attr({fill: colorCodes['success-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			failureOut = paper[activeObj].circle(x + (parseInt(shapeSizes[type]) / 2) - (parseInt(shapeSizes[type]) / 2) + 20, parseInt(y) + (parseInt(shapeSizes[type + '-height']) / 2), shapeSizes['port']).attr({fill: colorCodes['failure-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			inputPort = paper[activeObj].circle(x + (parseInt(shapeSizes[type]) / 2), parseInt(y) - (parseInt(shapeSizes[type + '-height']) / 2), shapeSizes['port']).attr({fill: colorCodes['input-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			var execLabel;
			if(taskType != 'wgroup') {
				execLabel = paper[activeObj].text(parseInt(xTmp) - (parseInt(shapeSizes[type]) / 2) + 5, parseInt(y) - (parseInt(shapeSizes[type + '-height']) / 2) + 10, execid).attr({fill: colorCodes['label'], 'font-size': '9', 'letter-spacing': '0.4', 'text-anchor': 'start'});
				execLabel.node.setAttribute('id', 'task_status_' + execid);
			}
		} else if(type == 'triangle') {
			for(i = 0; i < 3; i++) {
				obj = paper[activeObj].circle(parseInt(xTmp) + parseInt(shapeSizes[type]), parseInt(y) + 20, shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);

				obj = paper[activeObj].circle(parseInt(xTmp) - parseInt(shapeSizes[type]), parseInt(y) + 20, shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);

				obj = paper[activeObj].circle(xTmp, (parseInt(y) - parseInt(shapeSizes[type]) + 20), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);
			}
			successOut = paper[activeObj].circle(parseInt(xTmp) + parseInt(shapeSizes[type]), parseInt(y) + 20, shapeSizes['port']).attr({fill: colorCodes['success-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			failureOut = paper[activeObj].circle(parseInt(xTmp) - parseInt(shapeSizes[type]), parseInt(y) + 20, shapeSizes['port']).attr({fill: colorCodes['failure-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			inputPort = paper[activeObj].circle(xTmp, (parseInt(y) - parseInt(shapeSizes[type]) + 20), shapeSizes['port']).attr({fill: colorCodes['input-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
		} else if(type == 'diamond') {
			for(i = 0; i < 3; i++) {
				obj = paper[activeObj].circle(parseInt(xTmp) + (parseInt(shapeSizes[type]) * 2), y, shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);

				obj = paper[activeObj].circle(parseInt(xTmp) - (parseInt(shapeSizes[type]) * 2), y, shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);

				obj = paper[activeObj].circle(xTmp, parseInt(y) - parseInt(shapeSizes[type]), shapeSizes['port']).attr({'cursor': 'pointer'});
				obj.node.setAttribute('style', 'stroke-miterlimit: 0; fill: #DEDEDE; stroke: #757474; stroke-width: ' + glowOptions[i].width + '; stroke-opacity: ' + glowOptions[i].opacity);
				mySet.push(obj);
			}
			successOut = paper[activeObj].circle(parseInt(xTmp) + (parseInt(shapeSizes[type]) * 2), y, shapeSizes['port']).attr({fill: colorCodes['success-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			failureOut = paper[activeObj].circle(parseInt(xTmp) - (parseInt(shapeSizes[type]) * 2), y, shapeSizes['port']).attr({fill: colorCodes['failure-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
			inputPort = paper[activeObj].circle(xTmp, parseInt(y) - parseInt(shapeSizes[type]), shapeSizes['port']).attr({fill: colorCodes['input-port'], stroke: colorCodes['port-stroke'], 'stroke-width': 2, 'cursor': 'pointer'});
		} else {

		}

		if(type == 'rect' || type == 'triangle' || type == 'diamond') {
			//var shapeInput = paper[activeObj].image('images/expand.png', (parseInt(xTmp) + (parseInt(shapeSizes[type]) / 2) - 10), (parseInt(y) - (parseInt(shapeSizes[type + '-height']) / 2) - 10), 20, 20);
			//shapeInput.node.setAttribute('id', 'wf_input_' + execid);
			shapeObj.click(function() {
				shapeSelect(this);
			});
			if(taskType == 'wgroup') {
				shapeObj.dblclick(function() {
					addWorkshop(jobid, taskType, uniqueid, label);
					return false;
				});
				shapeLabel.dblclick(function() {
					addWorkshop(jobid, taskType, uniqueid, label);
					return false;
				});
			}
			successOut.click(function() {
				if(!this.data('output-line') && ISEDITABLE) {
					sourceObj = this;
					highlightPorts(successOut);
				}
			});
			failureOut.click(function() {
				if(!this.data('output-line') && ISEDITABLE) {
					sourceObj = this;
					highlightPorts(failureOut);
				}
			});
			inputPort.click(function() {
				if(ISEDITABLE && sourceObj)
					connectionCallback(sourceObj, this);
			});
			successOut.id = 's_out_' + execid;
			successOut.node.setAttribute('id', 's_out_' + execid);
			successOut.node.setAttribute('type', 's_out');

			failureOut.id = 'f_out_' + execid;
			failureOut.node.setAttribute('id', 'f_out_' + execid);

			failureOut.node.setAttribute('type', 'f_out');

			inputPort.id = 'input_' + execid;
			inputPort.node.setAttribute('id', 'input_' + execid);
			inputPort.node.setAttribute('type', 'input');
			var obj = addActionStatusIcons(shapeObj, taskType);
			/* obj.inputSuccessObj.click(function() {
				Hook.call('workflowInput', [execid, uniqueid, jobid, taskType]);
				return false;
			}); */
			mySet.push(successOut, failureOut, inputPort, obj.inputObj, execLabel);
			if(ISEDITABLE) {
				mySet.push(obj.clearObj, obj.deleteObj);
			}
			if(taskType == 'wgroup') {
				obj.expandObj.click(function() {
					addWorkshop(jobid, taskType, uniqueid, label);
					return false;
				});
				mySet.push(obj.expandObj);
			} else {
				obj.inputObj.click(function() {
					obj.inputObj.hide();
					setTimeout(function() {
						obj.inputObj.show();
					}, 500);
					Hook.call('workflowInput', [execid, uniqueid, jobid, taskType]);
					return false;
				});	
			}
		}
		//var glowObj = mySet.glow({fill: false, offsetx: 2, offsety: 2, color: '#333'});
		//mySet.push(glowObj);
		/* mySet.hover(
			function() {
				$('svg>#input_' + execid).nextAll('text.shape-icons.task-input').first().show();
				$('svg>#input_' + execid).nextAll('text.shape-icons.task-expand').first().show();
			},
			function() {
				$('svg>#input_' + execid).nextAll('text.shape-icons.task-input').first().hide();
				$('svg>#input_' + execid).nextAll('text.shape-icons.task-expand').first().hide();
			}
		); */
		if(ISDRAGGABLE)
			mySet.draggable();
		shapeSets[execid] = mySet;
		$('#' + uniqueid + '>svg').css('height', FLOWCHART_START);
	};

	/**
	  * @desc it will establish the connection path between the two passed shape object.
	  * @param object $fromObj - the shape object from where to start the connection path.
	  * @param object $destObj - the shape object from where to end the connection path.
	*/
	createConnection = function(fromObj, destObj) {
		var colorCode = colorCodes['success-conn'], connectionType = 'success';
		var source_id = fromObj.id.replace('s_out_', '');
		source_id = source_id.replace('f_out_', '');
		if(fromObj != null && destObj != null && source_id != destObj.id.replace('input_', '')) {
			if(fromObj.id.indexOf('f_out_') == 0) {
				colorCode = colorCodes['failure-conn'];
				connectionType = 'failure';
			}
			var connObj = paper[activeObj].connection(fromObj, destObj, "", colorCode + "|2.5");
			connections.push(connObj);
			pushConnectionData(destObj, connObj, 'input');
			pushConnectionData(fromObj, connObj, 'output');

			connObj.bg.click(function() {
				if(ISEDITABLE)
					shapeSelect(this);
			});
			sourceObj = null;
		
			$('svg [blink]').each(function(index, obj) {
				obj.removeAttribute('blink');
			});
			unHighlightPorts();
		}
	};

	/**
	  * @desc .
	  * @param array $array - .
	  * @param string $field - .
	*/
	moveSet = function(setId, source) {
		//if(setId != 'end') {
			var conntype = 'success', xDistance = 0;
			sourceId = source.id.replace('s_out_', '');
			if(sourceId.indexOf('f_out_') >= 0) {
				conntype = 'failure';
				sourceId = sourceId.replace('s_out_', '');
			}
			var sourceTask = paper[activeObj].getById(sourceId);
			var destTask = paper[activeObj].getById(setId);
			if(sourceTask.type == 'rect') xDistance = shapeSizes[sourceTask.type] - 20;

			$.each(shapeSets[setId].items, function(index, item) {
				switch(item.type) {
					case 'ellipse':
					case 'circle':
						item.animate({cx:parseInt(source.attrs.cx) + 100,cy:parseInt(source.attrs.cy) + 100}, TRANSITION_TIME);
						break;
					case 'rect':
					case 'text':
						item.animate({x:parseInt(source.attrs.cx) + 100, y:parseInt(source.attrs.cy) + 100}, TRANSITION_TIME);
						break;
					default:
						break;
				}
			});
			setTimeout(function() {
				for(var i = connections.length; i--;) {
					paper[activeObj].connection(connections[i]);
				}
			}, TRANSITION_TIME);
		//}
	};

	/**
	  * @desc .
	  * @param array $array - .
	  * @param string $field - .
	  * @param string $field - .
	*/
	pushConnectionData = function(shapeObj, connObj, connType) {
		var lineData = [], pathData = [];
		if(shapeObj.data(connType + '-line')) {
			$.merge(lineData, shapeObj.data(connType + '-line'));
			$.merge(pathData, shapeObj.data(connType + '-path'));
		}
		lineData.push(connObj.line.id);
		pathData.push(connObj.bg.id);
		shapeObj.data(connType + '-line', lineData);
		shapeObj.data(connType + '-path', pathData);
	};

	/**
	  * @desc this method will clear all the connection path object from the current workspace.
	*/
	clearAllConnections = function() {
		Object.keys(connections).forEach(function(key) {
			removeElement(connections[key].bg.id);
			removeElement(connections[key].line.id);
		});
	};

	/**
	  * @desc this method will clear all the connection path of the given shape object.
	  * @param object $shape - the shape for which to clear the connection.
	  * @param string $connectionType - what type of connection to remove (input or successful output or failure output).
	*/
	clearConnectionsByShape = function(shape, connectionType) {
		//connectionType = ['s_out', 'f_out', 'input'];
		var portIds = [], obj;
		Object.keys(shapeSets[shape.id].items).forEach(function(i) {
			if(typeof shapeSets[shape.id].items[i].node != 'undefined' && $.inArray(shapeSets[shape.id].items[i].node.getAttribute('type'), connectionType) > -1) {
				portIds.push(shapeSets[shape.id].items[i].id);
			}
		});
		Object.keys(connections).forEach(function(key) {
			if($.inArray(connections[key].from.id, portIds) > -1 || $.inArray(connections[key].to.id, portIds) > -1) {
				if(connections[key].bg.id != null)
					removeElement(connections[key].bg.id);
				if(connections[key].line.id != null)
					removeElement(connections[key].line.id);
				delete connections[key];
			}
		});
		for(var i = shapeSets[shape.id].items.length; i--;) {
			if(shapeSets[shape.id].items[i].type == 'circle') {
				obj = paper[activeObj].getById(shapeSets[shape.id].items[i].id);
				obj.removeData();
			}
		}
		connections = removeEmptyElementFromArray(connections);
	};

	/**
	  * @desc .
	  * @param object $shape - .
	*/
	deleteItem = function(shape) {
		if(shape.type != 'path' || (shape.type == 'path' && (shape.node.className.baseVal == 'diamond' || shape.node.className.baseVal == 'triangle'))) {
			removeShape(shape.id);
		} else {
			var connection = getObjectByKeyValue(connections, shape.id, 'bg', 'id');
			paper[activeObj].getById(connection.from.id).removeData();
			paper[activeObj].getById(connection.to.id).removeData();
			removeElement(shape.id);
		}
		$('svg>text.connection.delete-element').remove();
	};

	/**
	  * @desc .
	  * @param string $id - .
	*/
	removeElement = function(id) {
		if(typeof id != 'undefined' && paper[activeObj].getById(id) != null && typeof paper[activeObj].getById(id) != 'undefined') {
			paper[activeObj].getById(id).remove();
		}
	};

	/**
	  * @desc .
	  * @param object $shapeID - .
	*/
	removeShape = function(shapeId) {
		var obj = paper[activeObj].getById(shapeId);
		for(var i = shapeSets[shapeId].items.length; i--;) {
			if(shapeSets[shapeId].items[i].type == 'circle') {
				if(typeof shapeSets[shapeId].items[i].data('input-line') != 'undefined' && shapeSets[shapeId].items[i].data('input-line') != null) {
					removeMultiElements(shapeSets[shapeId].items[i].data('input-line'));
					removeMultiElements(shapeSets[shapeId].items[i].data('input-path'));
				}
				if(typeof shapeSets[shapeId].items[i].data('output-line') != 'undefined' && shapeSets[shapeId].items[i].data('output-line') != null) {
					removeMultiElements(shapeSets[shapeId].items[i].data('output-line'));
					removeMultiElements(shapeSets[shapeId].items[i].data('output-path'));
				}
			}		
			shapeSets[shapeId].items[i].remove();
		}
		delete shapeSets[shapeId];
	};

	/**
	  * @desc .
	  * @param array $arr - .
	*/
	removeMultiElements = function(arr) {
		for(var i = arr.length; i--;) {
			removeElement(arr[i]);
		}
	};

	/**
	  * @desc .
	  * @param object $shape - .
	*/
	shapeSelect = function(shape) {
		currentShape = shape;
		//$('svg text.shape-icons:not(.task-input)').hide();
		if(shape.node.id != 'start' && shape.node.id != 'end' && ISEDITABLE) {
			$('svg [selected]').each(function(index, obj) {
				obj.removeAttribute('selected');
				obj.removeAttribute('animate-dash');
			});
			shape.node.setAttribute('selected', '');
			if(shape.type == 'path' && shape.node.className.baseVal != 'diamond' && shape.node.className.baseVal != 'triangle') {
				$('svg>text.connection.delete-element').remove();
				shape.node.setAttribute('animate-dash', '');
				addActionIcon(shape);
				return false;
			} else {
				$('svg>#' + shape.id).nextAll('text.shape-icons.clear-connections').first().show();
				$('svg>#' + shape.id).nextAll('text.shape-icons.delete-element').first().show();
			}
		}
	};

	/**
	  * @desc .
	  * @param object $shape - .
	*/
	addActionIcon = function(shape) {
		var x = parseInt(shape.attrs.path[0][1]) + 25,
		y = parseInt(shape.attrs.path[0][2]) + 5;
		var deleteIcon = addIcon(x, y, 'delete-element', '#E7604A', 'Delete Task');
		deleteIcon.node.setAttribute('style', 'display: block;');
		deleteIcon.node.setAttribute('class', 'connection delete-element shape-icons');
	};

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	addActionStatusIcons = function(shape, taskType) {
		var x, y, obj = {};
		if(shape.type == 'ellipse') {
			x = parseInt(shape.attrs.cx) + parseInt(shape.attrs.rx) + 10;
			y = parseInt(shape.attrs.cy) - parseInt(shape.attrs.ry) + 5;
		} else if(shape.type == 'rect') {
			x = parseInt(shape.attrs.x) + parseInt(shape.attrs.width) - 12;
			y = parseInt(shape.attrs.y) + 14;
		} else if(shape.type == 'path') {
			x = parseInt(shape.attrs.path[0][1]) + 25;
			y = parseInt(shape.attrs.path[0][2]) + 5;
		}
		if(taskType == 'wgroup') {
			obj.expandObj = addIcon(x, y, shape.id, 'task-expand', 'Expand Task');
			x -= 19;
			//y += 20;
		} else {
			obj.inputObj = addIcon(x, y, shape.id, 'task-input', 'Task Input');
		}
		if(ISEDITABLE) {
			obj.deleteObj = addIcon(x, y, shape.id, 'delete-element', 'Delete Task');
			x -= 19;
			//obj.clearObj = addIcon(x, y, shape.id, 'clear-connections', 'Clear Connections');
			//x -= 19;
		}
		//obj.inputObj = addIcon(x, y, shape.id, 'task-input', 'Task Input');
		//obj.inputSuccessObj = addIcon(x, y, shape.id, 'task-success-input', 'Success');
		return obj;
	};

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	addIcon = function(x, y, id, icon, title) {
		var obj = paper[activeObj].text(x, y, fontIconList[icon].icon);
		obj.attr('font-size', fontIconList[icon].font);
		obj.attr('fill', fontIconList[icon].color);
		obj.attr('font-family','FontAwesome');
		obj.node.setAttribute('class', 'icon_' + id + ' shape-icons ' + icon);
		tippy(obj.node, {arrow: true, content: title});
		return obj;
	};

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	highlightPorts = function(port) {
		unHighlightPorts();
		port.node.setAttribute('selected', '');
		var source_id = port.node.id.replace('s_out_', '');

		source_id = source_id.replace('f_out_', '');
		$('svg [type="input"]').each(function(index, obj) {
			obj.removeAttribute('blink');
			if(source_id != obj.id.replace('input_', ''))
				obj.setAttribute('blink', '');
		});
	};

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	unHighlightPorts = function() {
		$('svg [selected]').each(function(index, obj) {
			obj.removeAttribute('selected');
		});
	};

	/**
	  * @desc it will take a array of objects, remove the duplicate object based on the given attribute.
	  * @param array $array - the initial array of objects with duplicate entries.
	  * @param string $field - attribute name by which attribute to check the duplicate entry.
	  * @return array - unique array of objects(attribute based).
	*/
	addForiegnObject = function(jobId, shapeID, tstatus) {
		var progressObj;
		$('foreignObject.exec_' + shapeID).remove();
		removeElement('exec_' + shapeID);
		removeElement('task_status_' + shapeID);
		var shape = paper[activeObj].getById(shapeID);
		if(shape != null) {
			if(typeof colorCodes[tstatus + '-fill'] != 'undefined')
				shape.node.setAttribute('style', 'fill: ' + colorCodes[tstatus + '-fill']);
			if(tstatus == 'EXECUTING') {
				shape.attr({"fill-opacity": 0.5, "stroke-width": 0});
				shape.animate({"fill-opacity": 1}, 500);
				tstatus += '...';
				var foreignObject = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject');
				var body = document.createElement('body');
				$(foreignObject).attr('class', jobId + ' exec_' + shapeID).attr("x", parseInt(shape.attrs.x) + 50).attr("y", parseInt(shape.attrs.y) + 8).attr("width", 140).attr("height", 20).append(body);
				$(body).append('<div class="loader-gif green" alt="' + localization['executing'] + '" title="' + localization['executing'] + '"></div>');
				$('#' + jobId + ' > svg').append(foreignObject);
				if(!paper[activeObj].getById('progress_' + shapeID)) {
					//progressObj = paper[activeObj].image('images/loader-orange.gif', parseInt(shape.attrs.x) + 64, parseInt(shape.attrs.y) + 6, 124, 12);
					//progressObj.id = 'progress_' + shapeID;
				}
			} else {
				removeElement('progress_' + shapeID);
			}
			if(tstatus == 'Pending') tstatus = localization['yet-start'];
			var labelObj = paper[activeObj].text(parseInt(shape.attrs.x) + 210, parseInt(shape.attrs.y) + 40, tstatus).attr({fill: '#FFF', "font-size": "8", "letter-spacing": "0.4"});
			labelObj.id = 'task_status_' + shapeID;
			labelObj.node.id = 'task_status_' + shapeID;
			labelObj.node.setAttribute('class', 'task_status');
			shapeSets[shapeID].undrag();
			//shapeSets[shapeID].push(progressObj, labelObj);
		}
	};
});
