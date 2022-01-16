import string
from json import dumps

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from django.views.generic import View, ListView, DeleteView
from utils.functions import id_generator
from apps.devices.forms import DeviceForm
from apps.devices.models import Device
from apps.maps.models import Map


class DevicesListView(ListView):
    template_name = 'devices_list.html'
    context_object_name = 'devices_list'
    paginate_by = 5

    def get_queryset(self):
        return Device.objects.filter(owner=self.request.user)


class DeviceEditView(View):
    def get(self, request, device_id):
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise Http404()
        else:
            if device.owner == request.user:
                device_form = DeviceForm(instance=device)
                return render(request, 'device_form.html', {
                    'device_id': device.id,
                    'device_form': device_form,
                    'change': True,
                })
            else:
                return HttpResponseBadRequest()

    def post(self, request, device_id):
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise Http404()
        else:
            if device.owner == request.user:
                device_form = DeviceForm(request.POST, request.FILES, instance=device)
                if device_form.is_valid():
                    edited_device = device_form.save(commit=False)
                    edited_device.width = int(request.POST['width'])
                    edited_device.save()

                    return HttpResponseRedirect(reverse('devices_list'))
                else:
                    return render(request, 'device_form.html', {
                        'device_id': device.id,
                        'device_form': device_form,
                        'change': True,
                    })
            else:
                return HttpResponseBadRequest()


class DeviceAddView(View):
    def get(self, request):
        if request.user.max_devices_count is None or Device.objects.filter(owner=request.user).count() < request.user.max_devices_count:
            return render(request, 'device_form.html', {
                'device_form': DeviceForm(),
            })
        else:
            return HttpResponseRedirect(reverse('devices_list'))

    def post(self, request):
        if request.user.max_devices_count is None or Device.objects.filter(owner=request.user).count() < request.user.max_devices_count:
            device_form = DeviceForm(request.POST, request.FILES)
            if device_form.is_valid():
                added_device = device_form.save(commit=False)
                added_device.owner = request.user
                added_device.add_position_password = id_generator(5, string.ascii_uppercase)
                added_device.width = int(request.POST['width'])
                added_device.save()

                return HttpResponseRedirect(reverse('devices_list'))
            else:
                return render(request, 'device_form.html', {
                    'device_form': device_form,
                })
        else:
            return HttpResponseRedirect(reverse('devices_list'))


class DeviceDeleteView(DeleteView):
    template_name = 'device_confirm_delete.html'
    model = Device
    success_url = reverse_lazy('devices_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(DeviceDeleteView, self).get_object()
        for user_map in Map.objects.all():
            user_map.locations.remove(obj)
        if not obj.owner == self.request.user:
            return HttpResponseBadRequest()
        return obj


class StatusesUpdateMapView(View):
    def get(self, request, device_id, status_id, update_map_key):
        if update_map_key != settings.TORNADING_KEY:
            raise Http404()
        try:
            _ = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise Http404()

        maps = Map.objects.filter(devices__exact=device_id)
        channel_layer = get_channel_layer()

        json_message = dumps({
            'message_type': 'device_status',
            'status_id': int(status_id),
            'device_id': int(device_id)
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
