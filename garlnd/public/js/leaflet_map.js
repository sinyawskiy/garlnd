if(typeof(Garland) === 'undefined'){Garland={};}
if(typeof(Garland.App) === 'undefined'){Garland.App={};}

Garland.App.T = {};
Garland.App.T.ballonTemplate = '<div class="terminal_ballon"><% if(photo_url.length){ %><div class="photo pull-right"><img src="<%= photo_url %>"></div><% } %><p>Номер терминала: <%= number %></p><p><%= organization%></p><p><%= address %></p><% if(services.length){ %><p><%= services %></p><% } %><% if(location.length){ %><p><%= location %></p><% } %><% if(schedule.length){ %><%= schedule %><% } %><% if(description.length){ %><p><%= description %></p><% } %><div class="btn btn-danger btn-block send_report" data-id="<%=id%>">Сообщить о проблеме</div></div>';
Garland.App.initialCenter = [59.938531, 30.313497];
Garland.App.initialZoom = 11;

Garland.App.setMapSize = function(){
    var map_handler = $('#map'),
        height = $(window).height()-160,
        map_height = height>500?height:500;

    map_handler.css('height', map_height + 'px');
};

$(document).ready(function(){
    Garland.App.setMapSize();
    var map = L.map('map'),
        osm = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        });

    map.setView(Garland.App.initialCenter, Garland.App.initialZoom);
    map.addLayer(osm);


    $(window).resize(function(){
        Garland.App.setMapSize();
    });

    var clusterer = new L.MarkerClusterGroup({
        maxClusterRadius: 100,
        spiderfyOnMaxZoom: false,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true
    });
    map.addLayer(clusterer);

    Garland.App.clusterer = clusterer;
    Garland.App.map = map;
    Garland.App.loadEventPoints();

        $(document).on('socket_initialize', function(e){
        console.log('socket_initialize');
        var conn = io.connect('http://garlnd.ru:8001'); //http://garlnd.ru:8001

        conn.on('connect', function() {
            console.log('socket connected');
        });

        conn.on('message', function(data) {
            if(data.event_type=='up'){
                Garland.App.removePoint(data.address_event_id)
            }else{
                data['created_at'] = '';
                Garland.App.addPoint(data)
            }
        });

        conn.on('disconnect', function() {
            console.log('socket disconnected');
        });
    });

});

