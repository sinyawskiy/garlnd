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

Garlnd.setMapCenter = function(map, marker){
    var position = marker.getLatLng();

    lat = Number(Garlnd.normalizeCoordinate(position['lat'])).toFixed(6);
    lng = Number(Garlnd.normalizeCoordinate(position['lng'])).toFixed(6);
    zoom = map.getZoom();

    $('#id_longitude').val(lng).next().text(lng);
    $('#id_latitude').val(lat).next().text(lat);
    $('#id_zoom').val(zoom).next().text(zoom);
};



$(document).ready(function(){

    $('input.lock_checkbox:not(:checked)').parent().closest('.mb-3').next().hide();
    $('span.create_password').click(function(){
        $(this).parent().find('input').val(Garlnd.utils.randomString(20, '110'));
    });
    $('input.lock_checkbox').click(function(){
        var self = $(this),
            controlGroupHandler = self.parent().closest('.mb-3').next();
        if(!self.is(':checked')){ //uncheck
            controlGroupHandler.hide();
//            controlGroupHandler.find('input').val('');
        }else{ //check
            controlGroupHandler.show();
        }
    });

    var mapHandler = $('#map_center'),
        initialCoordinates = [$('#id_latitude').val(), $('#id_longitude').val()],
        map = L.map('map_center');
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

    map.setView(initialCoordinates, $('#id_zoom').val());
    var marker = new L.Marker(initialCoordinates, {draggable:false});
    map.addLayer(marker);

    map.on('move', function () {
		marker.setLatLng(map.getCenter());
        Garlnd.setMapCenter(map, marker);
	});

    map.on('zoomstart', function(){
        this.tempCoordinates = this.getCenter();
    });

    map.on('zoomend', function(){
        this.panTo(this.tempCoordinates);
    });

});
