import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async

from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs
from django.http import HttpRequest

from accounts.models import ConnectedUsers
from notifications.models import Notification
from friendRequest.models import FollowRequest
from chatSystem.models import UserMessages
from chatSystem.serializers import PrivateChatRoomSerializer, GetChattedUserSerializer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        try:
            self.token_key = parse_qs(self.scope['query_string'].decode('utf8'))['token'][0]
            self.me = await get_user_obj(self.token_key)
            dataa = dict(self.scope['headers'])
            self.host_url = dataa[bytes('origin', 'utf-8')].decode('utf-8')
            await self.channel_layer.group_add(
                    self.token_key,
                    self.channel_name
                )
            await connect_user(self.me)
            await self.accept()
            
        except:
            self.close()
         
    async def disconnect(self, code):
        try:
            await disconnect_user(self.me)
        except:
            pass
    
    async def receive_json(self, content):
        print(content)
        command = content.get('command', None)
        try:
            await self.command[command](self,content)
        except:
            await self.send_json({
                'message':'Something went wrong. Try again or refresh the page.',
                'from':self.me.username,
            })
        
    async def single_notification(self, event):
        print('single_notification fimc')
        await self.send_json(
            {
                'command':event['ntype'],
                'count':event['count'],
            }
        )
        
    async def direct_notification(self, event):
        print('direct_notification func statrt3d')
        await self.send_json(
            {
                'command':event['ntype'],
                'userdata':event['data'],
            }
        )
        
    async def initial_notification(self, data):
        try:
            if self.token_key == data['token']:
                notifications = await get_initial_notifications(self.me)
                await self.send_json({
                    'command':'initial_notification',
                    'notifications':notifications,
                })
            else:
                await self.close()
        except:
            await self.close()
            
    
    command = {
        'initial_notification':initial_notification,
    }
          
                  
    
@database_sync_to_async    
def get_user_obj(key):
   # try:
    token_obj = Token.objects.get(key=key)
    return token_obj.user  
      #  except:
         #   return None

@database_sync_to_async
def connect_user(user):
    if user not in ConnectedUsers.objects.first().users.all():
        ConnectedUsers.objects.first().users.add(user)
   
@database_sync_to_async
def disconnect_user(user):
    obj = ConnectedUsers.objects.first()
    if user in obj.users.all():
           obj.users.remove(user)


@database_sync_to_async
def get_initial_notifications(user):
    maincount = Notification.objects.filter(target=user, read=False).count()
    reqrec = FollowRequest.objects.filter(receiver=user).count()
    reqsend = FollowRequest.objects.filter(sender=user).count()
    
    user_mssgs_qs = UserMessages.objects.filter(user=user)
    directcount = 0
    for i in user_mssgs_qs:
        if i.unread_mssg_count > 0:
            directcount += 1

    return {
        'maincount':maincount,
        'reqrec':reqrec,
        'reqsend':reqsend,
        'directcount':directcount,
    }        
            
        
