if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

Garlnd.App.initPositions = false;
Garlnd.App.reconnectInterval = null;
Garlnd.App.reconnectDelay = 1000; //ms
Garlnd.App.reconnectCount = 1;

Garlnd.App.setMapSize = function(){
    var map_handler = $('#map'),
        height = $(window).height()-100,
        map_height = height>500?height:500;

    map_handler.css('height', map_height + 'px');
};

Garlnd.App.getDevice = function(device_id){
    for(var i in Garlnd.App.devices){
        if(Garlnd.App.devices[i]['device_id']==device_id){
            return Garlnd.App.devices[i];
        }
    }
    return undefined;
};


Garlnd.App.addTrackPoint = function(data){
//    console.log(data);
    var device = Garlnd.App.getDevice(data.device_id);
    if(device!=undefined){
        if(device.points==undefined){
            device.points = [];
        }
        if(!device.points.length||(device.points.length && data.coordinates != device.points.slice(-1))){
            device.points.push(data.coordinates);

            if(device.points.length==1){
                if(!device.marker){
                    device.icon = new L.icon({iconUrl: device.image, iconSize: [30, 30]});
                    device.marker = new L.marker(data.coordinates, {icon:device.icon});
                    device.marker.addTo(Garlnd.App.map);
                }else{
                    device.marker.setOpacity(1);
                }
            }else{
                device.marker.setLatLng(data.coordinates).update();
                //draw polyline
                var pathCoordinates =  device.points.slice(-2),
                    polyline = new L.Polyline([
                        [pathCoordinates[0][0],pathCoordinates[0][1]],
                        [pathCoordinates[1][0],pathCoordinates[1][1]]
                    ],{
                        color: device.color,
                        weight: device.width,
                        opacity: 1
                    }).bindLabel(data.created_at+'<br>Скорость: '+data.speed+' км/ч', { direction: 'auto' });
                polyline.addTo(Garlnd.App.map);
            }
        }
    }
};

Garlnd.App.smallDurationBetweenPositions = function(end_time, start_time){
    return new Date(end_time).getTime() - new Date(start_time).getTime() < Garlnd.App.timeDeltaBetweenTracks*1000;
};

Garlnd.App.loadInitPositions = function(){
    console.log('load_positions');
    var self = this;
    $.ajax({
        type : 'GET',
        dataType : 'json',
        url: '/positions/init/'+Garlnd.App.mapId+'/?password='+Garlnd.App.viewPassword,
        error: function(){
            console.log('error load_positions');
        },
        success: function(data){
            console.log(data);
            var previousPosition, currentPosition, device, k, m, polyLine;
            for(k in data){
                device = Garlnd.App.getDevice(data[k].device_id);

                for(m in data[k].positions){
                    currentPosition = {
                        'coordinates': data[k].positions[m].coordinates,
                        'created_at': data[k].positions[m].created_at,
                        'speed': data[k].positions[m].speed
                    };
                    if(previousPosition && Garlnd.App.smallDurationBetweenPositions(currentPosition.created_at, previousPosition.created_at)){
                        polyLineLabel = new L.Polyline([previousPosition.coordinates, currentPosition.coordinates],{
                            weight: device.width,
                            opacity: 0
                        }).bindLabel(currentPosition.created_at+'<br>Скорость: '+currentPosition.speed+' км/ч', { direction: 'auto' });
                        polyLineLabel.addTo(Garlnd.App.map);

                        if(!polyLine){
                            polyLine = new L.Polyline([previousPosition.coordinates, currentPosition.coordinates],{
                                color: device.color,
                                weight: device.width,
                                opacity: 0.5
                            });
                            polyLine.addTo(Garlnd.App.map);
                        }else{
                            polyLine.spliceLatLngs(polyLine.getLatLngs().length, 0, currentPosition.coordinates);
                        }
                    }
                    previousPosition = currentPosition;
                }

                if(data[k].positions.length){
                    if(!device.marker){
                        device.icon = new L.icon({iconUrl: device.image, iconSize: [30, 30]});
                        device.marker = new L.marker(currentPosition.coordinates, {icon:device.icon});
                        device.marker.addTo(Garlnd.App.map);
                    }
                    device.marker.setOpacity(0.5);
                }
            }
            Garlnd.App.initPositions = true;
            $(document).trigger('socket_initialize');
        },
        beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Garlnd.getCookie('csrftoken'));}
    });
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


