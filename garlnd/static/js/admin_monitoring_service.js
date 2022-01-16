var SatsAdmin;
if(!SatsAdmin) SatsAdmin={};

(function($) {
    SatsAdmin.getPin=function(){
        var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');
        var rnd_length = 30;
        var rnd_str = '';
        for (var i = 0; i < rnd_length; i++) {
            rnd_str += chars[Math.floor(Math.random() * chars.length)];
        }
        $('#id_pin_code').val(rnd_str);
    };

    function add_pin_code_button(){
        $('#id_pin_code').after('&nbsp;<input type="button" value="Создать PIN код" id="pin_button" onclick="SatsAdmin.getPin();">')
    }

    $(document).ready(function() {
        add_pin_code_button();
    });
    
})(django.jQuery);