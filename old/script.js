function same(){
    // This isn't actually very useful, since the rendering is so fast
    document.getElementById("date").innerHTML="this is awesome!";
    document.getElementById("time").innerHTML="this is awesome too!";

    var x = 4;
    if (x < 5){
	document.getElementById("time").innerHTML="the value of x is less than five";
    }
}

function diff(){
    var y = confirm("yes or no?");
    if (y){
	    alert("yes!");
	}
    else{
	alert("no!");
    }
}

function power(){
    var power = Number(prompt("What power?"));
    var out = 1;
    while (power > 0){
	out = out * 2;
	power = power - 1;
    }
    alert("The answer is " + out);
}

function absolute(x){
    if (x >= 0){
	return x;
    }
    else{
	return -x;
    }
}

function doAbs(){
    var x = Number(prompt("x = "));
    x = absolute(x);
    alert(x);
}
