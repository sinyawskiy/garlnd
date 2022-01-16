import re
import datetime
from json import dumps

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.http import HttpResponseBadRequest, Http404, HttpResponse
from django.template.loader import get_template
from django.views.generic import View, ListView
import math
import pytz
from apps.devices.models import Device
from apps.maps.models import Map
from apps.positions.forms import ExportPositionForm
from apps.positions.models import Position, GPX_FORMAT, KML_FORMAT


# logger = logging.getLogger('mysql')
# class AddPositionView(View):
#     def send_event_to_map(self, device_id, position_id):
#         url = 'http://127.0.0.1:%(port)d/%(device_id)s/%(position_id)s/%(tornading_key)s/' % {
#             'port': settings.TORNADING_PORT,
#             'device_id': device_id,
#             'position_id': position_id,
#             'tornading_key': settings.TORNADING_KEY
#         }
#
#         logger.info(url)
#         try:
#             f = urllib.urlopen(url)
#             f.read()
#             f.close()
#         except IOError:
#             return False
#         return True
#
#     def parse_nmea_time(self, position_date): #20140315095336.0000
#         return datetime.datetime(
#             int(position_date[:4]), int(position_date[4:6]), int(position_date[6:8]),
#             int(position_date[8:10]), int(position_date[10:12]), int(position_date[12:14]),
#             int(position_date[15:])
#         )
#
#     def get(self, request, device_id, longitude, latitude, longitude_type, latitude_type, position_date):
#         if not 'password' in request.GET:
#             return HttpResponseBadRequest()
#         else:
#             password = request.GET['password']
#
#             try:
#                 device = Device.objects.get(id=device_id)
#             except Device.DoesNotExist:
#                 raise Http404()
#             else:
#                 position = Position()
#                 position.device = device
#                 position.longitude = float(longitude)
#                 position.longitude_type = longitude_type
#                 position.latitude = float(longitude)
#                 position.latitude_type = latitude_type
#                 position.created_at = self.parse_nmea_time(position_date)
#                 position.save()
#                 # self.send_event_to_map(address_event_id, status_id)
#                 return HttpResponse()


class ResponseGpx(HttpResponse):
    def __init__(self, data):
        super(ResponseGpx, self).__init__(data, content_type='application/gpx')

class ResponseKml(HttpResponse):
    def __init__(self, data):
        super(ResponseKml, self).__init__(data, content_type='application/kml')

class PositionsExportView(View):
    def get(self, request, device_id):
        user = request.user
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise Http404()
        else:
            if device.owner != user:
                return HttpResponseBadRequest('user have not this device')
            else:
                return render(request, 'positions_export_form.html', {
                    'device': device,
                    'export_form': ExportPositionForm(device_id)
                })

    def post(self, request, device_id):
        user = request.user
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise Http404()
        else:
            if device.owner != user:
                return HttpResponseBadRequest('user have not this device')

            if 'start_date' not in request.POST or 'end_date' not in request.POST or 'export_format' not in request.POST:
                return HttpResponseBadRequest('not start date or not end date in post request')
            try:
                export_format = int(request.POST['export_format'])
            except ValueError:
                return HttpResponseBadRequest('bad export format')

            re_date = re.compile('\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}')
            start_date_request = request.POST['start_date']
            end_date_request = request.POST['end_date']
            # logger.info('start_date:%s end_date:%s'%(start_date_request, end_date_request))
            if not re_date.match(start_date_request) or not re_date.match(end_date_request):
                positions = Position.objects.filter(device=device, is_broken=False).order_by('created_at')

                if positions.count():
                    start_date = positions[0].created_at
                else:
                    start_date = datetime.datetime.now()
            else:
                start_datetime_list = start_date_request.split(' ')
                end_datetime_list = end_date_request.split(' ')

                start_time_list = start_datetime_list[1].split(':')
                end_time_list = end_datetime_list[1].split(':')

                start_date_list = start_datetime_list[0].split('.')
                end_date_list = end_datetime_list[0].split('.')

                start_date = datetime.datetime(int(start_date_list[2]), int(start_date_list[1]), int(start_date_list[0]), int(start_time_list[0]), int(start_time_list[1]))
                end_date = datetime.datetime(int(end_date_list[2]), int(end_date_list[1]), int(end_date_list[0]), int(end_time_list[0]), int(end_time_list[1]))

                if end_date < start_date:
                    temp_date = start_date
                    start_date = end_date
                    end_date = temp_date

                positions = Position.objects.filter(device=device, is_broken=False, created_at__gt=start_date, created_at__lte=end_date).order_by('created_at')

                # logger.info('start_date:%s end_date:%s'%(start_date.strftime('%Y.%m.%d %H:%M'), end_date.strftime('%Y.%m.%d %H:%M')))

            export_track_context = {
                'device_title': device.title,
                'positions': positions
            }

            if export_format == GPX_FORMAT:
                response = ResponseGpx(get_template('positions_format_gpx.xml').render(export_track_context))
                response['Content-Disposition'] = 'attachment; filename=%s.gpx' % device.title

            elif export_format == KML_FORMAT:
                response = ResponseKml(get_template('positions_format_kml.xml').render(export_track_context))
                response['Content-Disposition'] = 'attachment; filename=%s.kml' % device.title
            else:
                return HttpResponseBadRequest('bad export format')
            return response


