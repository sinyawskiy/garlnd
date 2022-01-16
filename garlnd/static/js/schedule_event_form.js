if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

Garlnd.getCookie = function (name) {
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

Garlnd.App.getLocations = function(mapId, locationHandler){
    var options = '<option value="" selected="selected">---------</option>';
    if(mapId.length){
        $.ajax({
            type : 'GET',
            dataType : 'json',
            url: '/maps/'+mapId+'/locations/json/',
            error: function(){
                console.log('error load_events');
            },
            success: function(data){
                for(var el in data){
                    options += '<option value="' + data[el].location_id + '">' + data[el].title + '</option>';
                }
                locationHandler.html(options);
            },
            beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Garlnd.getCookie('csrftoken'));}
        });
    }else{
        locationHandler.html(options);
    }
};

$(document).ready(function(){
    $('.form_datetime').datetimepicker({
        language: 'ru',
        format: 'dd.mm.yyyy hh:ii',
        autoclose: true,
        todayBtn: true,
        pickerPosition: "bottom-left",
        minuteStep: 1
    });

    var eventTypeHandler = $('#id_event_type'),
        periodHandler = $('#id_period'),
        mapHandler = $('#id_event_map'),
        locationHandler = $('#id_location');

    periodHandler.find('input').slideControl({
        fromMinMaxBounds: true,
        findLabel: true,
        step: 1
    });

    var periodInputsHandler = periodHandler.find('input'),
        periodControlHandler = periodHandler.closest('.control-group');

    eventTypeHandler.change(function(){
        if(parseInt($(this).val())==1){
            console.log(periodInputsHandler);
            periodInputsHandler.val(0).trigger('change');
            periodControlHandler.hide();
        }else{
            periodControlHandler.show();
        }
    });
    eventTypeHandler.trigger('change');

    mapHandler.change(function(){
        Garlnd.App.getLocations($(this).val(), locationHandler);
    });
});