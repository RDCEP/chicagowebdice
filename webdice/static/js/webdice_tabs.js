(function() {
  "use strict";

  var parameter_tabs = d3.selectAll('#parameter_tabs li'),
    title_tabs = d3.selectAll('#title_legend li'),
    parameters = d3.select('#parameters_wrap');

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
      parent = d3.select(pane.node().parentNode);

    console.log(pane);

    title_tabs.classed('selected', false);
    t.classed('selected', true);

    if (tab == 'parameters') {
      parameters.classed('visuallyhidden', false);
    } else if (tab == 'runs') {
      parameters.classed('visuallyhidden', true);
    } else {
      parameters.classed('visuallyhidden', true);
      parent.select('.pane.selected').classed('selected', false);
      pane.classed('selected', true);
    }

  });

})();