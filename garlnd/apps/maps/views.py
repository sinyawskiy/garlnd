from json import dumps
from urllib.parse import quote as urlquote

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View, ListView, DeleteView, FormView
from apps.devices.models import Device
from apps.maps.forms import MapForm, AddDeviceToMapForm
from apps.maps.models import Map



class MapsListView(ListView):
    template_name = 'maps_list.html'
    context_object_name = 'maps_list'
    paginate_by = 5

    def get_queryset(self):
        return Map.objects.filter(owner=self.request.user)


class MapEditView(View):
    def get(self, request, map_id):
        try:
            edit_map = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            raise Http404()
        else:
            if edit_map.owner == request.user:
                map_form = MapForm(instance=edit_map)
                return render(request, 'map_form.html', {
                    'map_form': map_form,
                    'change': True,
                })
            else:
                return HttpResponseBadRequest()

    def post(self, request, map_id):
        try:
            edit_map = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            raise Http404()
        else:
            if edit_map.owner == request.user:
                map_form = MapForm(request.POST, instance=edit_map)
                if map_form.is_valid():
                    edited_map = map_form.save(commit=False)
                    edited_map.longitude = float(request.POST['longitude'])
                    edited_map.latitude = float(request.POST['latitude'])
                    edited_map.zoom = int(request.POST['zoom'])
                    edited_map.save()

                    return HttpResponseRedirect(reverse('maps_list'))
                else:
                    return render(request, 'map_form.html', {
                        'map_form': map_form,
                        'change': True,
                    })
            else:
                return HttpResponseBadRequest()


class MapAddView(View):
    def get(self, request):
        if request.user.max_maps_count is None or Map.objects.filter(owner=request.user).count() < request.user.max_maps_count:
            return render(request, 'map_form.html', {
                'map_form': MapForm(),
            })
        else:
            return HttpResponseRedirect(reverse('maps_list'))

    def post(self, request):
        if request.user.max_maps_count is None or Map.objects.filter(owner=request.user).count() < request.user.max_maps_count:
            map_form = MapForm(request.POST)
            if map_form.is_valid():
                added_map = map_form.save(commit=False)
                added_map.owner = request.user
                added_map.longitude = float(request.POST['longitude'])
                added_map.latitude = float(request.POST['latitude'])
                added_map.zoom = int(request.POST['zoom'])
                added_map.save()

                return HttpResponseRedirect(reverse('maps_list'))
            else:
                return render(request, 'map_form.html', {
                    'map_form': map_form,
                })
        else:
            return HttpResponseRedirect(reverse('maps_list'))


class MapView(View):
    template_name = 'map.html'

    def get(self, request, map_id):
        user = request.user
        try:
            viewed_map = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            raise Http404()
        else:

            if viewed_map.owner == user:
                can_edit_map = True
            else:
                can_edit_map = False

                if 'password' in request.GET:
                    password = request.GET['password']
                    if password == viewed_map.view_password:
                        request.session['auth_map_%s' % map_id] = True

                if not viewed_map.is_opened() and not request.session.get('auth_map_%s' % map_id, False):
                    return HttpResponseRedirect('%s?%s=%s' % (
                        reverse('password_required.views.map_login', kwargs={'map_id': map_id}),
                        REDIRECT_FIELD_NAME,
                        urlquote(request.get_full_path()),
                    ))

            return render(request, self.template_name, {
                'devices': Device.objects.filter(owner=viewed_map.owner),
                'web_socket_port': settings.WEB_SOCKET_PORT,
                'web_socket_browser_host': settings.WEB_SOCKET_BROWSER_HOST,
                'can_edit_map': can_edit_map,
                'object': viewed_map,
                'time_delta_between_tracks': settings.TIME_DELTA_BETWEEN_TRACKS
            })


class MapDeleteView(DeleteView):
    template_name = 'map_confirm_delete.html'
    model = Map
    success_url = reverse_lazy('maps_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(MapDeleteView, self).get_object()
        if not obj.owner == self.request.user:
            return HttpResponseBadRequest()
        return obj


class MapDevicesView(FormView):
    form_class = AddDeviceToMapForm
    template_name = 'map_devices_list.html'
    success_url = None
    paginate_by = 15

    def get_success_url(self):
        return reverse('map_devices_list', args=(self.map_to_adding.id,))

    def get_context_data(self, **kwargs):
        kwargs = super(MapDevicesView, self).get_context_data(**kwargs)
        kwargs.update({
            'map_to_adding': self.map_to_adding,
            'devices_list': self.map_to_adding.devices.all(),
            'with_form': self.map_to_adding.devices.all().count() < Device.objects.filter(owner=self.map_to_adding.owner).count()
        })
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(MapDevicesView, self).get_form_kwargs()
        kwargs.update({'map_to_adding': self.map_to_adding})
        return kwargs

    def get(self, request, map_id, *args, **kwargs):
        try:
            map_to_adding = Map.objects.get(id=map_id, owner=request.user)
        except Map.DoesNotExist:
            raise Http404()
        else:
            form_class = self.get_form_class()
            self.map_to_adding = map_to_adding
            form = self.get_form(form_class)
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, map_id, *args, **kwargs):
        try:
            map_to_adding = Map.objects.get(id=map_id, owner=request.user)
        except Map.DoesNotExist:
            raise Http404()
        else:
            form_class = self.get_form_class()
            self.map_to_adding = map_to_adding
            form = self.get_form(form_class)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def form_valid(self, form):
        device = form.cleaned_data.get('device')
        if device:
            if not self.map_to_adding.devices.filter(id=device.id).count():
                self.map_to_adding.devices.add(device)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponseBadRequest()


class MapDeviceDeleteView(View):
    def get(self, request, map_id, device_id):
        try:
            map_to_deleting = Map.objects.get(id=map_id, owner=request.user)
        except Map.DoesNotExist:
            raise Http404()
        else:
            try:
                device = Device.objects.get(id=device_id, owner=request.user)
            except Device.DoesNotExist:
                raise Http404()
            else:
                map_to_deleting.devices.remove(device)
                return HttpResponseRedirect(reverse('map_devices_list', args=(map_id,)))


class MapLocationsJsonView(View):
    def get(self, request, map_id):
        user = request.user
        try:
            locations_map = Map.objects.get(id=map_id)
        except Map.DoesNotExist:
            raise Http404()
        else:
            password = ''
            if 'password' in request.GET:
                password = request.GET['password']

            if locations_map.view_password == password or locations_map.owner == user:
                result = []
                return HttpResponse(dumps(result), content_type='application/json')
            else:
                raise Http404()


#TODO: сделать табы для списка и формы
#TODO: pagination to maps devices lists