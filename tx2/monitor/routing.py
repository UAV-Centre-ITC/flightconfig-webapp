from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/monitor/(?P<flight_name>\w+)/$', consumers.CameraLogConsumer.as_asgi()),
]
