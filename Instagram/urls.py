from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import homePageView

urlpatterns = [
    path('', homePageView),
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('allauth/', include('allauth.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('frequest/', include('friendRequest.urls', namespace='friend-request')),
    path('profile/', include('profiles.urls', namespace='profile')),
    
    path('chat/', include('chatSystem.urls', namespace='chat')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	
	urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)