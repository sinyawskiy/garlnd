if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

Garlnd.getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie.length) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

$(document).ready(function(){

    $('input.status').click(function(){
        var self = $(this);
        $.ajax({
            type : 'POST',
            url: self.data('url'),
            success: function(data){
                var rowHandler = self.closest('tr');
                if(rowHandler.hasClass('is_broken')){
                    rowHandler.removeClass('is_broken error');
                    self.val('Исключить');
                }else{
                    rowHandler.addClass('is_broken error');
                    self.val('Восстановить');
                }
                if(data.position_exist){
                    var nextPositionHandler = $('tr[data-id='+data.position_id+'] td');
                    if(nextPositionHandler.length){
                        $(nextPositionHandler[1]).html(data.duration);
                        $(nextPositionHandler[4]).html(data.distance);
                        $(nextPositionHandler[5]).html(data.speed);
                        $(nextPositionHandler[6]).html(data.acceleration);
                    }
                }
            },
            beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Garlnd.getCookie('csrftoken'));}
        });
    });
});
