from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, get_list_or_404

from .models import User
from profiles.models import Profile
from friendRequest.models import FollowRequest
from rest_auth.serializers import PasswordResetSerializer
from allauth.account.models import EmailAddress

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions

UserModel = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = ['Your password or username/email is incorrect. Please try again.', 'wrong_data']
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    dic = ['E-mail is not verified.', 'email']
                    raise serializers.ValidationError(dic)

        attrs['user'] = user
        return attrs         
        
class CustomPasswordResetSerializer(PasswordResetSerializer):
    def validate_email(self, value):
        user_obj = User.objects.filter(email=value)
        email_obj = EmailAddress.objects.filter(email=value)
        if not user_obj.exists() and not email_obj.exists():
            raise serializers.ValidationError('No user found with this email address.')
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value
        
class ReverifyEmailSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})
    
    
    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)
        return user
  
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None
        is_verified = False
        
        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Your password or username/email is incorrect. Please try again.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if email_address.verified:
                    is_verified = True

        attrs['user'] = user
        attrs['is_verified'] = is_verified
        return attrs                 

# serializers for registration 
class CustomRegisterSerializer(RegisterSerializer):
    full_name = serializers.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'full_name')
        
    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'full_name':self.validated_data.get('full_name',''),
        } 
        
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.full_name = self.cleaned_data.get('full_name')
        user.save()
        adapter.save_user(request, user, self)
        return user   
        
# serializer for giving authentication token and profile_pic and user        
class TokenSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'username')

    def get_username(self, obj):
        return obj.user.username
 
 
class InitialDataSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields = [
                'id',
                'username',
                'full_name',
                'profile_pic',
                'userType',
            ]
            
    def get_userType(self, obj):
        user=self.context['request'].user
        
        if user.username == obj.username:
            owner=True
            types = 'owner'
            return types
        else:
            owner=False
            
        try:
            requested = get_object_or_404(FollowRequest, sender=user, receiver=obj)
            if requested:
                types='requested'
                return types
        except:
            requested=False  
            
            
        profile = get_object_or_404(Profile, user=user)
        follower = profile.followers.filter(username=obj.username).exists()
        following = profile.followings.filter(username=obj.username).exists()
            
        if following:
            types = 'following'
            return types
            
        if follower:
            types='follower'
            return types
            
            
        if (not owner) & (not follower) & (not following) & (not requested):
            types='follow'
            return types            
 
# serializer mainly used by profile edit page
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
       model = User
       fields = [
            'pk',
            'username',
            'full_name',
            'email',
            'profile_pic',
            'bio',
            'website',
            'phone_no',
            'gender'
           ]        

# serializer for main profile page
class ProfileSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()
    userType = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    class Meta:
        model  = User
        fields = [
                'userType',                
                'username',
                'full_name',
                'bio',
                'friends',
                'privacy',
                'profile_pic',
                'posts',
            ]
            
    def get_friends(self, obj):
        qs = Profile.objects.get(user=obj)
        followers = qs.followers.count()
        followings = qs.followings.count()
        posts = obj.posts_set.count()
        
        return {
            'followers' : followers,
            'followings': followings,
            'posts':posts
        }
        
    def get_userType(self, obj):
        user=self.context['request'].user
        
        if user.username == obj.username:
            owner=True
            types = 'owner'
            return types
        else:
            owner=False
            
        profile = get_object_or_404(Profile, user=user)
        follower = profile.followers.filter(username=obj.username).exists()
        following = profile.followings.filter(username=obj.username).exists()
            
        if following:
            types = 'following'
            return types
            
        try:
            requested = get_object_or_404(FollowRequest, sender=user, receiver=obj)
            if requested:
                types='requested'
                return types
        except:
            requested=False            
            
        if follower:
            types='follower'
            return types

            
        if (not owner) & (not follower) & (not following) & (not requested):
            types='follow'
            return types
        
    def get_posts(self, obj):
        posts = obj.posts_set.count()
        if posts== 0 :
            return False
        else:
            return True
        

# for search page  
class UserSearchSerializer(serializers.ModelSerializer):
  
    class Meta:
        model=User
        fields=[
                'id',
                'username',
                'full_name',
                'profile_pic',
            ]
   
  

# only for privacy page  
class GetPrivacySerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
                'privacy'
            ]
  