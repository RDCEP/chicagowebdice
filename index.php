<?php

require_once('lib/spyc.php');

$configuration = Spyc::YAMLLoad('parameters.yaml');

$parameters = $configuration['parameters'];
$measurements = $configuration['measurements'];

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
		$arguments[] = escapeshellarg($name);
		$arguments[] = escapeshellarg($value);
	}
	
	$flattened = implode(' ', $arguments);
	$r = popen("bin/fakeDriver.py $flattened 2>&1", "r");
	
	while (($line = fgets($r)) !== FALSE) {
		echo $line;
	}
	
	pclose($r);
} else {
?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>RDCEP :: WebDICE</title>
  <link rel="stylesheet" href="styles.css" type="text/css" media="screen" title="Default Stylesheet" charset="utf-8"/>
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
<h1>RDCEP :: WebDICE</h1>
<div id='sidebar'>
  <form id='submission'>
    <div id='parameters'>
<?php
		foreach ($sections as $section) {
			$section_name = htmlentities($section['name']);
			$parameters = $section['parameters'];
			
			print "      <h2>$section_name</h2>\n";
			print "      <ul>\n";
			
			foreach ($parameters as $parameter) {
				$name = $parameter['name'];
				$machine_name = $parameter['machine_name'];
				$is_select_control = $parameter['is_select_control'];
				$is_range_control = $parameter['is_range_control'];
				
				if (isset($parameter['description'])) {
					$description = $parameter['description'];
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
					
					print "<span>$default</span> <input name='$machine_name' ";
					print "type='range' min='$min' max='$max' step='$step' value='$default'/></label></li>\n";
				}
			}
			
			print "      </ul>\n";
		}
		?>
    </div>
    <div id='controls'>
      <input type='reset' value='Reset'/><input type='submit' value='Make New Run'/>
    </div>
  </form>
  <div id='runs'>
    <ul>
      <li><label><span class='slab' style="background-color:#a03;border-color:#903;"></span> Default Parameters <input type='checkbox'/></label></li>
      <li><label><span class='slab' style="background-color:#390;border-color:#280;"></span> Sensitivity at 80% <input type='checkbox'/></label></li>
      <li><label><span class='slab' style="background-color:#39c;border-color:#28b;"></span> Sensitivity at 50% <input type='checkbox'/></label></li>
      <li><label><span class='slab' style="background-color:#aa3;border-color:#993;"></span> Sensitivity at 30% <input type='checkbox'/></label></li>
    </ul>
  </div>
</div>
<div id='content'>
  
</div>
</body>
</html><?php } ?>