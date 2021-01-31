from django.shortcuts import render, get_object_or_404, get_list_or_404

from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST
)

from .serializers import PrivateChatCreateSerializer, PrivateChatRoomSerializer, ChattedUserSerializer
from .models import ChatRoom, UserMessages, ChatMessages
from .utils import get_random_alphanumeric_string

from accounts.models import User
from accounts.serializers import UserSearchSerializer
from posts.views import CustomListApiView

# Normal django view
def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
# over    

'''
For making the ChatRoom objects b/w two users.
'''
class CreatePrivateChatApiView(generics.CreateAPIView):
    
    queryset = ChatRoom.objects.all()
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def create(self, request, *args, **kwargs):
        try:
            user1 = request.user
            user2 = request.data['userTwo']
            if user1.username == user2:
                return Response(status=HTTP_400_BAD_REQUEST)
                
            obj, created = ChatRoom.objects.get_or_new(user1, user2)
            if obj:
                return Response({'roomId':obj.roomName},status=HTTP_201_CREATED)
            else:
                return Response(status=HTTP_400_BAD_REQUEST)
        except:
            return Response(status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_400_BAD_REQUEST)

'''
To get the previously chatted room.
'''
class RetrieveChattedUserApiView(CustomListApiView):
    
    queryset = ChatRoom.objects.all()
    #serializer_class = PrivateChatRoomSerializer
    serializer_class = ChattedUserSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def get_queryset(self):
        user = self.request.user
        qs = UserMessages.objects.filter(user=user).order_by('-updated')
        newQs = []
        for i in qs:
            newQs.append(i.room)
            
        return newQs


'''
Here we uses User model. 
In this view 1st we check is the requested user in the provided check room . 
If, yes then gives the 2nd user info . 
Else, gives an error .
'''  
class ChatUserInfoApiView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSearchSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]    
        
    def get(self, request, *args, **kwargs):
        roomName = self.kwargs.get('roomname')
        user = request.user
        
        try:
            obj, is_user_room = ChatRoom.objects.user_in_room(user, roomName)
            
            if is_user_room:
                if obj.user1 == user:
                    serializer = self.get_serializer(obj.user2)
                if obj.user2 == user:
                    serializer = self.get_serializer(obj.user1)
                else:
                    Response(status=HTTP_400_BAD_REQUEST)
                    
                return Response(serializer.data)
            
            else:
                return Response(status=HTTP_400_BAD_REQUEST)
        
        except:
            Response(status=HTTP_400_BAD_REQUEST)
        

class DeleteChatApiView(generics.DestroyAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    queryset = ChatMessages.objects.all()
    lookup_field = 'id'
        
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            obj = get_object_or_404(UserMessages, user=request.user, room=instance.room)
            obj.messages.remove(instance)
            obj.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
class DeleteAllChatApiView(generics.GenericAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def delete(self, request, *args, **kwargs):
        try:
            roomid = self.kwargs.get('roomid')
            room = get_object_or_404(ChatRoom, roomName=roomid)
            qs=UserMessages.objects.filter(user=request.user, room=room)
            qs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
    