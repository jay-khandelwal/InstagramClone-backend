from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User
from .serializers import InitialDataSerializer, UserSerializer, ProfileSerializer, UserSearchSerializer, GetPrivacySerializer, ReverifyEmailSerializer
from profiles.models import Profile
from allauth.account.models import EmailAddress
from profiles.exceptions import NoProfileFound

from rest_auth.registration.app_settings import RegisterSerializer, register_permission_classes
from rest_auth.models import TokenModel
from allauth.account import app_settings as allauth_settings
from django.conf import settings
from rest_auth.app_settings import (TokenSerializer,
                                    JWTSerializer,
                                    create_token)
from allauth.account.utils import complete_signup 
from rest_auth.utils import jwt_encode
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from django.utils.translation import ugettext_lazy as _

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2')
)


def homePageView(request):
    return render(request, 'build/index.html')


class ReverifyEmailApiView(generics.GenericAPIView):
    serializer_class=ReverifyEmailSerializer
    permission_classes=[
            permissions.AllowAny,
        ]
        
    def send_email(self):
        if self.serializer.validated_data['is_verified']:
            return Response({"detail": _("Your email is already verified.")},
                            status=status.HTTP_200_OK)
        elif self.serializer.validated_data['is_verified'] == False:
            try:
                self.user = self.serializer.validated_data['user']
                email_address = EmailAddress.objects.get(
                    user=self.user,
                    email=self.user.email,
                )
                email_address.send_confirmation(self.request)
                return Response({'detail':_("Verification email has been sent.")}, status=status.HTTP_200_OK)
            except EmailAddress.DoesNotExist:
                return Response({"detail": _("Something wents wrong.")},
                            status=status.HTTP_403_FORBIDDEN)
        else:
           return Response({"detail": _("Something wents wrong.")},
                            status=status.HTTP_403_FORBIDDEN)
            
      
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data, context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        return self.send_email()
    

class InitialDataApiView(generics.RetrieveAPIView):
    queryset=User.objects.all()
    serializer_class=InitialDataSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def get_object(self):
        obj = get_object_or_404(User, username=self.request.user)
        return obj


# this view is for 'edit profile' page of an Instagram app.
class ProfileRetriveUpdateApiView(generics.RetrieveUpdateAPIView):
    
    queryset = User.objects.all()
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    serializer_class = UserSerializer
    
    def get_object(self):
        user = self.request.user
       # user = self.kwargs.get('username')
        obj = get_object_or_404(User,username=user)
        return obj


# for profile page
class ProfileDetailView(generics.RetrieveAPIView):
    
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
     
    def get_object(self):
        wantedUsername = self.kwargs.get('username')
        try : 
            obj = User.objects.get(username=wantedUsername)
            return obj
        except:
            raise NoProfileFound()
 

# only for explore page and navbar
class SearchUserListApiView(generics.ListAPIView):
    queryset=User.objects.all()
    serializer_class=UserSearchSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    filter_backends = [SearchFilter, OrderingFilter,]
    search_fields = ['username', 'full_name']
    
    def get_queryset(self):
        print(self.request.user)
        qs = User.objects.all().exclude(username=self.request.user.username)
     #   print(qs)
        return qs
    

# only for privacy page     
class RetrieveUpdatePrivacyApiView(generics.RetrieveUpdateAPIView):
    queryset=User.objects.all()
    serializer_class=GetPrivacySerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def get_object(self):
        return self.request.user

# for testing purpose        
class GetChattedUserApiView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [
            permissions.IsAuthenticated
        ]
    queryset = User.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        profile = get_object_or_404(Profile, user=user)
        followers = list(profile.followers.all())
        followings = list(profile.followings.all())
        # converting into set, to remive duplicate users
        qs = set((followers + followings))
        return list(qs)
    

# used in create/detail page from getting user profile pic    
class GetUserDetailApiView(generics.RetrieveAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [
            permissions.IsAuthenticated
        ]
    queryset = User.objects.all()
    
    def get_object(self):
        return self.request.user
        

class GetSuperuserApiView(generics.ListAPIView):
    permission_classes = [
            permissions.IsAuthenticated
        ]
    serializer_class = InitialDataSerializer
    
    def get_queryset(self):
        qs = User.objects.filter(is_superuser=True)
        return qs
            