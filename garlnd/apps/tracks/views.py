from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render

from django.utils.http import urlencode
from django.views.generic import View, ListView, DeleteView
from .forms import TrackForm
from .models import Track


class TrackView(View):
    template_name = 'track.html'

    def get(self, request, track_id):
        user = request.user
        try:
            viewed_track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise Http404()
        else:
            if viewed_track.owner == user:
                can_edit_track = True
            else:
                can_edit_track = False

                if 'password' in request.GET:
                    password = request.GET['password']
                    if password == viewed_track.view_password:
                        request.session['auth_track_%s' % track_id] = True

                if not viewed_track.is_opened() and not request.session.get('auth_track_%s' % track_id, False):
                    return HttpResponseRedirect('%s?%s=%s' % (
                        reverse('password_required.views.track_login', kwargs={'track_id': track_id}),
                        REDIRECT_FIELD_NAME,
                        urlencode(request.get_full_path()),
                    ))

            return render(request, self.template_name, {
                'object': viewed_track,
                'can_edit_track': can_edit_track,
                'initialCenter': {
                    'longitude': settings.DEFAULT_MAP_LONGITUDE,
                    'latitude': settings.DEFAULT_MAP_LATITUDE,
                    'zoom': settings.DEFAULT_MAP_ZOOM
                },
                'time_delta_between_tracks': settings.TIME_DELTA_BETWEEN_TRACKS
            })


class TracksListView(ListView):
    template_name = 'tracks_list.html'
    context_object_name = 'tracks_list'
    paginate_by = 25

    def get_queryset(self):
        return Track.objects.filter(owner=self.request.user)


class TrackEditView(View):
    def get(self, request, track_id):
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise Http404()
        else:
            if track.owner == request.user:
                track_form = TrackForm(instance=track)
                return render(request, 'track_form.html', {
                    'track_id': track.id,
                    'track_form': track_form,
                    'change': True,
                })
            else:
                return HttpResponseBadRequest()

    def post(self, request, track_id):
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            raise Http404()
        else:
            if track.owner == request.user:
                track_form = TrackForm(request.POST, request.FILES, instance=track)
                if track_form.is_valid():
                    track_form.save()

                    return HttpResponseRedirect(reverse('tracks_list'))
                else:
                    return render(request, 'track_form.html', {
                        'track_id': track.id,
                        'track_form': track_form,
                        'change': True,
                    })
            else:
                return HttpResponseBadRequest()


class TrackAddView(View):
    def get(self, request):
        if request.user.max_tracks_count is None or Track.objects.filter(owner=request.user).count() < request.user.max_tracks_count:
            return render(request, 'track_form.html', {
                'track_form': TrackForm(),
            })
        else:
            return HttpResponseRedirect(reverse('tracks_list'))

    def post(self, request):
        if request.user.max_tracks_count is None or Track.objects.filter(owner=request.user).count() < request.user.max_tracks_count:
            track_form = TrackForm(request.POST)
            if track_form.is_valid():
                added_track = track_form.save(commit=False)
                added_track.owner = request.user
                added_track.save()

                return HttpResponseRedirect(reverse('tracks_list'))
            else:
                return render(request, 'track_form.html', {
                    'track_form': track_form,
                })
        else:
            return HttpResponseRedirect(reverse('tracks_list'))


class TrackDeleteView(DeleteView):
    template_name = 'track_confirm_delete.html'
    model = Track
    success_url = reverse_lazy('tracks_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(TrackDeleteView, self).get_object()
        if not obj.owner == self.request.user:
            return HttpResponseBadRequest()
        return obj
