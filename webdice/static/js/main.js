(function() {
  'use strict';

  var parameters_wrap = d3.select('#parameters_wrap'),
    run_model = d3.select('#run_model'),
    clear_model = d3.select('#clear_model'),
    clear_runs = d3.select('#clear_runs'),
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
    used_colors = [],
    padding = [45, 15, 30, 60],// padding[3] needs to match $left_pad in _layout.sass

    simulation_periods = 60,
    graph_periods = 20,
    period_length = 10,
    start_year = 2005,
    end_year = start_year + ((graph_periods-1) * period_length),
    x_domain = [new Date(start_year, 0, 1),
      new Date(start_year + (graph_periods - 1) * period_length, 0, 1)],

    total_runs = 0,
    visible_runs = 0,
    active_graph_pane,
    metadata,
    charts = {},
    runs = [],
    all_data = {},
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
                if ((y < .01 || y > 99999) && y != 0) {
                  return d3.format('.1e')(y);
                } else {
                  return d3.format('.3r')(y);
                }
              })
              .title(metadata[dice_variable].title || '')
              .h_grid(true)
              .legend(true),
            small: chart_wrap.classed('small-chart')
          };
        }
      }
    }

//    initialized = true;

  };

  var update_graph = function(dice_variable) {

    if (charts.hasOwnProperty(dice_variable)) {

      // Set domain extents
      var ext = d3.extent(flatten_data(all_data[dice_variable])),
        min = ext[0] == 0 ? 0 : ext[0] - (ext[1] - ext[0]) / 10,
        max = ext[1] + (ext[1] - ext[0]) / 10;

      // Update chart data and redraw
      charts[dice_variable].chart
        .data(all_data[dice_variable])
        .domain(x_domain, [min, max])
        .colors(used_colors)
      ;
      if (initialized) {
        charts[dice_variable].chart
          .update_data();
      } else {
        charts[dice_variable].chart
          .hoverable(true)
          .draw();
      }

    }
  };

  var toggle_graph_hover = function(bool) {
    for (var dice_variable in charts) {
      if (charts.hasOwnProperty(dice_variable)) {
        charts[dice_variable].chart.toggle_hover(bool);
      }
    }
  };

  var get_updated_params = function() {
    /*
     Update list of non-default parameters (for run descriptions)
     */

    adjusted_params = [];

    d3.selectAll('#parameter_form section')
      .selectAll('input[type="range"], input[type="radio"]:checked')
      .filter(function() {
        return !this.hasAttribute('disabled');
      })
      .each(function(d, i) {
        var t = d3.select(this),
          type = t.attr('type'),
          dflt = t.attr('data-default'),
          val = t.property('value');
        val = type == 'range' ? +val : val;
        dflt = type == 'range' ? dflt == 'null' ? null : +dflt : dflt;
        if (dflt != val) {
          adjusted_params.push({
            name: d3.select(this.parentNode).select('.parameter-name').text(),
            value: type == 'radio' ? null : val,
            dflt: dflt == 'null' ? null : type == 'radio' ? null : dflt
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

    var change_event, click_event;

    if (document.createEvent) {
      change_event = document.createEvent('HTMLEvents');
      change_event.initEvent('change', true, true);
      click_event = document.createEvent('HTMLEvents');
      click_event.initEvent('click', true, true);
    } else {
      change_event = document.createEventObject();
      change_event.eventType = 'change';
      click_event = document.createEventObject();
      click_event.eventType = 'click';
    }

    change_event.eventName = 'change';
    click_event.eventName = 'click';

    d3.selectAll('#parameter_form section')
      .selectAll('input[type="range"], input[type="radio"]')
      .each(function(d, i) {
        var t = d3.select(this),
          type = t.attr('type'),
          dflt = t.attr('data-default'),
          val = t.property('value');
        val = type == 'range' ? +val : val;
        dflt = type == 'range' ? dflt == 'null' ? 0 : +dflt : dflt;
        if (type == 'radio') {
          if (val == dflt) {
            t.property('checked', true);
          }
        } else if (type == 'range' && val != dflt) {
          t.property('value', dflt);
        }

        if (document.createEvent) {
          this.dispatchEvent(change_event);
          this.dispatchEvent(click_event);
        } else {
          this.fireEvent('on' + change_event.eventType, change_event);
          this.fireEvent('on' + click_event.eventType, click_event);
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
        run_name += d.name;
        if (!(d.value === null)) { run_name += ': ' + d.value; }
        if (!(d.dflt === null)) { run_name += ' (' + d.dflt + ')'; }
        run_name += '<br>';
      });
      return run_name//.substring(0, -1)
    }
  };

  var rename_run = function() {
    var t = d3.select(this),
      index = +t.attr('data-run-id'),
      h3 = d3.select('#runs li[data-run-id="' + index +'"] h3'),
      input = h3.append('input')
        .classed('rename-input', true)
        .property('value', h3.text())
        .on('change', function() {
          var new_name = this.value,
            old_name = h3.text();
          for (var dice_variable in all_data) {
            if (all_data.hasOwnProperty(dice_variable)) {
              all_data[dice_variable].filter(function(d) {
                return d.run_name == old_name;
              }).forEach(function(d) {
                d.run_name = new_name;
              });
              update_graph(dice_variable);
            }
          }
          h3.text(new_name);
          d3.selectAll('[data-type]').attr('data-type', new_name);
          d3.select(this).remove();
        });
    input.node().select();
  };

  var show_run = function() {
    var t = d3.select(this),
      index = +t.attr('data-run-id');
    d3.selectAll('#graphs_wrap [data-run-id="' + index + '"]')
      .classed('visuallyhidden', false);
    t.text('hide')
      .on('click', hide_run);

    for(var dice_variable in charts) {
      if (charts.hasOwnProperty(dice_variable)) {
        charts[dice_variable].chart.show_run(index);
      }
    }

    ++visible_runs;

    if (visible_runs == 1) {
      toggle_graph_hover(true);
    }

  };

  var hide_run = function() {
    var t = d3.select(this),
      index = +t.attr('data-run-id');
    d3.selectAll('#graphs_wrap [data-run-id="' + index + '"]')
      .classed('visuallyhidden', true);
    t.text('show')
      .on('click', show_run);

    for(var dice_variable in charts) {
      if (charts.hasOwnProperty(dice_variable)) {
        charts[dice_variable].chart.hide_run(index);
      }
    }

    --visible_runs;

    if (visible_runs < 1) {
      toggle_graph_hover(false);
    }



  };

  var remove_run = function(index) {
    if (index === undefined) {
      index = +d3.select(this).attr('data-run-id');
    }
    d3.selectAll('#graphs_wrap [data-run-id="' + index + '"]').remove();
    for (var dice_variable in all_data) {
      if (all_data.hasOwnProperty(dice_variable)) {
        all_data[dice_variable] = all_data[dice_variable].filter(function(d) {
          return d.run_index != index;
        });
        update_graph(dice_variable);
      }
    }

    used_colors.splice(index, 1);

    --visible_runs;

    if (visible_runs < 1) {
      toggle_graph_hover(false);
    }

    d3.selectAll('#runs li[data-run-id="' + index + '"]').remove();

  };

  var add_run_to_list = function(index) {
    /*
     Add item to list of runs
     */

    var li = runs_list.append('li').attr('data-run-id', index);
    li.append('div').attr('class', 'run-swatch');
    li.append('h3').style({
      'border-right-color': color_list[index]
    }).append('span').text('Run #' + index);
    li.append('p').html(get_run_description());
    var buttons = li.append('p');
    buttons.append('mark')
      .attr('class', 'hide-run')
      .attr('data-run-id', total_runs)
      .text('hide')
      .on('click', hide_run);
    buttons.append('mark')
      .attr('class', 'delete-run')
      .attr('data-run-id', total_runs)
      .text('delete')
      .on('click', remove_run);
    buttons.append('mark')
      .attr('class', 'rename-run')
      .attr('data-run-id', total_runs)
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

    used_colors.push(color_list[total_runs]);

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

        all_data[dice_variable] = all_data[dice_variable] || [];
        all_data[dice_variable].push(graph_data);

        var chart_wrap = d3.select('#'+dice_variable+'_chart');

        if (!chart_wrap.empty()) {

          update_graph(dice_variable);

        }
      }
    }

    add_run_to_list(total_runs);

    if (!initialized) { initialized = true; }

    //TODO: Draw customizable chart

    resize_charts();

    ++total_runs;
    ++visible_runs;

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

  clear_runs.on('click', function() {
    used_colors = [];
    runs_list.selectAll('li').each(function() {
      remove_run(+d3.select(this).attr('data-run-id'));
    });
    d3.select('#runs_wrap').classed('visuallyhidden', true);
  });

  d3.selectAll('input[name="damages_model"]').on('click', function() {
    console.log(1);
    var pf = d3.select('#prod_frac'),
      active = d3.select('#productivity_fraction').property('checked');
    if (active) {
      pf.classed('disabled', false);
      pf.select('input').property('disabled', false);
    } else {
      pf.classed('disabled', true);
      pf.select('input').property('disabled', true);
    }
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