(function() {
  "use strict";

  var radios = d3.selectAll('#parameters input[type="radio"]'),
    sliders = d3.selectAll('#parameters .range-wrap input[type="range"]'),

    update_slider = function() {

      var t = d3.select(this),
        p = d3.select(t.node().parentNode.parentNode),
        current = p.select('.current-range-val span'),
        min = parseFloat(t.attr('min')),
        max = parseFloat(t.attr('max')),
        dot = p.select('.tick'),
        val = t.property('value'),
        pct = ((parseFloat(val) - min) / (max - min) - .5) * 100;

      current.text(val).style('left', pct + '%');

    };

  radios.on('change', function() {

    var t = d3.select(this),
      disabled = t.property('checked');

    radios.each(function() {

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
  });

  sliders.on('change', update_slider);
  sliders.on('input', update_slider);
})();