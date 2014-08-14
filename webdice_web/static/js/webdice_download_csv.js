(function() {
  "use strict";

  var download_csv = d3.select('#download_csv')
  ;

  download_csv.select('input[type="button"]').on('click', function() {

    d3.event.preventDefault();

    download_csv.selectAll('input[type="hidden"]').remove();

    download_csv.append('input')
      .attr({
        type: 'hidden',
        name: 'data',
        value: JSON.stringify(Options.runs)
      });
      download_csv.node().submit();

  });

})();