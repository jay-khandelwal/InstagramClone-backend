import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from channels.db import database_sync_to_async

from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

from .models import ChatRoom, ChatMessages, UserMessages, personal_user_mssgs_signal
from .exceptions import ClientError
from .serializers import getMessagesSerializers

from django.core.paginator import Paginator

class ChatConsumer(AsyncJsonWebsocketConsumer):
    
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            token_key = parse_qs(self.scope['query_string'].decode('utf8'))['token'][0]
            if (len(self.room_name)==32) and (token_key != None) :
                await self.try_accept_connection(self.room_name, token_key)
            else:
                await self.close(3500)
        except:
            await self.close(3500)
            
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
            
    async def disconnect(self, code):
        await disconnect_user(self.me, self.chatRoom_obj)
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        
    async def try_accept_connection(self,roomName, token_key):
        '''
        Try to get user from the token and query user and roomName in ChatRoom and accept the connection accordingly.
        '''
        try:
            self.me = await get_user_obj(token_key)
            chatRoom_obj, is_user_room = await get_room_or_error(self.me, roomName)
            if chatRoom_obj != None and is_user_room :
                self.chatRoom_obj = chatRoom_obj
                await connect_user_and_mark_mssg_as_read(self.chatRoom_obj, self.me)
                await self.channel_layer.group_add(
                    self.room_name,
                    self.channel_name
                )
                print('accepted connection.')
                await self.accept()
            else:
                await self.close(3500)
        except:
            await self.close(3500)
            
    async def new_message(self, data):
        try:
            if (data['roomName']  == self.room_name) :
                await self.broadcast_message(data['message'], data['sender'])
            else:
                await self.close()
        except:
            await self.close()     
            
    async def broadcast_message(self,mssg, from_user):
        try:
            chat_mssg_obj = await save_mssg_to_db(mssg, self.me, self.chatRoom_obj)
    
            await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": mssg,
                'sender':from_user,
                'timestamp':str(chat_mssg_obj.timestamp),
            }
            )      
        except:
            await self.send_json ({
                'message': 'stuck with a problem. Refresh the page and try again. '
            })
        
    async def chat_message(self, event):
        await self.send_json(
            {
                'command':'new_message',
                'message':{
                "sender": event['sender'],
                "message": event["message"],
                'timestamp':event['timestamp']
                }
            },
        )  
        
    async def leave(self, data):
        if data['username'] == self.me.username:
            chatRoom_obj, is_user_room = await get_room_or_error(self.me, data['roomName'])
            if is_user_room:
             #   await disconnect_user(self.me, self.chatRoom_obj)
                await self.channel_layer.group_discard(
                    data['roomName'],
                    self.channel_name,
                    )
                await self.close(3500)
                
    async def fetch_messages(self, data):
        print(data)
        print(self.me.username)
        try:
            assert isinstance(int(data['pagination']), int)
            if (self.me.username == data['username']) and (self.room_name == data['roomName']):
                page = int(data['pagination'])
                messages = await get_room_chat_messages(self.me, self.chatRoom_obj, page)
                if messages is None:
                    return
                if page == 1:
                    await self.send_json({
                        'command':'messages',
                        'messages':messages,
                    })
                else:
                    await self.send_json({
                        'command':'old_messages',
                        'messages':messages,
                    })
            else:
                print('clise 1')
                await self.close(3500)
        except:
            print('clise 2')
            await self.close(3500)
          
            
    command = {
        'new_message':new_message,
        'leave'      :leave,
        'fetch_messages':fetch_messages,
        'messages_payload': 'messages_payload'
    }
    
    
 
 
@database_sync_to_async    
def get_user_obj(key):
    token_obj = Token.objects.get(key=key)
    return token_obj.user           
            
@database_sync_to_async
def get_room_or_error(user, roomName):
    obj, is_user_room = ChatRoom.objects.user_in_room(user, roomName)
    return obj, is_user_room
    
@database_sync_to_async
def connect_user_and_mark_mssg_as_read(room, user):
    if user in room.connected_users.all():
        pass
    else:
        room.connected_users.add(user)
    
    userMessages_qs = UserMessages.objects.filter(user=user, room=room)
    if userMessages_qs.exists():
        if userMessages_qs.first().unread_mssg_count > 0 :
            if room.user1==user:
                another_user=room.user2
            elif room.user2==user:
                another_user=room.user1
            else:
                return False
            if another_user :
                chatMssg = ChatMessages.objects.filter(user=another_user, room=room, read=False).update(read=True)
                
            user_mssg_obj = userMessages_qs.first()
            user_mssg_obj.unread_mssg_count = 0
            user_mssg_obj.save()
            personal_user_mssgs_signal(user, user_mssg_obj)
            return True
    return True

@database_sync_to_async
def disconnect_user(room,user):
    if user in room.connected_users.all():
        room.connected_users.remove(user)
    else:
        pass
    return True

@database_sync_to_async    
def save_mssg_to_db(mssg, user, room_obj):
    try:
        if (room_obj.user1 == user) or (room_obj.user2==user):
            if room_obj.connected_users.count()==2:
                read=True
            else:
                read=False
            chat_mssg_obj = ChatMessages.objects.create(room=room_obj, user=user, content=mssg, read=read)
          #  add_to_user_messages(chat_mssg_obj)
            return chat_mssg_obj
    except:
        return None
        
def add_to_user_messages(mssg_obj):
    for user in (mssg_obj.room.user1, mssg_obj.room.user2):
        obj, created = UserMessages.objects.get_or_new(user=user, room=mssg_obj.room)
        obj.messages.add(mssg_obj)
        if user == mssg_obj.user :
            obj.unread_mssg_count = 0
        else:
            if mssg_obj.room.connected_users == 2 :
                obj.unread_mssg_count = 0
            else:
                obj.unread_mssg_count += 1
        obj.save()
        
@database_sync_to_async       
def get_room_chat_messages(user, room, page):
   # try:
    qs = UserMessages.objects.filter(user=user, room=room)
    if qs.count() > 0:
        userMessages_obj = qs.first()
        qs = userMessages_obj.messages.all().order_by('-timestamp')
        p = Paginator(qs, 20)
        try:
            paginated_qs = p.page(page).object_list
        except:
            return None
        #serializer the messages quertset
        serialize_data = getMessagesSerializers(paginated_qs, many=True).data
  
        data = {
            'data':serialize_data,
         #   'has_next':p.has_next(),
        }
        return data
        
    else:
        return []
            
  #  except:
     #   return None
        
def get_another_user(room, user):
        if room.user1 == user:
            return room.user2
        if room.user2==user:
            return room.user1
        return None        
        


