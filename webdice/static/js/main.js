(function() {
  'use strict';

  var parameters_wrap = d3.select('#parameters_wrap'),
    run_model = d3.select('#run_model'),
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
    padding = [45, 15, 30, 60],// padding[3] needs to match $left_pad in _layout.sass
    simulation_periods = 60,
    graph_periods = 20,
    period_length = 10,
    start_year = 2005,
    end_year = start_year + ((graph_periods-1) * period_length),
    colorsUsed = 0,
    total_runs = 0,
    active_graph_pane,
    metadata,
    charts = {},
    runs = [],
    data = {},
    color,
    width,
    height;


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

  var add_run = function(_data, _params) {

    console.log(_data);

    for (var dice_variable in _data) {

      if (_data.hasOwnProperty(dice_variable)) {

        var graph_data = {
          data: [],
          var: dice_variable,
          run: total_runs
        };

        _data[dice_variable].forEach(function(d, i) {
          /*
           Only show periods in first 200 years
           */
          if (i < graph_periods) {
            graph_data.data.push({
              y: d,
              y0: 0,
              x: new Date(start_year + i * period_length, 0, 1)
            })
          }
        });

        data[dice_variable] = data[dice_variable] || [];
        data[dice_variable].push(graph_data);

        var chart_wrap = d3.select('#'+dice_variable+'_chart');

        if (!chart_wrap.empty()) {

          var dims = get_dims(),
            h, w;

          if (chart_wrap.classed('small-chart')) {
            h = dims.h / 2 - 15;
            w = dims.w / 2 - 15;
            chart_wrap.style('height', h + 'px');
          } else {
            h = dims.h; w = dims.w;
          }

          var ext = d3.extent(graph_data.data, function(d, i) { return d.y; }),
            min = ext[0] == 0 ? 0 : ext[0] - (ext[1] - ext[0]) / 10,
            max = ext[1] + (ext[1] - ext[0]) / 10;

          charts[dice_variable] = charts[dice_variable] || {
            chart: new WebDICEGraph()
              .width(w)
              .height(h)
              .padding(padding[0], padding[1], padding[2], padding[3])
              .select(dice_variable+'_chart')
              .x(d3.time.scale())
              .y(d3.scale.linear())
              .domain(
                [new Date(start_year, 0, 1),
                 new Date(start_year + (graph_periods - 1) * period_length, 0, 1)],
                [min, max])
              .format_x(function(x) { return x.getFullYear(); })
              .format_y(function(y) { return d3.format('.1f')(y); })
              .title(metadata[dice_variable].title || '')
              .h_grid(true)
              .legend(true)
              .lines(true)
              .outlines(false),
            small: chart_wrap.classed('small-chart')
          };
          charts[dice_variable].chart
//            .data([{data: run.data, type: dice_variable, run: run.counter}])
            .data(data[dice_variable])
            .hoverable(true)
            .draw();
        }
      }
    }

    /*
     Draw customizable chart
     */

    resize_charts();

    ++total_runs;

  };

  var start_run = function() {

    var form = d3.select('#parameter_form'),
      inputs = form.selectAll('input'),
      run_params = {};

    inputs.each(function() {
      var t = d3.select(this);
      run_params[t.attr('name')] = t.property('value');
    });

    d3.xhr(form.attr('action'))
      .mimeType('application/json')
      .responseType('text')
      .post(JSON.stringify(run_params))
      .on('load', load_run)
      .on('error', function(e) {})
      .on('progress', function(r) {});

  };

  var load_run = function(r) {
    r = JSON.parse(r.response);

    add_run(r.data, r.parameters);

    d3.select('#parameters_tab').classed('selected', false);
    parameters_wrap
      .classed('visuallyhidden', true)
      .style('left', 0);

  };

  var get_params = function() {

  };

  run_model.on('click', function() {
    d3.event.preventDefault();
    start_run();

  });

  var get_dims = function() {
    var visible_chart_wrap = d3.select('.chart-pane.selected'),
      w = visible_chart_wrap.node().clientWidth,
      h = visible_chart_wrap.node().clientHeight;
    console.log(w, h);
    return {w: w, h: h};
  };

  var resize_charts = function() {

    var dims = get_dims();

    for (var chart in charts) {
      if (charts.hasOwnProperty(chart)) {

        var chart_wrap = d3.select('#'+chart+'_chart');
        if (chart_wrap.classed('small-chart')) {
          chart_wrap.style('height', (dims.h / 2 - 15) + 'px');
        }
        if (chart.small) {
          charts[chart].chart.width(dims.w / 2 - 15).height(dims.h / 2 - 15).redraw();
        } else {
          chart.width(dims.w - 1).height(dims.h - 15).redraw();
        }
      }
    }

  };

  d3.select(window).on('resize', function() {
    resize_charts();
  });

  d3.json('/static/js/meta_data.json?4', function(error, _metadata) {

    metadata = _metadata;
    start_run();

  });


  /*
   END NEW CODE
   */

})();