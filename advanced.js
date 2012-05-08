$(document).ready(function() {

	// Buttons
	$("#radioCarbon").buttonset();
	$("#radioDamage").buttonset();

	// Accordion
	$("#accordion3").accordion({
		autoHeight:false
	    });
	$("#accordion4").accordion({
		autoHeight:false
		    });
	$("#accordion5").accordion({
		autoHeight:false
		    });
	      
	// Sliders

	
	$("#slider8").slider({
		value:0,
		    min:0,
		    max:100,
		    step:5,
		    slide: function( event, ui ) {
		    $( "#abate20502" ).val(ui.value + "%" );
		    }
	    });
	$("#abate20502").val($("#slider8").slider("value") + "%");

	$("#slider9").slider({
		value:0,
		    min:0,
		    max:100,
		    step:5,
		    slide: function( event, ui ) {
		    $( "#abate21002" ).val(ui.value + "%" );
		    }
	    });
	$("#abate21002").val($("#slider9").slider("value") + "%");

	$("#slider10").slider({
		value:0,
		    min:0,
		    max:100,
		    step:5,
		    slide: function( event, ui ) {
		    $( "#abate21502" ).val(ui.value + "%" );
		    }
	    });
	$("#abate21502").val($("#slider10").slider("value") + "%");

	$("#slider11").slider({
		value:0,
		    min:0,
		    max:100,
		    step:5,
		    slide: function( event, ui ) {
		    $( "#climateSensitivity2" ).val(ui.value + "%" );
		    }
	    });
	$("#climateSensitivity2").val($("#slider11").slider("value") + "%");


	// Submit Buttons

	$("input:submit").button();



    });