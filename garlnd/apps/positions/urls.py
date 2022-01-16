from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.positions.views import PositionsInit, PositionsExportView, PositionsListView, PositionStatusView, PositionsUpdateMapView


urlpatterns = [
    # url(r'^positions/add/(?P<device_id>[1234567890]+)/(?P<longitude>[1234567890]+)/(?P<longitude_type>[nsNS])/(?P<latitude>[1234567890]+)/(?P<latitude_type>[ewEW])/(?P<position_date>[1234567890.]+)/$', AddPositionView.as_view()),
    path('update_on_map/<position_id>/<update_map_key>/', PositionsUpdateMapView.as_view()),
    path('init/<map_id>/', PositionsInit.as_view()),
    path('devices/<device_id>/positions/export/', login_required(PositionsExportView.as_view()), name='export_positions'),
    path('devices/<device_id>/positions/', login_required(PositionsListView.as_view()), name='positions_list'),
    path('<position_id>/status/', login_required(PositionStatusView.as_view()), name='status_position'),
]
