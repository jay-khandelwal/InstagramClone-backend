from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions

from .models import FollowRequest
from .serializers import ReceivedRequestSerializer, SendedRequestSerializer 
from accounts.models import User
from profiles.models import Profile
from notifications.models import Notification

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class SendRequestApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    def create(self, request, *args, **kwargs):
        sender = request.user
        receiver = request.data.get('receiver')
        receiver = get_object_or_404(User, username=receiver)
        
        sender_profile = get_object_or_404(Profile, user=sender)
        receiver_profile = get_object_or_404(Profile, user=receiver)
        
        a = sender_profile.followings.filter(username=receiver.username).exists()
        b = receiver_profile.followers.filter(username=sender.username).exists()
        
        if not (a and b):
            req, created = FollowRequest.objects.get_or_create(sender=sender, receiver=receiver)
            if created:
                return Response({'frequest':'request sended'}, status=status.HTTP_200_OK)
            
            if req:
                return Response({'frequest':'request already exists'}, status=status.HTTP_403_FORBIDDEN)
           
        else:
            return Response(status=status.HTTP_409_CONFLICT)

            
class CancelRequestApiView(generics.GenericAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def post(self, request, *args, **kwargs):
        sender = request.user
        receiver = request.data.get('receiver')
        receiver = get_object_or_404(User, username=receiver)
        
        obj = get_object_or_404(FollowRequest, sender=sender, receiver=receiver)
        '''
        try:
            notify = Notification.objects.get( target=receiver, from_user=sender, notification_types=Notification.RequestReceived)
            notify.delete()
        except:
            pass
        '''
        
        obj.delete()
        return Response({'frequest':'canceled'}, status=status.HTTP_204_NO_CONTENT)


class DeclineRequestApiView(generics.GenericAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def post(self, request, *args, **kwargs):
        receiver = request.user
        sender = request.data.get('sender')
        sender = get_object_or_404(User, username=sender)
        
        obj = get_object_or_404(FollowRequest, sender=sender, receiver=receiver)
        
        obj.delete()
        return Response({'frequest':'request decline successfully'}, status=status.HTTP_204_NO_CONTENT)


class ReceivedRequestApiView(generics.ListAPIView):
    model = FollowRequest
    serializer_class = ReceivedRequestSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    queryset = FollowRequest.objects.all()
    
    def get_queryset(self):
        receiver = self.request.user
        qs = FollowRequest.objects.filter(receiver=receiver)
       # qs = get_list_or_404(FollowRequest, receiver=receiver)
        
        return qs
        
        
class SendedRequestApiView(generics.ListAPIView):
    model = FollowRequest
    serializer_class = SendedRequestSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    queryset = FollowRequest.objects.all()
    
    def get_queryset(self):
        sender = self.request.user
        qs = FollowRequest.objects.filter(sender=sender)
      #  qs = get_list_or_404(FollowRequest, sender=sender)
        
        return qs
    

class AcceptRequestApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def create(self, request, *args, **kwargs):
        user = request.user
        request_sender = get_object_or_404(User, username=request.data.get('request_sender'))
        
        
        obj = get_object_or_404(FollowRequest, sender=request_sender, receiver=user)
        if obj:
            user_profile = get_object_or_404(Profile, user=user)
            sender_profile = get_object_or_404(Profile, user=request_sender)
            
            filt1 = user_profile.followers.filter(username=request_sender.username).exists()
        
            filt2 = sender_profile.followings.filter(username=user.username).exists()
            
            if not ( filt1 & filt2 ) :
                
                obj.delete()
            
                user_profile.followers.add(request_sender)
                sender_profile.followings.add(user)
               
                user_profile.save()
                sender_profile.save()
                
                create_notification = Notification.objects.create(target=request_sender, from_user=user, notification_types=Notification.RequestAccepted,  content_object=user_profile)
                
                return Response(status=status.HTTP_202_ACCEPTED)
                
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        
