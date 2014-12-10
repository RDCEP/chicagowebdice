(function() {



  var WebDICEPreview = function() {
    "use strict";
      var _f, _n, _h, _w, _t, _s,
        _l = false,
        svg = false,
        data,
        x = d3.scale.linear(),
        y,
        line = d3.svg.line().x(function (d) {
          return x(d.x);
        }).y(function (d) {
          return y(d.y);
        })
      ;
      this.init = function(t, f, h, w, v, m, s, o) {
        _f = f;
        _h = h;
        _w = w;
        _t = t;
        y = (s == 'log') ? d3.scale.log() : d3.scale.linear();
        data = _f(v, o);
        x.range([0, w]);
        y.range([h, 0]);

        x.domain(d3.extent(data, function (d) {
          return d.x;
        }));
        y.domain(d3.extent(_f(m, o), function (d) {
          return d.y;
        }));
        svg = !svg ? t.append('svg').attr({width: w, height: h})
          .append('g').attr('transform', 'translate(0,0)') : svg;
        _l = !_l ? svg.append('path').attr('class', 'parameter-preview-line') : _l;
        _l.datum(data)
          .attr('d', line);
        return this;
      };
      this.draw = function(v, o) {
        _l.datum(_f(v, o)).attr('d', line);
        return this;
      }
    },

    preview_graphs = {},
    radios = d3.selectAll('#parameters input[type="radio"]'),
    sliders = d3.selectAll('#parameters .range-wrap input[type="range"]'),

    update_slider = function() {
      var t = d3.select(this),
        p = d3.select(this.parentNode.parentNode),
        _eq = d3.select(this.form).classed('advanced')
          ? advanced_equations
          : standard_equations,
        current = p.select('.current-range-val'),
        preview = p.select('.parameter-preview-line'),
        name = t.attr('name'),
        reverse = t.classed('reverse'),
        min = reverse ? parseFloat(t.attr('max')) : parseFloat(t.attr('min')),
        max = reverse ? parseFloat(t.attr('min')) : parseFloat(t.attr('max')),
        dot = p.select('.tick'),
        val = parseFloat(t.property('value')),
        val = reverse ? Math.abs(100 - val) : val,
        prec = parseInt(t.attr('data-prec')),
        pct = ((parseFloat(val) - min) / (max - min) - .5) * 100;

      current.text(val.toFixed(prec).toString()).style('left', pct + '%');

      if (preview_graphs.hasOwnProperty(name)) {
        var o = false,
          eq = _eq[name];

        if (eq.hasOwnProperty('other_input')) {
          o = +d3.select('input[name="' + eq.other_input + '"]').property('value');
        }

        if (eq.shared) {
          preview_graphs[name].draw(o, val);
        } else {
          preview_graphs[name].draw(val, o);
        }

      }
    };

  sliders.each(function () {

    var input = d3.select(this),
      name = input.attr('name'),
      _eq = d3.select(this.form).classed('advanced')
        ? advanced_equations
        : standard_equations,
      t = d3.select('.parameter-preview[data-input-parameters*="' + name + '"]');
    if (!t.empty() && _eq.hasOwnProperty(name)) {
      var value = input.property('value'),
        eq = _eq[name];
      if (!eq.shared) {
        var max = +input.attr(eq['max']),
          s = eq['scale'],
          f = eq['output'],
          w = eq['width'],
          h = 100,
          oname = false,
          o;
        if (eq.hasOwnProperty('other_input')) {
          oname = eq.other_input;
          o = +d3.select('input[name="'+eq.other_input+'"]').property('value');
        }
        preview_graphs[name] = new WebDICEPreview()
          .init(t, f, h, w, value, max, s, o);
        t.append('figcaption').text(eq['legend']);
      } else {
        preview_graphs[name] = preview_graphs[eq.other_input];
      }
    }
  });

  radios.on('change', function () {

    var t = d3.select(this),
      disabled = t.property('checked');

    radios.each(function () {

      var p = d3.select(d3.select(this).node().parentNode.parentNode);

      p.selectAll('.not-disabled')
        .classed('not-disabled', false)
        .classed('disabled', true);
      p.selectAll('input')
        .property('disabled', true);
      p.selectAll('input[type="radio"]')
        .property('disabled', false)

    });

    if (disabled) {

      d3.select(t.node().parentNode.parentNode).selectAll('.disabled')
        .classed('not-disabled', true)
        .classed('disabled', false);
      d3.select(t.node().parentNode.parentNode).selectAll('input')
        .property('disabled', false);

    }

    if (t.attr('name') == 'damages_model') {
      if (t.property('value') != 'dice_2010') {
        d3.select('.parameter-preview[data-input-parameters="damages_exponent"]')
          .style('display', 'none');
      } else {
        d3.select('.parameter-preview[data-input-parameters="damages_exponent"]')
          .style('display', 'block');
      }
    }

  });

  sliders.on('change', update_slider);
  sliders.on('input', update_slider);
})();