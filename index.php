<?php

require_once('lib/spyc.php');
require_once('lib/markdown.php');

//Loads yaml file and sorts it into arrays
$configuration = Spyc::YAMLLoad('parameters.yaml');

$parameters = $configuration['parameters'];
$measurements = $configuration['measurements'];
$questions = $configuration['questions'];
$initial_help = $configuration['initial_help'];

$basic_help = $configuration['basic_help'];
$intermediate_help = $configuration['intermediate_help'];
$advanced_help = $configuration['advanced_help'];

//The next 100 lines or so are just checking to make sure all the data for each input is set
$missing_parameter = "Missing \"%s\" attribute on configuration element.";
$too_many_items = "Configuration_element has %d extra element(s).";
$option_no_name = "Parameter option element has no \"name\" option and should.";
$option_no_machine_name = "Parameter option element has no \"machine_name\" option and should.";
$non_numeric_configuration = "The \"min,\" \"max,\" and \"step\" options are numeric.";
$duplicate_property = "Multiple parameters with machine name \"%s\".";
$duplicate_option = "Multiple options with machine_name \"%s\".";
$invalid_default = "The default must be between the minimum and maximum.";
$no_graph_in_location = "There is no graph set to display in location %s.";

$tabs = array();
$all_parameters = array();
$selected_tab = NULL;
$graphs = array();

$graph_locations = array('topleft', 'topright', 'bottomleft', 'bottomright');

foreach ($parameters as $parameter) {
	$required = array("name", "machine_name", "section", "tab");
	$optional = array();
	
	$is_select_control = isset($parameter['values']);
	$is_range_control = isset($parameter['min']);
	$is_submit_control = isset($parameter['id']);
	
	if ($is_range_control)
		array_push($required, "min", "max", "default", "precision");
	else if ($is_select_control)
		array_push($required, "values");
	else if($is_submit_control)
		array_push($required, "id", "button_name");
	
	if (isset($parameter['step']))
		$optional[] = 'step';
	
	if (isset($parameter['description']))
		$optional[] = 'description';

	if(isset($parameter['unit']))
		$optional[] = 'unit';

	if(isset($parameter['subheading']))
		$optional[] = 'subheading';
	
	$size = count($required) + count($optional);
	
	if (count($parameter) > $size)
		trigger_error(sprintf($too_many_items, count($parameter) - $size), E_USER_ERROR);
	
	foreach ($required as $name) {
		if (!isset($parameter[$name]))
			trigger_error(sprintf($missing_parameter, $name), E_USER_ERROR);
	}
	
	$name = $parameter['name'];
	$machine_name = $parameter['machine_name'];
	$tab_name = $parameter['tab'];
	$cleaned_tab_name = preg_replace('/[^a-z]/', '', strtolower($parameter['tab']));
	$section_name = $parameter['section'];
	$cleaned_section_name = preg_replace('/[^a-z]/', '', strtolower($parameter['section']));
	
	$parameter['is_select_control'] = $is_select_control;
	$parameter['is_range_control'] = $is_range_control;
	$parameter['is_submit_control'] = $is_submit_control;
	
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
		    !is_numeric($parameter['precision']) ||
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
	
	if (!isset($tabs[$cleaned_tab_name])) {
		$tabs[$cleaned_tab_name] = array(
			"name" => $tab_name,
			"sections" => array( ),
			"html_id" => "tab-$cleaned_tab_name"
		);
		
		if ($selected_tab == NULL)
			$selected_tab = &$tabs[$cleaned_tab_name];
	}
	
	if (!isset($tabs[$cleaned_tab_name]["sections"][$cleaned_section_name])) {
		$tabs[$cleaned_tab_name]["sections"][$cleaned_section_name] = array(
			"name" => $section_name,
			"parameters" => array( )
		);
	}
	
	$tabs[$cleaned_tab_name]["sections"][$cleaned_section_name]["parameters"][] = $parameter;
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
	
	if (isset($measurement["location"]))
		$optional[] = "location";
	
	$size = count($required) + count($optional);
	
	if (count($measurement) > $size)
		trigger_error(sprintf($too_many_items, count($measurement) - $size), E_USER_ERROR);
	
	if (isset($measurement["location"])) {
		$location = $measurement["location"];
		
		if (isset($graphs[$location]))
			trigger_error(sprintf($duplicate_graph, $location), E_USER_ERROR);
		
		$graphs[$location] = &$measurement;
	}
}

