(function() {
  'use strict';

  var parameters_wrap = d3.select('#parameters_wrap'),
    run_model = d3.select('#run_model'),
    clear_model = d3.select('#clear_model'),
    runs_list = d3.select('#runs ul'),

    initialized = false,

    colorsUsed = 0,
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
    x_domain = [new Date(start_year, 0, 1),
      new Date(start_year + (graph_periods - 1) * period_length, 0, 1)],

    total_runs = 0,
    active_graph_pane,
    metadata,
    charts = {},
    runs = [],
    data = {},
    adjusted_params = [],

    color,
    width,
    height;

  var get_dims = function() {
    /*
     Get dimensions of current pane in interface
     */

    var visible_chart_wrap = d3.select('.chart-pane.selected'),
      w = visible_chart_wrap.node().clientWidth,
      h = visible_chart_wrap.node().clientHeight;
    return {w: w, h: h};
  };

  var flatten_data = function(_data) {
    var fd = [];

    _data.forEach(function(d) {
      fd = fd.concat(d.data);
    });
    fd.forEach(function(d, i) {
      fd[i] = d.y;
    });
    return fd;
  };

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

  var initialize_graphs = function(_data) {

    for (var dice_variable in _data) {
      if (_data.hasOwnProperty(dice_variable)) {

        var chart_wrap = d3.select('#' + dice_variable + '_chart');

        if (!chart_wrap.empty()) {

          // Set dimensions
          var dims = get_dims(),
            h, w;
          if (chart_wrap.classed('small-chart')) {
            h = dims.h / 2 - 15;
            w = dims.w / 2 - 15;
            chart_wrap.style('height', h + 'px');
          } else {
            h = dims.h;
            w = dims.w;
          }

          // Add chart to charts
          charts[dice_variable] = charts[dice_variable] || {
            chart: new WebDICEGraph()
              .width(w)
              .height(h)
              .padding(padding[0], padding[1], padding[2], padding[3])
              .select(dice_variable + '_chart')
              .x(d3.time.scale())
              .y(d3.scale.linear())
              .domain(x_domain, [0, 1])
              .format_x(function (x) {
                return x.getFullYear();
              })
              .format_y(function (y) {
                return d3.format('.1f')(y);
              })
              .title(metadata[dice_variable].title || '')
              .h_grid(true)
              .legend(true)
              .lines(true)
              .outlines(false),
            small: chart_wrap.classed('small-chart')
          };
        }
      }
    }

//    initialized = true;

  };

  var get_updated_params = function() {
    /*
     Update list of non-default parameters (for run descriptions)
     */

    //TODO: Parse policy and model parameters

    adjusted_params = [];

    d3.selectAll('#parameter_form section')
      .filter(function(){
        var id = d3.select(this).attr('id');
        return (id != 'policy_parameters') && (id != 'model_parameters');
      })
      .selectAll('input')
      .each(function(d, i) {
        var t = d3.select(this),
          dflt = +t.attr('data-default'),
          val = +t.property('value');
        if (dflt != val) {
          adjusted_params.push({
            name: d3.select(this.parentNode).select('.parameter-name').text(),
            value: val,
            dflt: dflt,
            diff: (val > dflt)
              ? '<span class="fa fa-chevron-up"></span>'
              : '<span class="fa fa-chevron-down"></span>'
          });
        }
      });
    return adjusted_params;
  };

  var reset_params = function() {
    /*
     Reset all parameters back to default values
     */

    //TODO: Reset policy and model parameters

    var event;

    if (document.createEvent) {
      event = document.createEvent('HTMLEvents');
      event.initEvent('change', true, true);
    } else {
      event = document.createEventObject();
      event.eventType = 'change';
    }

    event.eventName = 'change';

    d3.selectAll('#parameter_form section')
      .filter(function(){
        var id = d3.select(this).attr('id');
        return (id != 'policy_parameters') && (id != 'model_parameters');
      })
      .selectAll('input').each(function(d, i) {
        var t = d3.select(this),
          dflt = +t.attr('data-default'),
          val = +t.property('value');
        if (val != dflt) {
          t.property('value', dflt);

          if (document.createEvent) {
            this.dispatchEvent(event);
          } else {
            this.fireEvent('on' + event.eventType, event);
          }

        }
      });
  };

  var get_run_description = function() {
    /*
     Build run description from list of non-default parameters
     */

    var run_name = '',
      params = get_updated_params();
    if (params.length == 0) {
      return 'Default model';
    } else {
      params.forEach(function (d) {
//        run_name += d.name + ': ' + d.value + ' [' + d.diff + ' ' + d.dflt + ']<br>';
        run_name += d.name + ': ' + d.value + ' (' + d.dflt + ')<br>';
      });
      return run_name//.substring(0, -1)
    }
  };

  var rename_run = function() {

  };

  var hide_run = function(index) {

  };

  var remove_run = function(index) {

  };

  var add_run_to_list = function(index) {
    /*
     Add item to list of runs
     */

    var li = runs_list.append('li');
    li.append('div').attr('class', 'run-swatch');
    li.append('h3').style({
      'border-right-color': color_list[index]
    }).append('span').text('Run #' + index);
    li.append('p').html(get_run_description());
    var buttons = li.append('p');
    buttons.append('mark')
      .attr('class', 'hide-run')
      .text('hide')
      .on('click', hide_run);
    buttons.append('mark')
      .attr('class', 'delete-run')
      .text('delete')
      .on('click', remove_run);
    buttons.append('mark')
      .attr('class', 'rename-run')
      .text('rename')
      .on('click', rename_run);
  };

  var add_run = function(_data, _params) {
    /*
     Add run to interface.
     */

    if (!initialized) {
      initialize_graphs(_data)
    }

    for (var dice_variable in _data) {
      if (_data.hasOwnProperty(dice_variable)) {

        var graph_data = {
          data: [],
          var: dice_variable,
          run_index: total_runs,
          run_name: 'Run #' + total_runs
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

          // Set domain extents
          var ext = d3.extent(flatten_data(data[dice_variable])),
            min = ext[0] == 0 ? 0 : ext[0] - (ext[1] - ext[0]) / 10,
            max = ext[1] + (ext[1] - ext[0]) / 10;

          // Update chart data and redraw
          charts[dice_variable].chart
            .data(data[dice_variable])
            .domain(x_domain, [min, max])
            .hoverable(true);
          if (initialized) {
            charts[dice_variable].chart.update_data();
          } else {
            charts[dice_variable].chart.draw();
          }
        }
      }
    }

    add_run_to_list(total_runs);

    if (!initialized) { initialized = true; }

    //TODO: Draw customizable chart

    resize_charts();

    ++total_runs;

  };

  var start_run = function() {
    /*
     Gather parameters and begin AJAX call to run model.
     */

    var form = d3.select('#parameter_form'),
      inputs = form.selectAll('input'),
      run_params = {};

    inputs.each(function() {
      var t = d3.select(this);
      if (t.attr('type') == 'range') {
        run_params[t.attr('name')] = t.property('value');
      } else {
        if (t.property('checked')) {
          console.log(t.attr('name'), t.property('value'));
          run_params[t.attr('name')] = t.property('value');
        }
      }
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
    /*
     Upon successful run of model, add run and hide parameters pane
     */

    r = JSON.parse(r.response);

    add_run(r.data, r.parameters);

    d3.select('#parameters_tab').classed('selected', false);
    parameters_wrap.classed('visuallyhidden', true)

  };

  var resize_charts = function() {

    var dims = get_dims();

    for (var chart in charts) {
      if (charts.hasOwnProperty(chart)) {

        var chart_wrap = d3.select('#'+chart+'_chart'),
          chart_svg = chart_wrap.select('svg');
        if (chart_wrap.classed('small-chart')) {
          chart_wrap.style('height', (dims.h / 2 - 15) + 'px');
          chart_svg.style('height', (dims.h / 2 - 15) + 'px');
        }
        if (chart.small) {
          charts[chart].chart.width(dims.w / 2 - 15).height(dims.h / 2 - 15).redraw();
        } else {
          chart.width(dims.w - 1).height(dims.h - 15).redraw();
        }
      }
    }

  };

  /***************
   Event listeners
   ***************/

  run_model.on('click', function() {
    d3.event.preventDefault();
    start_run();
  });

  clear_model.on('click', function() {
    d3.event.preventDefault();
    reset_params();
  });

  d3.select(window).on('resize', function() {
    resize_charts();
  });

  /********************************************
   Trigger initial run and graph initialization
   ********************************************/

  d3.json('/static/js/meta_data.json?4', function(error, _metadata) {

    metadata = _metadata;
    start_run();

  });


  /*
   END NEW CODE
   */

})();

//FIXME: Legend doesn't disappear with Cmd+Alt+I