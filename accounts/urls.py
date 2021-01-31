from django.urls import path

from .views import InitialDataApiView, ProfileRetriveUpdateApiView, ProfileDetailView, SearchUserListApiView, RetrieveUpdatePrivacyApiView, GetChattedUserApiView, GetUserDetailApiView, ReverifyEmailApiView, GetSuperuserApiView


app_name = 'accounts'

urlpatterns = [
        path('initial-data/', InitialDataApiView.as_view()),
        path('profile/edit/', ProfileRetriveUpdateApiView.as_view()),
        path('search/', SearchUserListApiView.as_view()),
        path('get-set-privacy/', RetrieveUpdatePrivacyApiView.as_view()),
        path('profile/<slug:username>/', ProfileDetailView.as_view()),
        path('verify-email/', ReverifyEmailApiView.as_view()),
       
        path('user-detail/', GetUserDetailApiView.as_view()),
        path('get-superuser/', GetSuperuserApiView.as_view()),
        
        # for checking purposes
        path('chat/user/',GetChattedUserApiView.as_view() ),
]