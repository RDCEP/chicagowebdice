(function($) {
	var numberOfStepsInSimulation = 60;
	var startYear = 2005;
	var endYear = 2200;
	var colorsUsed = 0;
	var numberOfRunsInProgress = 0;
	
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
				
				formatMeasurement(nextRun, i, measurement.format, unit);
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
			data.removeColumns(index * getNumberOfMeasurements() + 1, getNumberOfMeasurements());
			
			runsBeingDisplayed.splice(index, 1);
			
			for (var i = 0; i < runsBeingDisplayed.length; i++) {
				runs[i].index = i;
			}
			
			updateAllData();
		}
		
		var removeAllRuns = function() {
			data.removeColumns(1, getNumberOfRuns() * getNumberOfMeasurements());
			
			colorsUsed = 0;
			
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
		
		for (var i = 0; i < Options.measurements.length; i++) {
			buildChart(i, Options.measurements[i]);
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
		
		var downloadTextarea = document.getElementById('download-textarea');
		var updateDownloadedText = function() {
			downloadTextarea.value = 'Approximate Year';
			
			for (var i = 0; i < getNumberOfRuns(); i++) {
				for (var j = 0; j < getNumberOfMeasurements(); j++) {
					var run = runsBeingDisplayed[i];
					var measurement = Options.measurements[j];
					
					var columnValue = run.description + ' / ' + measurement.name;
					
					downloadTextarea.value += ',' + columnValue;
				}
			}
			
			downloadTextarea.value += '\n';
			
			for (var y = 0; y < numberOfStepsInSimulation; y++) {
				downloadTextarea.value += data.getValue(y, 0);
				
				for (var i = 1; i < data.getNumberOfColumns(); i++) {
					downloadTextarea.value += ',' + data.getValue(y, i);
				}
				
				downloadTextarea.value += '\n';
			}
		}
		handlersForDataChanged.push(updateDownloadedText);
		
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
			
			$(form).find('input[type!=submit],select').each(function() {
				if (this.tagName.toLowerCase() == 'select') {
					var defaultValue = $(this).find('option').first().val().trim()
					var changedValue = $(this).find('option:checked').first().val().trim()
					var areEqual = (defaultValue == changedValue);
				} else {
					var defaultValue = this.defaultValue;
					var changedValue = this.value;
					var areEqual = (parseFloat(defaultValue) == parseFloat(changedValue));
				}
				
				if (!areEqual) {
					var description = this.parentNode.firstChild.nodeValue.trim();
					var heading = $(this.parentNode.parentNode.parentNode).prev('h2').first().text();
					
					changes.push([ '[' + heading + '] ' + description, changedValue ]);
				};
			});
			
			var runTextualDescription = "Run Parameters:";
			
			for (var i = 0; i < changes.length; i++) {
				var change = changes[i];
				
				runTextualDescription += "\n" + change[0] + ": " + change[1];
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
			createdLABEL.appendChild(progressIMG);
			createdLABEL.appendChild(textNode);
			runsUL.appendChild(createdLI);
			
			numberOfRunsInProgress++;
			
			updateRunsListHeight();
			
			$.ajax({
				type : 'POST',
				url : 'index.php',
				data : data,
				success : function(data, textStatus, xhr) {
					var runObject = addRunFromCSV("Run #" + (colorsUsed + 1), generateNextColor(), data);
					
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