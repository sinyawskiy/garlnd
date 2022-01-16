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

    $('input.activate_rule').click(function(){
        var self = $(this);
        $.ajax({
            type : 'POST',
            url: self.data('url'),
            success: function(data){
                var rowHandler = self.closest('tr');
                    iconHander = rowHandler.find('td.rule_icon i');
                if(rowHandler.hasClass('error')){
                    rowHandler.removeClass('error');
                    iconHander.removeClass('icon-ban-circle').addClass('icon-ok');
                    self.val('Деактивировать');
                }else{
                    rowHandler.addClass('error');
                    iconHander.removeClass('icon-ok').addClass('icon-ban-circle');
                    self.val('Активировать');
                }

                rowHandler.find('span.deactivated_at').html(data.deactivated_at);
                rowHandler.find('span.activated_at').html(data.activated_at);

            },
            beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Garlnd.getCookie('csrftoken'));}
        });
    });
});
