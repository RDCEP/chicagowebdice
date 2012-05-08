$(document).ready(function() {

	// Case of refresh
	$('#reload').click(function() {
		alert("hi");
		location.reload();
	    });

	// Set up trigger for exiting
	$(window).bind('beforeunload', function(){

		alert("hi");
    
		if (window.XMLHttpRequest)
		    {
			xmlhttp=new XMLHttpRequest();
		    }
		else
		    {
			xmlhttp=new XMLHttpRequest();
		    }
		
		xmlhttp.open("GET","revert.php",true);
		xmlhttp.send();
    
	    });


    });

function revert(){
    if (window.XMLHttpRequest)
	{
	    xmlhttp=new XMLHttpRequest();
	}
    else
	{
	    xmlhttp=new XMLHttpRequest();
	}

    xmlhttp.onreadystatechange=function()
	{
	    if (xmlhttp.readyState==4 && xmlhttp.status==200)
		{
		    simulationDICE1();
		    simulationDICE2();
		    simulationDICE3();
		    simulationDICE4();
		}
	}
    
    xmlhttp.open("GET","revert.php",true);
    xmlhttp.send();
}