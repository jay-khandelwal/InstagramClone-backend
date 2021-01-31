from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_list_or_404
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from accounts.models import User
from .utils import get_random_alphanumeric_string
from accounts.models import ConnectedUsers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.authtoken.models import Token

import json

user = get_user_model()


class ChatProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name='chat_profile', unique=True)
    friends = models.ManyToManyField(User, blank=True, related_name='chat_friends')
    
    def __str__(self):
        return self.user.username
        
    
class ChatRequest(models.Model):
    sender = models.ForeignKey(user, on_delete=models.CASCADE, related_name='chat_request_sender')
    receiver = models.ForeignKey(user, on_delete=models.CASCADE, related_name='chat_request_receiver')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat request from {self.sender.username} to {self.user2.username}"


class ChatRoomManager(models.Manager):
    def user_in_room(self, user, roomName):
        qlookup = (Q(user1=user) | Q(user2=user)) & Q(roomName=roomName)
        qlookup2 = Q(user1=user) & Q(user2=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        if qs.exists() :
            obj = qs.first()
            return obj, True
        return None, False
        
    def get_or_new(self, user1, user2):
        # user1 is user object and user2 is a username of user 2
        username = user1.username
        if username == user2:
            return None
        qlookup1 = Q(user1__username=username) & Q(user2__username=user2)
        qlookup2 = Q(user1__username=user2) & Q(user2__username=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.last(), False
        else:
            user2 = User.objects.get(username=user2)
            roomName = get_random_alphanumeric_string()
            obj = self.model.objects.create(user1=user1, user2=user2, roomName=roomName)
            return obj, True
        return None, False
        


class ChatRoom(models.Model):
    user1 = models.ForeignKey(user, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(user, on_delete=models.CASCADE, related_name="user2")
    roomName = models.CharField(max_length=32, blank=True, unique=True)
    connected_users = models.ManyToManyField(user, blank=True, related_name="connected_users")
    approved = models.BooleanField(default=False)
    
    objects = ChatRoomManager()
   
    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"
        
    def another_user(self, user):
        if user == self.user1:
            return self.user2
        elif user==self.user2:
            return self.user1
        else:
            return None


class ChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = RoomChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs        
        
        
class ChatMessages(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = ChatMessageManager()
    
    def __str__(self):
        return f"Chat message from  {self.user.username} :-  {self.content}"

    @property
    def get_other_user(self):
        """
        Get the other user in the chat room
        """
        if self.user == self.room.user1:
            return self.room.user2
        else:
            return self.room.user1        
        

class UserMessagesManager(models.Manager):
    def get_or_new(self, user, room):
        qs = self.get_queryset().filter(user=user, room=room)
        if qs.count()>0:
            return qs.last(), False
        else:
            new_obj = self.model.objects.create(user=user, room=room)
            return new_obj, True
            
        return None, False
            

class UserMessages(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    messages = models.ManyToManyField(ChatMessages, blank=True)
    unread_mssg_count = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)
    
    objects = UserMessagesManager()
    
    def __str__(self):
        return self.user.username
       

def personal_user_mssgs_signal(user, obj=None):
    if user in ConnectedUsers.objects.first().users.all():
        ''' for sending notification to direct icon button 
        '''
        channel_layer = get_channel_layer()
        token = Token.objects.get(user=user).key
        user_mssgs_qs = UserMessages.objects.filter(user=user)
        directcount = 0
        for i in user_mssgs_qs:
            if i.unread_mssg_count > 0:
                directcount += 1
        async_to_sync(channel_layer.group_send)(token, {
            'type':'single_notification',
            'ntype':'directcount',
            'count':directcount,
        })
        
        if obj != None:
            try:
                from .serializers import GetChattedUserSerializer
                serialize_data = GetChattedUserSerializer(obj.room, context={'user':user} ).data
                async_to_sync(channel_layer.group_send)(token, {
                    'type':'direct_notification',
                    'ntype':'userdata',
                    'data':serialize_data,
                })            
            except:
                pass


@receiver(post_save, sender=ChatMessages)
def ChatMessages_signal(sender, instance, created, **kwargs):
    if created:
        for user in (instance.room.user1, instance.room.user2):
            obj, created = UserMessages.objects.get_or_new(user=user, room=instance.room)
            obj.messages.add(instance)
            if user in instance.room.connected_users.all():
                obj.save()
            else:
                obj.unread_mssg_count += 1
                obj.save()
                personal_user_mssgs_signal(user, obj)
                    
      
                

        
    
    