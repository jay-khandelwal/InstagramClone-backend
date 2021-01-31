from django.shortcuts import render
from rest_framework import generics 
from rest_framework import permissions

from .serializers import NotificationsSerializers
from .models import Notification
from .signals import updateNotificationSignal
from posts.views import CustomListApiView

class GetNotificationsApiView(generics.ListAPIView):
    serializer_class = NotificationsSerializers  
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def get_queryset(self):
        user = self.request.user
        notify = Notification.objects.filter(target=user).order_by('-timestamp')
    
        Notification.objects.filter(target=user, read=False).update(read=True)
        updateNotificationSignal(user)        
      
        return notify
            
        