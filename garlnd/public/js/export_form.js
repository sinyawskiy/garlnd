$(document).ready(function(){
    $('.form_datetime').datetimepicker({
        language: 'ru',
        format: 'dd.mm.yyyy hh:ii',
        autoclose: true,
        todayBtn: true,
        pickerPosition: "bottom-left",
        minuteStep: 10
    });
});
