<?php

	function revert_output()
	{
		shell_exec('/var/www/chicagowebdice/revert.sh 2>&1');
	}	

	revert_output();

?>