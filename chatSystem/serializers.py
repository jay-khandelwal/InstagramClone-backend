from rest_framework import serializers
from django.shortcuts import get_object_or_404

from .models import ChatRoom, ChatMessages, UserMessages
from .utils import get_random_alphanumeric_string
from accounts.models import User
from accounts.serializers import UserSerializer

class PrivateChatCreateSerializer(serializers.ModelSerializer):
    userTwo = serializers.CharField(max_length=200)
    class Meta:
        model = ChatRoom
        fields = [
                'userTwo'
            ]
    
    
class PrivateChatRoomSerializer(serializers.ModelSerializer):
    
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
                'id',
                'user',
                'roomName'
            ]
   
    def get_user(self, obj):
        user = self.context['request'].user
        
        if user == obj.user1:
            anotherUser = obj.user2
        if user == obj.user2:
            anotherUser = obj.user1
            
        username = anotherUser.username
        full_name = anotherUser.full_name
        
        request = self.context.get('request')
        serializer_data = UserSerializer(
            anotherUser
        ).data
        profile_pic = serializer_data.get('profile_pic')
        
        if profile_pic == None:
            return {
            'profile_pic': None,
            'username':username,
            'full_name':full_name,            
            }        

        profile_pic = request.build_absolute_uri(profile_pic)                
        #profile_pic = anotherUser.profile_pic
        
        return {
            'username':username,
            'full_name':full_name,
            'profile_pic':profile_pic
        }
        
# used by the consumer bcz consumer don't have request object
class GetChattedUserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    lastmssg = serializers.SerializerMethodField()
    unread_mssg_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
                'id',
                'roomName',
                'username',
                'profile_pic',
                'lastmssg',
                'unread_mssg_count',
            ]
            
    def get_username(self, obj):
        user = self.context['user']
        return obj.another_user(user).username
      
    def get_profile_pic(self, obj):
        user = self.context['user']
        try:
            profile_pic = obj.another_user(user).profile_pic.url
        except:
            profile_pic=None
        return profile_pic
        
    def get_lastmssg(self, obj):
        user = self.context['user']
        messages = UserMessages.objects.filter(room=obj, user=user)
        if messages.exists():
            lastmssg = messages.first().messages.last()
            content = lastmssg.content
            if len(content) >= 25 :
                content = content[:23] + '...'
            if lastmssg.user==user:
                read=True
            else:
                read=lastmssg.read
            dic = {'content':content, 'timestamp':str(lastmssg.timestamp), 'read':read}
            return dic
        return None        
        
    def get_unread_mssg_count(self, obj):
        user = self.context['user']
        unread_mssg_count = UserMessages.objects.get(room=obj, user=user).unread_mssg_count
        return unread_mssg_count
        
        
        
class ChattedUserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    lastmssg = serializers.SerializerMethodField()
    unread_mssg_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
                'id',
                'roomName',
                'username',
                'profile_pic',
                'lastmssg',
                'unread_mssg_count',
            ]
            
    def get_username(self, obj):
        user = self.context['request'].user
        return obj.another_user(user).username
      
    def get_profile_pic(self, obj):
        user = self.context['request'].user
        try:
            img = self.context['request'].build_absolute_uri(obj.another_user(user).profile_pic.url)
        except:
            img=None
        return img
        
    def get_lastmssg(self, obj):
        user = self.context['request'].user
      #  lastmssg = ChatMessages.objects.filter(room=obj).last()
        messages = UserMessages.objects.filter(room=obj, user=user)
        if messages.exists():
            lastmssg = messages.first().messages.last()
            content = lastmssg.content
            if len(content) >= 25 :
                content = content[:23] + '...'
         
            if lastmssg.user==user:
                read=True
            else:
                read=lastmssg.read
                
            dic = {'content':content, 'timestamp':lastmssg.timestamp, 'read':read}
            return dic
            
        return None
        
    def get_unread_mssg_count(self, obj):
        user = self.context['request'].user
        unread_mssg_count = UserMessages.objects.get(room=obj, user=user).unread_mssg_count
        return unread_mssg_count
    
    
        
class getMessagesSerializers(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    class Meta:
        model = ChatMessages
        fields = [
               'id',
               'sender',
               'content',
               'read',
               'timestamp'
            ]
            
    def get_sender(self, obj):
        return obj.user.username
        
        
        
            