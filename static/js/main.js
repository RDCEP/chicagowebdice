(function($) {
  //This first bit is just color selection for the graphs
  var niceColors = [
    [ 204, 0, 0 ], [ 241, 194, 50 ], [106, 168, 79], [ 61, 133, 198 ], [ 103, 78, 167 ], [ 166, 77, 121 ],
    [ 230, 155, 56 ], [ 69, 129, 142 ], [ 60, 120, 216 ]
  ];

  var numberOfStepsInSimulation = 60,
    numberOfStepsInGraphs = 20,
    yearsInStep = 10,
    startYear = 2005,
    endYear = startYear + ((numberOfStepsInGraphs-1) * yearsInStep),
    colorsUsed = parseInt(Math.random() * niceColors.length),
    numberOfRunsInProgress = 0,
    color;

  var generateNextColor = function() {
    var nextColor = niceColors[(colorsUsed++) % niceColors.length];
    var rgb = [ nextColor[0], nextColor[1], nextColor[2] ];

    color = ("#" +
      (0xF00 + rgb[0]).toString(16).substring(1) +
      (0xF00 + rgb[1]).toString(16).substring(1) +
      (0xF00 + rgb[2]).toString(16).substring(1)
      );

    return color;
  };

  var darkenColorSlightly = function(c) {
    var n = parseInt(c.substring(1), 16);
    var rgb = [ (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff ];

    if (rgb[0] < 0x20) rgb[0] = 0x20;
    rgb[0] -= 0x20;

    if (rgb[1] < 0x20) rgb[1] = 0x20;
    rgb[1] -= 0x20;

    if (rgb[2] < 0x20) rgb[2] = 0x20;
    rgb[2] -= 0x20;

    color = "#" + (0xFF000000 + (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]).toString(16).substring(2);

    return color;
  };

  //This changes tabs when you click them by changing the css class. tab notselected is set to display:none, so only the selected tab shows.
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
  };

  var initializeUI = function() {
    var contentDiv = document.getElementById('content');
    var runsUL = document.getElementById('runs');
    var submissionDiv = document.getElementById('submission');
    var overlayDiv = document.getElementById('overlay');
    var advancedHelpDiv = document.getElementById('advanced-help');
    var sidebarDiv = document.getElementById('sidebar');
    var runsBeingDisplayed = [ ];
    var nextRunNumber = 1;
    var charts = [ ];
    var handlersForViewportChanged = [ ];
    var handlersForDataChanged = [ ];
    var data = new google.visualization.DataTable();
    // Measurement `m' of `M' for run `r' is is located at (r * M + m + 1)

    var getNumberOfMeasurements = function() {
      return Options.measurements.length;
    };

    var getNumberOfRuns = function() {
      return (data.getNumberOfColumns() - 1) / getNumberOfMeasurements();
    };

    var mapIndexToYear = function(index) {
      return (index / (numberOfStepsInGraphs - 1)) * (endYear - startYear) + startYear;
    };

    var formatColumnOfDataTable = function(table, columnID, format, unit) {
      var options = { };

      if (format !== undefined)
        options.pattern = format;

      if (unit !== undefined)
        options.suffix = ' ' + unit;

      var formatter = new google.visualization.NumberFormat(options);

      formatter.format(table, columnID);
    };

    var formatMeasurement = function(runIndex, measurement, format, unit) {
      var columnID = runIndex * getNumberOfMeasurements() + measurement + 1;

      return formatColumnOfDataTable(data, columnID, format, unit);
    };

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
    };

    var addRunFromCSV = function(description, color, result, changesFromDefault) {
      var fields = new Object;
      var lines = result.split('\n');

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i].split(" ").slice(0, numberOfStepsInSimulation+1);
        var name = line[0].trim();

        if (name.length > 0)
          fields[name] = line.slice(1);
      }

      return addRun(description, color, fields, changesFromDefault);
    };

    var removeRun = function(index) {
      data.removeColumns(index * getNumberOfMeasurements() + 1, getNumberOfMeasurements());

      runsBeingDisplayed.splice(index, 1);

      for (var i = 0; i < runsBeingDisplayed.length; i++) {
        runs[i].index = i;
      }

      updateAllData();
    };

    var removeAllRuns = function() {
      data.removeColumns(1, getNumberOfRuns() * getNumberOfMeasurements());

      colorsUsed = parseInt(Math.random() * niceColors.length);

      runsBeingDisplayed.splice(0, runsBeingDisplayed.length);

      updateAllData();
    };

    var buildChart = function(index, name, measurement) {
      var div = document.createElement("div");
      var fourGraphsDiv = document.getElementById(name+'-graphs');
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
      };

      var updateData = function() {
        var visibleColumns = [ ];

        for (var j = 0; j < data.getNumberOfColumns(); j++) {
          var measurementID = (j - 1) % getNumberOfMeasurements();
          var runID = parseInt((j - 1) / getNumberOfMeasurements());

          if ((j == 0) || (measurementID == index && runsBeingDisplayed[runID].visible))
            visibleColumns.push(j);
        }

        view.setColumns(visibleColumns);
        view.setRows(0,numberOfStepsInGraphs-1);
        updateViewport();
      };

      updateData();
      handlersForViewportChanged.push(updateViewport);
      handlersForDataChanged.push(updateData);
    };

    var buildLargeChart = function(option) {
      var div = document.getElementById(option+'-graph');
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

        var selectedXOption = $(selectXAxis).find('option[value=year]').text();
        var selectedYOption = $(selectYAxis).find('option[value='+option+']').text();

        var selectedXUnit = function() {
          var selectedXIndex = $(selectXAxis).find('option[value=year]').index('#select-x-axis option');
          if (selectedXIndex > 0) {
            var Unit = Options.measurements[selectedXIndex-1]['unit'];
            if (typeof Unit === 'undefined') {
              Unit = '';
            } else {
              Unit = '('+Unit+')';
            }
          } else {
            Unit = '';
          }
          return Unit;
        };
        var selectedYUnit = function() {
          var selectedYIndex = $(selectYAxis).find('option[value='+option+']').index('#select-y-axis option');
          var Unit = Options.measurements[selectedYIndex]['unit'];
          if (typeof Unit === 'undefined') {
            Unit = '';
          } else {
            Unit = '('+Unit+')';
          }
          return Unit;
        };

        var options = {
          title : (selectedYOption + ' vs. ' + selectedXOption),
          width : contentDiv.offsetWidth,
          //height : contentDiv.offsetHeight - 120,
          height : contentDiv.offsetHeight - 30,
          legend : {'position' : 'none' },
          colors : colors,
          pointSize : 2,
          hAxis : { title : selectedXOption + ' ' + selectedXUnit(), logScale : !!checkedLogarithmicX.checked },
          vAxis : { title : selectedYOption + ' ' + selectedYUnit(), logScale : !!checkedLogarithmicY.checked }
        };

        if (selectXAxis.value == 'year') {
          options.hAxis.format = '####';
          selectLabelsType.disabled = 'disabled';
          selectLabelsType.value = 'none';
        } else {
          selectLabelsType.disabled = false;
        }

        chart.draw(table, options);
      };

      var updateData = function() {
        var visibleColumns = [ ];
        var index = -1;

        var XAxis = 'year';
        var YAxis = option;
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

          for (var j = 0; j < numberOfStepsInGraphs; j++) {
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
      };

      selectXAxis.onchange = function() {
        checkedLogarithmicX.checked = false;

        if (previousXAxis == 'year')
          selectLabelsType.value = 'years';

        previousXAxis = selectXAxis.value;

        updateAllData();
      };

      selectYAxis.onchange = function() {
        checkedLogarithmicY.checked = false;

        updateAllData();
      };

      checkedLogarithmicX.onchange = function() {
        updateAllViewports();
      };

      checkedLogarithmicY.onchange = function() {
        updateAllViewports();
      };

      selectLabelsType.onchange = function() {
        updateAllData();
      };

      updateData();
      handlersForViewportChanged.push(updateViewport);
      handlersForDataChanged.push(updateData);
    };

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

        var selectedXUnit = function() {
          var selectedXIndex = $(selectXAxis).find('option:selected').index('#select-x-axis option');
          if (selectedXIndex > 0) {
            var Unit = Options.measurements[selectedXIndex-1]['unit'];
            if (typeof Unit === 'undefined') {
              Unit = '';
            } else {
              Unit = '('+Unit+')';
            }
          } else {
            Unit = '';
          }
          return Unit;
        };
        var selectedYUnit = function() {
          var selectedYIndex = $(selectYAxis).find('option:selected').index('#select-y-axis option');
          var Unit = Options.measurements[selectedYIndex]['unit'];
          if (typeof Unit === 'undefined') {
            Unit = '';
          } else {
            Unit = '('+Unit+')';
          }
          return Unit;
        };

        var options = {
          title : (selectedYOption + ' vs. ' + selectedXOption),
          width : contentDiv.offsetWidth,
          height : contentDiv.offsetHeight - 120,
          legend : {'position' : 'none' },
          colors : colors,
          pointSize : 2,
          hAxis : { title : selectedXOption + ' ' + selectedXUnit(), logScale : !!checkedLogarithmicX.checked },
          vAxis : { title : selectedYOption + ' ' + selectedYUnit(), logScale : !!checkedLogarithmicY.checked }
        };

        if (selectXAxis.value == 'year') {
          options.hAxis.format = '####';
          selectLabelsType.disabled = 'disabled';
          selectLabelsType.value = 'none';
        } else {
          selectLabelsType.disabled = false;
        }

        chart.draw(table, options);
      };

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

          for (var j = 0; j < numberOfStepsInGraphs; j++) {
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
      };

      selectXAxis.onchange = function() {
        checkedLogarithmicX.checked = false;

        if (previousXAxis == 'year')
          selectLabelsType.value = 'years';

        previousXAxis = selectXAxis.value;

        updateAllData();
      };

      selectYAxis.onchange = function() {
        checkedLogarithmicY.checked = false;

        updateAllData();
      };

      checkedLogarithmicX.onchange = function() {
        updateAllViewports();
      };

      checkedLogarithmicY.onchange = function() {
        updateAllViewports();
      };

      selectLabelsType.onchange = function() {
        updateAllData();
      };

      updateData();
      handlersForViewportChanged.push(updateViewport);
      handlersForDataChanged.push(updateData);
    };

    var updateAllViewports = function() {
      for (var i = 0; i < handlersForViewportChanged.length; i++) {
        handlersForViewportChanged[i]();
      }
    };

    var updateAllData = function() {
      for (var i = 0; i < handlersForDataChanged.length; i++) {
        handlersForDataChanged[i]();
      }
    };

    var updateRunsListHeight = function() {
      var bottomHeight = (runsBeingDisplayed.length + numberOfRunsInProgress) * 51;
      var outerHeight = bottomHeight;

      if (outerHeight > 200) outerHeight = 200;

      $(submissionDiv).animate({ bottom: outerHeight }, "slow");
      $(runsUL).animate({ height:outerHeight, scrollTop : (bottomHeight - outerHeight) }, "slow");
      $(sidebarDiv).animate( { height: '100%' }, "slow");
      $(contentDiv).animate( { height: '100%' }, "fast");
    };

    // Prepare initial contents of dataset for CSV download
    data.addColumn('number', 'Year');

    for (var i = 0; i < numberOfStepsInSimulation; i++) {
      data.addRow([ mapIndexToYear(i) ]);
    }

    formatMeasurement(0, -1, "####"); // hackish much?

    for ( var aa = 0; aa < Options.graphs.length; aa++ ) {
      var name = Options.graphs[aa];
      for ( var i = 0; i < Options.locations.length; i++) {
        var location = Options.locations[i];
        for ( var j = 0; j < Options.measurements.length; j++) {
          var measurement = Options.measurements[j];
          if (measurement.graphs) {
          for ( var bb = 0; bb < measurement.graphs.length; bb++) {
            var graph = measurement.graphs[bb];
            if ((graph.location == location) && (graph.name == name)) {
              buildChart(j, name, measurement);
            }
          }
          }
        }
      }
    }

    var deleteAllButton = document.getElementById('delete-all');
    deleteAllButton.onclick = function() {
      for (var i = 0; i < runsBeingDisplayed.length; i++)
        runsUL.removeChild(runsUL.firstChild);

      removeAllRuns();

      updateRunsListHeight();

      return false;
    };

