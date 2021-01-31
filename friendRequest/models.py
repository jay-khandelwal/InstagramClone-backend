from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token
from accounts.models import ConnectedUsers
#ram9601ram
User = settings.AUTH_USER_MODEL

class FollowRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.sender.username
 

def base_signal(instance):
    if instance.receiver in ConnectedUsers.objects.first().users.all():
        channel_layer = get_channel_layer()
        token = Token.objects.get(user=instance.receiver).key
        reqrec = FollowRequest.objects.filter(receiver=instance.receiver).count()
        async_to_sync(channel_layer.group_send)(token, {
            'type':'single_notification',
            'ntype':'reqrec',
            'count':reqrec,
        })
    if instance.sender in ConnectedUsers.objects.first().users.all():
        channel_layer = get_channel_layer()
        token = Token.objects.get(user=instance.sender).key
        reqsend = FollowRequest.objects.filter(sender=instance.sender).count()
        
        async_to_sync(channel_layer.group_send)(token, {
            'type':'single_notification',
            'ntype':'reqsend',
            'count':reqsend,
        }) 
    
@receiver(post_save, sender=FollowRequest)
def follow_request_create(sender, instance, created, **kwargs):
    if created:
        base_signal(instance)
        
        
@receiver(post_delete, sender=FollowRequest)
def follow_request_delete(sender, instance, **kwargs):
    base_signal(instance)
            
