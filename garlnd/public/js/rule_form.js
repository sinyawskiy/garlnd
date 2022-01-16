if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}


Garlnd.normalizeCoordinate = function(coordinate){
    coordinate = parseFloat(coordinate);
    if(coordinate<-180){
        return 180+coordinate%180;
    }else if(coordinate>180){
        return 180-coordinate%180;
    }
    return coordinate%180;
};


Garlnd.App.setLatLng = function(latitude, longitude){
    var lat = Number(Garlnd.normalizeCoordinate(latitude)).toFixed(6),
        lng = Number(Garlnd.normalizeCoordinate(longitude)).toFixed(6);

    $('#id_initial_longitude').val(lng).next().text(lng);
    $('#id_initial_latitude').val(lat).next().text(lat);
};

Garlnd.App.mapMove = function(){
    var mapCenter = Garlnd.App.map.getCenter();
    Garlnd.App.circle.setLatLng(mapCenter);
    Garlnd.App.marker.setLatLng(mapCenter);
    Garlnd.App.setLatLng(mapCenter.lat, mapCenter.lng);
};

Garlnd.App.isValueInList = function(value, values_list){
    for(var el in values_list){
        if(values_list[el]==value){
            return true;
        }
    }
    return false;
};


$(document).ready(function(){
    $("#id_phone_number_sms").mask("(999) 999-99-99");

    var ruleTypeHandler = $('#id_rule_type'),
        longitudeHandler = $('#id_initial_longitude'),
        latitudeHandler = $('#id_initial_latitude'),
        distanceHandler = $('#id_distance_offset'),
        mapHandler = $('#map_rule');

    distanceHandler.slideControl({
        fromMinMaxBounds: true,
        findLabel: false
    });

    var initialCoordinates = [latitudeHandler.val() || Garlnd.App.initialCenter[0], longitudeHandler.val() || Garlnd.App.initialCenter[1]],
        map = L.map('map_rule'),
        mapLocationsHandler = $('#id_map_rule');
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

    map.setView(initialCoordinates, Garlnd.App.initialZoom);

    var circle = new L.Circle(initialCoordinates, 100, {draggable:false});
    map.addLayer(circle);
    var marker = new L.Marker(initialCoordinates, {draggable:false});
    map.addLayer(marker);

    Garlnd.App.map = map;
    Garlnd.App.circle = circle;
    Garlnd.App.marker = marker;

    map.on('move', Garlnd.App.mapMove);

    map.on('zoomstart', function(){
        this.tempCoordinates = this.getCenter();
    });

    map.on('zoomend', function(){
        this.panTo(this.tempCoordinates);
    });

    distanceHandler.change(function(){
        var value = $(this).val();
            if(value.length){
                value=parseFloat(value);
                Garlnd.App.circle.setRadius(value*1000);
                Garlnd.App.map.fitBounds(Garlnd.App.circle.getBounds());
            }
    });

    ruleTypeHandler.change(function(){
        var ruleTypeVal = $(this).val(),
            ruleType = parseInt(ruleTypeVal?ruleTypeVal:''),
            mapControlHandler = mapHandler.closest('.control-group');

        if(ruleType===1||ruleType===2){
            mapControlHandler.show();
            Garlnd.App.map.invalidateSize();
        }else{
            mapControlHandler.hide();
        }

        $('input[data-type=rule]').each(function(){
            var self = $(this);
            if(Garlnd.App.isValueInList(ruleType, self.data('rule_id'))){
                self.parent().closest('.mb-3').show();
            }else{
                self.val('');
                self.parent().closest('.mb-3').hide();
            }
        });

        if(ruleType===1||ruleType===2){
            var distanceValue = distanceHandler.val() || 0.025;
            Garlnd.App.setLatLng(Garlnd.App.initialCenter[0], Garlnd.App.initialCenter[1]);
            distanceHandler.val(distanceValue);
            distanceHandler.trigger('change');
        }

    });
    ruleTypeHandler.trigger('change');

});

