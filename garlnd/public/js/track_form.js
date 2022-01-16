if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

$(document).ready(function(){

    $('input.lock_checkbox:not(:checked)').closest('.control-group').next().hide();

    $('span.create_password').click(function(){
        $(this).parent().find('input').val(Garlnd.utils.randomString(20, '110'));
    });

    $('input.lock_checkbox').click(function(){
        var self = $(this),
            controlGroupHandler = self.closest('.control-group').next();
        if(!self.is(':checked')){ //uncheck
            controlGroupHandler.hide();
        }else{ //check
            controlGroupHandler.show();
        }
    });

    $('.form_datetime').datetimepicker({
        language: 'ru',
        format: 'dd.mm.yyyy hh:ii',
        autoclose: true,
        todayBtn: true,
        pickerPosition: "bottom-left",
        minuteStep: 10
    });

});