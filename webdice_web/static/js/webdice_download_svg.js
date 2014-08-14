(function() {
  "use strict";

  var download_svg = d3.select('#download_svg')
    , serializer = new XMLSerializer()
    , xml
    , get_styles = function() {
        var styles = '';
        for (var i = 0; i < document.styleSheets[0].cssRules.length; i++) {
          var rule = document.styleSheets[0].cssRules[i];
          if (rule.selectorText) {
            if (rule.selectorText.indexOf(">") === -1) {
              styles += "\n" + rule.cssText;
            }
          }
        }
        return styles;
      }
  ;

  download_svg.select('input[type="button"]').on('click', function() {

    d3.event.preventDefault();

    download_svg.selectAll('input[type="hidden"]').remove();

    var svgs = d3.selectAll('#graphs_wrap svg');

    svgs.each(function() {
      var t = d3.select(this)
        , name = t.attr('id').replace('_chart_svg', '')
      ;

      xml = serializer.serializeToString(t.node())
        .replace('</defs>', '<style type="text/css"><![CDATA[' + get_styles() + ']]></style></defs>');


      download_svg.append('input')
        .attr({
          type: 'hidden',
          name: name,
          value: xml
        });
      download_svg.node().submit();

    });

  });

})();