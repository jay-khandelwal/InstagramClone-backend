from django.shortcuts import render, get_list_or_404, get_object_or_404
from rest_framework import generics 
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .serializers import PostsSerializers, FeedsSerializers, GetCommentsSerializers, PostSerializers
from .models import Posts, Comments, Likes
from .permissions import PostSeeingPermission
from .utils import get_random_slug
from profiles.models import Profile, SavedPosts
from accounts.models import User
from accounts.serializers import InitialDataSerializer, UserSearchSerializer
from django.contrib.contenttypes.models import ContentType
from rest_framework import pagination
from django.db.models.query import QuerySet

from .utils import Util

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# not use directly by url, but use by views
class CustomListApiView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if ( (isinstance(queryset, QuerySet) and queryset.exists()) or (isinstance(queryset, list) and len(queryset) > 0) ):
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
    
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
           
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class PostsListApiView(generics.ListAPIView):
    serializer_class = PostsSerializers  
    permission_classes=[
            permissions.IsAuthenticated,
            PostSeeingPermission
        ]
    
    def get_queryset(self):
        user = self.kwargs.get('username')
        post = Posts.objects.filter(user__username=user).order_by('-timestamp')
        return post
   
class PostsFeedsApiView(generics.ListAPIView):
    serializer_class = FeedsSerializers  
    permission_classes=[
            permissions.IsAuthenticated,
            PostSeeingPermission
        ]
    
    def get_queryset(self):
        user = self.kwargs.get('username')
        post = Posts.objects.filter(user__username=user).order_by('-timestamp')
        return post
        
class SavedPostsListApiView(generics.ListAPIView):
    serializer_class = PostsSerializers  
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def get_queryset(self):
        qs = SavedPosts.objects.filter(user=self.request.user)
      #  qs = get_list_or_404(SavedPosts, user=self.request.user)
        newQs = []
        for i in qs:
            newQs.append(i.post)
        return newQs
        
class CreateSavedPostApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def create(self, request, *args, **kwargs):
        try:
            slug = request.data['slug']
            if request.data['saved']==False :
                post = get_object_or_404(Posts, slug=slug)
                obj = SavedPosts.objects.create(post=post, user=request.user)
                return Response(status=status.HTTP_201_CREATED)
            
            if request.data['saved']==True :
                post = get_object_or_404(Posts, slug=slug)
                obj = get_object_or_404(SavedPosts, user=request.user, post=post)
                if obj:
                    obj.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                    
                
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class HomePagePostsApiView(CustomListApiView):
    queryset = Posts.objects.all()
    serializer_class = FeedsSerializers  
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def get_queryset(self):
        user = self.request.user
        profile = get_object_or_404(Profile, user=user)
        user_qs = User.objects.filter(username=user.username)
        followings_qs = profile.followings.all()
        # appending user_qs and followings_qs
        filter_qs = followings_qs.union(user_qs)
        filter_qs = list(filter_qs)
        obj = Posts.objects.filter(user__in=filter_qs).order_by('-timestamp')
        mytoken = 10
        base64e = urlsafe_base64_encode(force_bytes(mytoken))
        return obj
    

        
        
class PostDetailMobileApiView(generics.RetrieveAPIView):
    queryset = Posts.objects.all()
    serializer_class = FeedsSerializers
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    lookup_field = 'slug'

# only diffrence with above view is comments field    
class PostDetailDesktopApiView(generics.RetrieveAPIView):
    queryset = Posts.objects.all()
    serializer_class = PostSerializers
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    lookup_field = 'slug'
    

class CreatePostApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            caption = request.data['caption']
            image = request.data['post']    
            slug = get_random_slug()
            new_obj = Posts.objects.create(user=user, image=image, caption=caption, slug=slug)
            return Response(status=status.HTTP_201_CREATED)
       
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
            
class UpdatePostApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def patch(self, request, *args, **kwargs):
        try:
            user = request.user
            caption = request.data['caption']
            post = get_object_or_404(Posts, slug=request.data['slug'])
            if request.user == post.user:
                post.caption=caption
                post.save()
                return Response(status=status.HTTP_201_CREATED)
            
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
       
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
class DeletePostApiView(generics.DestroyAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    queryset = Posts.objects.all()
    lookup_field = 'slug'
   
            
class PostLikeApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def create(self, request, *args, **kwargs):
      #  try:
        post = get_object_or_404(Posts, slug=request.data['slug'])
        liked = request.data['liked']
        
        if (liked != None) :
            ct = ContentType.objects.get_for_model(Posts)
            if liked==False:
                Likes.objects.get_or_create(content_type=ct, object_id=post.id, user=request.user)
            if liked:
                like_obj = Likes.objects.filter(content_type=ct, object_id=post.id, user=request.user)
                if like_obj.exists():
                    like_obj.delete()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

            
class PostCommentApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def create(self, request, *args, **kwargs):
        try:
            post = get_object_or_404(Posts, slug=request.data['slug'])
            comment = request.data['comment']
                
            if (comment != None) and not (comment==''):
                comment = Comments.objects.create(user=request.user, comment=comment, post=post)
                #comment_notification(comment)
                user_data = GetCommentsSerializers(comment, context={'request':request})
                return Response(user_data.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetLikesApiView(CustomListApiView):
    queryset = User.objects.all()
    serializer_class = InitialDataSerializer
    permission_classes=[
            permissions.IsAuthenticated,
        ]
   # pagination_class = None
        
    def get_queryset(self):
        try:
            slug = self.kwargs.get('slug')
            post = get_object_or_404(Posts, slug=slug)
            liked_users = [i.user for i in post.like.all()]
            
            return liked_users
        except:
            return None
        
class GetCommentsApiView(generics.ListAPIView):
    queryset = Comments.objects.all()
    serializer_class = GetCommentsSerializers
    permission_classes=[
            permissions.IsAuthenticated,
        ]
  #  pagination_class = None
      
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        post = get_object_or_404(Posts, slug=slug)
        comments = Comments.objects.filter(post=post)
        return comments, post
        
    def list(self, request, *args, **kwargs):
        queryset, post = self.filter_queryset(self.get_queryset())
        
        user_data = UserSearchSerializer(post.user).data
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = {'comments':serializer.data, 'caption':post.caption, 'username':user_data['username'], 'timestamp':post.timestamp , 'profile_pic':request.build_absolute_uri(user_data['profile_pic'])} 
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        
        dic = {'comments':serializer.data, 'caption':post.caption, 'username':user_data['username'], 'timestamp':post.timestamp , 'profile_pic':request.build_absolute_uri(user_data['profile_pic'])}
        return Response(dic)
 

class CommentLikeApiView(generics.CreateAPIView):
    permission_classes=[
            permissions.IsAuthenticated,
        ]
    
    def create(self, request, *args, **kwargs):
        comment = get_object_or_404(Comments, id=request.data['id'])
        liked = request.data['liked']
        
        if (liked != None) :
            ct = ContentType.objects.get_for_model(Comments)
            if liked==False:
                Likes.objects.get_or_create(content_type=ct, object_id=comment.id, user=request.user)
            if liked:
                like_obj = Likes.objects.filter(content_type=ct, object_id=comment.id, user=request.user)
                if like_obj.exists():
                    like_obj.delete()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CommentDeleteApiView(generics.GenericAPIView):
    
    permission_classes=[
            permissions.IsAuthenticated,
        ]
        
    def post(self, request, *args, **kwargs):
        try:
            user = self.request.user
            comment_obj = get_object_or_404(Comments, id=self.request.data['id'])
            if user == comment_obj.user or user == comment_obj.post.user:
                comment_obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        