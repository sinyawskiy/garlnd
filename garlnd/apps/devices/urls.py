from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.devices.views import DevicesListView, DeviceEditView, DeviceAddView, DeviceDeleteView, StatusesUpdateMapView

urlpatterns = [
    path('devices/', login_required(DevicesListView.as_view()), name='devices_list'),
    path('devices/edit/<device_id>/', login_required(DeviceEditView.as_view()), name='edit_device'),
    path('devices/add/', login_required(DeviceAddView.as_view()), name='add_device'),
    path('devices/delete/<pk>/', login_required(DeviceDeleteView.as_view()), name='delete_device'),
    path('update_on_map/<device_id>/<status_id>/<update_map_key>/', StatusesUpdateMapView.as_view()),
]
