$(document).ready(function(){
  $('.help-button').hover(
    function() {
      var input = $(this).siblings('input');
      if (input.attr('type') == 'radio') {
        var id = input.attr('value');
      } else {
        var id = input.attr('name');
      }
      var ht = $(this).offset().top;
      $('#'+id+'-help').show();
      $('#help-wrapper').css('top', ht+'px');
    },
    function() {
      var input = $(this).siblings('input');
      if (input.attr('type') == 'radio') {
        var id = input.attr('value');
      } else {
        var id = input.attr('name');
      }
      var id = $(this).siblings('input').attr('name');
      $('#'+id+'-help').hide();
    }
  );
});