<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>RDCEP :: WebDICE</title>
  <link rel="stylesheet" href="styles.css" type="text/css" media="screen" title="Default Stylesheet" charset="utf-8"/>
  <link rel="stylesheet" type="text/css" media="screen, projection" href="http://www.frequency-decoder.com/demo/fd-slider/css/fd-slider.mhtml.min.css" />
  <script src="javascript/fd-slider.min.js"></script>
  <script src="javascript/jquery.min.js"></script>
  <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=default"></script>
  <script type='text/javascript'>
    Options = window.Options || { };
	Options.measurements = {{ measurements }};
	Options.locations = {{ graph_locations }};
  </script>
  <script type='text/javascript' src='https://www.google.com/jsapi'></script>
  <script type='text/javascript' src='javascript/main.js'></script>
</head>
<body>
<h1 id='heading'> <span>RDCEP</span> :: WebDICE</h1>
<div id='back-to-rdcep'><a href='http://www.rdcep.org/'>Back to RDCEP</a></div>
<ul id='help-menu'>
  <li id='display-help'>Documentation<ul>
    <li><a href="/docs/webdice_basic_help.pdf">Basic</a></li>
    <li><a href="/docs/webdice_intermediate_help.pdf">Intermediate</a></li>
    <li><a href="/docs/webdice_equation_help.pdf">Equations</a></li>
  </ul></li>
  <li id='view-source'><a href='https://www.github.com/RDCEP/chicagowebdice/' target='_blank'>View Source</a></li>
</ul>
<div id='sidebar'>
  <form id='submission'>
{{! tabs_html }}
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
  <div class='tabs'><a href='' class='selected' id='link-to-four-graphs'>Basic Graphs</a> <a href='#' id='link-to-custom-graph'>Advanced Graph</a></div>
  <div class='initial'>
{{! paragraphs_html }}
  </div>
  <div id='four-graphs' class='tab selected'></div>
  <div id='custom-graph' class='tab notselected'>
    <div id='large-graph'></div>
    <div id='graph-controls'>
      <div>
        <h2>X-Axis</h2>
        <select id='select-x-axis'>
          <option value='year'>Year</option>
{{! dropdowns }}
         </select>
         <label><input type='checkbox' id='logarithmic-x'/> Logarithmic</label>
      </div>
      <div>
        <h2>Y-Axis</h2>
        <select id='select-y-axis'>
{{! dropdowns }}
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
</body>
</html>