//		var runOptimizationButton = document.getElementById('run-opt');
//		runOptimizationButton.onclick = function() {
    //code to come later
    //run dice optimization
//			return false;
//		}

    /*
     *There was origionally going to be an image next to each parameter that linked to a specific
     *part of the FAQ for more information. I could never get this working and decided it was
     *unnecessary/redundant because of  the tooltip descriptions. I left the non-functional code here
     *however, in case anyone wanted to fix and implement it.
     */
    //var goToFAQPageButtonArray = document.getElementsById('faqbutton');
    //for(var i = 0; i<goToFAQPageButtonArray.length; i++){
    //	var currentFAQButton = goToFAQPageButton[i];
    //	currentFAQButton.onclick = function() {
    //		setVisibilityOfOverlay(true);
    //		window.location.assign("http://webdice.rdcep.org/#" . currentFAQButton.getAttribute("data-question_shortname"));
    //		return false;
    //	}
    //}

    //This is how the csv file is downloded. All the data for the runs are stored in $data. (csv means comma seperated value)
    var downloadTextarea = document.getElementById('download-textarea');
    var updateDownloadedText = function() {
      downloadTextarea.value = '';
      var downloadData = data;
      var columnValue = ',Year'
      for (var i = 0; i < downloadData.getNumberOfRows(); i++) {
        columnValue += ','+downloadData.getValue(i, 0);
      }
      columnValue += '\n';
      downloadTextarea.value += columnValue;
      for (var i = 0; i < getNumberOfRuns(); i++) {
        var run = runsBeingDisplayed[i];
        //Only selected, or visible, runs arw downloaded.
        if(run.visible){
          for (var j = 0; j < getNumberOfMeasurements(); j++) {
            var measurement = Options.measurements[j];
            if (j == 0) {
              columnValue = run.description + ',';
            } else {
              columnValue = ',';
            }
            columnValue += measurement.name + ' (' + measurement.unit + ')';
            for (var k = 0; k < downloadData.getNumberOfRows(); k++) {
              columnValue += ','+downloadData.getValue(k, (i*getNumberOfMeasurements())+j+1);
            }
            columnValue += '\n';
            downloadTextarea.value += columnValue;
          }
          columnValue += '\n';
          downloadTextarea.value += columnValue;
        }
      }
    };
    //whenever the data is changed, the above function will run
    handlersForDataChanged.push(updateDownloadedText);

    buildCustomizeableChart('large-graph');
    buildLargeChart('scc');
    initializeTrivialTabsUI();

    //checks if there are runs. If not, shows initial help page.
    var displayConditionalHelp = function() {
      var numberVisible = 0;

      for (var j = 0; j < getNumberOfRuns(); j++) {
        if (runsBeingDisplayed[j].visible)
          numberVisible++;
      }

      if (numberVisible > 0){
        contentDiv.setAttribute('class', 'hasruns');
      } else{
        contentDiv.setAttribute('class', 'hasnoruns');
      }

      deleteAllButton.disabled = (numberVisible == 0);
    };

    //the above function will run when the data is changed.
    handlersForViewportChanged.push(displayConditionalHelp);
    handlersForDataChanged.push(displayConditionalHelp);


    /*
     *Whenever something on the page changes (meaning is clicked by the user),
     *and it isn't handled by one of the .onclick methods way above, it is handled here.
     *It determines the type of input and updates the page accordingly.
     *(This is what runs when the user clicks "run model")
     */
