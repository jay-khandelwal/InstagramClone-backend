from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from friendRequest.models import FollowRequest
from accounts.models import ConnectedUsers

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token

User = settings.AUTH_USER_MODEL

class Notification(models.Model):
    PostLike = 'PostLike'
    PostComment = 'PostComment'
    CommentLike = 'CommentLike'
    RequestReceived = 'RequestReceived'
    RequestAccepted = 'RequestAccepted'
    
    Notification_Types = (
        (PostLike, 'PostLike'),
        (PostComment, 'PostComment'),
        (CommentLike, 'CommentLike'),
        (RequestReceived, 'RequestReceived'),
        (RequestAccepted, 'RequestAccepted'),
    )
    
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    notification_types = models.CharField(max_length=500, blank=True, null=True, choices=Notification_Types)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    
    def __str__(self):
        return self.target.username
        
'''      
@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        if instance.target in ConnectedUsers.objects.first().users.all():
            channel_layer = get_channel_layer()
            token = Token.objects.get(user=instance.target).key
            async_to_sync(channel_layer.group_send)(token, {
                'type':'chat_message',
                'ntype':instance.notification_types,
                'from_user':instance.from_user.username,
                'profile_pic':instance.from_user.profile_pic.url,
                'read':instance.read,
                'timestamp':str(instance.timestamp),
            })
'''
            
            
@receiver(post_save, sender=FollowRequest)
def create_notification(sender, instance, created, **kwargs):
    
    if created:
        Notification.objects.create(target=instance.receiver, from_user=instance.sender, notification_types=Notification.RequestReceived, content_object=instance)
        
        
@receiver(post_delete, sender=FollowRequest)
def delete_notification(sender, instance, **kwargs):
    try:
        obj = Notification.objects.get(target=instance.receiver, from_user=instance.sender, notification_types=Notification.RequestReceived)
        obj.delete()
    except:
        pass    
    

@receiver(post_save, sender=Notification)
def add_unread_notification_count(sender, instance, created, **kwargs):
    if created:
        if instance.target in ConnectedUsers.objects.first().users.all():
            channel_layer = get_channel_layer()
            token = Token.objects.get(user=instance.target).key
         
            maincount = Notification.objects.filter(target=instance.target, read=False).count()
            async_to_sync(channel_layer.group_send)(token, {
                'type':'single_notification',
                'ntype':'maincount',
                'count':maincount,
            })
            
@receiver(post_delete, sender=Notification)
def sub_unread_notification_count(sender, instance, **kwargs):
    if instance.target in ConnectedUsers.objects.first().users.all():
        channel_layer = get_channel_layer()
        token = Token.objects.get(user=instance.target).key
     
        maincount = Notification.objects.filter(target=instance.target, read=False).count()
        
        async_to_sync(channel_layer.group_send)(token, {
            'type':'single_notification',
            'ntype':'maincount',
            'count':maincount,
        })
    