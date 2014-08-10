var WebDICEGraph = function() {
  'use strict';
  var Options = window.Options || {},
    width = 700,
    height = 345,
    padding = {top: 10, right: 10, bottom: 30, left: 30},

    /***********************
     Scale and chart objects
     ***********************/

    _max_domains,
    _x = d3.scale.linear().domain([0, 1]).range([0, width]),
    _y = d3.scale.linear().domain([0, 1]).range([height, 0]),
    y_axis_format = function(d) {
      //FIXME: This is tres sloppy
      if (_y.domain()[1] < 100) {
        if ((d < .01 || d > 99999) && d != 0) {
          return d3.format('.1e')(d);
        }
        if (_y.domain()[1] < 0.1) {
          return d3.format('.3f')(d);
        }
        if (_y.domain()[1] < 1) {
          return d3.format('.2f')(d);
        }

        if (_y.domain()[0] < 1) {
          return d3.format('.1f')(d);
        }
        return d3.format('.0f')(d);
      }

      if (d < 1) {
        return d3.format('.2r')(d);
      }
      return d3.format('.0f')(d);
    },
    x_axis = d3.svg.axis().scale(_x).orient('bottom')
      .tickSize(6).innerTickSize(6),
    y_axis = d3.svg.axis().scale(_y).orient('left')
      .tickFormat(function(d) { return y_axis_format(d); }),
    y_twin_axis = d3.svg.axis().scale(_y).orient('right')
      .tickFormat(function(d) { return y_axis_format(d); }),
    _line = d3.svg.line()
      .x(function(d) { return _x(d.x); })
      .y(function(d) { return _y(d.y + d.y0); }),

    /**************
     Data and color
     **************/

    graph_data = {
      graphs: [],       // Graph objects
      data: [],         // Data
      nested: [],       // Nested data needed for handles when graphing multiple series
      twin_graphs: [],  // Twin graph objects
      twin_data: [],    // Twin data
      twin_nested: []   // Twin nested data needed for handles when graphing multiple series

    },
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
    hidden_runs = [],
    _color,
    _twin = false,

    /*********************
     SVG and layer objects
     *********************/

    svg_id = null,
    svg_wrap,
    svg,
    svg_defs,
    grid_layer,
    twin_graph_layer,
    graph_layer,
    axes_layer,
    handle_layer,
    button_layer,
    segment_width,
    title,
    subtitle,
    _custom_graph = false,

    /**********************
     X-segments and handles
     **********************/

    handles,
    tool_tip,
    data_points,

    /******
     States
     ******/

    _hoverable = false,
    _h_grid = true,

    /*****************
     'Private' methods
     *****************/

    color = function(i) {
      /*
       Return color from array
       */
      return color_list[i % color_list.length];
    },
    format_x = function(_d) {
      /*
       Return x-value for hover legend, label, axis
       */
      return _d;
    },
    format_y = function(_d) {
      /*
       Return y-value for hover legend, label, axis
       */
      return _d;
    },
    redraw = function() {
      tool_tip.classed('hidden', true);
      svg_wrap.style({
        width: (width + padding.left) + 'px',
        height: (height + padding.top + padding.bottom) + 'px'});
      svg_defs.select('rect').attr({
        width: width,
        height: height});
      _x.range([0, width]);
      _y.range([height, 0]);
      graph_data.graphs
        .data(graph_data.data)
        .attr('d', function(d) { return _line(d.data); });
      if (_h_grid) {
        grid_layer.selectAll('.grid-line')
          .data(_y.ticks())
          .attr('x1', _x.range()[0])
          .attr('x2', _x.range()[1])
          .attr('y1', function(d) { return _y(d); })
          .attr('y2', function(d) { return _y(d); });
      }
      axes_layer.select('.y.axis').call(y_axis);
      axes_layer.select('.x.axis')
        .attr('transform', 'translate(0,' + (height + 5) + ')')
        .call(x_axis);
    },
    nested = function(arr) {
      /*
       Transform series data into data nested by time period
       */
      return d3.nest()
        .key(function(d) { return d.x; })
        .entries([].concat.apply([], arr.map(function(d) {
          d.data.forEach(function(dd) {
            dd.run_name = d.run_name;
            dd.run_id = d.run_index;
          });
          return d.data;
        })));
    },
    normal_legend = function(d, i) {
      var _h = '';
      if (i == 0) { _h += format_x(d.x) + '<br>';}
      if (hidden_runs.indexOf(+d.run_id) == -1) {
        var _c = d3.select('.chart-line[data-run-id="' + d.run_id + '"]').style('stroke');
        _h += '<span data-run-id=' + d.run_id + '>';
        _h += '<b style="color:' + _c + '">';
        _h += d.run_name.replace(/ /g, '&nbsp;') + ':&nbsp;</b>' + format_y(d.y) + '</span><br>';
      }
      return _h;
    },
    custom_legend = function(d, i) {
      var _h = '';
      if (hidden_runs.indexOf(+d.run_id) == -1) {
        var _c = d3.select('.chart-line[data-run-id="' + d.run_id + '"]').style('stroke');
        _h += '<span data-run-id=' + d.run_id + '>';
        _h += '<b style="color:' + _c + '">';
        _h += d.run_name.replace(/ /g, '&nbsp;') + '</b><br>';
        _h += format_x(d.x) + ', ' + format_y(d.y) + '</span><br>';
      }
      return _h;
    },
    update_legend = function(_d) {
      var arr = [], _h = '';
      _d.forEach(function(d, i) {
        arr.push({
          color: color(i),
          y: d.y,
          name: d.run_name
        });
      });
      if (_d.length > 1) {
        _d = _d.sort(function(a, b) {
          return d3.descending(a.y, b.y);
        });
      }
      _d.forEach(function(d, i) {
        if (_custom_graph) {
          _h += custom_legend(d, i);
        } else {
          _h += normal_legend(d, i);
        }
      });
      tool_tip
        .html(_h)
        .style('left', (_x(_d[0].x) + padding.left + 10) + 'px')
        .style('top', (_y(_d[0].y) + padding.top) + 'px')
        .classed('active', true);
    },
    add_hover_points = function() {
      segment_width = _x(graph_data.data[0].data[1].x) - _x(graph_data.data[0].data[0].x);
      handles = handle_layer.selectAll('.segment')
        .data(graph_data.nested);
      handles.exit().remove();
      handles.enter().append('g')
        .attr('class', 'segment')
        .attr('transform', function(d) {
          return 'translate(' + (_x(d.values[0].x) - segment_width / 2) + ',0)';
        });
      handles.each(function(d) {
        var visible = ((_x(d.values[0].x) >= _x.range()[0]) && (_x(d.values[0].x) <= _x.range()[1])),
          t = d3.select(this);
        t.append('rect')
          .attr('class', 'segment-rect')
          .attr('height', _y.range()[0])
          .attr('width', segment_width)
          .attr('data-x', function(d) { return d.values[0].x; })
          .style('fill', 'transparent')
          .style('pointer-events', function() { return visible ? 'all' : 'none'; });
        var dpt = t.selectAll('.data-point.tight')
          .data(function(d) { return d.values; });
        dpt.exit().remove();
        dpt.enter().append('circle')
          .classed('data-point', function() { return visible; })
          .classed('hoverable', function() { return visible; })
          .classed('tight', true)
          .attr('data-x', function(d) { return d.x; })
          .attr('data-y', function(d) { return d.y; })
          .attr('data-run-id', function(d) { return d.run_id; })
          .attr('data-type', function(d) { return d.run_name; })
          .attr('cx', segment_width / 2)
          .attr('cy', function(d) { return _y(d.y + d.y0); })
          .attr('r', function() { return visible ? 4 : 0; })
          .style('stroke', function(d, i) { return color(i); });
        handles.data(graph_data.data[0]);
      });
      add_hover();
    },
    add_custom_hover_points = function() {
//      console.log('add');
      handles = handle_layer.selectAll('.segment')
        .data(graph_data.data);
      handles.attr('class', 'segment')
        .attr('transform', function(d) {
          return 'translate(0,0)';
        });
      handles.enter().append('g');
      handles.exit().remove();
      handles.each(function(dd, j) {
        var t = d3.select(this);
        data_points = t.selectAll('.data-point.tight')
          .data(dd.data);
        data_points.enter().append('circle');
        data_points.classed('data-point', function() { return true; })
          .classed('hoverable', function() { return true; })
          .classed('tight', true)
          .attr('data-x', function(d) { return d.x; })
          .attr('data-y', function(d) { return d.y; })
          .attr('data-run-id', function(d) { return d.run_id; })
          .attr('data-type', function(d) { return d.run_name; })
          .attr('cx', function(d) { return _x(d.x); })
          .attr('cy', function(d) { return _y(d.y + d.y0); })
          .attr('r', 3)
          .style('stroke', function(d, i) { return color(j); })
          .style('stroke-width', 1.5)
          .style('fill', 'white')
          .style('pointer-events', 'all');
        data_points.exit().remove();
      });
//      handles.exit().remove();
//      add_custom_hover();
    },
    add_hover = function() {
      /*
       Attach mouse events to <rect>s with hoverable handles (toggle .active)
       */
      handles.each(function(d) {
        var handle = d3.select(this);
        handle.select('.segment-rect')
          .on('mouseover', function() {
            update_legend(d.values);
            tool_tip.classed('hidden', !_hoverable);
            handle.selectAll('.data-point.tight')
              .classed('active', true);
          })
          .on('mouseout', function() {
            tool_tip.classed('hidden', true);
            d3.selectAll('.data-point.tight')
              .classed('active', false)
              .classed('hovered', false);
            handle.selectAll('data-point')
              .classed('active', false);
          });
      });
    },
    add_custom_hover = function() {
      /*
       Attach mouse events to <rect>s with hoverable handles (toggle .active)
       */
      handles.each(function(d) {
        var t = d3.select(this);
        t.selectAll('.data-point').each(function() {
          d3.select(this).on('mouseover', function(d) {
            update_legend([d]);
            tool_tip.classed('hidden', !_hoverable);
          })
          .on('mouseout', function() {
            tool_tip.classed('hidden', true);
          });
        });
      });
    },
    remove_hover = function() {
      /*
       Remove mouse events from <rect>s with hoverable handles (toggle .active)
       */
      handles.selectAll('rect, .data-point')
        .on('mouseover', function() { return null; })
        .on('mouseout', function() { return null; });
    },
    draw_axes = function() {
      /*
       Draw x and y axes, ticks, etc.
       */
      axes_layer.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + (height + 5) + ')')
        .call(x_axis);
      axes_layer.append('g')
        .attr('class', 'y axis')
        .attr('transform', 'translate(-5,0)')
        .call(y_axis);
    },
    draw_twin_axes = function() {
      /*
       Draw x and y axes, ticks, etc.
       */
      axes_layer.append('g')
        .attr('class', 'y twin axis')
        .attr('transform', 'translate('+ (width + 5) + ',0)')
        .call(y_twin_axis);
    },
    pre_id = function(str) {
      return svg_id + '_' + str;
    };

  /****************
   'Public' methods
   ****************/

  this.padding = function(all, sides, bottom, left) {
    if (!all) { return padding; }
    padding = {top: all, right: all, bottom: all, left: all};
    if (typeof(sides) == 'number') {
      padding.right = sides;
      padding.left = sides;
      if (typeof(bottom) == 'number') {
        padding.bottom = bottom;
        if (typeof(left) == 'number') {
          padding.left = left;
        }
      }
    }
    return this;
  };
  this.width = function(val) {
    /*
     Set width of graph.
     ...
     Args
     ----
     val (int): width of DOM element to use as container (Note: *not* the width of the graph itself!)
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (!val) { return width; }
    width = val - padding.left - padding.right;
    return this;
  };
  this.height = function(val) {
    if (!val) { return height; }
    height = val - padding.top - padding.bottom;
    return this;
  };
  this.select = function(el) {
    if (!el) { return svg_id; }
    svg_id = el.replace('#', '');
    svg_wrap = d3.select('#'+svg_id).append('div')
      .attr('class', 'chart-wrap')
      .style({
        'left': '-' + padding.left + 'px',
        'width': (width + padding.left) + 'px'
      });
    svg = svg_wrap
      .append('svg')
      .attr({ 'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'version': '1.1',
        'width': width + padding.left + padding.right,
        'height': height + padding.top + padding.bottom,
        'id': pre_id('chart_svg') })
      .append('g')
      .attr('transform', 'translate(' + padding.left + ',' + padding.top + ')');
    svg_defs = svg.append('defs');
    grid_layer = svg.append('g').attr('id', pre_id('grid_layer'));
    twin_graph_layer = svg.append('g').attr('id', pre_id('twin_graph_layer'));
    graph_layer = svg.append('g').attr('id', pre_id('graph_layer'));
    svg_defs.append('clipPath').attr("id", "graph_clip").append("rect")
      .attr({'width': width, 'height': height });
    axes_layer = svg.append('g').attr('id', pre_id('axes_layer'));
    handle_layer = svg.append('g').attr('id', pre_id('handle_layer'));
    button_layer = svg.append('g').attr('id', pre_id('button_layer'));
    svg.selectAll('g').attr('class', 'chart-layer');
    tool_tip = d3.select('#'+svg_id).append('div').attr('class', 'tool_tip');
    return this;
  };
  this.title = function(str, align) {
    if (str === undefined) { return title.text(); }
    title = title || d3.select('#' + svg_id).insert('h3', '.chart-wrap');
    title.html(str);
    return this;
  };
  this.subtitle = function(str) {
    if (str === undefined) { return subtitle.text(); }
    subtitle = subtitle || d3.select('#' + svg_id).insert('h4', '.chart-wrap');
    subtitle.html(str);
    return this;
  };
  this.x = function(val) {
    if (!val) { return _x; }
    _x = val;
    _x.range([0, width]);
    x_axis.scale(_x);
    return this;
  };
  this.y = function(val) {
    if (!val) { return _y; }
    _y = val;
    _y.range([height, 0]);
    y_axis.scale(_y);
    return this;
  };
  this.domain = function(xd, yd) {
    if (xd === undefined) { return [_x.domain(), _y.domain()]; }
    _x.domain(xd);
    if (yd) {
      _y.domain(yd);
    }
    return this;
  };
  this.format_x = function(func) {
    /*
     Format function for data in x axis
     ...
     Args
     ----
     func (Function): function that accepts an argument and returns a String
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (func === undefined) { return format_x; }
    format_x = func;
    return this;
  };
  this.format_y = function(func) {
    /*
     Format function for data in y axis
     ...
     Args
     ----
     func (Function): function that accepts an argument and returns a String
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (func === undefined) { return format_y; }
    format_y = func;
    return this;
  };
  this.colors = function(func) {
    if (func === undefined) { return color; }
    if (typeof func === 'function') {
      color = func;
    } else if (typeof func === 'string') {
      color = function() { return func; }
    } else {
      color_list = func;
    }
    return this;
  };
  this.color = function(color) {
    _color = color;
  };
  this.data = function(arr) {
    /*
     Set data series to graph.
     ...
     Args
     ----
     arr (Array): Array of Arrays of Objects {x: foo, y: bar, y0: [0]}
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (arr === undefined) { return graph_data.data; }
    graph_data.data = arr;
    graph_data.nested = nested(arr);
    return this;
  };
  this.twin_data = function(arr) {
    /*
     Set twin data series to graph.
     ...
     Args
     ----
     arr (Array): Array of Arrays of Objects {x: foo, y: bar, y0: [0]}
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (arr === undefined) { return graph_data.twin_data; }
    _twin = true;
    graph_data.twin_data = arr;
    graph_data.twin_nested = nested(arr);
    return this;
  };
  this.hide_run = function(index) {
    hidden_runs.push(index);
  };
  this.show_run = function(index) {
    if (hidden_runs.length > 0) {
      hidden_runs.splice(hidden_runs.indexOf(index), 1);
    }
  };
  this.toggle_hover = function(bool) {
    if (bool === undefined) { return _hoverable; }
    if (bool === false) {
      d3.selectAll('.data-point.tight').classed('hoverable', bool);
      remove_hover();
      return this;
    }
    if (bool === true) {
      d3.selectAll('.data-point.tight').classed('hoverable', bool);
      add_hover();
      return this;
    }
  };
  this.hoverable = function(bool) {
    /*
     Create hoverable interface.
     ...
     Args
     ----
     bool (Boolean): true if graph should be hoverable
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (bool === undefined) { return _hoverable; }
    _hoverable = bool;
    if (bool === false) {
      d3.selectAll('.data-point.tight').classed('hoverable', false);
      remove_hover();
      return this;
    }
    if (_custom_graph) {
      add_custom_hover_points();
      add_custom_hover();
    } else {
      add_hover_points();
      add_hover();
    }
    return this;
  };
  this.h_grid = function(bool) {
    /*
     Draw horizontal gridlines
     ...
     Args
     ----
     bool (Boolean): true if gridlines should be drawn
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    if (bool === undefined) { return _h_grid; }
    if (bool === false) {
      grid_layer.selectAll('.grid-line').remove();
      return this;
    }
    grid_layer.selectAll('.grid-line')
      .data(_y.ticks()).enter()
      .append('line')
      .attr('class', 'grid-line')
      .attr('x1', _x.range()[0])
      .attr('x2', _x.range()[1])
      .attr('y1', function(d) { return _y(d); })
      .attr('y2', function(d) { return _y(d); });
    return this;
  };
  this.interpolate = function(str) {
    if (str === undefined) { return this; }
    _line.interpolate(str);
    return this;
  };
  this.legend = function(bool) {
    //TODO: Don't return this without bool
    if (bool === undefined) { return this; }
    if (bool) {
      var legend = d3.select('#' + svg_id).insert('div', '.chart-wrap')
        .attr('class', 'chart-legend');
      graph_data.data.forEach(function(d, i) {
        var legend_unit = legend.append('span')
          .attr('class', 'legend-row');
        legend_unit.append('span').attr('class', 'legend-swatch')
          .style('background-color', color(i));
//          .style('background-color', _color);
        legend_unit.append('span').attr('class', 'legend-text').text(d.run_name);
      });
    }
    return this;
  };
  this.draw = function() {
    /*
     Draw all data
     ...
     Args
     ----
     null
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    graph_data.graphs = graph_layer.selectAll('.chart-line')
      .data(graph_data.data).enter().append('path')
      .attr('d', function(d) { return _line(d.data); })
      .attr('class', 'chart-line')
      .attr('clip-path', 'url(#graph_clip)')
      .attr('data-type', function(d) { return d.run_name ? d.run_name : null; })
      .attr('data-run-id', function(d) { return typeof(d.run_index) == 'number' ? d.run_index : null; })
      .style('fill', function(d, i) { return null; })
      .style('stroke', function(d, i) { return color(i); });
    draw_axes();
    return this;
  };
  this.twin_draw = function() {
    /*
     Draw all data
     ...
     Args
     ----
     null
     ...
     Returns
     -------
     RPSGraph
     ...
     */
    graph_data.twin_graphs = twin_graph_layer.selectAll('.chart-line')
      .data(graph_data.twin_data).enter().append('path')
      .attr('d', function(d) { return _line(d.data); })
      .attr('class', 'chart-line')
      .attr('clip-path', 'url(#graph_clip)')
      .attr('data-type', function(d) { return d.run_name ? d.run_name : null; })
      .attr('data-run-id', function(d) { return typeof(d.run_index) == 'number' ? d.run_index : null; })
      .attr('stroke-dasharray', '5, 5')
      .style('stroke', function(d, i) { return color(i); });
    draw_twin_axes();
    return this;
  };
  this.custom = function(bool) {
    if (bool === undefined) { return this; }
    _custom_graph = bool;
    //FIXME: Total crap below. Can't rely on this.
    segment_width = _x(graph_data.data[0].data[1].x) - _x(graph_data.data[0].data[0].x);
    return this;
  };
  this.update_data = function() {
    graph_data.graphs = graph_layer.selectAll('.chart-line')
      .data(graph_data.data);
    graph_data.graphs.enter().append('path');
    graph_data.graphs.attr('class', 'chart-line')
      .attr('clip-path', 'url(#graph_clip)')
      .attr('data-type', function(d) { return d.run_name ? d.run_name : null; })
      .attr('data-run-id', function(d) { return typeof(d.run_index) == 'number' ? d.run_index : null; })
      .style('stroke', function(d, i) { return color(i); });
//    graph_data.graphs.exit().remove();
    if (_custom_graph) {
//      add_custom_hover_points();
      add_custom_hover();
    } else {
      handles.data(graph_data.nested);
//      add_hover_points();
      add_hover();
    }
    axes_layer.select('.y.axis').call(y_axis);
  };
  this.update_custom_data = function() {

  };
  this.update_twin_data = function() {
    graph_data.twin_graphs = graph_layer.selectAll('.chart-line')
      .data(graph_data.data);
    graph_data.twin_graphs.exit().remove();
    graph_data.twin_graphs.enter().append('path')
      .attr('d', function(d) { return _line(d.data); })
      .attr('class', 'chart-line')
      .attr('clip-path', 'url(#graph_clip)')
      .attr('data-type', function(d) { return d.run_name ? d.run_name : null; })
      .attr('data-run-id', function(d) { return typeof(d.run_index) == 'number' ? d.run_index : null; })
      .attr('stroke-dasharray', '5, 5')
      .style('stroke', function(d, i) { return color(i); });
    handles.data(graph_data.twin_nested);
    add_hover();
  };
  this.redraw = function() {
    redraw();
    if (_custom_graph) {
//      add_custom_hover_points();
      handle_layer.selectAll('.data-point').remove();
      this.hoverable(true);
    } else {
      handle_layer.selectAll('.segment').remove();
      this.hoverable(true);
    }

    return this;
  };
  this.change_y = function() {
    axes_layer.select('.y.axis').call(y_axis);
    graph_data.graphs
      .data(graph_data.data)
      .attr('d', function(d) { return _line(d.data); });
    handles.data(graph_data.nested)
      .each(function(dd, i) {
        d3.select(this).selectAll('.data-point')
          .attr('data-x', function(d) { return d.x; })
          .attr('data-y', function(d) { return d.y; })
          .attr('cy', function(d) { return _y(d.y + d.y0); })
          .attr('cx', function(d) {
            return _x(d.x);
          });
      });
    add_hover();
  };
  this.change_x = function() {
    axes_layer.select('.x.axis').call(x_axis);
    graph_data.graphs
      .data(graph_data.data)
      .attr('d', function(d) { return _line(d.data); });
    handles.data(graph_data.nested)
      .each(function(dd, i) {
        d3.select(this).selectAll('.data-point')
          .attr('data-x', function(d) { return d.x; })
          .attr('data-y', function(d) { return d.y; })
          .attr('cy', function(d) { return _y(d.y + d.y0); })
          .attr('cx', function(d) {
//            return _x(d.x) - ((segment_width * i) - segment_width  / 2);
            return _x(d.x);
          });
      });
    add_hover();
  };
};