$(document).ready(function(){

    // Make sure html5 color element is not replaced
    $('#id_color_rgb').each(function(i, elm){
        if(elm.type!='color'){
            $(elm).minicolors();
        }
    });
});
