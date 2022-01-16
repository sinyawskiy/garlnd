if(typeof(Garlnd) === 'undefined'){Garlnd={};}
if(typeof(Garlnd.App) === 'undefined'){Garlnd.App={};}

Garlnd.App.setMapSize = function(){
    var map_handler = $('#map'),
        height = $(window).height()-100,
        map_height = height>500?height:500;

    map_handler.css('height', map_height + 'px');
};

Garlnd.App.padZero = function(s, len, c){
    c = c || '0';
    s=s+'';
    while(s.length < len){ s = c + s; }
    return s;
};

Garlnd.App.formatDuration = function(totalSeconds){
    var result = '', days = 0, hours = 0, minutes= 0, seconds =0;
    days = Math.floor(totalSeconds / (3600*24));
    totalSeconds %= (3600*24);
    hours = Math.floor(totalSeconds / 3600);
    totalSeconds %= 3600;
    minutes = Math.floor(totalSeconds / 60);
    seconds = totalSeconds % 60;
    result = Garlnd.App.padZero(hours,2)+':'+Garlnd.App.padZero(minutes,2)+':'+Garlnd.App.padZero(seconds,2);
    return days? days +' дн. '+result:result;
};

Garlnd.App.getAverageSpeed = function(totalSeconds, totalKilometers){
    return totalKilometers/(totalSeconds/3600)||0;
};

Garlnd.App.getDescription = function(statistic, full_statistic){
    var result = '';
    if(!full_statistic||full_statistic==statistic){
        result = statistic.start_time + ' &mdash; ' + statistic.end_time +
           '<br>Время в пути: '+ Garlnd.App.formatDuration(statistic.duration)+
           '<br>Расстояние: '+statistic.distance.toFixed(3)+' км'+
           '<br>Максимальная скорость: '+statistic.max_speed.toFixed(2)+' км/ч'+
           '<br>Средняя скорость: '+Garlnd.App.getAverageSpeed(statistic.duration, statistic.distance).toFixed(2)+' км/ч'+
           '<br>Путевых точек: '+statistic.points;
    }else{
        result = statistic.start_time + ' &mdash; ' + statistic.end_time + '<br>('+full_statistic.start_time + ' &mdash; ' + full_statistic.end_time +')'+
           '<br>Время в пути: '+ Garlnd.App.formatDuration(statistic.duration)+' ('+ Garlnd.App.formatDuration(full_statistic.duration) +')'+
           '<br>Расстояние: '+statistic.distance.toFixed(3)+' ('+ full_statistic.distance.toFixed(3) +') км'+
           '<br>Максимальная скорость: '+statistic.max_speed.toFixed(2)+' ('+ full_statistic.max_speed.toFixed(2) +') км/ч'+
           '<br>Средняя скорость: '+Garlnd.App.getAverageSpeed(statistic.duration, statistic.distance).toFixed(2)+' ('+ Garlnd.App.getAverageSpeed(full_statistic.duration, full_statistic.distance).toFixed(2) + ') км/ч'+
           '<br>Путевых точек: '+statistic.points+' ('+full_statistic.points+')';
    }
    return result;
};


Garlnd.App.calcAveragePosition = function(currentPosition, previousPosition){
    var averagePosition = {
       'created_at': currentPosition.created_at,
       'distance': currentPosition.distance,
       'duration': currentPosition.duration,
       'speed': currentPosition.speed
    };

    if(previousPosition){
        averagePosition.coordinates = [
            (currentPosition.coordinates[0]+previousPosition.coordinates[0])/2.0,
            (currentPosition.coordinates[1]+previousPosition.coordinates[1])/2.0
        ];
    }else{
        averagePosition.coordinates = currentPosition.coordinates;
    }
    return averagePosition;
};


