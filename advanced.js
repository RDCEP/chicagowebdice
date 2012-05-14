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

	$("#slider12").slider({
		value:2,
		    min:0.5,
		    max:3,
		    step:.5,
		    slide: function( event, ui ) {
		    $( "#elasmu" ).val(ui.value + "%" );
		    }
	    });
	$("#elasmu").val($("#slider12").slider("value") + "%");

	$("#slider13").slider({
		value:1.5,
		    min:0,
		    max:3,
		    step:0.5,
		    slide: function( event, ui ) {
		    $( "#discount" ).val(ui.value + "%" );
		    }
	    });
	$("#discount").val($("#slider13").slider("value") + "%");

	$("#slider14").slider({
		value:0.2,
		    min:0.15,
		    max:0.3,
		    step:0.05,
		    slide: function( event, ui ) {
		    $( "#savings" ).val(ui.value + "%" );
		    }
	    });
	$("#savings").val($("#slider14").slider("value") + "%");

	$("#slider15").slider({
		value:0.2,
		    min:0.15,
		    max:0.3,
		    step:0.05,
		    slide: function( event, ui ) {
		    $( "#popcap" ).val(ui.value + "%" );
		    }
	    });
	$("#popcap").val($("#slider15").slider("value") + "%");

	$("#slider16").slider({
		value:0.2,
		    min:0.15,
		    max:0.3,
		    step:0.05,
		    slide: function( event, ui ) {
		    $( "#initGDPgrowth" ).val(ui.value + "%" );
		    }
	    });
	$("#initGDPgrowth").val($("#slider16").slider("value") + "%");

	$("#slider17").slider({
		value:0.2,
		    min:0.15,
		    max:0.3,
		    step:0.05,
		    slide: function( event, ui ) {
		    $( "#GDPdecline" ).val(ui.value + "%" );
		    }
	    });
	$("#GDPdecline").val($("#slider17").slider("value") + "%");

	$("#slider18").slider({
		value:0.2,
		    min:0.15,
		    max:0.3,
		    step:0.05,
		    slide: function( event, ui ) {
		    $( "#capitaldeprec" ).val(ui.value + "%" );
		    }
	    });
	$("#capitaldeprec").val($("#slider18").slider("value") + "%");

	$("#slider19").slider({
		value:0.2,
		    min:0.15,
		    max:0.3,
		    step:0.05,
		    slide: function( event, ui ) {
		    $( "#fosslim" ).val(ui.value + "%" );
		    }
	    });
	$("#fosslim").val($("#slider19").slider("value") + "%");



	// Submit Buttons

	$("input:submit").button();



    });