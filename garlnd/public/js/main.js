if(typeof(Garland) === 'undefined'){Garland={};}
if(typeof(Garland.App) === 'undefined'){Garland.App={};}

Garland.App.getIntRandom = function(min, max){
  return Math.floor(Math.random() * (max - min) + min);
};


$(document).ready(function(){
    setInterval(function(){
        var starsHandler= $('.hero-unit .star'),
            el = Garland.App.getIntRandom(0, starsHandler.length),
            starHandler = $(starsHandler[el]);

        if(starHandler.is(':visible')){
            starHandler.fadeOut('slow');
        }else{
            var colors = ['#ff6600','#ff3366','#33ccff'],
            color = colors[Garland.App.getIntRandom(0,2)];

            starHandler.css('background-color', color);
            starHandler.fadeIn('slow');
        }
    }, 1500);
});
