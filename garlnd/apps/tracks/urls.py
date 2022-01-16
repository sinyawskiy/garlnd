from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.tracks.views import TrackView, TracksListView, TrackEditView, TrackAddView, TrackDeleteView


urlpatterns = [
    path('', login_required(TracksListView.as_view()), name='tracks_list'),
    path('add/', login_required(TrackAddView.as_view()), name='add_track'),
    path('<track_id>/', TrackView.as_view(), name='track'),
    path('edit/<track_id>/', login_required(TrackEditView.as_view()), name='edit_track'),
    path('delete/<pk>/', login_required(TrackDeleteView.as_view()), name='delete_track'),
]
