$(document).ready(function(){
    $('.help-button').hover(
        function() {
            var id = $(this).siblings('input').attr('name');
            var ht = $(this).offset().top;
            $('#'+id+'-help').show();
            $('#help-wrapper').css('top', ht+'px');
        },
        function() {
            var id = $(this).siblings('input').attr('name');
            $('#'+id+'-help').hide();
        }
    );
});