Garland.getCookie = function (name) {
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

//Garland.App.getCenterBounds=function(){
//    var min_longitude = 0, max_longitude = 0, min_latitude = 0, max_latitude = 0;
//
//    for(var el in this.pointsArray){
//        var coordinates = this.pointsArray[el].geometry.getCoordinates(),
//            longitude =  coordinates[1],
//            latitude = coordinates[0];
//
//        if((longitude < min_longitude) || (!min_longitude)){
//            min_longitude = longitude;
//        }
//        if((longitude > max_longitude) || (!max_longitude)){
//            max_longitude = longitude;
//        }
//        if((latitude < min_latitude) || (!min_latitude)){
//            min_latitude = latitude;
//        }
//        if((latitude > max_latitude) || (!max_latitude)){
//            max_latitude = latitude;
//        }
//    }
//
//    return [[min_latitude, min_longitude], [max_latitude, max_longitude]];
//};
//
//Garland.App.getContainerSize = function(){
//    var map_handler = $("#map");
//    return [map_handler.width(), map_handler.height()];
//};
//
//Garland.App.setCenterMap=function(){
//    if(this.pointsArray.length){
//        var bounds = this.getCenterBounds(),
//        centerAndZoom = ymaps.util.bounds.getCenterAndZoom(bounds, this.getContainerSize());
//        this.map.setCenter(centerAndZoom.center, centerAndZoom.zoom, { checkZoomRange: true });
//    }else{
//        this.resetMap();
//    }
//};
//
//Garland.App.resetMap = function(){
//    this.clusterer.removeAll();
//    this.map.setCenter(this.initialCenter, this.initialZoom);
//};
//
////Garland.App.showPoints = function(points, openBalloon){
////    var el= 0,
////        icon_image = Garland.App.staticUrl + 'img/map_icons/info_terminal_icon.svg',
////        pointsArray = [];
////
////    var ballonTemplate = _.template(Garland.App.T.ballonTemplate);
////
////    for(el in points){
////        var PointObject = points[el];
////        var baloonPointContent = {},
////            ballonHtml = ballonTemplate(PointObject);
////
////        var Point = new ymaps.GeoObject({
////            geometry: {
////                 type: "Point",
////                 coordinates: PointObject.coordinates
////                },
////                    properties: {
////                        hintContent: PointObject.address + '<br>' + PointObject.organization,
////                        clusterCaption: PointObject.number,
////                        balloonContentBody: ballonHtml
////                    }
////                },{
////                    iconImageSize: [30, 30],
////                    iconImageHref: icon_image,
////                    iconOffset: [+5, +40],
////                    hideIconOnBalloonOpen: false,
////                    draggable: false,
////                    balloonCloseButton: true,
////                    hintHideTimeout: 0
////        });
////        Point.terminalAttributes = PointObject;
////        // Добавляем геообъект на карту
////        pointsArray.push(Point);
////
////        if(openBalloon){
////            Garland.App.map.balloon.open(
////                PointObject.coordinates,{
////                    content: ballonHtml
////                },{
////                    closeButton: true
////                }
////            );
////
////        }
////
////    }
////
////    Garland.App.clusterer.add(pointsArray);
////    Garland.App.setCenterMap(points);
////};
////
////
////Garland.App.getTerminalAddress = function(){
////    for(var element in Garland.App.terminalAddresses){
////        if(Garland.App.terminalAddresses[element]['id']==Garland.App.terminalId){
////            return [Garland.App.terminalAddresses[element]];
////        }
////    }
////    return Garland.App.terminalAddresses;
////};

Garland.App.getAddressImage = function(address_type_id, event_type){
    console.log(address_type_id);
    console.log(event_type);
    for(var element in Garland.App.addressTypes){
        if(Garland.App.addressTypes[element]['id']==address_type_id){
            console.log(Garland.App.addressTypes[element][event_type+'_image']);
            return Garland.App.addressTypes[element][event_type+'_image'];
        }
    }
    console.log(Garland.App.addressTypesDefault[event_type]);
    return Garland.App.addressTypesDefault[event_type];
};

Garland.App.loadEventPoints = function(){
    console.log('load_events');
    var self = this,
        pointsArray = [];
    $.ajax({
        type : 'GET',
        dataType : 'json',
        url: '/events/',
        error: function(){
            console.log('error load_events');
        },
        success: function(data){
            var i = 0;
            for(i in data){
                var point = data[i];
                var pointObject = L.marker(new L.LatLng(point.coordinates[0], point.coordinates[1]), {
                    icon: L.icon({
                        'iconUrl': self.getAddressImage(point.address_type_id, 'down'),
                        'iconSize': [30, 30],
                        'iconAnchor': [5, 10]
                    }),
                    title: point.address
                });
                pointObject.event_id = point.event_id;
                pointObject.address_event_id = point.address_event_id;
                pointsArray.push(pointObject);
            }
            self.pointsArray = pointsArray;
            self.clustererRefresh();
            $(document).trigger('socket_initialize');
        },
        beforeSend : function(jqXHR) { jqXHR.setRequestHeader("X-CSRFToken", Garland.getCookie('csrftoken'));}
    });
};


Garland.App.addPoint = function(point){
//    console.log('show '+point.address_event_id);
    var self = Garland.App,
        exist = false,
        pointsArray = [];
    for(var el in self.pointsArray){
        if(self.pointsArray[el].address_event_id == point.address_event_id){
            exist = true;
        }
        pointsArray.push(self.pointsArray[el]);
    }
    if(!exist){
       var pointObject = L.marker(new L.LatLng(point.coordinates[0], point.coordinates[1]), {
                    icon: L.icon({
                        'iconUrl': self.getAddressImage(point.address_type_id, 'down'),
                        'iconSize': [30, 30],
                        'iconAnchor': [5, 10]
                    }),
                    title: point.address
                });
                pointObject.event_id = point.event_id;
                pointObject.address_event_id = point.address_event_id;
        pointObject.event_id = point.event_id;
        pointObject.address_event_id = point.address_event_id;
        pointsArray.push(pointObject);
        self.pointsArray = pointsArray;

        self.clusterer.addLayer(pointObject);
    }
};

Garland.App.removePoint = function(address_event_id){
//    console.log('hide '+address_event_id);
    var self = Garland.App,
        exist = false,
        pointsArray = [];

    for(var el in self.pointsArray){
        if(self.pointsArray[el].address_event_id != address_event_id){
            pointsArray.push(self.pointsArray[el]);
        }else{
            self.clusterer.removeLayer(self.pointsArray[el]);
            exist = true;
        }
    }
    self.pointsArray = pointsArray;

};

Garland.App.clustererRefresh = function(){
    var self = Garland.App;
    console.log(self.pointsArray.length);
    //self.clusterer.removeAll();
    for(var el in self.pointsArray){
        self.clusterer.addLayer(self.pointsArray[el]);
    }

//    self.clusterer.refresh();
//    self.setCenterMap();
   // setTimeout(function(){Garland.App.clustererRefresh();}, 3000);
};
