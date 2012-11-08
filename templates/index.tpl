<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
  <title>RDCEP :: WebDICE</title>
  <link rel="stylesheet" href="/static/css/styles.css?{{ now }}" type="text/css" media="screen" title="Default Stylesheet"/>
  <link rel="stylesheet" type="text/css" media="screen, projection" href="/static/css/fd-slider.min.css" />
  <script src="/static/js/fd-slider.min.js"></script>
  <script src="/static/js/jquery.min.js"></script>
  <script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=default"></script>
  <script type="text/javascript">
    Options = window.Options || { };
	Options.measurements = {{! measurements }};
	Options.locations = {{! graph_locations }};
  </script>
  <script type="text/javascript" src="https://www.google.com/jsapi"></script>
  <script type="text/javascript" src="/static/js/main.js?{{ now }}"></script>
</head>
<body>
<h1 id="heading"> <span>RDCEP</span> :: WebDICE</h1>
<div id="back-to-rdcep"><a href="http://www.rdcep.org/">Back to RDCEP</a></div>
<ul id="help-menu">
  <li id="display-help">Documentation<ul>
    <li><a target="_blank" href="/static/docs/webdice_basic_help.pdf">Basic</a></li>
    <li><a target="_blank" href="/static/docs/webdice_intermediate_help.pdf">Intermediate</a></li>
    <li><a target="_blank" href="/static/docs/webdice_equation_help.pdf">Equations</a></li>
  </ul></li>
  <li id="view-source"><a href="https://www.github.com/RDCEP/chicagowebdice/" target="_blank">View Source</a></li>
</ul>
<div id="sidebar">
  <form id="submission" method="post" action="/">
<!--TODO: replace this with {{! tabs_html }} -->
      <div id="parameters" class="has-tabs">
          <div id="sidebar-tabs" class="tabs">
              <a href="" class="selected" id="link-to-tab-basic">Basic</a>
              <a href="" id="link-to-tab-advanced">Advanced</a>
              <a href="" id="link-to-tab-optimization">Optimization</a>
          </div>

          <div id="tab-basic" class="tab selected">
              <h2>Your beliefs about the climate and the future</h2>
              <ul>
                  <li><label title="Temperature increase in degrees C from doubling of atmospheric CO2" >Climate sensitivity: How much will temperatures go up? <span class="label"><span class="label-number">3.0</span><span>°C</span></span></label> <input name="t2xco2"  type="range" min="1" max="5" step="0.5" value="3.0" data-prec="1"/>
                      <div class="tick-wrap"><span class="tick" style="left:0%" >&bullet;</span></div></li>
                  <li><label title="Increase in harms from climate change due to an increase in temperatures" >Exponent of damage function: How large will the harms be? <span class="label"><span class="label-number">2.0</span></span></label> <input name="a3"  type="range" min="1" max="4" step="0.5" value="2.0" data-prec="1"/>
                      <div class="tick-wrap"><span class="tick" style="left:-16%" >&bullet;</span></div></li>
                  <li><label title="Decline in the rate of growth in productivity over time" >How much will growth slow down in the future? <span class="label"><span class="label-number">0.1</span><span>%</span></span></label> <input name="dela"  type="range" min="0.05" max="1.5" step="0.05" value="0.1" data-prec="2"/>
                      <div class="tick-wrap"><span class="tick" style="left:-46%" >&bullet;</span></div></li>
                  <li><label title="Rate of decline in energy use per $ of GDP" >Change in Energy intensity (higher number means more energy intensive) <span class="label"><span class="label-number">0.3</span><span>%</span></span></label> <input name="dsig"  type="range" min="0.0" max="6.0" step="0.1" value="0.3" data-prec="1"/>
                      <div class="tick-wrap"><span class="tick" style="left:-45%" >&bullet;</span></div></li>
              </ul>
              <h2>Simulated climate treaty <input type="checkbox" id="treaty_switch" name="treaty_switch" style="width:auto"/>:<br/>Choose limitations on emissions (as a percent of 2005 emissions):</h2>
              <ul>
                  <li class="disabled"><label title="The mandated decrease in emissions by 2050 as a share of 2005 year emissions." >2050 <span class="label"><span class="label-number">500</span><span>%</span></span></label> <input name="e2050"  type="range" min="0" max="500" step="10" value="500" data-prec="0" disabled="disabled"/>
                      <div class="tick-wrap"><span class="tick" style="left:50%" >&bullet;</span></div></li>
                  <li class="disabled"><label title="The mandated decrease in emissions by 2100 as a share of 2005 year emissions." >2100 <span class="label"><span class="label-number">500</span><span>%</span></span></label> <input name="e2100"  type="range" min="0" max="500" step="10" value="500" data-prec="0" disabled="disabled"/>
                      <div class="tick-wrap"><span class="tick" style="left:50%" >&bullet;</span></div></li>
                  <li class="disabled"><label title="The mandated decrease in emissions by 2150 as a share of 2005 year emissions." >2150 <span class="label"><span class="label-number">500</span><span>%</span></span></label> <input name="e2150"  type="range" min="0" max="500" step="10" value="500" data-prec="0" disabled="disabled"/>
                      <div class="tick-wrap"><span class="tick" style="left:50%" >&bullet;</span></div></li>
              </ul>
          </div>
          <div id="tab-advanced" class="tab notselected">
              <h2>Additional Parameters</h2>
              <ul>
                  <li><label title="Number, in millions, that the population grows asymptotically towards" >Max population <span class="label"><span class="label-number">8600</span><span> billions</span></span></label> <input name="popasym"  type="range" min="8000" max="12000" step="200" value="8600" data-prec="0"/>
                      <div class="tick-wrap"><span class="tick" style="left:-35%" >&bullet;</span></div></li>
                  <li><label title="Rate of depreciation per year" >Depreciation rate <span class="label"><span class="label-number">0.1</span><span>%</span></span></label> <input name="dk"  type="range" min="0.08" max="0.2" step="0.01" value="0.1" data-prec="2"/>
                      <div class="tick-wrap"><span class="tick" style="left:-33%" >&bullet;</span></div></li>
                  <li><label title="Savings are per year" >Savings rate <span class="label"><span class="label-number">0.2</span><span>%</span></span></label> <input name="savings"  type="range" min="0.15" max="0.25" step="0.05" value="0.2" data-prec="2"/>
                      <div class="tick-wrap"><span class="tick" style="left:0%" >&bullet;</span></div></li>
                  <li><label title="Fossil fuels remaining, measured in CO2 emissions" >Fossil fuel reserves <span class="label"><span class="label-number">6000</span><span> Gt&nbsp;C</span></span></label> <input name="fosslim"  type="range" min="6000" max="9000" step="500" value="6000" data-prec="0"/>
                      <div class="tick-wrap"><span class="tick" style="left:-50%" >&bullet;</span></div></li>
              </ul>
              <h2>Model Design</h2>
              <ul>
                  <li><label title="Oceanic model of carbon transfer" class="disabled">Carbon cycle </label>
                      <select name="oceanmodel" disabled="disabled">
                          <option id="dice_carbon">DICE</option>
                      </select></li>
                  <li><label title="Way that climate change harms enter the economy" class="disabled">Damages model </label>
                      <select name="damages_model" disabled="disabled">
                          <option id="dice" title="Climate change destroys a certain percentage of global output">DICE Damages to Gross Output</option>
                      </select></li>
              </ul>
              <h2>Costs of emissions control</h2>
              <ul>
                  <li><label title="Additional cost from more abatement" >Marginal cost of abatement <span class="label"><span class="label-number">2.8</span></span></label> <input name="expcost2"  type="range" min="2" max="4" step="0.1" value="2.8" data-prec="1"/>
                      <div class="tick-wrap"><span class="tick" style="left:-10%" >&bullet;</span></div></li>
                  <li><label title="Rate of decline in costs of reduction emissions" >Rate of decline of clean energy costs <span class="label"><span class="label-number">0.05</span><span>%</span></span></label> <input name="gback"  type="range" min="0" max="0.2" step="0.05" value="0.05" data-prec="2"/>
                      <div class="tick-wrap"><span class="tick" style="left:-25%" >&bullet;</span></div></li>
                  <li><label title="Cost of replacing all emissions in 2012 $ per ton of CO_{2} , relative to future cost" >Ratio of current to future clean energy costs <span class="label"><span class="label-number">2.0</span></span></label> <input name="backrat"  type="range" min="0.5" max="4" step="0.5" value="2.0" data-prec="1"/>
                      <div class="tick-wrap"><span class="tick" style="left:-7%" >&bullet;</span></div></li>
              </ul>
          </div>
          <div id="tab-optimization" class="tab notselected">
              <h2>Additional Parameters</h2>
              <ul>
                  <li><label title="Exponent of consumption in utility function" >Elasticity of marg. consump. <span class="label"><span class="label-number">2.0</span></span></label> <input name="elasmu"  type="range" min="1" max="3" step="0.1" value="2.0" data-prec="1"/>
                      <div class="tick-wrap"><span class="tick" style="left:0%" >&bullet;</span></div></li>
                  <li><label title="Discount rate applied to utility" >Pure rate of time preference <span class="label"><span class="label-number">0.015</span></span></label> <input name="prstp"  type="range" min="0" max="4" step="0.005" value="0.015" data-prec="3"/>
                      <div class="tick-wrap"><span class="tick" style="left:-49%" >&bullet;</span></div></li>
              </ul>
              <h2>Run Model</h2>
              <ul>
                  <li><label >Run optimization </label><input type="submit" id="run-opt" value="Run"/></li>
              </ul>
          </div>
