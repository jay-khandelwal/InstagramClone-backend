from rest_framework import serializers
from .models import Notification

class NotificationsSerializers(serializers.ModelSerializer):
    
    from_user = serializers.SerializerMethodField()
    ntype = serializers.SerializerMethodField()
    fprofile_pic = serializers.SerializerMethodField()
    other = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
                'id',
                'from_user',
                'fprofile_pic',
                'ntype',
                'read',
                'timestamp',
                'other',
            ]
            
    def get_from_user(self, obj):
        return obj.from_user.username
        
    def get_ntype(self, obj):
        return obj.notification_types
        
    def get_fprofile_pic(self,obj):
      #  request = self.context.get("request")
      #  return request.build_absolute_uri(obj.from_user.profile_pic.url)
        try:
            return obj.from_user.profile_pic.url
        except:
            return None
       
    def get_other(self, obj):
        if (obj.notification_types == 'PostLike') or (obj.notification_types == 'PostComment' or obj.notification_types == 'CommentLike'):
            request = self.context.get("request")
            if obj.notification_types == 'PostLike':
                post = obj.content_object.content_object
                return {
                    'post':request.build_absolute_uri(post.image.url), 
                    'slug':post.slug,
                }
            if obj.notification_types == 'PostComment':
                comment = obj.content_object
                post = obj.content_object.post
                return {'post':request.build_absolute_uri(post.image.url), 'slug':post.slug, 'comment':comment.comment}
            
            if obj.notification_types == 'CommentLike':
                comment = obj.content_object.content_object
                return {
                    'comment':comment.comment,
                    'slug':comment.post.slug,
                    'post':request.build_absolute_uri(comment.post.image.url),
                }
        else:
            return None
       
    
    