<?php
	$msg=$_GET["msg"];
	
	function callDriver()
	{
		$stuff = shell_exec('/var/www/chicagowebdice/execute.sh 2>&1');
		return $stuff;
	}

	function writeIt($m)
	{

		$fn="/var/www/chicagowebdice/input.csv";
		$fh=fopen($fn,'w') or die("can't open file");

		fwrite($fh,$m);
		fclose($fh);
	}

	writeIt($msg);
	echo "=====!" . callDriver() . "!=====";
?>