<!-- ENDTODO -->
    </div>
    <div id="controls">
      <input type="reset" id="reset-inputs" value="Reset Inputs"/>
      <input type="submit" id="delete-all" value="Clear Graphs" disabled="disabled"/>
      <input type="submit" value="Run Model"/>
    </div>
  </form>
  <ul id="runs"></ul>
</div>
<div id="content" class="hasnoruns">
  <div class="tabs"><a href="" class="selected" id="link-to-four-graphs">Basic Graphs</a> <a href="#" id="link-to-custom-graph">Advanced Graph</a></div>
  <div class="initial">
{{! paragraphs_html }}
  </div>
  <div id="four-graphs" class="tab selected"></div>
  <div id="custom-graph" class="tab notselected">
    <div id="large-graph"></div>
    <div id="graph-controls">
      <div>
        <h2>X-Axis</h2>
        <select id="select-x-axis">
          <option value="year">Year</option>
{{! dropdowns }}
         </select>
         <label><input type="checkbox" id="logarithmic-x"/> Logarithmic</label>
      </div>
      <div>
        <h2>Y-Axis</h2>
        <select id="select-y-axis">
{{! dropdowns }}
        </select>
        <label><input type="checkbox" id="logarithmic-y"/> Logarithmic</label>
      </div>
      <div>
        <h2>Labels</h2>
        <select id="series-labels">
          <option value="none">None</option>
          <option value="years">Years</option>
        </select>
      </div>
    </div>
  </div>
  <form method="post" id="download-data" action="/csv" target="_blank">
    <textarea name="data" id="download-textarea"></textarea>
    <input type="submit" value="Download Selected Runs as CSV"/>
  </form>
</div>
</body>
</html>
