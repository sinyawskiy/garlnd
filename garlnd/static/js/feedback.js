if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

Garlnd.App.randomString = function(length) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');

    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }

    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
};

$(document).ready(function () {
    $('img.captcha').click(function(){
//        console.log('click');
        $.getJSON('/captcha/refresh/?'+Garlnd.App.randomString(5), {}, function(json) {
            $('img.captcha').attr('src', json['image_url']);
            $('#id_captcha_0').val(json['key']);
//            console.log(json);
        });
    });
});