foreach ($questions as $question){
	$required = array("question", "answer");
	foreach($required as $name){
		if(!isset($question[$name]))
			trigger_error(sprintf($missing_parameter, $name), E_USER_ERROR);
	}

	$size = count($required);
	
	if (count($question) > $size)
		trigger_error(sprintf($too_many_items, count($measurement) - $size), E_USER_ERROR);

}

foreach ($graph_locations as $location) {
	if (!isset($graphs[$location]))
		trigger_error(sprintf($no_graph_in_location, $location), E_USER_ERROR);
}
//End checking

//This is the part that runs matlab
if (strtoupper($_SERVER['REQUEST_METHOD']) != 'GET') {
	if (isset($_POST['data'])) {
		
		header('Content-type: application/octet-stream');
		header('Content-Disposition: attachment; filename="WebDICE-Data.csv"');
		header('Cache-Control: private');
		
		echo $_POST['data'];
		
	} else {
		/*
		 *Each user specified parameter is added to a large string ordered as
		 *"parameter name" "parameter value" "parameter2 name" "parameter2 value"
		 *with spaces as delimiters. This string will be used in the command line
		 *loading of matlab. Matlab parses all these inputs and then uses the values.
		*/
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
		
		//This loads the matlab compiler runtime
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
		
		/*
		 *This is the actual command to run matlab. popen opens a pipe to run the matlab compiler runtime.
		 *We pass it the type of run, the type of step, and $flattened, the string of parameters and values.
		 *The output is recorded into $r.
		*/
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
	}
} else {
	
	function format_for_web($text) {
		return preg_replace('/^\(([^)]+)\)/', '<sup>$1</sup>',
			preg_replace('/_\(([^)]+)\)/', '<sub>$1</sub>', htmlentities($text)));
	}
	
	function markdownify($text) {
		$formatted = str_replace("\n", "\n\n", $text);
		
		return Markdown($formatted);
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
  <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=default"></script>
  <script type='text/javascript'>
<?php
	echo "    Options = window.Options || { }\n";
	
	$json = json_encode($measurements);
	$locations = json_encode($graph_locations);
	echo "    Options.measurements = $json;\n";
	echo "    Options.locations = $locations;\n";
	?>
  </script>
  <script type='text/javascript' src='https://www.google.com/jsapi'></script>
  <script type='text/javascript' src='javascript/main.js'></script>
</head>
<body>
<h1 id='heading'> <span>RDCEP</span> :: WebDICE</h1>
<div id='back-to-rdcep'><a href='http://www.rdcep.org/'>Back to RDCEP</a></div>
<a id='display-help'>Documentation</a> <a id='view-source' href='https://www.github.com/RDCEP/chicagowebdice/' target='_blank'>View Source</a>
<div id='sidebar'>
  <form id='submission'>
<?php
		if (count($tabs) <= 1)
			print "    <div id='parameters'>\n";
		else
			print "    <div id='parameters' class='has-tabs'>\n";
		
		print "      <div id='sidebar-tabs' class='tabs'>\n";
		
		/*
		 *We now iterate through each tab, constructing the sidebar. This works by printing html code
		 *using the parameters in the yaml file. The order we go in here is tab:section:item.
		*/
		foreach ($tabs as $tab) {
			$tab_name = format_for_web($tab['name']);
			$tab_id = htmlentities($tab['html_id']);
			
			if ($tab === $selected_tab)
				print "        <a href='' class='selected' id='link-to-$tab_id'>$tab_name</a>\n";
			else
				print "        <a href='' id='link-to-$tab_id'>$tab_name</a>\n";
		}
		print "      </div>\n";
		
		foreach ($tabs as $tab) {
			$tab_id = htmlentities($tab['html_id']);
			$sections = $tab['sections'];
			
			if ($tab === $selected_tab)
				print "      <div id='$tab_id' class='tab selected'>\n";
			else
				print "      <div id='$tab_id' class='tab notselected'>\n";
			
			foreach ($sections as $section) {
				$section_name = format_for_web($section['name']);
				$parameters = $section['parameters'];
				
				print "      <h2>$section_name</h2>\n";
				print "        <ul>\n";
				
				foreach ($parameters as $parameter) {
					$name = format_for_web($parameter['name']);
					$machine_name = htmlentities($parameter['machine_name']);
					$is_select_control = $parameter['is_select_control'];
					$is_range_control = $parameter['is_range_control'];
					$is_submit_control = $parameter['is_submit_control'];
					
					if (isset($parameter['description'])) {
						if(isset($parameter['unit'])){ 
							/*
							 *Support for units was added but they were never implemented as most
							 *parameters are percentages or raw numbers. You may want to delete units.
							*/
							$unit = $parameter['unit'];
							$description = htmlentities($parameter['description']);
							print "          <li><label title='$description'>$name ($unit) ";
						} else {
							$description = htmlentities($parameter['description']);
							print "          <li><label title='$description'>$name ";
						}
					} else {
						if(isset($parameter['unit'])){
							$unit = $parameter['unit'];
							print "          <li>$name  ($unit) ";
						} else {
							print "          <li><label>$name ";
						}
					}

					
					if ($is_select_control) {
						$values = $parameter['values'];
						
						print "<select name='$machine_name'>\n";
						
						foreach ($values as $value) {
							$option_machine_name = $value['machine_name'];
							$option_name = $value['name'];
							
							if (isset($value['description'])) {
								$description = htmlentities($value['description']);
							
								print "            <option name='$option_machine_name' ";
								print "title='$description'>$option_name</option>\n";
							} else {
								print "            <option name='$option_machine_name'>$option_name</option>\n";
							}
						}
						
						print "            </select></li>\n";

					} else if ($is_range_control) {
						$min = $parameter['min'];
						$max = $parameter['max'];
						$step = $parameter['step'];
						$default = $parameter['default'];
						$precision = $parameter['precision'];

						$tickMarkRight = ((($max - $default)/($max - $min)) * 66);
						$tickMarkRight = ($tickMarkRight - (pow($tickMarkRight, 2.1362) *0.0008)) + 6; //to adjust for spacing issues
						$tickMarkRightWithUnit = $tickMarkRight . "px";
						print"<span id='tick' style=\"right:$tickMarkRightWithUnit\">^</span>";
				
						print "<span class='label'>$default</span> <input name='$machine_name' ";
						print "type='range' min='$min' max='$max' step='$step' value='$default' data-prec='$precision'/></label></li>\n";

					} else if ($is_submit_control){
						$id = $parameter['id'];
						$button_name = $parameter['button_name'];

						print "<input type='submit' id='$id' value='$button_name'/>";

					}
				}

				print "        </ul>\n";
			}
			
			print "      </div>";
		}
		/*
		 *The next bits are going to be HTML that creates all the buttons and graphs.
		 *What each button does is handled in the javascript code.
		*/
		?>
    </div>
    <div id='controls'>
      <input type='reset' id='reset-inputs' value='Reset Inputs'/>
      <input type='submit' id='delete-all' value='Clear Graphs' disabled='disabled'/>
      <input type='submit' value='Run Model'/>
    </div>
  </form>
  <ul id='runs'></ul>
</div>
<div id='content' class='hasnoruns'>
  <div class='tabs'><a href='' class='selected' id='link-to-four-graphs'>Four Graphs</a> <a href='#' id='link-to-custom-graph'>Single Graph</a></div>
  <div class='initial'>
<?php
		$paragraphs = explode("\n", $initial_help);
		
		foreach ($paragraphs as $paragraph) {
			echo "    <p>$paragraph</p>\n";
		}
?>  </div>
  <div id='four-graphs' class='tab selected'></div>
  <div id='custom-graph' class='tab notselected'>
    <div id='large-graph'></div>
    <div id='graph-controls'>
      <div>
        <h2>X-Axis</h2>
        <select id='select-x-axis'>
          <option value='year'>Year</option>
<?php
		foreach ($measurements as $measurement) {
			$machine_name = htmlentities($measurement['machine_name']);
			$measurement_name = htmlentities($measurement['name']);

			print "          <option value='$machine_name'>$measurement_name</option>\n";
		}
?>
         </select>
         <label><input type='checkbox' id='logarithmic-x'/> Logarithmic</label>
      </div>
      <div>
        <h2>Y-Axis</h2>
        <select id='select-y-axis'>
<?php
		foreach ($measurements as $measurement) {
			$machine_name = htmlentities($measurement['machine_name']);
			$measurement_name = htmlentities($measurement['name']);

			print "          <option value='$machine_name'>$measurement_name</option>\n";
		}
?>
        </select>
        <label><input type='checkbox' id='logarithmic-y'/> Logarithmic</label>
      </div>
      <div>
        <h2>Labels</h2>
        <select id='series-labels'>
          <option value='none'>None</option>
          <option value='years'>Years</option>
        </select>
      </div>
    </div>
  </div>
  <form method='post' id='download-data' action='index.php' target='_blank'>
    <textarea name='data' id='download-textarea'></textarea>
    <input type='submit' value='Download Selected Runs as CSV'/>
  </form>
</div>
<!-- This is where we create the "documentaion page" overlay. -->
<div id='overlay'>
  <div class='slug'></div>
  <div class='article' id='advanced-help'>
    <div class='tabs'>
      <a href='' class='selected' id='link-to-help-basic'>Basic</a>
      <a href='' id='link-to-help-intermediate'>Intermediate</a>
      //<a href='' id='link-to-faq'>FAQ</a>
      <a href='' id='link-to-help-advanced'>Model Equations</a>
    </div>
    <?php
	/*
	 **This is the construction page for the FAQ. We iterate through the yaml file, adding questions to the
	 **string $top and answers to the string $bottom, complete with line breaks, whitespace, and internal 
	 **bookmarks for <a> linking the questions to answers. the '.' concatenates strings.
	 **NOTE: The FAQ is not set to display because the documentation pdfs have a sort of
	* *FAQ in them, rendering this tab unecessary. I will leave in the support for it.
	*$quesnum = 0;
	*$top = "<h1>FAQ<br /><u>Questions</u></h1><br />";
	*$bottom = "<h1><u>Answers</u></h1><br />";
	*foreach($questions as $questiondata){
	*	$question = $questiondata['question'];
	*	$question_shortname = "question" . $quesnum;
	*	$answer = $questiondata['answer'];

	*	$top = $top . "<a href=#" . $question_shortname . "> " . $question . " </a> </br>";
	*	$bottom = $bottom . "<a name=" . $question_shortname . "></a>" . "<u><h3>" . $question . "</h3></u>" . $answer . "<br /><br />";

	*	$quesnum = $quesnum + 1;
	*}

	*$faq = $top . "<br /><br />" . $bottom;
	*/
    ?>
    
    <div id='help-basic' class='tab selected'><object data="images/basicTab.pdf" type="application/pdf" width=100% height=98%></object></div>
    <div id='help-intermediate' class='tab notselected'><object data="images/intermediateTab.pdf" type="application/pdf" width=100% height=98%></object></div>
    //<div id='faq' class='tab notselected'><?php echo markdownify("$faq"); ?></div>
    <div id='help-advanced' class='tab notselected'><object data="images/equationTab.pdf" type="application/pdf" width=100% height=98%></object></div>
    
    <a href='' id='hide-help'>Hide</a>
  </div>
</div>
</body>
</html><?php } ?>
