(function() {
  "use strict";

  var parameter_tabs = d3.selectAll('#parameter_tabs li'),
    title_tabs = d3.selectAll('#title_legend li'),
    parameter_tabs_a = parameter_tabs.selectAll('a'),
    title_tabs_a = title_tabs.selectAll('a'),
    parameters = d3.select('#parameters_wrap');

  parameter_tabs.on('click', function() {

    var t = d3.select(this),
      tab = t.attr('data-pane'),
      form = d3.select('#parameter_form');

    form.selectAll('section').classed('visuallyhidden', true);
    d3.select('#'+tab+'_parameters_pane').classed('visuallyhidden', false);

    parameter_tabs.classed('selected', false);
    t.classed('selected', true);

  });

  title_tabs.on('click', function() {

    var t = d3.select(this),
      tab = t.attr('data-pane');

    title_tabs.classed('selected', false);
    t.classed('selected', true);

    if (tab == 'parameters') {
      parameters.classed('visuallyhidden', false);
//      parameters.hide();
    } else if (tab == 'runs') {
      parameters.classed('visuallyhidden', true);
    } else {
      parameters.classed('visuallyhidden', true);
      d3.selectAll('.chart-pane').classed('selected', false);
      d3.select('#' + tab).classed('selected', true);
    }

  });

})();