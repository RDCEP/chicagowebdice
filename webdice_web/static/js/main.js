(function() {
  'use strict';

  var parameters_wrap = d3.select('#parameters_wrap'),
    run_model = d3.select('#run_model'),
    clear_model = d3.select('#clear_model'),
    clear_runs = d3.select('#clear_runs'),
    runs_list = d3.select('#runs ul'),
    damages_model = d3.selectAll('input[name="damages_model"]'),
    select_x_axis = d3.select('#select-x-axis'),
    select_y_axis = d3.select('#select-y-axis'),
    select_y2_axis = d3.select('#select-y2-axis'),
    logarithmic_axes = d3.selectAll('.logarithmic-axis'),
    loader_gif = d3.selectAll('.loader_gif'),

    initialized = false,

    color_list = [
      d3.rgb(86, 180, 233), // sky blue
      d3.rgb(230, 159, 0),  // orange
      d3.rgb(0, 158, 115),  // bluish green
      d3.rgb(240, 228, 66), // yellow
      d3.rgb(0, 114, 178),  // blue
      d3.rgb(213, 94, 0),   // vermilion
      d3.rgb(204, 121, 167), // reddish purple
      d3.rgb(50, 50, 50), //black
    ],
    used_colors = [],
    padding = [45, 15, 30, 60],  // padding[3] needs to match $left_pad in _layout.sass

    graph_periods = 20,
    period_length = 10,
    start_year = 2005,
    end_year = start_year + ((graph_periods - 1) * period_length),
    x_domain = [new Date(start_year, 0, 1), new Date(end_year, 0, 1)],
    x_custom_domain = [new Date(start_year, 0, 1), new Date(end_year, 0, 1)],
    x_custom_domain_var = false,

    total_runs = 0,
    visible_runs = 0,
    metadata,
    graphs = {},
    runs = [],
    all_data = {},
    custom_data = [[], []],
    adjusted_params = [],
    custom_vars = ['damages', 'backstop'],
    show_twin = false,

    height;

  var get_dims = function() {
    /*
     Get dimensions of current pane in interface
     */

    var visible_graph_wrap = d3.select('.graph-pane.selected'),
      w = visible_graph_wrap.node().clientWidth,
      h = visible_graph_wrap.node().clientHeight;
    return {w: w, h: h};
  };

  var get_extents = function(data, index, val) {
    /**
     * Clips utility when consumption = twigs + beetles
     */
    var extents = d3.extent(data);
    extents = (val == 'utility') || (val == 'utility_discounted')
      ? [d3.max([extents[0], -1]), extents[1]]
      : extents;
    return extents;
  };

  var flatten_runs = function(runs, axis) {

    if (axis === undefined) {
      axis = 'y';
    }

    var flat_runs = [];

    runs.forEach(function(d) {
      flat_runs = flat_runs.concat(d.data);
    });
    flat_runs.forEach(function(d, i) {
      flat_runs[i] = d[axis];
    });
    return flat_runs;
  };

  var build_data_object = function(_data, dice_variable, custom_x_domain) {

    var graph_data = {
      data: [],
      var: dice_variable,
      y_title: metadata[dice_variable].title,
      x_title: custom_x_domain
        ? metadata[custom_x_domain].title
        : 'Year',
      run_index: total_runs,
      run_name: 'Run #' + total_runs,
      unit: metadata[dice_variable].unit,
      visible: true
    };

    _data[dice_variable].forEach(function(d, i) {
      /*
       Only show periods in first 200 years
       */
      if (i < graph_periods) {

        graph_data.data.push({
          y: d,
          y0: 0,
          x: custom_x_domain
            ? all_data[custom_x_domain][all_data[dice_variable].length - 1].data[i].y
            : new Date(start_year + i * period_length, 0, 1)
        })
      }
    });

    return graph_data;

  };

  var initialize_graph = function(dice_variable, graph_wrap) {

    var dims = get_dims(),
      h, w;
    if (graph_wrap.classed('small-graph')) {
      h = dims.h / 2 - 15;
      w = dims.w / 2 - 15;
      graph_wrap.style('height', h + 'px');
    } else {
      h = dims.h;
      w = dims.w;
    }
    graphs[dice_variable] = graphs[dice_variable] || {
      graph: new WebDICEGraph()
        .twin(dice_variable == 'twin')
        .width(w)
        .height(h)
        .padding(padding[0], padding[1], padding[2], padding[3])
        .select(dice_variable + '_graph')
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
        .subtitle(get_subtitle(dice_variable))
        .legend(true),
      small: graph_wrap.classed('small-graph')
    };
  };

  var update_custom_graphs = function() {

    var _graphs = [[0, 'custom'], [1, 'twin']];
    for (var i = 0; i < _graphs.length; ++i) {
      update_custom_graph(
        _graphs[i][1],
        _graphs[i][0]
      );
    }

    resize_graphs();

  };

  var update_custom_graph = function(g, i) {

    graphs[g].graph
      .data(custom_data[i])
      .domain(x_custom_domain,
              get_extents(flatten_runs(custom_data[i]),
                          i,
                          //FIXME This next line seems really kludgy
                          custom_data[i][0] ? custom_data[i][0].var : ''))
      .colors(used_colors);

    if (initialized) {
      graphs[g].graph
        .update_data();
    } else {
      graphs[g].graph
        .twin(i == 1)
        .custom(true)
        .hoverable(true)
        .padding(45, 60, 45, 60)
        .draw();
    }

  };

  var update_graph = function(dice_variable) {

    if (graphs.hasOwnProperty(dice_variable)) {

      // Set domain extents
      var extents = d3.extent(flatten_runs(all_data[dice_variable]));

      // Update graph data and redraw
      graphs[dice_variable].graph
        .data(all_data[dice_variable])
        .domain(x_domain, extents)
        .colors(used_colors)
      ;
      if (initialized) {
        graphs[dice_variable].graph
          .update_data();
      } else {
        graphs[dice_variable].graph
          .hoverable(true)
          .draw();
      }
    }
  };

  var update_x_axis = function (dice_variable) {

    var _graphs = [[0, 'custom'], [1, 'twin']];
    for (var i = 0; i < _graphs.length; ++i) {
      var index = _graphs[i][0],
        graph = _graphs[i][1];

      custom_data[index].forEach(function(r, i) {
        r.x_title = metadata[dice_variable].title;
        r.data.forEach(function(d, j) {
          d.x = dice_variable == 'year'
            ? new Date(start_year + j * period_length, 0, 1)
            : all_data[dice_variable][i].data[j].y;
        });
      });

      if (dice_variable == 'year') {
        graphs[graph].graph.format_x(function(x) { return x.getFullYear(); });
        graphs[graph].graph.x(d3.time.scale());
        x_custom_domain = x_domain;
        x_custom_domain_var = false;
      } else {
        graphs[graph].graph.format_x(graphs.custom.graph.format_y());
        graphs[graph].graph.x(d3.scale.linear());
        x_custom_domain = get_extents(flatten_runs(all_data[dice_variable]),
                                      index,
                                      dice_variable);
        x_custom_domain_var = dice_variable;
        console.log(x_custom_domain[0], x_custom_domain[1], x_custom_domain_var,
          x_domain);

      }

      var title = metadata[custom_vars[index]].title + ' v. ';
      title += x_custom_domain_var ? metadata[x_custom_domain_var].title : 'Time';

      graphs[graph].graph
        .title(title)
        .subtitle(get_subtitle(index));
//        .change_x();

      /*TODO: This is being called twice because change_x() needs to be
        called for each graph*/
      update_custom_graph(graph, index);

      graphs[graph].graph.change_x();

    }

    resize_graphs();

  };

  var get_subtitle = function (index) {

    if (typeof index == 'string') {
      return metadata[index].title_unit || metadata[index].title;
    }
    var subtitle = (metadata[custom_vars[index]].title_unit || metadata[custom_vars[index]].title);
    subtitle += ' v. ';
    subtitle += x_custom_domain_var ? metadata[x_custom_domain_var].title_unit : 'years';
    return subtitle;

  };

  var update_y_axis = function(graph, val) {

    var index = graph == 'custom' ? 0 : 1,
      title = '';

    custom_vars[index] = val;
    custom_data[index][0].var = val;

    if ((graph == 'twin') && (val == 'none')) {
      custom_vars[index] = false;
      show_twin = false;
      graphs[graph].graph
        .title('')
        .subtitle('');
    } else {
      if ((graph == 'twin') && (val != 'none')) {
        show_twin = true;
      }
      title = metadata[custom_vars[index]].title + ' v. ';
      title += x_custom_domain_var ? metadata[x_custom_domain_var].title : 'Time';

      custom_data.forEach(function (v, k) {
        v.forEach(function (r, i) {
          if (custom_vars[k]) {
            r.y_title = metadata[custom_vars[k]].title;
            r.unit = metadata[custom_vars[k]].unit;
          }
          r.data.forEach(function (d, j) {
            if (custom_vars[k]) {
              d.y = all_data[custom_vars[k]][i].data[j].y;
            }
          });
        });
      });

      graphs[graph].graph
        .twin(show_twin)
        .title(title)
        .subtitle(get_subtitle(index))
        .change_y();
    }

    update_custom_graphs();

  };

  var toggle_graph_hover = function(bool) {
    for (var dice_variable in graphs) {
      if (graphs.hasOwnProperty(dice_variable)) {
        graphs[dice_variable].graph.toggle_hover(bool);
      }
    }
  };

  var add_run = function(_data, parameters) {
    /*
     Add run to interface.
     */

    used_colors.push(color_list[total_runs % color_list.length]);

    for (var dice_variable in _data) {
      if (_data.hasOwnProperty(dice_variable)) {

        all_data[dice_variable] = all_data[dice_variable] || [];
        all_data[dice_variable].push(
          build_data_object(_data, dice_variable)
        );

        var graph_wrap = d3.select('#'+dice_variable+'_graph');

        if (!graph_wrap.empty()) {

          if (!initialized) {
            initialize_graph(dice_variable, graph_wrap);
          }
          update_graph(dice_variable);

        }
      }
    }

    if (!initialized) {
      initialize_graph('custom', d3.select('#custom_graph'));
      initialize_graph('twin', d3.select('#twin_graph'));
    }

    custom_data[0].push(build_data_object(_data, custom_vars[0], x_custom_domain_var));
    custom_data[1].push(build_data_object(_data, custom_vars[1], x_custom_domain_var));

    update_custom_graphs();

    add_run_to_list(total_runs);

    Options.runs[total_runs] = {
      parameters: parameters,
      data: _data,
      name: 'Run #' + total_runs
    };

    initialized = true;

    resize_graphs();

    ++total_runs;
    ++visible_runs;

    /* Switch back to graphs after running model */
    d3.select('#parameters_wrap').classed('visuallyhidden', true);
    d3.select('#parameters_tab').classed('selected', false);
    /* End switch*/

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

  var start_run = function() {
    /*
     Gather parameters and begin AJAX call to run model.
     */

    run_model.attr('disabled', true);
    loader_gif.style({
      display: 'block',
      'z-index': 999
    });

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

  var unphysical = function(r) {
    var uphys = false;
    r.data['consumption_pc'].forEach(function(d) {
      if (d <= .25) { uphys = true; }
    });
    return uphys;
  };

  var load_run = function(r) {
    /*
     Upon successful run of model, add run and hide parameters pane
     */

    r = JSON.parse(r.response);

    add_run(r.data, r.parameters);

//    d3.select('#parameters_tab').classed('selected', false);
//    parameters_wrap.classed('visuallyhidden', true);

    run_model.attr('disabled', null);
    loader_gif.style('display', 'none');

    if (unphysical(r)) {
      show_warning();
    }

  };

  var show_warning = function() {
    var modal_click = function() {
      d3.selectAll('.modal').classed('visuallyhidden', true);
    };
    d3.selectAll('.modal')
      .classed('visuallyhidden', false)
      .on('click', modal_click);
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
      .each(function() {
        var t = d3.select(this),
          type = t.attr('type'),
          dflt = t.attr('data-default'),
          name = t.attr('name'),
          val = t.property('value');
        val = type == 'range' ? +val : val;
        dflt = type == 'range' ? dflt == 'null' ? null : +dflt : dflt;
        if (dflt != val) {
          var param = {
            name: d3.select(this.parentNode).select('.parameter-name').text(),
            value: type == 'radio' ? null : val,
            dflt: dflt == 'null' ? null : type == 'radio' ? null : dflt
          };
          //This is pretty dull
          if (name.slice(0, 2) == 'p2') {
            param.name = 'Participation ' + param.name;
          }
          if (name.slice(0, 2) == 'e2') {
            param.name = 'Reduction ' + param.name;
          }
          adjusted_params.push(param);
        }
      });
    return adjusted_params;
  };

  var reset_params = function() {
    /*
     Reset all parameters back to default values
     */

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
      .each(function() {
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
      return run_name;
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

          custom_data[0].filter(function(d) {
            return d.run_name == old_name;
          }).forEach(function(d) {
            d.run_name = new_name;
          });
          update_custom_graphs();

          h3.text(new_name);
          d3.selectAll('[data-type]').attr('data-type', new_name);
          d3.select(this).remove();
          Options.runs[index].name = new_name;
        });
    input.node().select();

  };

  var show_run = function() {
    var t = d3.select(this),
      index = +t.attr('data-run-id');
    d3.selectAll('#graphs_wrap [data-run-id="' + index + '"]')
      .filter(function() {
        if (d3.select('#select-y2-axis').property('value') == 'none') {
          return !d3.select(this).classed('twin');
        }
        return true;
      })
      .classed('visuallyhidden', false);
    t.text('hide')
      .on('click', hide_run);

    for(var dice_variable in graphs) {
      if (graphs.hasOwnProperty(dice_variable)) {
        graphs[dice_variable].graph.show_run(index);
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

    for(var dice_variable in graphs) {
      if (graphs.hasOwnProperty(dice_variable)) {
        graphs[dice_variable].graph.hide_run(index);
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

    used_colors.splice(used_colors.indexOf(color_list[index]), 1);

    d3.selectAll('#graphs_wrap [data-run-id="' + index + '"]').remove();
    for (var dice_variable in all_data) {
      if (all_data.hasOwnProperty(dice_variable)) {
        all_data[dice_variable] = all_data[dice_variable].filter(function(d) {
          return d.run_index != index;
        });
        update_graph(dice_variable);
      }
    }

    custom_data.forEach(function(d, i) {
      custom_data[i] = custom_data[i].filter(function(dd) {
        return dd.run_index != index;
      });
    });
    update_custom_graphs();

    delete Options.runs[index];

    --visible_runs;

    if (visible_runs < 1) {
      toggle_graph_hover(false);
    }

    d3.selectAll('#runs li[data-run-id="' + index + '"]').remove();

  };

  var resize_graphs = function() {

    var dims = get_dims(),
      tall = (dims.h - 15) - 70; //TODO: Get height of #graph-controls

    for (var graph in graphs) {
      if (graphs.hasOwnProperty(graph)) {

        var graph_wrap = d3.select('#'+graph+'_graph'),
          graph_svg = graph_wrap.select('svg');
        if (graph_wrap.classed('small-graph')) {
          graph_wrap.style('height', (dims.h / 2 - 30) + 'px');
          graph_svg.style('height', (dims.h / 2 - 30) + 'px');
        } else {
//          graph_wrap.style('height', tall + 'px');
          graph_svg.style('height', tall + 'px');
        }
        if (graphs[graph].small) {
          graphs[graph].graph.width(dims.w / 2 - 15).height(dims.h / 2 - 30).redraw();
        } else {
          graphs[graph].graph.width(dims.w - 1).height(tall).redraw();
        }
      }
    }

    if (!show_twin) {
        d3.selectAll('.graph-line.twin, .data-point.twin, h3.twin, h4.twin, .y.axis.twin')
          .classed('visuallyhidden', true);
      } else {
//        d3.selectAll('.graph-line.twin, .data-point.twin, h3.twin, h4.twin, .y.axis.twin')
        d3.selectAll('h3.twin, h4.twin, .y.axis.twin')
          .classed('visuallyhidden', false);
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

  damages_model.on('click', function() {
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

  select_x_axis.on('change', function() {

    update_x_axis(this.value);
    if (!x_custom_domain_var) {
      d3.select('#logarithmic_x').attr('disabled', true);
    } else {
      d3.select('#logarithmic_x').attr('disabled', null);
    }
  });

  select_y_axis.on('change', function() {

    update_y_axis('custom', this.value);

  });

  select_y2_axis.on('change', function() {

    update_y_axis('twin', this.value);
    if (!show_twin) {
      d3.select('#logarithmic_y2').attr('disabled', true);
    } else {
      d3.select('#logarithmic_y2').attr('disabled', null);
    }

  });

  logarithmic_axes.on('click', function() {
    var t = d3.select(this),
      checked = this.checked,
      axis = t.attr('id').split('_')[1];

    if (checked) {
      if (axis == 'y2') {
        graphs.twin.graph.y(d3.scale.log());
      } else if (axis == 'y') {
        graphs.custom.graph.y(d3.scale.log());
      } else {
        graphs.custom.graph.x(d3.scale.log());
      }
    } else {
      if (axis == 'y2') {
        graphs.twin.graph.y(d3.scale.linear());
      } else if (axis == 'y') {
        graphs.custom.graph.y(d3.scale.linear());
      } else {
        graphs.custom.graph.x(d3.scale.linear());
      }
    }
    graphs.twin.graph.update_data();
    graphs.custom.graph.update_data();
    resize_graphs();
  });

  d3.select(window).on('resize', function() {
    resize_graphs();
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