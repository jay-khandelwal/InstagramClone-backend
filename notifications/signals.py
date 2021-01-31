from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token

def updateNotificationSignal(user):
    channel_layer = get_channel_layer()
    token = Token.objects.get(user=user).key
    async_to_sync(channel_layer.group_send)(token, {
            'type':'single_notification',
            'ntype':'maincount',
            'count':0,
        })
    
    

