function getTFP(GDPgrowth)
{
    // from 1-year to 10-year (geometric sum okay?)
    var GDPgrowth1 = (GDPgrowth + 1.0)^(10);

    var c1 = 137.0;
    var c2 = 170.0;

    var l1 = 6514.0;
    var l2 = 7130.0;

    var g = 0.3;
    var TFPgrowth = (GDPgrowth + 1.0) * (c1 / c2)^g * (l1 / l2)^(1.0-g) - 1.0;
    var TFPgrowth1 = TFPgrowth^(0.1);
    
    return TFPgrowth1;
}

$(document).ready(function() {

	// Accordion
	$("#accordion1").accordion({
		autoHeight:false,
		    });
	$("#accordion2").accordion({
		autoHeight:false
		    });
	      
	// Sliders
	// Parameters

	// Slider 1: Climate Sensitivity
	$("#slider1").slider({
		value:3,
		    min:1,
		    max:5,
		    step:.5,
		    slide: function( event, ui ) {
		    $( "#climateSensitivity" ).val(ui.value );
		    }
	    });
	$("#climateSensitivity").val($("#slider1").slider("value"));

	// Slider 2: Environmental Damages
	$("#slider2").slider({
		value:2,
		    min:1,
		    max:3,
		    step:.5,
		    slide: function( event, ui ) {
		    $( "#damages" ).val(ui.value );
		    }
	    });
	$("#damages").val($("#slider2").slider("value"));

	// Slider 3: Population Growth
	$("#slider3").slider({
		value:.35,
		    min:.1,
		    max:.5,
		    step:.05,
		    slide: function( event, ui ) {
		    $( "#popGrowth" ).val(ui.value );
		    }
	    });
	$("#popGrowth").val($("#slider3").slider("value"));

	// Technological Growth
	$("#slider4").slider({
		value:.092,
		    min:.05,
		    max:.15,
		    step:.05,
		    slide: function( event, ui ) {
		    $( "#techGrowth" ).val(ui.value );
		    }
	    });
	$("#techGrowth").val($("#slider4").slider("value"));

	// Carbon Abatement Strategy
	$("#slider5").slider({
		value:0,
		    min:0,
		    max:100,
		    step:10,
		    slide: function( event, ui ) {
		    $( "#abate2050" ).val(ui.value + "%" );
		    }
	    });
	$(".abate2050").val($("#slider5").slider("value") + "%");

	$("#slider6").slider({
		value:0,
		    min:0,
		    max:100,
		    step:10,
		    slide: function( event, ui ) {
		    $( "#abate2100" ).val(ui.value + "%" );
		    }
	    });
	$("#abate2100").val($("#slider6").slider("value") + "%");

	$("#slider7").slider({
		value:0,
		    min:0,
		    max:100,
		    step:10,
		    slide: function( event, ui ) {
		    $( "#abate2150" ).val(ui.value + "%" );
		    }
	    });
	$("#abate2150").val($("#slider7").slider("value") + "%");

	// Submit Buttons

	$("input:submit").button();
	$("input:reset").button();

    });