Garlnd.App.loadTrack = function(){
   
    var previousPosition, currentPosition, sourcePosition, el, polyLine,
        device = Garlnd.App.device, manyTracks=false,
        currentTrack, marker, lastPoint=false,
        icon = new L.icon({iconUrl: device.image, iconSize: [30, 30]}),
        statistic = {
            'duration': 0,
            'max_speed': 0,
            'distance': 0,
            'points': 0,
            'start_time': '',
            'end_time': ''
        },
        full_statistic = {
            'duration': 0,
            'max_speed': 0,
            'distance': 0,
            'points': 0,
            'start_time': '',
            'end_time': ''
        };

    for(el in Garlnd.App.positions){

        sourcePosition = Garlnd.App.positions[el];
        currentPosition = Garlnd.App.calcAveragePosition(sourcePosition, previousPosition);

        currentTrack = previousPosition?currentPosition.duration<Garlnd.App.timeDeltaBetweenTracks:false;
        if(!currentTrack){
            console.log([currentPosition, Garlnd.App.timeDeltaBetweenTracks, currentTrack]);
        }

        if(!statistic.start_time.length){
            statistic.start_time = currentPosition.created_at;
        }
        statistic.max_speed = currentPosition.speed>statistic.max_speed? currentPosition.speed: statistic.max_speed;

        if(!full_statistic.start_time.length){
            full_statistic.start_time = currentPosition.created_at;
        }

        statistic.points += 1;

        if(previousPosition && currentTrack){
            if(!polyLine){
                polyLine = new L.Polyline([previousPosition.coordinates, currentPosition.coordinates],{
                    color: device.color,
                    weight: device.width,
                    opacity: 0.5
                });
                polyLine.addTo(Garlnd.App.map).bringToBack();
            }else{
                var latLngs = polyLine.getLatLngs();
                latLngs.splice(latLngs.length, 0, currentPosition.coordinates);
                polyLine.redraw();
            }

            polyLineLabel = new L.Polyline([previousPosition.coordinates, currentPosition.coordinates],{
                weight: device.width,
                opacity: 0
            }).bindLabel(currentPosition.created_at+'<br>Скорость: '+currentPosition.speed+' км/ч', { direction: 'auto' }).on('mouseover', function(e){ e.target.setStyle({opacity:1}); }).on('mouseout', function(e){ e.target.setStyle({opacity:0}); });
            polyLineLabel.addTo(Garlnd.App.map).bringToFront();

            statistic.end_time = currentPosition.created_at;
            statistic.duration += currentPosition.duration;
            statistic.distance += currentPosition.distance;

            full_statistic.end_time = currentPosition.created_at;
            lastPoint = false;
        }else if(previousPosition && !currentTrack){

            if(statistic.points>1){
                marker = new L.marker(previousPosition.coordinates, {icon:icon, riseOnHover:true}).on('mouseover', function(e){ e.target.setOpacity(1); }).on('mouseout', function(e){ e.target.setOpacity(0.5); });
                marker.addTo(Garlnd.App.map).bindLabel(device.title + '<br>' + Garlnd.App.getDescription(statistic), { direction: 'auto' });
                marker.setOpacity(0.5);
            }

            full_statistic.duration += statistic.duration;
            full_statistic.max_speed = statistic.max_speed>full_statistic.max_speed? statistic.max_speed: full_statistic.max_speed;
            full_statistic.distance += statistic.distance;
            full_statistic.points += statistic.points;

            statistic = {
                'duration': 0,
                'max_speed': 0,
                'distance': 0,
                'points': 0,
                'start_time': '',
                'end_time': ''
            };
            polyLine=undefined;
            manyTracks = true;
            if(Garlnd.App.positions.length < parseInt(el)+1){
                lastPoint = true;
            }
        }

        previousPosition = currentPosition;
    }

    marker = new L.marker(currentPosition.coordinates, {icon:icon, riseOnHover:true});
    if(manyTracks){
        if(!lastPoint){
            full_statistic.duration += statistic.duration;
            full_statistic.max_speed = statistic.max_speed>full_statistic.max_speed? statistic.max_speed: full_statistic.max_speed;
            full_statistic.distance += statistic.distance;
            full_statistic.points += statistic.points;
        }
        marker.addTo(Garlnd.App.map).bindLabel(device.title + '<br>' + Garlnd.App.getDescription(statistic, full_statistic), { direction: 'auto' });
    }else{
        marker.addTo(Garlnd.App.map).bindLabel(device.title + '<br>' + Garlnd.App.getDescription(statistic), { direction: 'auto' });
    }
//    setTimeout(Garlnd.App.setCenterMap, 1);
};

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

    Garlnd.App.map = map;
    Garlnd.App.loadTrack();
    setTimeout(function(){
        Garlnd.App.map.fitBounds(Garlnd.App.map.getBounds());
        }, 1
    );
});