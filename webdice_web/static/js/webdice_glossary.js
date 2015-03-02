(function() {
  "use strict";

  var l = d3.selectAll('.link-to-advanced-glossary')
    , sl = d3.selectAll('#alpha_links a')
    , term = window.location.hash.substr(1)
  ;

  var glossary_scroll = function(term) {
    term || d3.event.preventDefault();
    var start_y = window.pageYOffset
      , scroll_object_id = term || this.getAttribute('data-scroll-object')
      , scroll_object = document.getElementById(scroll_object_id)
      , scroll_object_y = scroll_object.getBoundingClientRect().top
      , scroll_object_h = scroll_object.getBoundingClientRect().height
//          , buffer_y = document.getElementById('text_wrap').getBoundingClientRect().top
      , buffer_y = 60
      , body = document.body
      , html = document.documentElement
      , height = Math.max( body.scrollHeight, body.offsetHeight,
          html.clientHeight, html.scrollHeight, html.offsetHeight )
    ;
    window.scrollTo(0, scroll_object_y + start_y - buffer_y - 30);
  };

  if (term.length > 0) {
//    window.scrollTo(0, document.body.scrollHeight - 60);
    window.scrollTo(0, 0);
    glossary_scroll('glossary__' + term);
  }

  sl.on('click', glossary_scroll);

  l.on('click', function() {

    d3.event.preventDefault();

    var link = d3.select(this)
      , div = d3.select(this.parentNode.parentNode)
      , term = div.attr('id').split('__')[1]
    ;

    d3.xhr('/glossary/advanced/'+term)
    .responseType('html')
    .get()
    .on('load', function(_data) {

      var html = _data.response;
      div.select('.advanced-term')
        .html(html);
//          .transition()
//          .duration(100)
//          .attr({
//            cx: this.x,
//            cy: this.y
//          });
      MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
      link.remove();
    });

  });

  d3.selectAll('a').filter(function(d) {
    return d3.select(this).attr('href').substr(0, 11) == '#glossary__';
  })
    .on('click', function() {
      d3.event.preventDefault();
      var t = d3.select(this).attr('href').substr(1);
      glossary_scroll(t);
      window.location.hash = t.substr(10);
      d3.select('#main-nav').style('display', 'none').style('display', 'block');
    });

})();