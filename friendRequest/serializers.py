from rest_framework import serializers

from .models import FollowRequest
from accounts.serializers import UserSerializer

class ReceivedRequestSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username')
    sender_name = serializers.CharField(source='sender.full_name')
    sender_profile_pic = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = FollowRequest
        fields = [
                'sender_username',
                'sender_name',
                'sender_profile_pic',
            ]
            
    def get_image_url(self, obj):
        request = self.context.get("request")
        serializer_data = UserSerializer(
            obj.sender
        ).data
        profile_pic = serializer_data.get('profile_pic')
        if profile_pic == None:
            return None
        profile_pic = request.build_absolute_uri(profile_pic)
        return profile_pic
        
        
class SendedRequestSerializer(serializers.ModelSerializer):
    receiver_username = serializers.CharField(source='receiver.username')
    receiver_name = serializers.CharField(source='receiver.full_name')
    reveiver_profile_pic = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = FollowRequest
        fields = [
                'receiver_username',
                'receiver_name',
                'reveiver_profile_pic',
            ]
            
    def get_image_url(self, obj):
        request = self.context.get("request")
        serializer_data = UserSerializer(
            obj.receiver
        ).data
        profile_pic = serializer_data.get('profile_pic')
        if profile_pic == None:
            return None
        profile_pic = request.build_absolute_uri(profile_pic)
        return profile_pic
