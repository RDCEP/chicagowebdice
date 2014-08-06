(function() {
  "use strict";

  var parameter_tabs = d3.selectAll('#parameter_tabs li'),
    title_tabs = d3.selectAll('#title_legend li'),
    parameters = d3.select('#parameters_wrap'),
    runs = d3.select('#runs_wrap');

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
      pane = d3.select('#' + tab),
      parent = d3.select(pane.node().parentNode),
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
    } else if (tab == 'runs') {
      vis = !runs.classed('visuallyhidden');
      t.classed('selected', !vis);
      runs.classed('visuallyhidden', vis).style('z-index', 998);
      parameters.classed('visuallyhidden', true);
    } else {
//      parameters.classed('visuallyhidden', true);
//      runs.classed('visuallyhidden', true);
      parent.select('.pane.selected').classed('selected', false);
      pane.classed('selected', true).style('z-index', 998);
    }

  });

})();