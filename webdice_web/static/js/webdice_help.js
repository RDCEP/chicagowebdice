$(document).ready(function(){
  var id, ht, input;
  $('.help-button').hover(
    function() {
      input = $(this).siblings('input');
      if (input.attr('type') == 'radio') {
        id = input.attr('value');
      } else {
        id = input.attr('name');
      }
      ht = $(this).offset().top;
      $('#'+id+'-help').show();
      $('#help-wrapper').css('top', ht+'px');
    },
    function() {
      input = $(this).siblings('input');
      if (input.attr('type') == 'radio') {
        id = input.attr('value');
      } else {
        id = input.attr('name');
      }
      $('#'+id+'-help').hide();
    }
  );
});