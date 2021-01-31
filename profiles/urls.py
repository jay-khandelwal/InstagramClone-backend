from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
        path('followers/<slug:username>/', views.FollowerListApiView.as_view()),
        path('followings/<slug:username>/', views.FollowingListApiView.as_view()),
    
        path('unfollow/', views.UnfollowApiView.as_view()),
    ]