Garlnd.App.updateDeviceStatus = function(data){
    var device = Garlnd.App.getDevice(data.device_id);
    if(device&&device.marker){
        if(!data.status_id){
            device.marker.setOpacity(0.5);
        }else{
            device.marker.setOpacity(1);
        }
    }
};

//TODO: Сделать установку центра карты по количеству точек

$(document).ready(function(){
    Garlnd.App.setMapSize();
    var map = L.map('map'),
        osm = L.tileLayer('/tiles/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        });

    map.setView(Garlnd.App.initialCenter, Garlnd.App.initialZoom);
    map.addLayer(osm);


    $(window).resize(function(){
        Garlnd.App.setMapSize();
    });


    var clusterer = new PruneClusterForLeaflet();

    map.addLayer(clusterer);

    Garlnd.App.clusterer = clusterer;
    Garlnd.App.map = map;
    Garlnd.App.loadInitPositions();

    $(document).on('socket_initialize', function(e){
        if(Garlnd.App.initPositions){
            console.log('socket_initialize');

            const conn = new WebSocket('ws://'+window.location.host+'/ws/map/?map_id='+Garlnd.App.mapId+'&view_password='+Garlnd.App.viewPassword+'&connection_type=map')

            conn.onopen = function(client) {
                console.log('socket connected');
                Garlnd.App.reconnectCount = 1;
            };

            conn.onmessage = function(data) {
                if(data.type === 'message') {
                    var message = JSON.parse(data.data)
                    if (message.message_type === 'location_event') {
                        console.log(message);
                        var status = Garlnd.App.getStatus(message.status_id);
                        if (status.action) {
                            message.image = status.image;
                            Garlnd.App.addEventPoint(message)
                        } else {
                            Garlnd.App.removeEventPoint(message.location_id)
                        }
                    } else if (message.message_type === 'device_position') {
                        console.log(message);
                        Garlnd.App.addTrackPoint(message);
                    } else if (message.message_type === 'device_status') {
                        Garlnd.App.updateDeviceStatus(message);
                    }
                }
            };

            conn.onclose = function() {
                console.log('socket disconnected');
                if(Garlnd.App.reconnectInterval){
                    clearTimeout(Garlnd.App.reconnectInterval);
                }
                Garlnd.App.reconnectInterval = setTimeout(function(){
                    Garlnd.App.reconnectCount+=1;
                    $(document).trigger('socket_initialize');
                }, Garlnd.App.reconnectDelay*Garlnd.App.reconnectCount)
            };
        }
    });

    // var DebugGrid = VirtualGrid.extend({
    //     options: {
    //       cellSize: 10,
    //       pathStyle: {
    //         color: '#3ac1f0',
    //         weight: 2,
    //         opacity: 0.5,
    //         fillOpacity: 0.25
    //       }
    //     },
    //
    //     initialize: function  (options) {
    //       L.Util.setOptions(this, options);
    //       this.rects = {};
    //     },
    //
    //     createCell: function (bounds, coords) {
    //       this.rects[this.coordsToKey(coords)] = L.rectangle(bounds, this.options.pathStyle).addTo(map);
    //     },
    //
    //     cellEnter: function (bounds, coords) {
    //       var rect = this.rects[this.coordsToKey(coords)];
    //       map.addLayer(rect);
    //     },
    //
    //     cellLeace: function (bounds, coords) {
    //       var rect = this.rects[this.coordsToKey(coords)];
    //       map.removeLayer(rect);
    //     },
    //
    //     coordsToKey: function (coords) {
    //       return coords.x + ':' + coords.y + ':' +coords.z;
    //     }
    //   });
    //
    //   var debugGrid = new DebugGrid().addTo(Garlnd.App.map);
    //
    //   Garlnd.App.map.on('zoomend', function(e){
    //      console.log('zoomend', e.target._zoom);
    //
    //   });
    //
    //   Garlnd.App.map.on('load', function(e){
    //       console.log(e.target._zoom);
    //   });

});

Garlnd.curPos = 360;
Garlnd.updatePosition = function(){
    Garlnd.App.addTrackPoint({device_id: 1, coordinates: [1,Garlnd.curPos]});
    Garlnd.curPos-=1;
};
Garlnd.test = function(){
    for(var i=1;i<360;i++){
        setTimeout(Garlnd.updatePosition, 200*i)
    }
};