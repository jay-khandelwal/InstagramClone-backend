from django.urls import path
from . import views

app_name= 'friend-request'

urlpatterns = [
        path('send/', views.SendRequestApiView.as_view()),
        path('cancel/', views.CancelRequestApiView.as_view()),
  
        path('received/', views.ReceivedRequestApiView.as_view()),
        path('sended/', views.SendedRequestApiView.as_view()),
     
        path('accept/', views.AcceptRequestApiView.as_view()),
        path('decline/', views.DeclineRequestApiView.as_view()),
      
      #  path('unfollow/', views.UnfollowApiView.as_view()),
]