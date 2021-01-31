from django.urls import re_path

from . import consumers
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    re_path('notification/', NotificationConsumer),
]