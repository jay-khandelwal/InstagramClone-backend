from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from notifications.models import Notification
from accounts.models import User
from accounts.serializers import InitialDataSerializer
from .exceptions import UnauthorizedExcp

class FollowerListApiView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = InitialDataSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    def get_queryset(self):
        user = self.request.user
        
        wantedUser = get_object_or_404(User, username=self.kwargs.get('username'))
        wantedProfile = get_object_or_404(Profile, user=wantedUser)
        
        inFollowing = wantedProfile.followers.filter(username=user.username).exists()
        
        if (user == wantedUser) or (not wantedUser.privacy) or (wantedUser.privacy & inFollowing) :
            profile = get_object_or_404(Profile, user=wantedUser)
            qs = profile.followers.all()
            return qs
        else:
            raise UnauthorizedExcp()

class FollowingListApiView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = InitialDataSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    def get_queryset(self):
        user = self.request.user
        
        wantedUser = get_object_or_404(User, username=self.kwargs.get('username'))
        wantedProfile = get_object_or_404(Profile, user=wantedUser)
        
        inFollowing = wantedProfile.followers.filter(username=user.username).exists()
        
        if (user == wantedUser) or (not wantedUser.privacy) or (wantedUser.privacy & inFollowing) :
            profile = get_object_or_404(Profile, user=wantedUser)
            qs = profile.followings.all()
            return qs
        else:
            raise UnauthorizedExcp()

       
class UnfollowApiView(generics.GenericAPIView):
  
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def post(self, request, *args, **kwargs):
        user = request.user
        anotherUser = get_object_or_404(User, username=request.data.get('anotherUser'))
        
        profile = get_object_or_404(Profile, user=user)
        anotherProfile = get_object_or_404(Profile, user=anotherUser)
        
        a = profile.followings.filter(username=anotherUser.username).exists
        b = anotherProfile.followers.filter(username=user.username).exists
        
        if a and b :
            profile.followings.remove(anotherUser)
            profile.save()
            
            anotherProfile.followers.remove(user)
            anotherProfile.save()
            
            try:
                del_notification = Notification.objects.get(target=user, from_user=anotherUser, notification_types=Notification.RequestAccepted)
                del_notification.delete()
            except:
                pass
            
            return Response({'message':'user removed'},status=status.HTTP_202_ACCEPTED)
            
        else:
            return Response({'message':'400 bad request'}, status=status.HTTP_400_BAD_REQUEST)