if (typeof(Garlnd) === 'undefined') Garlnd = {};
if (typeof(Garlnd.utils) === 'undefined') Garlnd.utils = {};

Garlnd.utils.randomString = function(length, strType){
    if(!strType||typeof(strType)=='undefined'||strType=='000'){
        strType = '111';
    }
    var chars = ['0123456789', 'ABCDEFGHIJKLMNOPQRSTUVWXTZ', 'abcdefghiklmnopqrstuvwxyz'],
        strTypeArr= strType.split(''),
        resultChars = '',
        resultString = '';

    for(var el in strTypeArr){
        if(strTypeArr[el]!='0'){
            resultChars+=chars[el];
        }
    }
    var charsArr = resultChars.split('');

    if (! length) {
        length = Math.floor(Math.random() * charsArr.length);
    }

    for (var i = 0; i < length; i++) {
        resultString += charsArr[Math.floor(Math.random() * charsArr.length)];
    }
    return resultString;
};

$(document).ready(function(){
   $('div.triangle').addClass('run');
});