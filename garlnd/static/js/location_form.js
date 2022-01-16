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

Garlnd.setMapCenter = function(marker){
    var position = marker.getLatLng();

    lat = Number(Garlnd.normalizeCoordinate(position['lat'])).toFixed(6);
    lng = Number(Garlnd.normalizeCoordinate(position['lng'])).toFixed(6);

    $('#id_longitude').val(lng).next().text(lng);
    $('#id_latitude').val(lat).next().text(lat);
};

Garlnd.getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie.length) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

Garlnd.App.addLocations = function(map, mapId){
    var self = this;

    map.eachLayer(function(pointObject){
       if(pointObject.is_location){
            map.removeLayer(pointObject);
       }
    });

    if(mapId.length){
        $.ajax({
            type : 'GET',
            dataType : 'json',
            url: '/maps/'+mapId+'/locations/json/',
            error: function(){
                console.log('error load_events');
            },
            success: function(data){
                if(data.length){
                    var layerGroup = L.featureGroup();
                    for(var el in data){
                        var point = data[el],
                            pointObject = L.marker(point.coordinates, {
                            icon: L.icon({
                                'iconUrl': point.image,
                                'iconSize': [30, 30],
                                'iconAnchor': [5, 10]
                            }),
                            opacity: typeof(Garlnd.App.locationId)!=='undefined' && point.location_id==Garlnd.App.locationId ?0.375: 0.75,
                            title: point.title
                        });
                        layerGroup.addLayer(pointObject);
                    }
                    layerGroup.is_location = true;
                    layerGroup.addTo(map).bringToBack();
                    map.fitBounds(map.getBounds());
                }
            },
            beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Garlnd.getCookie('csrftoken'));}
        });
    }
};

$(document).ready(function(){
    var imageControlGroupHandler = $('#id_image').closest('.control-group'),
        showAlwaysHandler = $('#id_show_always'),
        mapHandler = $('#map_location'),
        initialCoordinates = [$('#id_latitude').val(), $('#id_longitude').val()],
        map = L.map('map_location'),
        mapLocationsHandler = $('#id_map_locations');
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

    map.setView(initialCoordinates, Garlnd.App.initialZoom);
    var marker = new L.Marker(initialCoordinates, {draggable:false});

    if(typeof(Garlnd.App.locationId)!=='undefined' && Garlnd.App.locationImage.length){
        marker.setIcon(L.icon({
            'iconUrl': Garlnd.App.locationImage,
            'iconSize': [30, 30],
            'iconAnchor': [5, 10]
        }));
    }

    map.addLayer(marker);

    map.on('move', function () {
		marker.setLatLng(map.getCenter());
        Garlnd.setMapCenter(marker);
	});

    map.on('zoomstart', function(){
        this.tempCoordinates = this.getCenter();
    });

    map.on('zoomend', function(){
        this.panTo(this.tempCoordinates);
    });

    showAlwaysHandler.change(function(){
        if($(this).val()=='False'){
            imageControlGroupHandler.hide();
        }else{
            imageControlGroupHandler.show();
        }
    });
    if(showAlwaysHandler.val()=='False'){
        imageControlGroupHandler.hide();
    }

    mapLocationsHandler.change(function(){
        Garlnd.App.addLocations(map, $(this).val());
    });
    mapLocationsHandler.trigger('change');

});
