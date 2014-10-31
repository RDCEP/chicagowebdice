(function() {
  "use strict";

  var hashes = window.location.hash.slice(1).split(',');

  for (var i = 0; i < hashes.length; ++i) {

    var hash = hashes[i].split(':')
      , hash_section = hash[0]
      , hash_tab = hash[1]
      , parameter_tabs = d3.selectAll('#parameter_tabs li[data-pane]')
      , title_tabs = d3.selectAll('#title_legend li')
        .filter(function() { return !d3.select(this).classed('glossary'); })
      , parameters = d3.select('#parameters_wrap')
      , runs = d3.select('#runs_wrap')
      , t
      ;

    if (hash_section == 'graph') {

      var tab = d3.select('.graph-tab[data-pane="' + hash_tab + '"]')
        , pane = d3.select('#' + hash_tab + '_graphs')
        , parent = d3.select(pane.node().parentNode)
        ;

      d3.selectAll('.graph-tab').classed('selected', false);
      tab.classed('selected', true);
      parent.select('.pane.selected').classed('selected', false);
      pane.classed('selected', true).style('z-index', 998);

    }

    if (hash_section == 'option') {

      var vis
        ;

      d3.selectAll('.option-tab').classed('selected', false);
      t = d3.select('#' + hash_tab + '_tab');

      if (hash_tab == 'parameters') {

        vis = !parameters.classed('visuallyhidden');
        t.classed('selected', !vis);
        parameters
          .classed('selected', !vis)
          .classed('visuallyhidden', vis)
          .style('z-index', 998);
        runs.classed('visuallyhidden', true);

      } else if (tab == 'runs') {
        vis = !runs.classed('visuallyhidden');
        t.classed('selected', !vis);
        runs
          .classed('selected', !vis)
          .classed('visuallyhidden', vis)
          .style('z-index', 998);
        parameters.classed('visuallyhidden', true);
      }

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
      vis;

    if (t.classed('graph-tab')) {
      d3.selectAll('.graph-tab').classed('selected', false);
      d3.selectAll('.graph-tab').style('font-weight', null);
    } else {
      d3.selectAll('.option-tab').classed('selected', false);
//      d3.selectAll('.graph-tab').style('font-weight', 'normal');
    }

    t.classed('selected', true);

    if (tab == 'parameters') {
      vis = !parameters.classed('visuallyhidden');
      t.classed('selected', !vis);
      parameters
        .classed('selected', !vis)
        .classed('visuallyhidden', vis)
        .style('z-index', 998);
      runs.classed('visuallyhidden', true);
      if (!vis) {
        d3.selectAll('.graph-tab').style('font-weight', 'normal');
        window.location.hash = 'option:parameters';
      } else {
        var g = d3.select('.graph-tab.selected');
        g.style('font-weight', null);
        window.location.hash = 'graph:' + g.attr('data-pane');
      }

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