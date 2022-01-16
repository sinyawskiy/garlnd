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
        mapHandler = $('#map_graticule'),
        latAngle1 = $('#id_latitude_angle_1').val(),
        lonAngle1 = $('#id_longitude_angle_1').val(),
        latAngle2 = $('#id_latitude_angle_2').val(),
        lonAngle2 = $('#id_longitude_angle_2').val(),
        initialCoordinates1,
        initialCoordinates2,
        map = L.map('map_graticule'),
        mapLocationsHandler = $('#id_map_locations');
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

    map.setView(Garlnd.App.initialCenter, Garlnd.App.initialZoom+1);

    if(latAngle1&&latAngle2&&lonAngle1&&lonAngle2){
        initialCoordinates1 = [latAngle1, lonAngle1];
        initialCoordinates2 = [latAngle2, lonAngle2];
    }else{
        var mapBounds = map.getBounds();
        initialCoordinates1 = mapBounds.getNorthWest();
        initialCoordinates2 = mapBounds.getSouthEast();
    }

    var marker1 = new L.Marker(initialCoordinates1, {draggable: true}),
        marker2 = new L.Marker(initialCoordinates2, {draggable: true});

    marker1.setIcon(L.icon({
        'iconUrl': Garlnd.App.locationImage1,
        'iconSize': [30, 30],
        'iconAnchor': [5, 10]
    }));

    marker2.setIcon(L.icon({
        'iconUrl': Garlnd.App.locationImage2,
        'iconSize': [30, 30],
        'iconAnchor': [5, 10]
    }));

    map.setView(Garlnd.App.initialCenter, Garlnd.App.initialZoom-1);

    map.addLayer(marker1);
    map.addLayer(marker2);

    var Graticule = VirtualGrid.extend({
        options: {
            cellSizeKm: 5,
            cellSize: 100,
            pathStyle: {
                color: '#3ac1f0',
                weight: 2,
                opacity: 0.5,
                fillOpacity: 0.25
            },
            bounds: L.latLngBounds(initialCoordinates1, initialCoordinates2)
        },
        initialize: function  (options) {
            L.Util.setOptions(this, options);
            this.rects = {};
        },
        createCell: function (bounds, coords) {
            this.rects[this.coordsToKey(coords)] = L.rectangle(bounds, this.options.pathStyle).addTo(map);
        },
        cellLeace: function (bounds, coords) {
            var rect = this.rects[this.coordsToKey(coords)];
            map.removeLayer(rect);
        },
        coordsToKey: function (coords) {
            return coords.x + ':' + coords.y + ':' +coords.z;
        },
        cellEnter: function (bounds, coords) {
            var rect = this.rects[this.coordsToKey(coords)];
            map.addLayer(rect);
            console.log(this.rects);
        },
        _cellCoordsToBounds: function (coords) {
            var map = this._map;
            var cellSize = this._getCellSize();
            var nwPoint = coords.multiplyBy(cellSize);
            var sePoint = nwPoint.add([cellSize, cellSize]);
            var nw = map.wrapLatLng(map.unproject(nwPoint, coords.z));
            var se = map.wrapLatLng(map.unproject(sePoint, coords.z));

            return L.latLngBounds(nw, se);
        },
        _getCellSize: function () {
             var metersPerPixel = 40075016.686 * Math.abs(Math.cos(this._map.getCenter().lat * 180/Math.PI)) / Math.pow(2, this._map.getZoom()+8),
                 pixels = this.options.cellSizeKm*1000/metersPerPixel;
             console.log(pixels);
             return pixels;
        },
        _getBounds: function() {
            var bounds;
            if(this.options.bounds){
                bounds = L.bounds(
                    this._map.latLngToLayerPoint(this.options.bounds.getNorthWest()),
                    this._map.latLngToLayerPoint(this.options.bounds.getSouthEast())
                )
            }else{
                bounds = this._map.getPixelBounds();
            }
            bounds = this._map.getPixelBounds();
            console.log(bounds);

            return bounds;
        },
        _update: function () {
              if (!this._ok) {
                return;
              }

              if (!this._map) {
                return;
              }

              var bounds = this._getBounds();
              var cellSize = this._getCellSize();

              // cell coordinates range for the current view
              var cellBounds = L.bounds(
                bounds.min.divideBy(cellSize).floor(),
                bounds.max.divideBy(cellSize).floor());

              this._removeOtherCells(cellBounds);
              this._addCells(cellBounds);

              this.fire('cellsupdated');

              this._ok = false;
              console.log(this._cells);
        }
    });


    var graticule = new Graticule().addTo(map);


 //    map.on('move', function () {
//		marker.setLatLng(map.getCenter());
//        Garlnd.setMapCenter(marker);
//	});
//
//    map.on('zoomstart', function(){
//        this.tempCoordinates = this.getCenter();
//    });
//
//    map.on('zoomend', function(){
//        this.panTo(this.tempCoordinates);
//    });
//
//    showAlwaysHandler.change(function(){
//        if($(this).val()=='False'){
//            imageControlGroupHandler.hide();
//        }else{
//            imageControlGroupHandler.show();
//        }
//    });
//    if(showAlwaysHandler.val()=='False'){
//        imageControlGroupHandler.hide();
//    }
//
//    mapLocationsHandler.change(function(){
//        Garlnd.App.addLocations(map, $(this).val());
//    });
//    mapLocationsHandler.trigger('change');

});
