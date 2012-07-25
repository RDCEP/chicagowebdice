(function($) {
	var niceColors = [
		[ 204, 0, 0 ], [ 241, 194, 50 ], [106, 168, 79], [ 61, 133, 198 ], [ 103, 78, 167 ], [ 166, 77, 121 ],
		[ 230, 155, 56 ], [ 69, 129, 142 ], [ 60, 120, 216 ]
	]
	
	var numberOfStepsInSimulation = 60;
	var startYear = 2005;
	var endYear = 2200;
	var colorsUsed = parseInt(Math.random() * niceColors.length);
	var numberOfRunsInProgress = 0;
	
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
	
	var initializeTrivialTabsUI = function() {
		$('.tabs').each(function() {
			var currentlySelectedLink = $(this).find('a.selected')[0]
			var currentlySelectedTabID = (currentlySelectedLink.getAttribute('id') || '').substring(8);
			var currentlySelectedTab = document.getElementById(currentlySelectedTabID);
			
			$(this).find('a').each(function() {
				var tabID = (this.getAttribute('id') || '').substring(8);
				var tabElement = document.getElementById(tabID);
				
				this.onclick = function() {
					if (currentlySelectedLink)
						currentlySelectedLink.setAttribute('class', '');
					if (currentlySelectedTab)
						currentlySelectedTab.setAttribute('class', 'tab notselected');
					
					currentlySelectedLink = this;
					currentlySelectedTab = tabElement;
					
					if (currentlySelectedLink)
						currentlySelectedLink.setAttribute('class', 'selected');
					if (currentlySelectedTab)
						currentlySelectedTab.setAttribute('class', 'tab selected');
					
					return false;
				}
				
			});	
		});
	}
	
	var initializeUI = function() {
		var contentDiv = document.getElementById('content');
		var fourGraphsDiv = document.getElementById('four-graphs');
		var runsUL = document.getElementById('runs');
		var submissionDiv = document.getElementById('submission');
		var overlayDiv = document.getElementById('overlay');
		var advancedHelpDiv = document.getElementById('advanced-help');
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
			return (index / (numberOfStepsInSimulation - 1)) * (endYear - startYear) + startYear;
		}
		
		var formatColumnOfDataTable = function(table, columnID, format, unit) {
			var options = { };
			
			if (format !== undefined)
				options.pattern = format;
			
			if (unit !== undefined)
				options.suffix = ' ' + unit;
			
			var formatter = new google.visualization.NumberFormat(options);
			
			formatter.format(table, columnID);
		}
		
		var formatMeasurement = function(runIndex, measurement, format, unit) {
			var columnID = runIndex * getNumberOfMeasurements() + measurement + 1;
			
			return formatColumnOfDataTable(data, columnID, format, unit);
		}
		
		var addRun = function(description, color, fields, changesFromDefault) {
			var nextRun = getNumberOfRuns();
			
			for (var i = 0; i < Options.measurements.length; i++) {
				var measurement = Options.measurements[i];
				
				data.addColumn('number', measurement.name);
				
				var format = measurement.format;
				var unit = measurement.unit;
				var dataArray = fields[measurement.machine_name];
				
				for (var j = 0; j < numberOfStepsInSimulation; j++) {
					if (dataArray)
						var value = parseFloat(dataArray[j]);
					else
						var value = null;
					
					data.setCell(j, getNumberOfMeasurements() * nextRun + i + 1, value);
				}
				
				formatMeasurement(nextRun, i, measurement.format, unit);
			}
			
			var runObject =  { description : description, color : color,
			                   visible : true, index : nextRun,
			                   changesFromDefault : changesFromDefault };
			runsBeingDisplayed.push(runObject);
			
			updateAllData();
			
			return runObject;
		}
		
		var addRunFromCSV = function(description, color, result, changesFromDefault) {
			var fields = new Object;
			var lines = result.split('\n');
			
			for (var i = 0; i < lines.length; i++) {
				var line = lines[i].split(" ");
				var name = line[0].trim();
				
				if (name.length > 0)
					fields[name] = line.slice(1);
			}
			
			return addRun(description, color, fields, changesFromDefault);
		}
		
		var removeRun = function(index) {
			data.removeColumns(index * getNumberOfMeasurements() + 1, getNumberOfMeasurements());
			
			runsBeingDisplayed.splice(index, 1);
			
			for (var i = 0; i < runsBeingDisplayed.length; i++) {
				runs[i].index = i;
			}
			
			updateAllData();
		}
		
		var removeAllRuns = function() {
			data.removeColumns(1, getNumberOfRuns() * getNumberOfMeasurements());
			
			colorsUsed = parseInt(Math.random() * niceColors.length);
			
			runsBeingDisplayed.splice(0, runsBeingDisplayed.length);
			
			updateAllData();
		}
		
		var buildChart = function(index, measurement) {
			var div = document.createElement("div");
			div.setAttribute('class', 'graph');
			fourGraphsDiv.appendChild(div);
			
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
					height : (contentDiv.offsetHeight - 30) / 2.05,
					hAxis : { format : '####', title : 'year' },
					vAxis : { title : measurement.unit },
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
		
		var buildCustomizeableChart = function() {
			var div = document.getElementById('large-graph');
			var selectXAxis = document.getElementById('select-x-axis');
			var selectYAxis = document.getElementById('select-y-axis');
			var checkedLogarithmicX = document.getElementById('logarithmic-x');
			var checkedLogarithmicY = document.getElementById('logarithmic-y');
			var selectLabelsType = document.getElementById('series-labels');
			var previousXAxis = selectXAxis.value;
			
			var chart = new google.visualization.LineChart(div);
			var table = null;
			
			var updateViewport = function() {
				var colors = [ ];
				
				for (var j = 0; j < getNumberOfRuns(); j++) {
					if (runsBeingDisplayed[j].visible)
						colors.push(runsBeingDisplayed[j].color);
				}
				
				var selectedXOption = $(selectXAxis).find('option:selected').text();
				var selectedYOption = $(selectYAxis).find('option:selected').text();
				
				var options = {
					title : (selectedYOption + ' vs. ' + selectedXOption),
					width : contentDiv.offsetWidth,
					height : contentDiv.offsetHeight - 120,
					legend : {'position' : 'none' },
					colors : colors,
					pointSize : 2,
					hAxis : { title : selectedXOption, logScale : !!checkedLogarithmicX.checked },
					vAxis : { title : selectedYOption, logScale : !!checkedLogarithmicY.checked }
				};
				
				if (selectXAxis.value == 'year') {
					options.hAxis.format = '####';
					selectLabelsType.disabled = 'disabled';
					selectLabelsType.value = 'none';
				} else {
					selectLabelsType.disabled = false;
				}
				
				chart.draw(table, options);
			}
			
			var updateData = function() {
				var visibleColumns = [ ];
				var index = -1;
				
				var XAxis = selectXAxis.value;
				var YAxis = selectYAxis.value;
				var isTimeSeriesData = (XAxis == 'year')
				
				var XMeasurementIndex = null, XMeasurement = null, XLabel = null;
				var YMeasurementIndex = null, YMeasurement = null;
				
				if (isTimeSeriesData) {
					XLabel = "Time";
				} else {
					for (var i = 0; i < Options.measurements.length; i++) {
						if (Options.measurements[i].machine_name == XAxis) {
							XMeasurementIndex = i;
							XMeasurement = Options.measurements[i];
						}
					}
				}
				
				for (var i = 0; i < Options.measurements.length; i++) {
					if (Options.measurements[i].machine_name == YAxis) {
						YMeasurementIndex = i;
						YMeasurement = Options.measurements[i];
					}
				}
				
				var dataLiteral = {
					cols : [{ label : XLabel, type: 'number' }],
					rows : [ ]
				};
				
				var numberOfColumnsInNewTable = 1;
				
				for (var i = 0; i < getNumberOfRuns(); i++) {
					if (runsBeingDisplayed[i].visible)
						numberOfColumnsInNewTable += 3;
				}
				
				for (var i = 0; i < getNumberOfRuns(); i++) {
					if (!runsBeingDisplayed[i].visible)
						continue;
					
					var newRowColumnIndex = dataLiteral.cols.length;
					
					dataLiteral.cols.push({ label : YMeasurement.name, type: 'number' });
					dataLiteral.cols.push({ type : 'string', role : 'tooltip', p : { role : 'tooltip' } });
					dataLiteral.cols.push({ type : 'string', role : 'annotation', p : { role : 'annotation' } });
					
					if (isTimeSeriesData)
						var columnX = 0;
					else
						var columnX = i * getNumberOfMeasurements() + XMeasurementIndex + 1;
					var columnY = i * getNumberOfMeasurements() + YMeasurementIndex + 1;
					
					for (var j = 0; j < numberOfStepsInSimulation; j++) {
						var rows = [ ];
						var y = parseInt(mapIndexToYear(j));
						var isPossibleYear = (j == 0 || ((j % 20) == 0) || j == 59)
						var displayYearLabels = isPossibleYear && (selectLabelsType.value == 'years');
						
						if (isTimeSeriesData)
							var tooltip = (
								runsBeingDisplayed[i].description + "\n" +
								"Year: " + y + "\n" +
								YMeasurement.name + ": " + data.getFormattedValue(j, columnY)
							);
						else
							var tooltip = (
								runsBeingDisplayed[i].description + "\n" +
								"Year: " + y + "\n" +
								XMeasurement.name + ": " + data.getFormattedValue(j, columnX) + "\n" +
								YMeasurement.name + ": " + data.getFormattedValue(j, columnY)
							);
						
						for (var k = 0; k < numberOfColumnsInNewTable; k++) {
							if (k == newRowColumnIndex)
								rows[k] = { v : data.getValue(j, columnY) };
							else if (k == (newRowColumnIndex + 1))
								rows[k] = { v : tooltip, f : tooltip };
							else if (k == (newRowColumnIndex + 2) && displayYearLabels)
								rows[k] = { v : y };
							else if (k == 0)
								rows[k] = { v : data.getValue(j, columnX) };
							else
								rows[k] = null;
						}
						
						dataLiteral.rows.push({
							c : rows
						});
					}
				}
				
				var view = table = new google.visualization.DataTable(dataLiteral);
				
				for (var k = 0; k < numberOfColumnsInNewTable; k++) {
					if (k == 0 && isTimeSeriesData) {
						
						formatColumnOfDataTable(table, 0, '####', null);
						
					} else {
						if (k == 0)
							var measurement = XMeasurement;
						else
							var measurement = YMeasurement;
						
						formatColumnOfDataTable(table, k, measurement.format, measurement.unit);
					}
				}
				
				updateViewport();
			}
			
			selectXAxis.onchange = function() {
				checkedLogarithmicX.checked = false;
				
				if (previousXAxis == 'year')
					selectLabelsType.value = 'years';
				
				previousXAxis = selectXAxis.value;
				
				updateAllData();
			}
			
			selectYAxis.onchange = function() {
				checkedLogarithmicY.checked = false;
				
				updateAllData();
			}
			
			checkedLogarithmicX.onchange = function() {
				updateAllViewports();
			}
			
			checkedLogarithmicY.onchange = function() {
				updateAllViewports();
			}
			
			selectLabelsType.onchange = function() {
				updateAllData();
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
			var bottomHeight = (runsBeingDisplayed.length + numberOfRunsInProgress) * 51;
			var outerHeight = bottomHeight;
			
			if (outerHeight > 200) outerHeight = 200;
			
			$(submissionDiv).animate({ bottom: outerHeight }, "slow");
			$(runsUL).animate({ height:outerHeight, scrollTop : (bottomHeight - outerHeight) }, "slow");
		}
		
		var setVisibilityOfOverlay = function(visible) {
			if (visible) {
				var overlayVisibility = 1.0;
				var advancedHelpOffset = 0;
				var overlayDisplay = 'block';
			} else {
				var overlayVisibility = 0.0;
				var advancedHelpOffset = 200;
				var overlayDisplay = 'none';
			}
			
			$(overlayDiv).css({ display : 'block' }).animate({ opacity : overlayVisibility }, function() {
				$(overlayDiv).css({ display : overlayDisplay });
			});
			$(advancedHelpDiv).animate({ top : advancedHelpOffset });
		}
		
		// Prepare initial contents of dataset.
		
		data.addColumn('number', 'Year');
		
		for (var i = 0; i < numberOfStepsInSimulation; i++) {
			data.addRow([ mapIndexToYear(i) ]);
		}
		
		formatMeasurement(0, -1, "####"); // hackish much?
		
		for (var i = 0; i < Options.locations.length; i++) {
			var location = Options.locations[i];
			
			for (var j = 0; j < Options.measurements.length; j++) {
				var measurement = Options.measurements[j];
				
				if (measurement.location == location)
					buildChart(j, measurement);
			}
		}
		
		var helpButton = document.getElementById('display-help');
		helpButton.onclick = function() {
			setVisibilityOfOverlay(true);
			
			return false;
		}
		
		var hideHelpButton = document.getElementById('hide-help');
		hideHelpButton.onclick = function() {
			setVisibilityOfOverlay(false);
			
			return false;
		}
		
		var deleteAllButton = document.getElementById('delete-all');
		deleteAllButton.onclick = function() {
			for (var i = 0; i < runsBeingDisplayed.length; i++)
				runsUL.removeChild(runsUL.firstChild);
			
			removeAllRuns();
			
			updateRunsListHeight();
			
			return false;
		}

		var runOptimizationButton = document.getElementById('run-opt');
		runOptimizationButton.onclick = function() {
			//code to come later
			//run dice optimization
			return false;
		}
		
		var downloadTextarea = document.getElementById('download-textarea');
		var updateDownloadedText = function() {
			downloadTextarea.value = 'Approximate Year';
			var downloadData = data;
			var unselectedCols = new Array();
			
			for (var i = 0; i < getNumberOfRuns(); i++) {
				var run = runsBeingDisplayed[i];
				if(run.visible){
					for (var j = 0; j < getNumberOfMeasurements(); j++) {
					
							var measurement = Options.measurements[j];

							var columnValue = run.description + ' / ' + measurement.name + ' (' + measurement.unit + ')';

							downloadTextarea.value += ',' + columnValue;

					} 
				} else {
					unselectedCols.push(i*5 + 1);
					unselectedCols.push(i*5 + 2);
					unselectedCols.push(i*5 + 3);
					unselectedCols.push(i*5 + 4);
					unselectedCols.push(i*5 + 5);
				}
			}
			
			downloadTextarea.value += '\n';
			
			for (var y = 0; y < numberOfStepsInSimulation; y++) {
				downloadTextarea.value += downloadData.getValue(y, 0);
				
				for (var i = 1; i < downloadData.getNumberOfColumns(); i++) {
					if(unselectedCols.indexOf(i) == -1){
						downloadTextarea.value += ',' + downloadData.getValue(y, i);
					}
				}
				
				downloadTextarea.value += '\n';
			}
		}
		handlersForDataChanged.push(updateDownloadedText);
		
		buildCustomizeableChart();
		initializeTrivialTabsUI();
		
		var displayConditionalHelp = function() {
			var numberVisible = 0;
			
			for (var j = 0; j < getNumberOfRuns(); j++) {
				if (runsBeingDisplayed[j].visible)
					numberVisible++;
			}
			
			if (numberVisible > 0)
				contentDiv.setAttribute('class', 'hasruns');
			else
				contentDiv.setAttribute('class', 'hasnoruns');
			
			deleteAllButton.disabled = (numberVisible == 0);
		}
		
		handlersForViewportChanged.push(displayConditionalHelp);
		handlersForDataChanged.push(displayConditionalHelp);


		
		var form = document.getElementById('submission');
		form.onsubmit = function() {
			var data = $(form).serialize();
			var changes = [ ];
			
			$(form).find('input[type!=submit][type!=reset],select').each(function() {
				if (this.tagName.toLowerCase() == 'select') {
					var defaultValue = $(this).find('option').first().val().trim()
					var changedValue = $(this).find('option:checked').first().val().trim()
					var areEqual = (defaultValue == changedValue);
					var deviation = (areEqual ? 0 : 0.10); // 25% deviation.
				} else {
					var defaultValue = this.defaultValue;
					var changedValue = this.value;
					var areEqual = (parseFloat(defaultValue) == parseFloat(changedValue));
					var deviation = Math.abs(Math.log(parseFloat(changedValue) / parseFloat(defaultValue)));
				}
				
				if (!areEqual) {
					var description = this.parentNode.firstChild.nodeValue.trim();
					var heading = $(this.parentNode.parentNode.parentNode).prev('h2').first().text();
					
					changes.push([ heading, description, changedValue, defaultValue, deviation ]);
				};
			});
			
			changes.sort(function(a, b) { return b[4] - a[4]; });
			
			var runTextualDescription = "Run Parameters:";
			
			for (var i = 0; i < changes.length; i++) {
				var change = changes[i];
				
				runTextualDescription += "\n[" + change[0] + "] " + change[1] + ": " + change[2];
			}
			
			if (changes.length == 0)
				runTextualDescription += " (default parameters)";
			
			var createdLI = document.createElement('li');
			var createdLABEL = document.createElement('label');
			var progressIMG = document.createElement('img');
			var textNode = document.createTextNode("Executing run...");
			
			createdLI.setAttribute('title', runTextualDescription);
			
			progressIMG.setAttribute('src', 'images/progress.gif');
			createdLI.appendChild(createdLABEL);
			createdLABEL.appendChild(textNode);
			createdLABEL.appendChild(progressIMG);
			runsUL.appendChild(createdLI);
			
			numberOfRunsInProgress++;
			
			updateRunsListHeight();
			
			$.ajax({
				type : 'POST',
				url : 'index.php',
				data : data,
				success : function(data, textStatus, xhr) {
					var runObject = addRunFromCSV("Run #" + (getNumberOfRuns() + 1),
						generateNextColor(), data, changes);
					
					numberOfRunsInProgress--;
					
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
					
					$(createdLABEL).css({backgroundColor:'#fe0'});
					
					setTimeout(function() {
						numberOfRunsInProgress--;
						
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
			//var s = Math.ceil(Math.log(parseFloat(this.value)));
			//if (!(s > s) && !(s < s)) s = 1;
			
			//var offset = Math.pow(10, 3 - s);
			//var value = parseInt(parseFloat(this.value) * offset) / offset;
			var value = (parseFloat(this.value)).toFixed(this.data-precision);
			
			$(this).parents('label').find('span.label').text(value);
		});
		
		$('#reset-inputs').click(function(e) {
			e.preventDefault();
			form.reset();
			$('input[type=range]', form).change();
		});
		
		window.onresize = function() {
			updateAllViewports();
		}
	}
	
	google.load('visualization', '1.0', {'packages' : ['corechart']});
	google.setOnLoadCallback(initializeUI);
})(jQuery);