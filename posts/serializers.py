from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from .models import Posts, Likes, Comments
from accounts.models import User
from profiles.models import SavedPosts, Profile
from friendRequest.models import FollowRequest

from accounts.serializers import UserSearchSerializer
from django.contrib.contenttypes.models import ContentType

from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param
from django.urls import reverse


from . import views

class PostsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = [
                'id',
                'user',
                'image',
                #'caption',
                'slug',
            #    'timestamp',
            ]
            
            
            
class FeedsSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    saved = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Posts
        fields = [
                'id',
                'image',
                'caption',
                'timestamp',
                'slug',
                'liked',
                'likes',
                'user',
                'saved',
                'comments',
                'owner',
            ]
            
    def get_user(self, obj):
        request = self.context.get("request")
        user_serializer_data = UserSearchSerializer(obj.user).data
        user_serializer_data['profile_pic']=request.build_absolute_uri(user_serializer_data['profile_pic'])
        return user_serializer_data
    
    def get_liked(self, obj):
        user = self.context.get('request').user
        ct = ContentType.objects.get_for_model(Posts)
        if Likes.objects.filter(object_id=obj.id, content_type=ct, user=user).exists():
            return True
        else:
            return False
  
    def get_likes(self, obj):
        likes = obj.like.count()
        return likes
        
        
    def get_saved(self, obj):
        try:
            my_obj = SavedPosts.objects.get(user=self.context.get("request").user, post=obj)
            if my_obj.post == obj:
                return True
            else:
                return False
        except:
            return False
    
    
    def get_comments(self, obj):
        return Comments.objects.filter(post=obj).count()
        
    def get_owner(self, obj):
        user = self.context.get('request').user
        if obj.user == user:
            return True
        else:
            return False
     
class GetCommentsSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
  #  post_user = serializers.SerializerMethodField()
    class Meta:
        model = Comments
        fields = [
                'id',
                'comment',
                'timestamp',
                'user',
                'liked',
                'likes',
                'can_delete',
            ]
    def get_user(self, obj):
        request = self.context.get("request")
        user_serializer_data = UserSearchSerializer(obj.user).data
        try:
            user_serializer_data['profile_pic']=request.build_absolute_uri(user_serializer_data['profile_pic'])
        except:
            pass
        return user_serializer_data     
        
    def get_liked(self, obj):
        user = self.context.get("request").user
        if user in [i.user for i in obj.likes.all()] :
            return True
        else:
            return False
            
    def get_likes(self, obj):
        likes = obj.likes.count()
        return likes
        
    def get_can_delete(self, obj):
        user = self.context.get("request").user
        if user == obj.user or user == obj.post.user:
            return True
        else:
            return False
        
            
class PostSerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    saved = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
   # comments = GetCommentsSerializers(many=True, read_only=True)
    userType = serializers.SerializerMethodField()

    class Meta:
        model = Posts
        fields = [
                'id',
                'image',
                'caption',
                'comments',
                'timestamp',
                'slug',
                'liked',
                'likes',
                'user',
                'saved',
                'userType',
                'owner',
            ]
            
    def get_user(self, obj):
        request = self.context.get("request")
        user_serializer_data = UserSearchSerializer(obj.user).data
        user_serializer_data['profile_pic']=request.build_absolute_uri(user_serializer_data['profile_pic'])
        return user_serializer_data
  
    def get_liked(self, obj):
        user = self.context.get('request').user
        ct = ContentType.objects.get_for_model(Posts)
        if Likes.objects.filter(object_id=obj.id, content_type=ct, user=user).exists():
            return True
        else:
            return False
            
    def get_likes(self, obj):
        likes = obj.like.count()
        return likes
        
    def get_saved(self, obj):
        try:
            my_obj = SavedPosts.objects.get(user=self.context.get("request").user, post=obj)
            if my_obj.post == obj:
                return True
            else:
                return False
        except:
            return False
  
    def get_userType(self, obj):
        user=self.context['request'].user
        
        if user.username == obj.user.username:
            owner=True
            types = 'owner'
            return types
        else:
            owner=False
            
        profile = get_object_or_404(Profile, user=user)
        follower = profile.followers.filter(username=obj.user.username).exists()
        following = profile.followings.filter(username=obj.user.username).exists()
            
        if following:
            types = 'following'
            return types
            
        if follower:
            types='follower'
            return types
            
        try:
            requested = get_object_or_404(FollowRequest, sender=user, receiver=obj.user)
            if requested:
                types='requested'
                return types
        except:
            requested=False

            
        if (not owner) & (not follower) & (not following) & (not requested):
            types='follow'
            return types
           
    def get_next_link(self, request):
        if not self._paginator.page.has_next():
            return None
        url = request.build_absolute_uri(reverse('posts:post-comments',kwargs={'slug':self.obj.slug}))
        page_number = self._paginator.page.next_page_number()
        return replace_query_param(url, self._paginator.page_query_param, page_number)
    
    def paginator(self, queryset, request):
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        if pagination_class is None:
            return GetCommentsSerializers(queryset, many=True, read_only=True, context={'request': request}).data
        else:
            self._paginator = pagination_class()
            new_qs = self._paginator.paginate_queryset(queryset=queryset, request=request, view=None)
         
            serializer_data = GetCommentsSerializers(new_qs, many=True, context={'request': request}).data
            return {'results':serializer_data, 'next_url':self.get_next_link(request)}
    
    def get_comments(self, obj):
        request=self.context['request']
        self.obj = obj
        comment_qs = Comments.objects.filter(post=obj)
        serializer_data = self.paginator(comment_qs, request)
        return serializer_data

    def get_owner(self, obj):
        user = self.context.get('request').user
        if obj.user == user:
            return True
        else:
            return False