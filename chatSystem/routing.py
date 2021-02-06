from django.urls import re_path

from . import consumers
from notifications.consumers import NotificationConsumer
#as_asgi()
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path('ws/notification/', NotificationConsumer.as_asgi()),
]