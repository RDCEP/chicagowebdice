var WebDICEGraphZoom = function() {
  'use strict';
  var width = 700,
    height = 345,
    zoom_height = 30,
    padding = {top: 10, right: 60, bottom: 10, left: 60},

    /***********************
     Scale and chart objects
     ***********************/

    _max_domains,
    _x = d3.scale.linear().domain([0, 1]).range([1, width - 1]),
    _y = d3.scale.linear().domain([0, 1]).range([zoom_height - 1, 1]),
    _y2 = d3.scale.linear().domain([0, 1]).range([zoom_height - 1, 1]),
    x_axis = d3.svg.axis().scale(_x)
      .orient('bottom')
      .tickSize(0).innerTickSize(0)
      .tickFormat(function(d) { return null; }),
    _line = d3.svg.line()
      .defined(function(d) { return d.y != null; })
      .x(function(d) { return _x(d.x); })
      .y(function(d) { return _y(d.y + d.y0); }),
    _line2 = d3.svg.line()
      .defined(function(d) { return d.y != null; })
      .x(function(d) { return _x(d.x); })
      .y(function(d) { return _y2(d.y + d.y0); }),
    _brush = d3.svg.brush().x(_x),

    /**************
     Data and color
     **************/

    graph_data = {
      graphs: [],       // Graph objects
      twin_graphs: [],  // Twin graph objects
      zoomed_graphs: [],
      data: [],         // Data
      twin_data: [],    // Data for twin graph
    },
    color_list = ['#ccc'],
    hidden_runs = [],
    _color,
    _twin = false,

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
    brush_layer,
    _custom_graph = false,

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
      svg_root.attr({
        width: (width + padding.left + padding.right) + 'px',
        height: zoom_height + 'px'});
      svg_wrap.style({
        width: (width + padding.left) + 'px',
        height: (height + padding.top + padding.bottom) + 'px'});
      svg_defs.select('rect').attr({
        width: width,
        height: zoom_height});
      svg.attr('transform', 'translate(' + padding.left + ',' + (height - 30) + ')');
      _x.range([1, width - 1]);
      _y.range([zoom_height - 1, 1]);
      _y2.range([zoom_height - 1, 1]);
      graph_data.graphs
        .data(graph_data.data)
        .attr('d', function(d) { return _line(d.data); });
      if (_twin) {
        graph_data.twin_graphs
          .data(graph_data.twin_data)
          .attr('d', function (d) {
            return _line2(d.data);
          });
      }
      axes_layer.select('.x.axis')
        .attr('transform', 'translate(0,' + zoom_height + ')')
        .call(x_axis);
    },
    draw_axes = function() {
      /*
       Draw x and y axes, ticks, etc.
       */
      axes_layer.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + (zoom_height + 5) + ')')
        .call(x_axis);
    },
    pre_id = function(str) {
      return svg_id + '_' + str;
    },
    _brushed = function() {
      var bex = _brush.extent(),
        zoom_domain = _brush.empty() ? _x.domain() : bex,
        date_0 = new Date(zoom_domain[0]),
        date_1 = new Date(zoom_domain[1]),
        year_0 = date_0.getFullYear(),
        year_1 = date_1.getFullYear(),
        d0 = _x.domain()[0].getFullYear(),
        d1 = _x.domain()[1].getFullYear(),
        index_0 = year_0 < d0 + 10 ? 0 : Math.floor((year_0 - d0) / 10),
        index_1 = year_1 > d1 - 10 ? (d1 - d0) / 10 : Math.ceil((year_1 - d0) / 10)
      ;
      graph_data.zoomed_graphs.forEach(function(g) {
        g.graph.domain(zoom_domain);
        if (!g.graph.twin() || _twin) {
          g.graph.zoom(index_0, index_1, date_0, date_1);
        }
      });
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
    svg = svg_root.append('g')
      .attr('transform', 'translate(' + padding.left + ',' + (height - 110) + ')');
    graph_layer = svg.append('g').attr('id', pre_id('graph_layer'));
    svg_defs.append('clipPath').attr('id', pre_id('graph_clip')).append('rect')
      .attr({'width': width, 'height': zoom_height });
    axes_layer = svg.append('g').attr('id', pre_id('axes_layer'));
    brush_layer = svg.append('g').attr('id', pre_id('brush_layer'));
    svg.selectAll('g').attr('class', 'graph-layer');
    return this;
  };
  this.twin = function(bool) {
    if (bool == undefined) { return _twin; }
    _twin = bool;
    return this;
  };
  this.x = function(val) {
    if (!val) { return _x; }
    _x = val.range(_x.range()).domain(_x.domain());
    x_axis.scale(_x);
    _brush.x(_x);
    return this;
  };
  this.y = function(val) {
    if (!val) { return _y; }
    _y = val.range(_y.range()).domain(_y.domain());
    return this;
  };
  this.y2 = function(val) {
    if (!val) { return _y2; }
    _y2 = val.range(_y2.range()).domain(_y2.domain());
    return this;
  };
  this.domain = function(xd, yd, y2d) {
    if (xd === undefined) { return [_x.domain(), _y.domain()]; }
    _x.domain(xd);
    _brush.x(_x);
    if (yd) {
      _y.domain(yd);
    }
    if (y2d) {
      _y2.domain(y2d);
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
    graph_data.data = arr[0];
    graph_data.twin_data = arr[1];
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
  this.interpolate = function(str) {
    if (str === undefined) { return this; }
    _line.interpolate(str);
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
      .style('stroke-dasharray', function(d, i) { return (_twin) ? '2, 2' : null; });
    if (_twin) {
      graph_data.twin_graphs = graph_layer.selectAll('.graph-line-twin')
        .data(graph_data.twin_data).enter().append('path')
        .attr('d', function (d) {
          return _line2(d.data);
        })
        .attr('class', 'graph-line-twin')
        .attr('clip-path', 'url(#' + pre_id('graph_clip') + ')')
        .attr('data-type', function (d) {
          return d.run_name ? d.run_name : null;
        })
        .attr('data-run-id', function (d) {
          return typeof(d.run_index) == 'number' ? d.run_index : null;
        })
        .classed('twin', _twin)
        .classed('visuallyhidden', function (d) {
          return hidden_runs.indexOf(+d.run_index) > -1;
        })
        .style('fill', function (d, i) {
          return null;
        })
        .style('stroke', function (d, i) {
          return color(i);
        })
        .style('stroke-dasharray', function (d, i) {
          return (_twin) ? '2, 2' : null;
        });
    }
    draw_axes();
    _brush.on('brush', _brushed);
    brush_layer.append('g')
      .attr('class', 'x brush')
      .call(_brush)
      .selectAll('rect')
      .attr('y', 0)
      .attr('height', zoom_height);
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
      .classed('visuallyhidden', function(d) { return hidden_runs.indexOf(+d.run_index) > -1; })
      .style('stroke', function(d, i) { return color(i); })
      .style('stroke-dasharray', null);
    if (_twin) {
      graph_data.twin_graphs = graph_layer.selectAll('.graph-line.twin')
        .data(graph_data.twin_data);
      graph_data.twin_graphs.enter().append('path');
      graph_data.twin_graphs.attr('class', 'graph-line twin')
        .attr('clip-path', 'url(#' + pre_id('graph_clip') + ')')
        .attr('data-type', function (d) {
          return d.run_name ? d.run_name : null;
        })
        .attr('data-run-id', function (d) {
          return typeof(d.run_index) == 'number' ? d.run_index : null;
        })
        .classed('visuallyhidden', function (d) {
          return hidden_runs.indexOf(+d.run_index) > -1;
        })
        .style('stroke', function (d, i) {
          return color(i);
        })
        .style('stroke-dasharray', '4, 2' );
    }
  };
  this.redraw = function() {
    redraw();
    return this;
  };
  this.zoomed_graphs = function(arr) {
    graph_data.zoomed_graphs = arr;
    return this;
  };
  this.empty_brush = function() {
    d3.selectAll('.brush').call(_brush.clear());
  };
  this.change_y = function() {
    graph_data.graphs
      .data(graph_data.data)
      .attr('d', function(d) { return _line(d.data); })
      .classed('twin', _twin);
    graph_data.twin_graphs
      .data(graph_data.twin_data)
      .attr('d', function(d) { return _line2(d.data); })
      .classed('twin', _twin);
  };
  this.change_x = function() {
    axes_layer.select('.x.axis').call(x_axis);
    graph_data.graphs
      .data(graph_data.data)
      .attr('d', function(d) { return _line(d.data); })
      .style('stroke-width', function(d) { return hidden_runs.indexOf(d.run_index) > -1 ? null : null; });
    graph_data.twin_graphs
      .data(graph_data.twin_data)
      .attr('d', function(d) { return _line2(d.data); })
      .style('stroke-width', function(d) { return hidden_runs.indexOf(d.run_index) > -1 ? null : null; });
  };
  this.show_twin = function(bool) {
    _twin = bool;
    return this;
  }
};
