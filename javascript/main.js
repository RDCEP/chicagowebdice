(function($) {
	var numberOfStepsInSimulation = 60;
	var startYear = 2005;
	var endYear = 2200;
	var colorsUsed = 0;
	var sampleData = {
"emissionsTotal":[87.972,97.4694,107.3874,117.5434,127.9259,138.6092,149.7031,161.327,173.5988,186.6307,200.5293,215.3959,231.3355,248.4487,266.8345,286.5923,307.8236,330.6331,355.1294,381.426,409.6416,439.9006,472.3341,507.0793,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
		"massAtmosphere":[808.9,865.7592,923.846,984.0294,1046.7543,1112.32,1181.0093,1253.1377,1329.0655,1409.1958,1493.969,1583.8566,1679.3575,1781.0031,1889.3525,2004.9914,2128.5333,2260.6209,2401.9292,2553.1677,2715.0831,2888.4629,3074.1371,3272.9821,3485.9224,3169.6534,2932.7024,2751.4072,2609.3204,2495.0039,2400.498,2320.2588,2250.4199,2188.2803,2131.9485,2080.0957,2031.7843,1986.3486,1943.3124,1902.3314,1863.1533,1825.5904,1789.4999,1754.7708,1721.3146,1689.0587,1657.942,1627.9117,1598.9212,1570.9283,1543.8946,1517.7842,1492.5636,1468.201,1444.6664,1421.9307,1399.9665,1378.7473,1358.2475,1338.4426],
		"tempAtmosphere":[0.7307,0.93217,1.1528,1.3844,1.6221,1.8632,2.1061,2.3499,2.5944,2.8394,3.0851,3.3239,3.5587,3.7915,4.0238,4.2565,4.4903,4.7256,4.9627,5.2017,5.4429,5.6861,5.9316,6.1791,6.4288,6.4893,6.4471,6.354,6.2398,6.1208,6.0053,5.8968,5.7963,5.7033,5.6169,5.536,5.4595,5.3864,5.316,5.2476,5.1807,5.1149,5.05,4.9858,4.9222,4.8591,4.7964,4.734,4.6721,4.6105,4.5494,4.4886,4.4283,4.3685,4.3091,4.2503,4.192,4.1342,4.0771,4.0205],
		"consumptionpercapita":[6.6805,7.6168,8.7525,10.0641,11.5486,13.2146,15.0766,17.1532,19.4657,22.0376,24.8941,28.0663,31.5843,35.48,39.7866,44.5394,49.7752,55.5328,61.8527,68.7773,76.3508,84.6193,93.6306,103.4344,114.0819,126.428,140.5904,156.6279,174.593,194.5553,216.6109,240.884,267.5263,296.7147,328.649,363.5501,401.6585,443.2336,488.5533,537.9138,591.63,650.0358,713.4846,782.3504,857.0279,937.9338,1025.5073,1120.2109,1222.5314,1332.9805,1452.0959,1580.4416,1718.6091,1867.2178,2026.916,2198.3818,2382.323,2579.4786,2790.6191,3016.547]
	};
	
	var niceColors = [
		[ 204, 0, 0 ], [ 241, 194, 50 ], [106, 168, 79], [ 61, 133, 198 ], [ 103, 78, 167 ], [ 166, 77, 121 ],
		[ 230, 155, 56 ], [ 69, 129, 142 ], [ 60, 120, 216 ]
	]
	
	var generateNextColor = function() {
		var nextColor = niceColors[(colorsUsed++) % niceColors.length];
		var rgb = [ nextColor[0], nextColor[1], nextColor[2] ];
		
		var color = ("#" +
			(0xF00 + rgb[0]).toString(16).substring(1) +
			(0xF00 + rgb[1]).toString(16).substring(1) +
			(0xF00 + rgb[2]).toString(16).substring(1)
		);
		
		return color;
	}
	
	var darkenColorSlightly = function(c) {
		var n = parseInt(c.substring(1), 16);
		var rgb = [ (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff ];
		
		if (rgb[0] < 0x20) rgb[0] = 0x20;
		rgb[0] -= 0x20;
		
		if (rgb[1] < 0x20) rgb[1] = 0x20;
		rgb[1] -= 0x20;
		
		if (rgb[2] < 0x20) rgb[2] = 0x20;
		rgb[2] -= 0x20;
		
		var color = "#" + (0xFF000000 + (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]).toString(16).substring(2);
		
		return color;
	}
	
	var initializeUI = function() {
		var contentDiv = document.getElementById('content');
		var runsUL = document.getElementById('runs');
		var submissionDiv = document.getElementById('submission');
		var runsBeingDisplayed = [ ];
		var nextRunNumber = 1;
		
		var charts = [ ];
		var handlersForViewportChanged = [ ];
		var handlersForDataChanged = [ ];
		var data = new google.visualization.DataTable();
		  // Measurement `m' of `M' for run `r' is is located at (r * M + m + 1)
		
		var getNumberOfMeasurements = function() {
			return Options.measurements.length;
		}
		
		var getNumberOfRuns = function() {
			return (data.getNumberOfColumns() - 1) / getNumberOfMeasurements();
		}
		
		var mapIndexToYear = function(index) {
			return (index / numberOfStepsInSimulation) * (endYear - startYear) + startYear;
		}
		
		var formatMeasurement = function(runIndex, measurement, format, unit) {
			var columnId = runIndex * getNumberOfMeasurements() + measurement + 1;
			
			var options = { };
			
			if (format !== undefined)
				options.pattern = format;
			
			if (unit !== undefined)
				options.suffix = ' ' + unit;
			
			var formatter = new google.visualization.NumberFormat(options);
			
			formatter.format(data, columnId);
		}
		
		var addRun = function(description, color, fields) {
			var nextRun = getNumberOfRuns();
			
			for (var i = 0; i < Options.measurements.length; i++) {
				var measurement = Options.measurements[i];
				
				data.addColumn('number', measurement.name);
				
				var format = measurement.format;
				var unit = measurement.unit;
				var dataArray = fields[measurement.machine_name];
				
				for (var j = 0; j < numberOfStepsInSimulation; j++) {
					var value = parseFloat(dataArray[j]);
					
					data.setCell(j, getNumberOfMeasurements() * nextRun + i + 1, value);
				}
				
				formatMeasurement(nextRun, i, measurement.format, unit, color);
			}
			
			var runObject =  { description : description, color : color,
			                   visible : true, index : nextRun };
			runsBeingDisplayed.push(runObject);
			
			updateAllData();
			
			return runObject;
		}
		
		var addRunFromCSV = function(description, color, result) {
			var fields = new Object;
			var lines = result.split('\n');
			
			for (var i = 0; i < lines.length; i++) {
				var line = lines[i].split(" ");
				var name = line[0].trim();
				
				if (name.length > 0)
					fields[name] = line.slice(1);
			}
			
			return addRun(description, color, fields);
		}
		
		var removeRun = function(index) {
			data.removeColumns(index * getNumberOfMeasurements(), getNumberOfMeasurements());
			
			runsBeingDisplayed.splice(index, 1);
			
			for (var i = 0; i < runsBeingDisplayed.length; i++) {
				runs[i].index = i;
			}
			
			updateAllData();
		}
		
		var buildChart = function(index, measurement) {
			var div = document.createElement("div");
			contentDiv.appendChild(div);
			
			var chart = new google.visualization.LineChart(div);
			var view = new google.visualization.DataView(data);
			
			var updateViewport = function() {
				var colors = [ ];
				
				for (var j = 0; j < getNumberOfRuns(); j++) {
					if (runsBeingDisplayed[j].visible)
						colors.push(runsBeingDisplayed[j].color);
				}
				
				var options = {
					title : measurement.name,
					width : contentDiv.offsetWidth / 2.05,
					height : contentDiv.offsetHeight / 2.05,
					hAxis : { format : '####' },
					legend : {'position' : 'none' },
					colors : colors
				};
				
				chart.draw(view, options);
			}
			
			var updateData = function() {
				var visibleColumns = [ ];
				
				for (var j = 0; j < data.getNumberOfColumns(); j++) {
					var measurementID = (j - 1) % getNumberOfMeasurements();
					var runID = parseInt((j - 1) / getNumberOfMeasurements());
					
					if ((j == 0) || (measurementID == index && runsBeingDisplayed[runID].visible))
						visibleColumns.push(j);
				}
				
				view.setColumns(visibleColumns);
				
				updateViewport();
			}
			
			updateData();
			handlersForViewportChanged.push(updateViewport);
			handlersForDataChanged.push(updateData);
		}
		
		var updateAllViewports = function() {
			for (var i = 0; i < handlersForViewportChanged.length; i++) {
				handlersForViewportChanged[i]();
			}
		}
		
		var updateAllData = function() {
			for (var i = 0; i < handlersForDataChanged.length; i++) {
				handlersForDataChanged[i]();
			}
		}
		
		var updateRunsListHeight = function() {
			var bottomHeight = (runsBeingDisplayed.length + 1) * 51;
			var outerHeight = bottomHeight;
			
			if (outerHeight > 200) outerHeight = 200;
			
			$(submissionDiv).animate({ bottom: outerHeight }, "slow");
			$(runsUL).animate({ height:outerHeight, scrollTop : (bottomHeight - outerHeight) }, "slow");
		}
		
		// Prepare initial contents of dataset.
		
		data.addColumn('number', 'Year');
		
		for (var i = 0; i < numberOfStepsInSimulation; i++) {
			data.addRow([ mapIndexToYear(i) ]);
		}
		
		formatMeasurement(0, -1, "####"); // hackish much?
		
		addRun("Default Run", generateNextColor(), sampleData);
		
		for (var i = 0; i < Options.measurements.length; i++) {
			buildChart(i, Options.measurements[i]);
		}
		
		var form = document.getElementById('submission');
		form.onsubmit = function() {
			var data = $(form).serialize();
			
			var createdLI = document.createElement('li');
			var createdLABEL = document.createElement('label');
			var progressIMG = document.createElement('img');
			var textNode = document.createTextNode("Executing run...");
			
			progressIMG.setAttribute('src', 'images/progress.gif');
			createdLI.appendChild(createdLABEL);
			createdLABEL.appendChild(progressIMG);
			createdLABEL.appendChild(textNode);
			runsUL.appendChild(createdLI);
			
			updateRunsListHeight();
			
			$.ajax({
				type : 'POST',
				url : 'index.php',
				data : data,
				success : function(data, textStatus, xhr) {
					var runObject = addRunFromCSV("Run #" + getNumberOfRuns(), generateNextColor(), data);
					
					textNode.nodeValue = runObject.description;
					createdLABEL.removeChild(progressIMG);
					
					var visibilityCheckbox = document.createElement('input');
					visibilityCheckbox.setAttribute('type', 'checkbox');
					visibilityCheckbox.setAttribute('checked', 'checked');
					
					visibilityCheckbox.onchange = function() {
						runObject.visible = visibilityCheckbox.checked;
						updateAllData();
					}
					
					createdLABEL.appendChild(visibilityCheckbox);
					
					var colorSlab = document.createElement('span');
					colorSlab.style.backgroundColor = runObject.color;
					colorSlab.style.borderColor = darkenColorSlightly(runObject.color);
					colorSlab.setAttribute('class', 'slab');
					
					createdLABEL.appendChild(colorSlab);
				},
				error : function(xhr, textStatus, errorType) {
					textNode.nodeValue = "Model Run Failed!";
					createdLABEL.removeChild(progressIMG);
					runObject.removed = true;
					
					$(createdLABEL).css({backgroundColor:'#fe0'});
					
					setTimeout(function() {
						$(createdLI).remove();
						updateRunsListHeight();
					}, 5000);
				},
				dataType : 'text',
				timeout : 10000
			});
			
			return false;
		}
		
		$('input[type=range]', form).change(function() {
			var s = Math.ceil(Math.log(parseFloat(this.value)));
			if (!(s > s) && !(s < s)) s = 1;
			
			var offset = Math.pow(10, 3 - s);
			var value = parseInt(parseFloat(this.value) * offset) / offset;
			
			$(this).parents('label').find('span.label').text(value);
		});
		
		window.onresize = function() {
			updateAllViewports();
		}
	}
	
	google.load('visualization', '1.0', {'packages' : ['corechart']});
	google.setOnLoadCallback(initializeUI);
})(jQuery);