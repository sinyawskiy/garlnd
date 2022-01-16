var SatsAdmin;
if(!SatsAdmin) SatsAdmin={};

(function($) {
    function addMapRow(){
        $('div.form-row.field-latitude.field-longitude').after('<div class="form-row field-map"><div><label>Карта:</label><div id="YMapsID" style="width:690px;height:450px;"></div></div></div>');
    }

    SatsAdmin.setCoordinates=function(coords){
        SatsAdmin.latitude_handler.val(Number(coords[0]).toFixed(6));
        SatsAdmin.longitude_handler.val(Number(coords[1]).toFixed(6));
    };

    SatsAdmin.saveCoordinates=function(coords){
        var new_coords = [coords[0].toFixed(6), coords[1].toFixed(6)];
		SatsAdmin.placeMark.getOverlay().getData().geometry.setCoordinates(new_coords);
        SatsAdmin.setCoordinates(new_coords);
    };

    SatsAdmin.initializeMap = function(){
        var coords = [Number(SatsAdmin.latitude_handler.val()), Number(SatsAdmin.longitude_handler.val())];
        var map = new ymaps.Map('YMapsID', {center: coords, zoom: 10});

        map.zoomRange.get(coords).then(function (range) {
            map.setCenter(coords, range[1]);
        });

        var SearchControl = new ymaps.control.SearchControl({noPlacemark:true});

        map.controls.add(SearchControl)
                    .add('zoomControl', { top: '5px', right: '5px' })
                    .add('typeSelector',{ top: '5px', right: '50px' })
                    .add('mapTools')
                    .add('scaleLine');

        //Определяем метку и добавляем ее на карту
        var myPlacemark = new ymaps.Placemark(coords,{}, {preset: "twirl#redIcon", draggable: true});

        map.geoObjects.add(myPlacemark);

        //Отслеживаем событие перемещения метки
        myPlacemark.events.add("dragend", function (e) {
            var coords = this.geometry.getCoordinates();
            SatsAdmin.setCoordinates(coords);
        }, myPlacemark);

        SatsAdmin.placeMark = myPlacemark;

        //Отслеживаем событие щелчка по карте
        map.events.add('click', function (e) {
            var coords = e.get('coordPosition');
			SatsAdmin.saveCoordinates(coords);
        });

        //Отслеживаем событие выбора результата поиска
        SearchControl.events.add("resultselect", function (e) {
            var coords = SearchControl.getResultsArray()[0].geometry.getCoordinates();
            SatsAdmin.saveCoordinates(coords);
        });

        //Ослеживаем событие изменения области просмотра карты - масштаб и центр карты
//        map.events.add('boundschange', function (event) {
////            var coords = this.geometry.getCoordinates();
//            if (event.get('newZoom') != event.get('oldZoom')) {
//                SatsAdmin.saveCoordinates();
//            }
//            if (event.get('newCenter') != event.get('oldCenter')) {
//                SatsAdmin.saveCoordinates();
//            }
//
//        });
        SatsAdmin.map = map;

    };

    $(document).ready(function() {
        SatsAdmin.longitude_handler = $('#id_longitude');
        SatsAdmin.latitude_handler = $('#id_latitude');
        SatsAdmin.latitude_handler.attr('disabled','disabled');
        SatsAdmin.longitude_handler.attr('disabled','disabled');
        addMapRow();
        ymaps.ready(function () {
           SatsAdmin.initializeMap();
        });
        $('div.submit-row input').click(function(){
             SatsAdmin.latitude_handler.removeAttr('disabled');
            SatsAdmin.longitude_handler.removeAttr('disabled');
        });

    });
})(django.jQuery);