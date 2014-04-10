(function() {
  'use strict';

  var content_div = d3.select('#main_content'),
    runs_ul = d3.select('#runs'),
    submission = d3.select('#submission'),
    overlay_div = d3.select('#overlay'),
    advancedHelpDiv = d3.select('#advanced-help'),
    sidebar_div = d3.select('#sidebar'),
    runsBeingDisplayed = [],
    nextRunNumber = 1,
    charts = {
    },
    data = [],
    handlersForViewportChanged = [],
    handlersForDataChanged = [],
    color_list = [
      //d3.rgb(0, 0, 0), //black
      d3.rgb(86, 180, 233), // sky blue
      d3.rgb(230, 159, 0),  // orange
      d3.rgb(0, 158, 115),  // bluish green
      d3.rgb(240, 228, 66), // yellow
      d3.rgb(0, 114, 178),  // blue
      d3.rgb(213, 94, 0),   // vermilion
      d3.rgb(204, 121, 167) // reddish purple
    ],
    padding = [50, 10, 50, 100],
    simulation_periods = 60,
    graph_periods = 20,
    period_length = 10,
    start_year = 2005,
    end_year = start_year + ((graph_periods-1) * period_length),
    colorsUsed = 0,
    numberOfRunsInProgress = 0,
    active_graph_pane,
    color;

  d3.select('#top_nav').style('padding', '0 '+padding[1]+'px 0 '+padding[3]+'px');
  d3.select('#title_legend').style('padding', '0 '+padding[1]+'px 0 '+padding[3]+'px');

  var graph_tabs = d3.selectAll('#title_legend li');
  graph_tabs.on('click', function() {
    var t = d3.select(this);
    graph_tabs.classed('selected', false);
    t.classed('selected', true);
    d3.selectAll('.chart-pane').classed('selected', false);
    d3.select('#' + t.attr('data-pane')).classed('selected', true);
  })

  var active_tab = function() {
    d3.selectAll('.tabs').each(function() {
      var t = d3.select(this),
        current_tab = t.select('.selected'),
        current_pane = t.select('#'+current_tab.attr('data-pane'));
      t.selectAll('a').on('click', function() {
        var tt = d3.select(this);
        if (current_tab != tt) {
          current_tab.classed('selected', false);
          current_pane.classed('selected', false);
          current_tab = tt;
          current_pane = tt.select('#'+current_tab.attr('data-pane'));
        }
        current_tab.classed('selected', true);
        current_pane.classed('selected', true);
      });
    });

  };

  var resize_charts = function() {

    for (var chart in charts) {
      var visible_chart_wrap = d3.select('.chart-pane.selected'),
        width = visible_chart_wrap.node().clientWidth,
        height = visible_chart_wrap.node().clientHeight;
      if (chart.small) {
        charts[chart].chart.width(width / 2 - 1).height(height / 2).redraw(); }
      else { chart.width(width - 1).height(height).redraw(); }
    }


  };

  var initialize_charts = function(_data, _params, _metadata) {

    console.log(_metadata);

    for (var p in _data) {
      if (_data.hasOwnProperty(p)) {
        var this_data = [];
        _data[p].forEach(function(d, i) {
          if (i < graph_periods) {
            this_data.push({
              y: d,
              y0: 0,
              x: new Date(start_year + i * period_length, 0, 1)
            })
          }
        });



        var chart_wrap = d3.select('#'+p+'_chart');
        if (!chart_wrap.empty()) {

          var ext = d3.extent(this_data, function(d, i) { return d.y; }),
            min = ext[0] == 0 ? 0 : ext[0] - (ext[1] - ext[0]) / 10,
            max = ext[1] + (ext[1] - ext[0]) / 10;

          charts[p] = {
            chart: new WebDICEGraph()
              .padding(padding[0], padding[1], padding[2], padding[3])
//              .width(0).height(0)
              .select(p+'_chart')
              .x(d3.time.scale())
              .y(d3.scale.linear())
              .domain([new Date(start_year, 0, 1), new Date(start_year + (graph_periods - 1) * period_length, 0, 1)],
                [min, max])
              .format_x(function(x) { return x.getFullYear(); })
              .format_y(function(y) { return d3.format('.1f')(y); })
              .data([{data: this_data, type: p}])
              .title(_metadata[p].title || '')
              .h_grid(true)
              .hoverable(true)
              .legend(true)
              .lines(true)
              .outlines(false)
              .draw(),
            small: chart_wrap.classed('small-chart')
          };
        }
      }
    }

    resize_charts();

  };

  var add_run = function(_data, _params) {

  };

  d3.select(window).on('resize', function() {
    resize_charts();
  })

  d3.json('/run/'+Options.dice_version, function(error, _data) {

    d3.json('/static/js/meta_data.json', function(error, _metadata) {

      initialize_charts(_data.data, _data.parameters, _metadata);

      data.push(_data);

    });

  });

  /*
   END NEW CODE
   */

})();