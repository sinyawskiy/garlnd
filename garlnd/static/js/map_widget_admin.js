if(typeof(DjangoAdmin) === 'undefined'){DjangoAdmin={};}
if(typeof(DjangoAdmin.MapWidget) === 'undefined'){DjangoAdmin.MapWidget={};}

(function($) {
    DjangoAdmin.MapWidget.initializeMap=function(){
        var map_handler = $('#map_widget_admin'),
            longitude = parseFloat(map_handler.attr('data-longitude')),
            latitude = parseFloat(map_handler.attr('data-latitude')),
            address = map_handler.attr('data-address');

        var map = new ymaps.Map('map_widget_admin',{
           center: [latitude, longitude],
           zoom: 15,
           behaviors: ["default", "scrollZoom"]
        });

        var searchControl = new ymaps.control.SearchControl({ provider: 'yandex#publicMap' });
        map.controls.add('zoomControl', { top: '5px', right: '5px' })
                   .add('typeSelector',{ top: '5px', right: '50px' })
                   .add('mapTools')
                   .add('scaleLine')
                   .add(searchControl, { left: '120px', top: '5px' });

        var addressItem = new ymaps.GeoObject({
                geometry: {
                    type: "Point",
                    coordinates: [latitude,longitude]
                },
                properties: {
                    hintContent: address
                }
            },{
                preset: "twirl#redDotIcon",
                draggable: false,
                balloonCloseButton: false
        });

        map.geoObjects.add(addressItem);

        DjangoAdmin.MapWidget.map = map;

        DjangoAdmin.MapWidget.map.zoomRange.get([latitude, longitude]).then(function (zoomRange) {
            DjangoAdmin.MapWidget.map.setZoom(zoomRange[1]-1);
        });

    };

    $(document).ready(function () {
        ymaps.ready(function(){
            DjangoAdmin.MapWidget.initializeMap();
        });

        $('#tabs').bind('tabsshow', function (event, ui) {
            if(ui.index==1){
                var map_handler = $('#map_widget_admin'),
                longitude = parseFloat(map_handler.attr('data-longitude')),
                latitude = parseFloat(map_handler.attr('data-latitude'));
                var map = DjangoAdmin.MapWidget.map;
                map.setCenter([latitude, longitude]);
            }
        });
    });
})(django.jQuery);
