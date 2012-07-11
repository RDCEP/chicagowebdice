<?php

require_once('lib/spyc.php');

$configuration = Spyc::YAMLLoad('parameters.yaml');

$parameters = $configuration['parameters'];
$measurements = $configuration['measurements'];
$initial_help = $configuration['initial_help'];
$advanced_help = $configuration['advanced_help'];

$missing_parameter = "Missing \"%s\" attribute on configuration element.";
$too_many_items = "Configuration_element has %d extra element(s).";
$option_no_name = "Parameter option element has no \"name\" option and should.";
$option_no_machine_name = "Parameter option element has no \"machine_name\" option and should.";
$non_numeric_configuration = "The \"min,\" \"max,\" and \"step\" options are numeric.";
$duplicate_property = "Multiple parameters with machine name \"%s\".";
$duplicate_option = "Multiple options with machine_name \"%s\".";
$invalid_default = "The default must be between the minimum and maximum.";

$sections = array();
$all_parameters = array();

foreach ($parameters as $parameter) {
	$required = array("name", "machine_name", "section");
	$optional = array();
	
	$is_select_control = isset($parameter['values']);
	$is_range_control = !$is_select_control;
	
	if ($is_range_control)
		array_push($required, "min", "max", "default");
	else if ($is_select_control)
		array_push($required, "values");
	
	if (isset($parameter['step']))
		$optional[] = 'step';
	
	if (isset($parameter['description']))
		$optional[] = 'description';
	
	$size = count($required) + count($optional);
	
	if (count($parameter) > $size)
		trigger_error(sprintf($too_many_items, count($parameter) - $size), E_USER_ERROR);
	
	foreach ($required as $name) {
		if (!isset($parameter[$name]))
			trigger_error(sprintf($missing_parameter, $name), E_USER_ERROR);
	}
	
	$name = $parameter['name'];
	$machine_name = $parameter['machine_name'];
	$section_name = $parameter['section'];
	$cleaned_section_name = preg_replace('/[^a-z]/', '', strtolower($parameter['section']));
	
	$parameter['is_select_control'] = $is_select_control;
	$parameter['is_range_control'] = $is_range_control;
	
	if ($is_select_control) {
		$parameter['indexed_values'] = array();
		$values = $parameter['values'];
		
		foreach ($values as $value) {
			if (!isset($value['name']))
				trigger_error($option_no_name, E_USER_ERROR);
			if (!isset($value['machine_name']))
				trigger_error($option_no_machine_name, E_USER_ERROR);
			
			$option_machine_name = $value['machine_name'];
			
			if (isset($parameter['indexed_values'][$option_machine_name]))
				trigger_error($duplicate_option, E_USER_ERROR);
			
			$parameter['indexed_values'][$option_machine_name] = $value;
		}
	} else if ($is_range_control) {
		if (!is_numeric($parameter['min']) ||
		    !is_numeric($parameter['max']) ||
		    !is_numeric($parameter['step']) ||
		    !is_numeric($parameter['default']))
			trigger_error($non_numeric_configuration, E_USER_ERROR);
		
		if (($parameter['default'] > $parameter['max']) ||
		    ($parameter['default'] < $parameter['min']))
			trigger_error($invalid_default, E_USER_ERROR);
	}
	
	if (isset($all_parameters[$machine_name]))
		trigger_error(sprintf($duplicate_property, $machine_name), E_USER_ERROR);
	else
		$all_parameters[$machine_name] = $parameter;
	
	if (!isset($sections[$cleaned_section_name])) {
		$sections[$cleaned_section_name] = array(
			"name" => $section_name,
			"parameters" => array( )
		);
	}
	
	$sections[$cleaned_section_name]["parameters"][] = $parameter;
}

foreach ($measurements as $measurement) {
	$required = array("name", "machine_name", "unit");
	$optional = array();
	
	foreach ($required as $name) {
		if (!isset($measurement[$name]))
			trigger_error(sprintf($missing_parameter, $name), E_USER_ERROR);
	}
	
	if (isset($measurement["description"]))
		$optional[] = "description";
	
	if (isset($measurement["format"]))
		$optional[] = "format";
	
	$size = count($required) + count($optional);
	
	if (count($measurement) > $size)
		trigger_error(sprintf($too_many_items, count($measurement) - $size), E_USER_ERROR);
}