//        $('#run-opt').click(function(){
//            $('#optimize').val('true');
//        });
    var form = document.getElementById('submission');
    form.onsubmit = function(e) {
      e.preventDefault();
      /* We're putting the hackish-equivalent of a try...finally statement here! (Jermey's Safari fix that I accidentally somehow deleted)*/

      setTimeout(function() {
        var data = $(form).serialize();
        var changes = [ ];
        /*
         *All of this is just to find the changes in values for a submitted run so that
         *It can be put in a tooltip display when the user hovers over the "run #" in the bottom
         *left hand corner.
         */
        $(form).find('input[type!=submit][type!=reset][type!=checkbox][type!=hidden],select').each(function() {
          if (this.tagName.toLowerCase() == 'select') {
            var defaultValue = $(this).find('option').first().val().trim()
            var changedValue = $(this).find('option:checked').first().val().trim()
            var areEqual = (defaultValue == changedValue);
            var deviation = (areEqual ? 0 : 0.10); // 25% deviation.
          } else {
            var defaultValue = this.defaultValue;
            var changedValue = parseFloat(this.value).toFixed(this.getAttribute("data-prec"));
            var areEqual = (parseFloat(defaultValue) == parseFloat(changedValue));
            var deviation = Math.abs(Math.log(parseFloat(changedValue) / parseFloat(defaultValue)));
          }
          //TODO: Thus assumes that there won't we any radio inputs other than the policy ones
          if (($(this).attr('name') != 'policy_type') && ($(this).attr('name') != 'damages_model')) {
            if (!areEqual) {
              var description = $(this.parentNode).children('label').attr('title').trim();
              var heading = $(this.parentNode.parentNode.parentNode).prev('h2').first().text();
              changes.push([ heading, description, changedValue, defaultValue, deviation ]);
            }
          }
        });

        changes.sort(function(a, b) { return b[4] - a[4]; });

        var runTextualDescription = "Run Parameters:"; //This is going to be the tooltip

        for (var i = 0; i < changes.length; i++) {
          var change = changes[i];

          runTextualDescription += " [" + change[0] + "] " + change[1] + ": " + change[2];
        }

        if (changes.length == 0) {
          runTextualDescription += " (default parameters)";
        }

        var createdLI = document.createElement('li');
        var createdLABEL = document.createElement('label');
        var progressIMG = document.createElement('img');
        var textNode = document.createTextNode("Executing run...");

        createdLI.setAttribute('title', runTextualDescription);

        progressIMG.setAttribute('src', '/static/images/progress.gif');
        createdLI.appendChild(createdLABEL);
        createdLABEL.appendChild(textNode);
        createdLABEL.appendChild(progressIMG);
        runsUL.appendChild(createdLI);

        numberOfRunsInProgress++;

        updateRunsListHeight();

        /*
         This maps the values form the basic inputs to actual values,
         and then writes the query string -- rather than using jQuery
         serialize()
         */
        if ($(form).hasClass('basic')) {
          var new_values = {
              't2xco2': [1,2,3,4,5],
              'a3': [1, 1.4, 2.0, 2.8, 4.0],
//                            'dela': [0.0, 0.03, 0.1, 0.38, 1.5],
//                            'dsig': [0.0, 0.06, 0.3, 1.3, 6.0],
              'dela': [1.5, 0.38, 0.1, 0.03, 0.0],
              'dsig': [6.0, 1.3, 0.3, 0.06, 0.0],
              'backrat': [1, 1.4, 2.0, 2.8, 4.0]
            }
          ;
          data = data.slice(0,data.search('t2xco2'));
          $('#tab-beliefs').find('input').each(function() {
            $(this).val(function(i, v) {
              data += '&' + $(this).attr('name') + '=';
              data += new_values[$(this).attr('name')][v-1];
              return v;
            });
          });
        }
        /*
         End value mapping for basic form
         */
        $('html, body').animate({scrollTop:$(document).height()}, 'slow');
        $.ajax({ //Now we are going to actually execute the run
          type : 'POST',
          url : '/run',
          data : data,
          success : function(data, textStatus, xhr) {
            var runObject = addRunFromCSV("Run #" + (getNumberOfRuns() + 1),
              generateNextColor(), data, changes);
            numberOfRunsInProgress--;

            //textNode.nodeValue = runObject.description;

            textNode.nodeValue = null;
            var clickableRunLabel = document.createElement('span');
            clickableRunLabel.setAttribute('class', 'clickable-run-label');
            clickableRunLabel.appendChild(textNode);
            clickableRunLabel.onclick = function() {
              if ($(this).children('input').length == 0) {
                var clickableRunInput = document.createElement('input');
                clickableRunInput.setAttribute('type', 'text');
                clickableRunInput.setAttribute('class', 'clickable-run-input');
                clickableRunInput.setAttribute('value', $(this).text());
                $(this).html(clickableRunInput);
                $(this).children('.clickable-run-input').focus();
                $(this).children('.clickable-run-input').blur(function() {
                  var value = $(this).val();
                  $(this).parent().html(value);
                  runObject.description = value;
                  updateAllData();
                });
              }
            }
            textNode.nodeValue = runObject.description;
            createdLABEL.appendChild(clickableRunLabel);

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

            $(createdLABEL).append(colorSlab).each(function() {
              return false;
            });
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
          timeout : 50000
        });

      }, 0); return false;
    };

    $('input[type=range]', form).change(function() {
      /*
       *Here is where we update the label next to the range slider when the user
       *drags it. We first round this value to a specified number of decimal places,
       *then set the label to that value.
       */
      var value = parseFloat(this.value).toFixed(this.getAttribute("data-prec"));
      if ($(this).hasClass('percent')) {
        Math.round(value = value * 100, 0);
      }
      /* This is a hack for the treaty sliders, so that they can move
       *'backwards' from 100 to 0.
       */
      if ($(this).hasClass('reverse')) {
        value = Math.abs(100 - value);
      }
      $(this).prevAll('label').children('span.label').children('.label-number').text(value);
    });

    /*
     *This runs when you click "reset inputs". It runs the function above on a form
     *reset so all its inputs are what they were when the page was intitalized.
     */
    $('#reset-inputs').click(function(e) {
      e.preventDefault();
      form.reset();
      $('input[type=range]', form).change();
      $('.init-disabled').addClass('disabled').children('input').each(function() {
        $(this).attr('disabled', 'disabled');
      });
    });

//        $('#treaty_switch').change(function(e) {
//            $(this).parent('h2').next('ul').children('li').toggleClass('disabled');
//            $(this).parent('h2').next('ul').children('li').children('input').each(function() {
//                var $this = $(this);
//                if ($this.attr('disabled')) $this.removeAttr('disabled');
//                else $this.attr('disabled', 'disabled');
//            });
//        });
    $('input[name=policy_type]').change(function(e) {
      $('input[name=policy_type]').each(function() {
        var $this = $(this).parent('h2').nextAll('ul').children('li');
        if ($(this).is(':checked')) {
          $this.children('input').removeAttr('disabled');
          $this.removeClass('disabled');
        }
        else {
          $this.children('input').attr('disabled', 'disabled');
          $this.addClass('disabled');
        }
      });
    });

    $('select[name=damages_model]').change(function(e) {
      console.log(1);
      var prod_frac = $('input[name=prod_frac]');
      if ($(this).val() == 'productivity_fraction') {
        prod_frac.removeAttr('disabled');
        prod_frac.parent().removeClass('disabled');
      } else {
        prod_frac.attr('disabled', 'disabled');
        prod_frac.parent().addClass('disabled');
      }
    })

    window.onresize = function() {
      updateAllViewports();
    }
  };

  google.load('visualization', '1.0', {'packages' : ['corechart']});
  google.setOnLoadCallback(initializeUI);
})(jQuery);