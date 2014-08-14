(function() {
  "use strict";

  var hash = window.location.hash.split(':')
    , hash_section = hash[0].slice(1)
    , hash_tab = hash[1]
    , parameter_tabs = d3.selectAll('#parameter_tabs li[data-pane]')
    , title_tabs = d3.selectAll('#title_legend li')
    , parameters = d3.select('#parameters_wrap')
    , runs = d3.select('#runs_wrap')
    , t
  ;

  if (hash_section == 'graph') {

    var pane = d3.select('#' + hash_tab + '_graphs')
      , parent = d3.select(pane.node().parentNode)
    ;

    t = d3.select('#' + hash_tab + '_graph')
    d3.selectAll('.graph-tab').classed('selected', false);
    parent.select('.pane.selected').classed('selected', false);
    pane.classed('selected', true).style('z-index', 998);

  }

  if (hash_section == 'option') {

    var vis
    ;

    d3.selectAll('.option-tab').classed('selected', false);
    t = d3.select('#' + tab + '_tab')

    if (tab == 'parameters') {

      vis = !parameters.classed('visuallyhidden');
      t.classed('selected', !vis);
      parameters.classed('visuallyhidden', vis).style('z-index', 998);
      runs.classed('visuallyhidden', true);

    } else if (tab == 'runs') {
      vis = !runs.classed('visuallyhidden');
      t.classed('selected', !vis);
      runs.classed('visuallyhidden', vis).style('z-index', 998);
      parameters.classed('visuallyhidden', true);
    }

  }

  parameter_tabs.on('click', function() {

    var t = d3.select(this),
      tab = t.attr('data-pane'),
      form = d3.select('#parameter_form');

    form.selectAll('section').classed('selected', false);
    d3.select('#' + tab).classed('selected', true);

    parameter_tabs.classed('selected', false);
    t.classed('selected', true);

  });

  title_tabs.on('click', function() {

    var t = d3.select(this),
      tab = t.attr('data-pane'),
      pane = d3.select('.pane[data-pane="' + tab + '"]'),
//      parent = d3.select(pane.node().parentNode),
      vis;

    if (t.classed('graph-tab')) {
      d3.selectAll('.graph-tab').classed('selected', false);
    } else {
      d3.selectAll('.option-tab').classed('selected', false);
    }

    t.classed('selected', true);

    if (tab == 'parameters') {
      vis = !parameters.classed('visuallyhidden');
      t.classed('selected', !vis);
      parameters.classed('visuallyhidden', vis).style('z-index', 998);
      runs.classed('visuallyhidden', true);
      window.location.hash = 'option:parameters';
    } else if (tab == 'runs') {
      vis = !runs.classed('visuallyhidden');
      t.classed('selected', !vis);
      runs.classed('visuallyhidden', vis).style('z-index', 998);
      parameters.classed('visuallyhidden', true);
    } else {
      //
      parameters.classed('visuallyhidden', true);
      d3.select('#parameters_tab').classed('selected', false);
      d3.select(pane.node().parentNode).select('.pane.selected').classed('selected', false);
      pane.classed('selected', true).style('z-index', 998);
      window.location.hash = 'graph:' + tab.replace('_graphs', '');
    }

  });

})();