if (strtoupper($_SERVER['REQUEST_METHOD']) != 'GET') {
	$values = array();
	
	foreach ($all_parameters as $machine_name => $parameter) {
		if (isset($_POST[$machine_name])) {
			$value = $_POST[$machine_name];
		} else if ($parameter['is_range_control']){
			$value = $parameter['default'];
		} else {
			$value = NULL;
		}
		
		if ($parameter['is_range_control']) {
			if ($value < $parameter['min'])
				$value = $parameter['min'];
			
			if ($value > $parameter['max'])
				$value = $parameter['max'];
		
			/*
			 * We quantize parameters because it might be useful to
			 * try and cache requests. Discretized parameter parsing
			 * is crucial to that effort.
			 */
			$value = round(($value - $parameter['min']) / $parameter['step']) * $parameter['step'];
			
		} else if ($parameter['is_select_control']) {
			if (!isset($parameter['indexed_values'][$machine_name])) {
				$keys = array_keys($parameter['indexed_values']);
				$value = $keys[0];
			}
		}
		
		$values[$machine_name] = $value;
	}
	
	$arguments = array( );
	
	foreach ($values as $name => $value) {
		$arguments[] = "param";
		$arguments[] = escapeshellarg($name);
		$arguments[] = escapeshellarg($value);
	}
	
	$current_load_path = getenv("LD_LIBRARY_PATH");
	$new_load_path = 
		"/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/bin/glnx86:".
		"/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/runtime/glnx86:".
		"/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/os/glnx86:".
		"/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386/native_threads:".
		"/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386/server:".
		"/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/sys/java/jre/glnx86/jre/lib/i386:".
		"/usr/lib/x86_64-linux-gnu/:".
		"/var/www/development/lib";
	if ($current_load_path) $new_load_path = "$current_load_path:$new_load_path";
	
	putenv("LD_LIBRARY_PATH=$new_load_path");
	putenv("XAPPLRESDIR=/usr/local/MATLAB/MATLAB_Compiler_Runtime/v716/X11/app-defaults");
	
	$flattened = implode(' ', $arguments);
	$r = popen("bin/diceDriver run DICE2007Run step DICE2007Step $flattened", "r");
	
	$number_of_blank_lines = 0;
	$output = "";
	while (($line = fgets($r)) !== FALSE) {
		if (strlen(trim($line)) <= 1) $number_of_blank_lines++;
		else if ($number_of_blank_lines > 2)
			$output .= $line;
	}
	
	if (pclose($r) != 0)
		header('HTTP/1.0 500 Internal Server Error');
	else
		echo $output;
	
	putenv("LD_LIBRARY_PATH=$current_load_path");
} else {
	
	function format_for_web($text) {
		return preg_replace('/^\(([^)]+)\)/', '<sup>$1</sup>',
			preg_replace('/_\(([^)]+)\)/', '<sub>$1</sub>', htmlentities($text)));
	}
	
?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>RDCEP :: WebDICE</title>
  <link rel="stylesheet" href="styles.css" type="text/css" media="screen" title="Default Stylesheet" charset="utf-8"/>
  <link rel="stylesheet" type="text/css" media="screen, projection" href="http://www.frequency-decoder.com/demo/fd-slider/css/fd-slider.mhtml.min.css" />
  <script src="javascript/fd-slider.min.js"></script>
  <script src="javascript/jquery.min.js"></script>
  <script type="text/javascript" src="javascript/MathJax.js?config=default"></script>
  <script type='text/javascript'>
<?php
	echo "    Options = window.Options || { }\n";
	
	$json = json_encode($measurements);
	echo "    Options.measurements = $json;\n";
	?>
  </script>
  <script type='text/javascript' src='https://www.google.com/jsapi'></script>
  <script type='text/javascript' src='javascript/main.js'></script>
</head>
<body>
<h1 id='heading'> <span>RDCEP</span> :: WebDICE</h1>
<a id='display-help' href=''>Documentation</a>
<div id='sidebar'>
  <form id='submission'>
    <div id='parameters'>
<?php
		foreach ($sections as $section) {
			$section_name = format_for_web($section['name']);
			$parameters = $section['parameters'];
			
			print "      <h2>$section_name</h2>\n";
			print "      <ul>\n";
			
			foreach ($parameters as $parameter) {
				$name = format_for_web($parameter['name']);
				$machine_name = htmlentities($parameter['machine_name']);
				$is_select_control = $parameter['is_select_control'];
				$is_range_control = $parameter['is_range_control'];
				
				if (isset($parameter['description'])) {
					$description = htmlentities($parameter['description']);
					print "        <li><label title='$description'>$name ";
				} else {
					print "        <li><label>$name ";
				}
				
				if ($is_select_control) {
					$values = $parameter['values'];
					
					print "<select name='$machine_name'>\n";
					
					foreach ($values as $value) {
						$option_machine_name = $value['machine_name'];
						$option_name = $value['name'];
						
						if (isset($value['description'])) {
							$description = htmlentities($value['description']);
							
							print "          <option name='$option_machine_name' title='$description'>$option_name</option>\n";
						} else {
							print "          <option name='$option_machine_name'>$option_name</option>\n";
						}
					}
					
					print "        </select></li>\n";
				} else if ($is_range_control) {
					$min = $parameter['min'];
					$max = $parameter['max'];
					$step = $parameter['step'];
					$default = $parameter['default'];
					
					print "<span class='label'>$default</span> <input name='$machine_name' ";
					print "type='range' min='$min' max='$max' step='$step' value='$default'/></label></li>\n";
				}
			}
			
			print "      </ul>\n";
		}
		?>
    </div>
    <div id='controls'>
      <input type='submit' id='delete-all' value='Delete All Runs' disabled='disabled'/><input type='submit' value='Make New Run'/>
    </div>
  </form>
  <ul id='runs'></ul>
</div>
<div id='content'>
  <div class='initial'>
<?php
		$paragraphs = explode("\n", $initial_help);
		
		foreach ($paragraphs as $paragraph) {
			echo "    <p>$paragraph</p>\n";
		}
?>  </div>
</div>
<div id='overlay'>
  <div class='slug'></div>
  <div class='article' id='advanced-help'>
<?php
		$paragraphs = explode("\n", $advanced_help);
		
		foreach ($paragraphs as $paragraph) {
			$paragraph = htmlentities($paragraph);
			
			if (preg_match('/^##### (.*)/', $paragraph, $matches))
				echo "    <h5>{$matches[1]}</h5>\n";
			else if (preg_match('/^#### (.*)/', $paragraph, $matches))
				echo "    <h4>{$matches[1]}</h4>\n";
			else if (preg_match('/^### (.*)/', $paragraph, $matches))
				echo "    <h3>{$matches[1]}</h3>\n";
			else if (preg_match('/^## (.*)/', $paragraph, $matches))
				echo "    <h2>{$matches[1]}</h2>\n";
			else if (preg_match('/^# (.*)/', $paragraph, $matches))
				echo "    <h1>{$matches[1]}</h1>\n";
			else
				echo "    <p>$paragraph</p>\n";
		}
?>
    <a href='' id='hide-help'>Hide</a>
  </div>
</div>
</body>
</html><?php } ?>