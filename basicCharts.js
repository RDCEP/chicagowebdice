$(document).ready(function() {
	
	simulationDICE1();
	simulationDICE2();
	simulationDICE3();
	simulationDICE4();
    });

function simulationDICE(){

    if (window.XMLHttpRequest)
	{
	    xmlhttp=new XMLHttpRequest();
	}
    else
	{
	    xmlhttp=new XMLHttpRequest();
	}

    // pull parameters from sliders
    var cs = $("#slider1").slider("value");
    var ed = $("#slider2").slider("value");
    var pg = $("#slider3").slider("value");
    var tg = $("#slider4").slider("value");

    var msg = "\n param t2xco2 " + cs + "\n param a3 " + ed + "\n param gpop0 " + pg + "\n param ga0 " + tg;
    // update graphs
    xmlhttp.onreadystatechange=function()
	{
	    if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
		    simulationDICE1();
		    simulationDICE2();
		    simulationDICE3();
		    simulationDICE4();

		    document.getElementById("bar").innerHTML=xmlhttp.responseText;
		}
	}

    // call php -> execute webDICE
    xmlhttp.open("GET","server.php?msg="+msg,true);
    xmlhttp.send();

}

function simulationDICE1(){
    var options = {
	chart: {
	    renderTo:'chart1',
	    zoomType:'x',
	},
	title: {
	    text: 'Total Emissions'
	},
	xAxis: {
	    type: 'datetime',
	    maxZoom: 5 * 10 * 365.25 * 24 * 3600000
	},
	yAxis: {
	    title:{
		text: 'Gigatons of carbon per 10 years'
	    },
	    min: 0,
	    startOnTick:false,
	    showFirstLabel:false
	},
	tooltip: {
	    shared:true
	},
	series: []
    };
    
    $.get('output.csv', function(data) {
	    // Split lines
	    var lines = data.split('\n');
	    
	    // Iterate over lines and add series
	    $.each(lines, function(lineNo, line) {
		    var items = line.split(',');
		    
		    // extract from line 0
		    if (lineNo == 0) {
			var series = {
			    type: 'area',
			    pointInterval: 10 * 365 * 24 * 3600000,
			    pointStart: Date.UTC(2005,0,01),
			    data: []
			};
			$.each(items, function(itemNo, item) {
				if (itemNo == 0) {
				    series.name = item;
				} else {
				    if (itemNo < 22) {
					series.data.push(parseFloat(item));
				    }
				}
			    });
			options.series.push(series);
		    }

		    /*
		    // header has title text
		    if (lineNo == 0) {
			$.each(items,function(itemNo, item) {
				options.title.text = item;
			    });
		    }
		    
		    // other lines have data for series
		    else{
			var series = {
			    type: 'area',
			    pointInterval: 10 * 365 * 24 * 3600000,
			    pointStart: Date.UTC(2005,0,01),
			    data: []
			};
			$.each(items, function(itemNo, item) {
				if (itemNo == 0) {
				    series.name = item;
				} else {
				    series.data.push(parseFloat(item));
				}
			    });
			options.series.push(series);
		    }
		    */
		});
	    
	    // Create the chart
	    var chart = new Highcharts.Chart(options);
	    
	});
}

function simulationDICE2(){
    var options = {
	chart: {
	    renderTo:'chart2',
	    zoomType:'x',
	},
	title: {
	    text: 'Carbon Mass in Atmosphere'
	},
	xAxis: {
	    type: 'datetime',
	    maxZoom: 5 * 10 * 365 * 24 * 3600000
	},
	yAxis: {
	    title:{
		text: 'Gigatons of Carbon'
	    },
	    min: 0,
	    startOnTick:false,
	    showFirstLabel:false
	},
	tooltip: {
	    shared:true
	},
	series: []
    };
    
    $.get('output.csv', function(data) {
	    // Split lines
	    var lines = data.split('\n');
	    
	    // Iterate over lines and add series
	    $.each(lines, function(lineNo, line) {
		    var items = line.split(',');
		    
		    // extract from line 1
		    if (lineNo == 1) {
			var series = {
			    type: 'area',
			    pointInterval: 10 * 365 * 24 * 3600000,
			    pointStart: Date.UTC(2005,0,01),
			    data: []
			};
			$.each(items, function(itemNo, item) {
				if (itemNo == 0) {
				    series.name = item;
				} else {
				    if (itemNo < 22){
					series.data.push(parseFloat(item));
				    }
				}
			    });
			options.series.push(series);
		    }
		});
	    
	    // Create the chart
	    var chart = new Highcharts.Chart(options);
	    
	});
}

function simulationDICE3(){
    var options = {
	chart: {
	    renderTo:'chart3',
	    zoomType:'x',
	},
	title: {
	    text: 'Atmospheric Temperature Increase'
	},
	xAxis: {
	    type: 'datetime',
	    maxZoom: 5 * 10 * 365 * 24 * 3600000
	},
	yAxis: {
	    title:{
		text: 'Degrees Celcius increase from 1900'
	    },
	    min: 0,
	    startOnTick:false,
	    showFirstLabel:false
	},
	tooltip: {
	    shared:true
	},
	series: []
    };
    
    $.get('output.csv', function(data) {
	    // Split lines
	    var lines = data.split('\n');
	    
	    // Iterate over lines and add series
	    $.each(lines, function(lineNo, line) {
		    var items = line.split(',');
		    
		    // extract from line 2
		    if (lineNo == 2) {
			var series = {
			    type: 'area',
			    pointInterval: 10 * 365 * 24 * 3600000,
			    pointStart: Date.UTC(2005,0,01),
			    data: []
			};
			$.each(items, function(itemNo, item) {
				if (itemNo == 0) {
				    series.name = item;
				} else {
				    if (itemNo < 22) {
					series.data.push(parseFloat(item));
				    }
				}
			    });
			options.series.push(series);
		    }

		    
		});
	    
	    // Create the chart
	    var chart = new Highcharts.Chart(options);
	    
	});
}

function simulationDICE4(){
    var options = {
	chart: {
	    renderTo:'chart4',
	    zoomType:'x',
	},
	title: {
	    text: 'Per Capita Consumption'
	},
	xAxis: {
	    type: 'datetime',
	    maxZoom: 5 * 10 * 365 * 24 * 3600000
	},
	yAxis: {
	    title:{
		text: 'Dollars per Person'
	    },
	    min: 0,
	    startOnTick:false,
	    showFirstLabel:false
	},
	tooltip: {
	    shared:true
	},
	series: []
    };
    
    $.get('output.csv', function(data) {
	    // Split lines
	    var lines = data.split('\n');
	    
	    // Iterate over lines and add series
	    $.each(lines, function(lineNo, line) {
		    var items = line.split(',');

		    // extract from line 3
		    if (lineNo == 3) {
			var series = {
			    type: 'area',
			    pointInterval: 10 * 365 * 24 * 3600000,
			    pointStart: Date.UTC(2005,0,01),
			    data: []
			};
			$.each(items, function(itemNo, item) {
				if (itemNo == 0) {
				    series.name = item;
				} else {
				    if (itemNo < 22) {
					series.data.push(parseFloat(item));
				    }
				}
			    });
			options.series.push(series);
		    }
		    

		});
	    
	    // Create the chart
	    var chart = new Highcharts.Chart(options);
	    
	});
}