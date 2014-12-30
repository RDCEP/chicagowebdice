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
    _x = d3.scale.linear().domain([0, 1]).range([1, width - 1]),
    _y = d3.scale.linear().domain([0, 1]).range([height - 1, 1]),

    y_axis_format = function(d) {
      var d0 = _y.domain()[0],
        d1 = _y.domain()[1],
        dd = Math.abs(d1 - d0),
        log = Math.log10(dd),
        df = Math.floor(Math.abs(log)) + 1;
      if (0 < d < .01 || d > 9999) { return d3.format('.1e')(d); }
      else if (log <= 0) { return d3.format('.' + (df+1) + 'f')(d); }
      else if (log <= 1) { return d3.format('.' + (df) + 'f')(d); }
      return d3.format('.0f')(d);
    },
    x_axis = d3.svg.axis().scale(_x)
      .orient('bottom')
      .tickSize(6).innerTickSize(6),
    y_axis = d3.svg.axis().scale(_y)
      .orient('left')
      .tickFormat(function(d) { return y_axis_format(d); }),
    _line = d3.svg.line()
      .defined(function(d) { return d.y != null; })
      .x(function(d) { return _x(d.x); })
      .y(function(d) { return _y(d.y + d.y0); }),

    /**************
     Data and color
     **************/

    graph_data = {
      graphs: [],       // Graph objects
      data: [],         // Data
      nested: []        // Nested data needed for handles when graphing multiple series
    },
    color_list = [
      d3.rgb(86, 180, 233),  // sky blue
      d3.rgb(230, 159, 0),   // orange
      d3.rgb(0, 158, 115),   // bluish green
      d3.rgb(240, 228, 66),  // yellow
      d3.rgb(0, 114, 178),   // blue
      d3.rgb(213, 94, 0),    // vermilion
      d3.rgb(204, 121, 167), // reddish purple
      d3.rgb(50, 50, 50)        //black
    ],
    hidden_runs = [],
    _color,
    _twin = false,
    _timex = true,

    /*********************
     SVG and layer objects
     *********************/

    svg_id = null,
    svg_wrap,
    svg_root,
    svg,
    svg_defs,
    grid_layer,
    graph_layer,
    axes_layer,
    handle_layer,
    button_layer,
    segment_width,
    title_layer,
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
      return color_list[i % (color_list.length)];
    },
    format_x = function(_d) {
      /*
       Return x-value for hover legend, label, axis
       */
      return null;
    },
    format_y = function(_d) {
      /*
       Return y-value for hover legend, label, axis
       */
      return null;
    },

    redraw = function() {
      tool_tip.classed('hidden', true);
      svg_root.attr({
        width: (width + padding.left + padding.right) + 'px',
        height: (height + padding.top + padding.bottom) + 'px'});
      svg_wrap.style({
        width: (width + padding.left) + 'px',
        height: (height + padding.top + padding.bottom) + 'px'});
      svg_defs.select('rect').attr({
        width: width,
        height: height});
      _x.range([1, width - 1]);
      _y.range([height - 1, 1]);
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
      d3.select('#' + pre_id('graph_clip_expanded') + ' rect')
        .attr({width: width + 7, height: height + 7});
      d3.select('#' + pre_id('graph_clip') + ' rect')
        .attr({width: width, height: height})
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
            dd.unit = d.unit || '';
            dd.run_id = d.run_index;
            dd.x_title = d.x_title;
            dd.y_title = d.y_title;
          });
          return d.data;
        })));
    },
    normal_legend = function(d, i) {
      var _h = '';
      if (i == 0) { _h += format_x(d.x) + '<br>';}
      if (hidden_runs.indexOf(+d.run_id) == -1) {
        var _c = d3.select('.graph-line[data-run-id="' + d.run_id + '"]').style('stroke');
        _h += '<span data-run-id=' + d.run_id + '>';
        _h += '<b style="color:' + _c + '">';
        _h += d.run_name.replace(/ /g, '&nbsp;') + ':&nbsp;</b>';
        _h += format_y(d.y) + '&nbsp;' + d.unit + '</span><br>';
      }
      return _h;
    },
    custom_legend = function(d, i) {
      var _h = '';
      if (hidden_runs.indexOf(+d.run_id) == -1) {
        var _c = d3.select('.graph-line[data-run-id="' + d.run_id + '"]').style('stroke');
        _h += '<span data-run-id=' + d.run_id + '>';
        _h += '<b style="color:' + _c + '">';
        _h += d.run_name.replace(/ /g, '&nbsp;') + '</b><br>';
        _h += d.x_title.replace(/ /g, '&nbsp;') + ':&nbsp;' + format_x(d.x) + '<br>';
        /*
         This is a bit hackish. Using .slice() so d3 doesn't reorder the DOM
         on sort().
         */
        var x_runs = d3.selectAll('#custom_graphs .data-point[data-x="' + d.x + '"][data-run-id="' + d.run_id + '"]')
          .filter(function() { return !d3.select(this).classed('visuallyhidden'); })
          .slice(0)[0]
          .sort(function(a, b) {
            return a.cy.baseVal.value - b.cy.baseVal.value;
          })
          .forEach(function(dd) {
            dd = dd.__data__;
            _h += dd.y_title.replace(/ /g, '&nbsp;') + ':&nbsp;';
            var yval = dd.y == -999999 ? '-Infinity' : format_y(dd.y);
            _h += yval + '&nbsp;' + dd.unit + '</span><br>';
          });

      }
      return _h;
    },
    update_legend = function(_d, rect) {
      var arr = [], _h = '';
      _d.forEach(function(d, i) {
        arr.push({
          color: color(i),
          y: d.y,
          name: d.run_name,
          unit: d.unit
        });
      });
      _d = _d.sort(function(a, b) {
        return d3.descending(a.y, b.y);
      });
      _d.forEach(function(d, i) {
        if (_custom_graph) {
          _h += custom_legend(d, i);
        } else {
          _h += normal_legend(d, i);
        }
      });
      tool_tip
        .html(_h)
        .style('left', (rect.right + 5) + 'px')
        .style('top', (rect.top + 5 + document.body.scrollTop) + 'px')
        .classed('active', true);
    },
    move_custom_hover_points = function() {
      handle_layer.selectAll('.data-point')
        .attr('cx', function(d) { return _x(d.x); })
        .attr('cy', function(d) { return _y(d.y + d.y0); });
    },
    add_hover_points = function() {
      segment_width = graph_data.data.length > 0
        ? _x(graph_data.data[0].data[1].x) - _x(graph_data.data[0].data[0].x)
        : 0;
      handles = handle_layer.selectAll('.segment')
        .data(graph_data.nested);
      handles.enter().append('g');
      handles.exit().remove();
      handles.attr('class', 'segment')
        .attr('transform', function(d) {
          return 'translate(' + (_x(d.values[0].x) - segment_width / 2) + ',-' + padding.top + ')';
        });
//      handles.exit().remove();
      handles.each(function(d) {
        var visible = ((_x(d.values[0].x) >= _x.range()[0]) && (_x(d.values[0].x) <= _x.range()[1])),
          t = d3.select(this);
        t.append('rect')
          .attr('class', 'segment-rect')
          .attr('height', _y.range()[0] + padding.top + padding.bottom)
          .attr('width', segment_width)
          .attr('data-x', function(d) { return d.values[0].x; })
          .style('fill', 'none')
          .style('pointer-events', function() { return visible ? 'all' : 'none'; });
        data_points = t.selectAll('.data-point.tight')
          .data(function(d) { return d.values; });
        data_points.exit().remove();
        data_points.enter().append('circle')
          .classed('data-point', function() { return visible; })
          .classed('hoverable', function() { return visible; })
          .classed('tight', true)
          .classed('visuallyhidden', function(dd) {
            return hidden_runs.indexOf(+dd.run_id) > -1; })

          .attr('data-x', function(d) { return d.x; })
          .attr('data-y', function(d) { return d.y; })
          .attr('data-run-id', function(d) { return d.run_id; })
          .attr('data-type', function(d) { return d.run_name; })
          .attr('cx', segment_width / 2)
          .attr('cy', function(d) { return _y(d.y + d.y0) + padding.top; })
          .attr('r', function() { return visible ? 4 : 0; })
          .style('stroke', function(d, i) { return color(i); });
        handles.data(graph_data.data[0]);
      });
      add_hover();
    },
    add_custom_hover_points = function() {
      handles = handle_layer.selectAll('.segment')
        .data(graph_data.data);
      handles.enter().append('g');
      handles.exit().remove();
      handles.attr('class', 'segment')
        .attr('transform', function(d) {
          return 'translate(0,0)';
        });
      handles.each(function(dd, j) {
        var t = d3.select(this);
        data_points = t.selectAll('.data-point.tight')
          .data(dd.data);
        data_points.enter().append('circle');
        data_points.classed('data-point', function() { return true; })
          .classed('hoverable', function() { return true; })
          .classed('tight', true)
          .classed('twin', _twin)
          .classed('visuallyhidden', function(d) {
            return hidden_runs.indexOf(+d.run_id) > -1; })
          .attr('data-x', function(d) { return d.x; })
          .attr('data-y', function(d) { return d.y; })
          .attr('data-run-id', function(d) { return d.run_id; })
          .attr('data-type', function(d) { return d.run_name; })
          .attr('cx', function(d) { return _x(d.x); })
          .attr('cy', function(d) { return _y(d.y + d.y0); })
          .attr('r', 3.5)
          .attr('clip-path', 'url(#' + pre_id('graph_clip_expanded') + ')')
          .style('stroke', function(d, i) { return color(j); })
          .style('stroke-width', 1.5)
          .style('fill', 'white')
          .style('pointer-events', 'all');
        data_points.exit().remove();
      });
    },
    add_hover = function() {
      /*
       Attach mouse events to <rect>s with hoverable handles (toggle .active)
       */
      handles.each(function(d) {
        var handle = d3.select(this);
        handle.select('.segment-rect')
          .on('mouseover', function() {
            var  dp = handle.selectAll('.data-point.tight')
                .classed('active', true),
              rect = dp.sort(function(a, b) {
                return d3.descending(a.y, b.y);
              }).filter(function(d, i) { return i == 0; });
            update_legend(d.values, rect.node().getBoundingClientRect());
            tool_tip.classed('hidden', !_hoverable);
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
      d3.selectAll('.data-point')
        .on('mouseover', function(d) {
          var t = d3.select(this)
            , rect = this.getBoundingClientRect()
            , dpxs = d3.selectAll('#custom_graphs .data-point[data-x="' + d.x + '"]')
            , dpys = []
          ;
          dpxs
            .filter(function(dd) {
              return dd.run_id == d.run_id;
            })
            .each(function(d) {
              dpys.push(Math.floor(this.getBoundingClientRect().bottom / 4));
            });
          dpxs
            .filter(function(dd) {
              return dpys.indexOf(
                Math.floor(this.getBoundingClientRect().bottom / 4)) > -1;
            })
            .style('fill', 'none');
          dpxs
            .filter(function(dd) { return dd.run_id == d.run_id; })
            .style('fill', t.style('stroke'));

          update_legend([d], rect);

          tool_tip.classed('hidden', !_hoverable);
        })
        .on('mouseout', function() {
          d3.selectAll('#custom_graphs .data-point')
            .style('fill', 'white');
          tool_tip.classed('hidden', true);
        });
    },
    remove_hover = function() {
      /*
       Remove mouse events from <rect>s with hoverable handles (toggle .active)
       */
      //TODO: This doens't work, handles is undefined
      //handles.selectAll('rect, .data-point')
      //  .on('mouseover', function() { return null; })
      //  .on('mouseout', function() { return null; });

    },
    draw_axes = function() {
      /*
       Draw x and y axes, ticks, etc.
       */
      if (!_twin) {
        axes_layer.append('g')
          .attr('class', 'x axis')
          .attr('transform', 'translate(0,' + (height + 5) + ')')
          .call(x_axis);
        axes_layer.append('g')
          .attr('class', 'y axis')
          .attr('transform', 'translate(-5,0)')
          .call(y_axis);
      } else {
        axes_layer.append('g')
          .attr('class', 'y axis twin')
          .attr('transform', 'translate(' + (_x.range()[1] - padding.right - 15) + ',0)')
          .call(y_axis.orient('right'));
      }

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
    _x.range([0, width]);
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
      .attr('class', 'graph-wrap')
      .style({
        'left': '-' + padding.left + 'px',
        'width': (width + padding.left) + 'px'
      });
    svg_root = svg_wrap
      .append('svg')
      .attr({ 'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'version': '1.1',
        'width': width + padding.left + padding.right,
        'height': height + padding.top + padding.bottom,
        'id': pre_id('graph_svg') })
      .classed('twin', _twin);
    svg_defs = svg_root.append('defs');
    title_layer = svg_root.append('g')
      .attr('transform', 'translate(' + padding.left + ',' + (padding.top - 5) + ')');
    svg = svg_root.append('g')
      .attr('transform', 'translate(' + padding.left + ',' + padding.top + ')');
    grid_layer = svg.append('g').attr('id', pre_id('grid_layer'));
    graph_layer = svg.append('g').attr('id', pre_id('graph_layer'));
    svg_defs.append('clipPath').attr('id', pre_id('graph_clip')).append('rect')
      .attr({'width': width, 'height': height });
    svg_defs.append('clipPath').attr('id', pre_id('graph_clip_expanded')).append('rect')
      .attr({'width': width + 7, 'height': height + 7 })
      .attr('transform', 'translate(-3.5, -3.5)');
    axes_layer = svg.append('g').attr('id', pre_id('axes_layer'));
    handle_layer = svg.append('g').attr('id', pre_id('handle_layer'));
    button_layer = svg.append('g').attr('id', pre_id('button_layer'));
    svg.selectAll('g').attr('class', 'graph-layer');
    tool_tip = d3.select('#tool_tip');
    return this;
  };
  this.title = function(str, align) {
    if (str === undefined) { return title.text(); }
    var xo = _twin ? (width - padding.left - padding.right - 5) : 0,
      talign =  _twin ? 'right' : 'left',
      tanchor = _twin ? 'end' : 'start';
    title = title || title_layer.append('text')
      .attr('transform', 'translate(' + xo + ',-12)')
      .style({
        'font-weight': 'bold',
        'font-size': 12,
        'text-align': talign,
        'text-anchor': tanchor
      })
      .classed('twin', _twin);
    title.text(str);
    return this;
  };
  this.subtitle = function(str) {
    if (str === undefined) { return subtitle.text(); }
    var xo = _twin ? (width - padding.left - padding.right - 5) : 0,
      talign =  _twin ? 'right' : 'left',
      tanchor = _twin ? 'end' : 'start';
    subtitle = subtitle || title_layer.append('text')
      .attr('transform', 'translate(' + xo + ',0)')
      .style({
        'font-size': 10,
        'text-align': talign,
        'text-anchor': tanchor
      })
      .classed('twin', _twin);
    subtitle.text(str);
    return this;
  };
  this.twin = function(bool) {
    if (bool == undefined) { return _twin; }
    _twin = bool;
    return this;
  };
  this.x = function(val, bool) {
    if (!val) { return _x; }
    _x = val.range(_x.range()).domain(_x.domain());
    x_axis.scale(_x);
    _timex = bool === undefined ? true : bool;
    return this;
  };
  this.y = function(val) {
    if (!val) { return _y; }
    _y = val.range(_y.range()).domain(_y.domain());
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
      var legend = d3.select('#' + svg_id).insert('div', '.graph-wrap')
        .attr('class', 'graph-legend');
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
    graph_data.graphs = graph_layer.selectAll('.graph-line')
      .data(graph_data.data).enter().append('path')
      .attr('d', function(d) { return _line(d.data); })
      .attr('class', 'graph-line')
      .attr('clip-path', 'url(#' + pre_id('graph_clip') + ')')
      .attr('data-type', function(d) { return d.run_name ? d.run_name : null; })
      .attr('data-run-id', function(d) { return typeof(d.run_index) == 'number' ? d.run_index : null; })
      .classed('twin', _twin)
      .classed('visuallyhidden', function(d) { return hidden_runs.indexOf(+d.run_index) > -1; })
      .style('fill', function(d, i) { return null; })
      .style('stroke', function(d, i) { return color(i); })
      .style('stroke-dasharray', function(d, i) { return (_twin) ? '40, 8' : null; });
    draw_axes();
    return this;
  };
  this.custom = function(bool) {
    if (bool === undefined) { return this; }
    _custom_graph = bool;
    return this;
  };
  this.update_data = function() {
    graph_data.graphs = graph_layer.selectAll('.graph-line')
      .data(graph_data.data);
    graph_data.graphs.enter().append('path');
    graph_data.graphs.attr('class', 'graph-line')
      .attr('clip-path', 'url(#' + pre_id('graph_clip') + ')')
      .attr('data-type', function(d) { return d.run_name ? d.run_name : null; })
      .attr('data-run-id', function(d) { return typeof(d.run_index) == 'number' ? d.run_index : null; })
      .classed('twin', _twin)
      .classed('visuallyhidden', function(d) { return hidden_runs.indexOf(+d.run_index) > -1; })
      .style('stroke', function(d, i) { return color(i); })
      .style('stroke-dasharray', function(d, i) { return (_twin) ? '40, 8' : null; });
    if (_custom_graph) {
      add_custom_hover_points();
      add_custom_hover();
    } else {
      handles.data(graph_data.nested);
      add_hover_points();
      add_hover();
    }
    axes_layer.select('.y.axis').call(y_axis);
  };
  this.redraw = function() {
    redraw();
    if (_custom_graph) {
      handle_layer.selectAll('.data-point').remove();
      this.hoverable(true);
    } else {
      handle_layer.selectAll('.segment').remove();
      this.hoverable(true);
    }
    return this;
  };
  this.zoom = function(domain) {
    var new_nest = graph_data.nested.slice().sort(function(a, b) {
            return _timex ? new Date(a.key) - new Date(b.key) : +a.key - +b.key; })
      , ax = false
      , bx = false
      , cx = false
      , dx = false
      , previous = [
          _timex
            ? new Date(new_nest[0].key)
            : +new_nest[0].key,
          new_nest[0].values
        ]
      , as, bs, cs, ds
      , ys = []
      , maxys = []
      , minys = []
      , qy = function(ax, ay, bx, by, qx) {
        return ay + (qx - ax) * ((by - ay) / (bx - ax));
      }
    ;
    new_nest.forEach(function(d, i) {
      if (i > 0) {
        var k = _timex ? new Date(d.key) : +d.key;
        if (k >= domain[0]) {
          if (k <= domain[1]) {
            maxys.push(d3.max(d.values, function (dd) {
              return dd.y;
            }));
            minys.push(d3.min(d.values, function (dd) {
              return dd.y;
            }));
          }
          if (!ax) {
            ax = previous[0];
            as = previous[1].filter(function (d) {
              return hidden_runs.indexOf(+d.run_id) == -1;
            });
            bx = k;
            bs = d.values.filter(function (d) {
              return hidden_runs.indexOf(+d.run_id) == -1;
            });
          }
          if ((k >= domain[1]) && (!cx)) {
            cx = previous[0];
            cs = previous[1].filter(function (d) {
              return hidden_runs.indexOf(+d.run_id) == -1;
            });
            dx = k;
            ds = d.values.filter(function (d) {
              return hidden_runs.indexOf(+d.run_id) == -1;
            });
          }
        }
        previous = [k, d.values];
      }
    });
    for (var i = 0; i < as.length; ++i) {
      ys.push(qy(ax, as[i].y, bx, bs[i].y, domain[0]));
      ys.push(qy(cx, cs[i].y, dx, ds[i].y, domain[1]));
    }
    ys.push(d3.max(maxys));
    ys.push(d3.min(minys));
    _y.domain([
      d3.min(ys),
      d3.max(ys)
    ]);
    graph_data.graphs
      .data(graph_data.data)
      .attr('d', function(d) { return _line(d.data); });
    axes_layer.select('.y.axis').call(y_axis);
    axes_layer.select('.x.axis')
      .attr('transform', 'translate(0,' + (height + 5) + ')')
      .call(x_axis);
    move_custom_hover_points();
  };
  this.change_y = function() {
    axes_layer.select('.y.axis').call(y_axis);
    graph_data.graphs
      .data(graph_data.data)
      .attr('d', function(d) { return _line(d.data); })
      .classed('twin', _twin);
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
      .attr('d', function(d) { return _line(d.data); })
      .style('stroke-width', function(d) { return hidden_runs.indexOf(d.run_index) > -1 ? null : null; });
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
};