class PositionsListView(ListView):
    template_name = 'positions_list.html'
    context_object_name = 'positions_list'
    paginate_by = 50
    extra_context = {}

    def get_queryset(self, device_id):
        return Position.objects.filter(device_id=device_id).order_by('-created_at')

    def get(self, request, device_id, *args, **kwargs):
        try:
            device = Device.objects.get(id=device_id, owner=request.user)
        except Device.DoesNotExist:
            raise Http404()
        else:

            self.object_list = self.get_queryset(device_id)
            allow_empty = self.get_allow_empty()

            if not allow_empty:
                # When pagination is enabled and object_list is a queryset,
                # it's better to do a cheap query than to load the unpaginated
                # queryset in memory.
                if (self.get_paginate_by(self.object_list) is not None
                    and hasattr(self.object_list, 'exists')):
                    is_empty = not self.object_list.exists()
                else:
                    is_empty = len(self.object_list) == 0
                if is_empty:
                    raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                            % {'class_name': self.__class__.__name__})

            self.extra_context.update({'device':device})
            context = self.get_context_data()
            return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        for key, value in self.extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
        return context


def distance_between_positions(lat1, lon1, lat2, lon2):
    if lat1 == lat2 and lon1 == lon2:
        return 0
    else:
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lon = math.radians(lon2) - math.radians(lon1)
        delta_lat = phi2 - phi1
        a = (math.sin(delta_lat/2))**2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lon/2))**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return c*6371


class PositionStatusView(View):
    def post(self, request, position_id):
        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            raise Http404()
        else:
            if position.device.owner == request.user:
                position.is_broken = not position.is_broken
                position.save()

                next_position_qs = Position.objects.filter(id__gt=position.id, device=position.device, is_broken=False).order_by('id')[:1]
                result = {'position_exist':False}
                if next_position_qs.count():
                    next_position = next_position_qs[0]
                    before_position_qs = Position.objects.filter(id__lt=next_position.id, device=next_position.device, is_broken=False).order_by('-id')[:1]
                    if before_position_qs.count():
                        before_position = before_position_qs[0]
                        time_diff = next_position.created_at - before_position.created_at
                        duration = time_diff.seconds
                        if duration:
                            next_position.duration = duration
                            distance = distance_between_positions(before_position.latitude, before_position.longitude, next_position.latitude, next_position.longitude)
                            next_position.distance = distance
                            speed = (distance*3600)/duration
                            next_position.speed = speed
                            acceleration = (speed - before_position.speed)/(duration*3.6)
                            next_position.acceleration = acceleration
                            next_position.is_broken = 1 if abs(acceleration) > settings.MAX_ABS_ACCELERATION else 0
                            next_position.save()
                            result = {
                                'position_exist': True,
                                'position_id': next_position.id,
                                'duration': duration,
                                'distance': distance,
                                'speed': speed,
                                'acceleration': acceleration
                            }

                return HttpResponse(dumps(result), content_type='application/json')
            else:
                raise Http404()


class PositionsInit(View):
    def get(self, request, map_id):
        try:
            devices_map = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            raise Http404()
        else:
            password = request.GET['password'] if 'password' in request.GET else ''
            today = datetime.datetime.today()
            this_day = datetime.datetime(today.year, today.month, today.day, hour=0, minute=0, second=0)
            local_tz = pytz.timezone(settings.TIME_ZONE)
            if devices_map.is_opened() or password == devices_map.view_password:
                result = []
                for device in devices_map.devices.all():
                    result.append({
                        'positions': [{
                                'coordinates': [position.latitude, position.longitude],
                                'created_at': '%s' % position.created_at.astimezone(local_tz).strftime('%Y.%m.%d %H:%M:%S'),
                                'speed': position.get_speed()
                        } for position in Position.objects.filter(is_broken=False, device=device, created_at__gte=this_day)],
                        'device_id': device.id,
                    })
                return HttpResponse(dumps(result), content_type='application/json')
            else:
                return HttpResponseBadRequest()


class PositionsUpdateMapView(View):
    def get(self, request, position_id, update_map_key, *args, **kwargs):
        if update_map_key != settings.TORNADING_KEY:
            raise Http404()
        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            raise Http404()

        maps = Map.objects.filter(devices__exact=position.device_id)
        channel_layer = get_channel_layer()

        json_message = dumps({
            'message_type': 'device_position',
            'device_id': position.device_id,
            'coordinates': [position.latitude, position.longitude],
            'speed': int(position.speed * 10) / 10.0 if position.speed else 0,
            'distance': position.distance,
            'created_at': position.created_at.strftime('%Y.%m.%d %H:%M:%S')
        })

        for _map in maps:
            group_name = f'map_{_map.id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'update_map',
                    'message': json_message
                }
            )
        return HttpResponse(dumps({'message': 'ok'}), content_type='application/json')
