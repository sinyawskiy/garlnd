from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.maps.views import MapView, MapsListView, MapEditView, MapAddView, MapDeleteView, MapDevicesView, MapDeviceDeleteView

urlpatterns = [
    path('', login_required(MapsListView.as_view()), name='maps_list'),
    path('add/', login_required(MapAddView.as_view()), name='map_add'),
    path('edit/<map_id>/', login_required(MapEditView.as_view()), name='map_edit'),
    path('delete/<pk>/', login_required(MapDeleteView.as_view()), name='map_delete'),
    path('<map_id>/', MapView.as_view(), name='map'),
    path('<map_id>/devices/', login_required(MapDevicesView.as_view()), name='map_devices_list'),
    path('<map_id>/devices/delete/<device_id>/', login_required(MapDeviceDeleteView.as_view()), name='map_device_delete'),
]
