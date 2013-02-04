<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8"/>
    <title>RDCEP :: WebDICE</title>
    <link rel="stylesheet" href="/static/css/styles.css?{{ now }}" type="text/css" media="all" title="Default Stylesheet"/>
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
        <div id="parameters" class="has-tabs">
            <div id="sidebar-tabs" class="tabs">
                <a href="" class="selected" id="link-to-tab-policy">Policy</a>
                <a href="" id="link-to-tab-beliefs">Beliefs</a>
            </div>
            <div id="tab-policy" class="tab selected">
                <h2>
                    <input type="radio" value="default" name="policy_type" style="width:auto" checked="checked"/>
                    Default policy
                </h2>
                <h2 class="disabled">
                    <input type="radio" value="carbon_tax" name="policy_type" style="width:auto" disabled="disabled"/>
                    Simulated carbon tax</h2>
                <ul>
                    <li class="disabled init-disabled"><label title="Simulated carbon tax" >Tax rate <span class="label"><span class="label-number">0</span><span>%</span></span></label>
                        <input name="carbon_tax" class="percent" type="range" min="0" max="1" step=".01" value="0" data-prec="2" disabled="disabled"/>
                        <div class="tick-wrap"><span class="tick" style="left:-50%" >&bullet;</span></div>
                    </li>
                </ul>
                <h2>
                    <input type="radio" value="treaty" name="policy_type" style="width:auto"/>
                    Simulated climate treaty:<br/>Choose limitations on emissions (as a percent of 2005 emissions):</h2>
                <ul>
                    <li class="disabled init-disabled"><label title="The mandated decrease in emissions by 2050 as a share of 2005 year emissions." >2050 <span class="label"><span class="label-number">100</span><span>%</span></span></label>
                        <input name="e2050" class="reverse" type="range" min="0" max="100" step="5" value="0" data-prec="0" disabled="disabled"/>
                        <div class="tick-wrap"><span class="tick" style="left:-50%" >&bullet;</span></div></li>
                    <li class="disabled init-disabled"><label title="The mandated decrease in emissions by 2100 as a share of 2005 year emissions." >2100 <span class="label"><span class="label-number">100</span><span>%</span></span></label>
                        <input name="e2100" class="reverse" type="range" min="0" max="100" step="5" value="0" data-prec="0" disabled="disabled"/>
                        <div class="tick-wrap"><span class="tick" style="left:-50%" >&bullet;</span></div></li>
                    <li class="disabled init-disabled"><label title="The mandated decrease in emissions by 2150 as a share of 2005 year emissions." >2150 <span class="label"><span class="label-number">100</span><span>%</span></span></label>
                        <input name="e2150" class="reverse" type="range" min="0" max="100" step="5" value="0" data-prec="0" disabled="disabled"/>
                        <div class="tick-wrap"><span class="tick" style="left:-50%" >&bullet;</span></div></li>
                </ul>
                <h2>
                    <input type="radio" value="optimized" name="policy_type" style="width:auto" />
                    <input type="hidden" value="false" id="optimize" name="optimize"/>
                    Optimized policy
                </h2>
            </div>
            <div id="tab-beliefs" class="tab notselected">
                <h2>Your beliefs about the climate and the future</h2>
                <ul>
                    <li><label title="Temperature increase in degrees C from doubling of atmospheric CO2" >Climate sensitivity: How much will temperatures go up?</label>
                        <input name="t2xco2"  type="range" min="1" max="5" step="0.5" value="3.0" data-prec="1"/>
                        <div class="minimum-range-value">less than expected</div>
                        <div class="maximum-range-value">more than expected</div>
                        <span class="help-button">?</span>
                    </li>
                    <li><label title="Increase in harms from climate change due to an increase in temperatures" >How large will the harms be?</label>
                        <input name="a3"  type="range" min="1" max="4" step="0.5" value="2.0" data-prec="1"/>
                        <span class="help-button">?</span>
                    </li>
                    <li><label title="Decline in the rate of growth in productivity over time" >Decline in rate of growth of productivity</label>
                        <input name="dela"  type="range" min="0.0" max="1.5" step="0.05" value="0.1" data-prec="2"/>
                        <span class="help-button">?</span>
                    </li>
                    <li><label title="Rate of decline in energy use per $ of GDP" >Change in energy intensity</label>
                        <input name="dsig"  type="range" min="0.0" max="6.0" step="0.1" value="0.3" data-prec="1"/>
                        <span class="help-button">?</span>
                    </li>
                    <li><label title="Cost of replacing all emissions in 2012 $ per ton of CO_{2} , relative to future cost" >How low will the costs of renewables go?</label>
                        <input name="backrat"  type="range" min="1.0" max="4" step="0.5" value="2.0" data-prec="1"/>
                        <div class="minimum-range-value">very inexpensive</div>
                        <div class="maximum-range-value">very expensive</div>
                        <span class="help-button">?</span>
                    </li>
                </ul>
            </div>
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
    <div class="tabs"><a href="" class="selected" id="link-to-four-graphs">Basic Graphs</a>
        <a href="#" id="link-to-custom-graph">Advanced Graph</a></div>
    <div class="initial">
        {{! paragraphs_html }}
    </div>
    <div id="four-graphs" class="tab selected"></div>
    <div id="custom-graph" class="tab notselected">
        <div id="large-graph">
            <div id="large-graph-chart" style="height:90%;"></div>
            <div id="large-graph-zoom" style="height:10%;"></div>
        </div>
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
<div id="help-wrapper">
    <div class="help-text" id="t2xco2-help">
        <p>TKTK</p>
    </div>
    <div class="help-text" id="a3-help">
        <p>TKTK</p>
    </div>
    <div class="help-text" id="dela-help">
        <p>TKTK</p>
    </div>
    <div class="help-text" id="dsig-help">
        <p>TKTK</p>
    </div>
    <div class="help-text" id="backrat-help">
        <p>TKTK</p>
    </div>
</div>
<script src="/static/js/webdice_help.js"></script>
</body>
</html>
