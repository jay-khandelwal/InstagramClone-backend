from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
  
    path('room/', views.CreatePrivateChatApiView.as_view(), name='private-room'),
    path('delete/<id>/', views.DeleteChatApiView.as_view()),
    path('chatted/user/', views.RetrieveChattedUserApiView.as_view(), name ='chatted-user'),
    path('edit/<slug:roomid>/', views.DeleteAllChatApiView.as_view()),
    path('user-info/<slug:roomname>/', views.ChatUserInfoApiView.as_view()),
    
    path('<str:room_name>/', views.room, name='room'),
]