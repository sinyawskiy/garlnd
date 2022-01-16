from django.urls import path

from custom_channels.consumers import MapConsumer

websocket_urlpatterns = [
    path('ws/map/', MapConsumer.as_asgi()),
]
