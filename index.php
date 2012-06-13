<?php

require_once('lib/spyc.php');

$configuration = Spyc::YAMLLoad('parameters.yaml');

$parameters = $configuration['parameters'];

$missing_parameter = "Missing \"%s\" attribute on parameter configuration element.";
$too_many_items = "Parameter configuration_element has %i extra element(s).";
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
		trigger_error(sprintf($missing_parameter, count($parameter) - $size), E_USER_ERROR);
	
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
			
			$machine_name = $value['machine_name'];
			
			if (isset($parameter['indexed_values'][$machine_name]))
				trigger_error($duplicate_option, E_USER_ERROR);
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

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>RDCEP :: WebDICE</title>
  <link rel="stylesheet" href="styles.css" type="text/css" media="screen" title="Default Stylesheet" charset="utf-8"/>
</head>
<body>
<h1>RDCEP :: WebDICE</h1>
<div id='sidebar'>
  <form>
    <div id='parameters'><?php
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
				$default = $parameter['default'];
				
				print "        <li>$name ";
				
				if ($is_select_control) {
					$values = $parameter['values'];
					
					print "<select name='$machine_name'>";
					
					foreach ($values as $value) {
						$option_machine_name = $value['machine_name'];
						$option_name = $value['name'];
						
						print "          <option name='$option_machine_name'>$option_name</option>";
					}
					
					print "        </li>\n";
				} else if ($is_range_control) {
					$min = $parameter['min'];
					$max = $parameter['max'];
					$step = $parameter['step'];
					$default = $parameter['default'];
					
					print "<span>$default</span> <input name='$machine_name' ";
					print "type='range' min='$min' max='$max' step='$step' value='$default'/></li>\n";
				}
			}
			
			print "      </ul>\n";
		}
		?>
      <h2>Model Parameters</h2>
      <ul>
      <li>Climate Sensitivity <span>3</span> <input type='range' min='1' max='5' step='0.5' value='3'/></li>
      <li>Environment Damages <span>2</span> <input type='range' min='1' max='3' step='0.5' value='2'/></li>
      <li>Population Growth <span>0.35</span> <input type='range' min='0.1' max='0.5' step='0.05' value='0.35'/></li>
      <li>Technology Growth <span>0.1</span> <input type='range' min='0.05' max='0.15' step='0.01' value='0.1'/></li>
      <h2>Carbon Controls</h2>
      <ul>
      <li>Emissions by 2050 <span>0%</span> <input type='range' min='0' max='100' step='5' value='0'/></li>
      <li>Emissions by 2100 <span>0%</span> <input type='range' min='0' max='100' step='5' value='0'/></li>
      <li>Emissions by 2150 <span>0%</span> <input type='range' min='0' max='100' step='5' value='0'/></li>
      </ul>
      <h2>Model Design</h2>
      <ul>
      <li>Oceanic Model <select><option>DICE 2007</option><option>Glotter</option></select></li>
      <li>Climate Sensitivity <span>0%</span><input type='range' min='0' max='100' step='5' value='0'/></li>
      </ul>?>
    </div>
    <div id='controls'>
      <input type='reset' value='Reset'/><input type='submit' value='Make New Run'/>
    </div>
  </form>
</div>
<div id='runs'>
  <ul>
    <li><label><span style="background-color:#a03;border-color:#903;"></span><input type='checkbox'/></label></li>
    <li><label><span style="background-color:#390;border-color:#280;"></span><input type='checkbox'/></label></li>
    <li><label><span style="background-color:#39c;border-color:#28b;"></span><input type='checkbox'/></label></li>
    <li><label><span style="background-color:#aa3;border-color:#993;"></span><input type='checkbox'/></label></li>
  </ul>
</div>
<div id='content'>
  <div class='graph'></div>
  <div class='graph'></div>
  <div class='graph'></div>
  <div class='graph'></div>
</div>
</body>
</html>