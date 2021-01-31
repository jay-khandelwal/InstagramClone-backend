from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from notifications.models import Notification
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

 

class Likes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
  #  notification = GenericRelation(Notification, related_query_name='likes')
    def __str__(self):
        return self.user.username



class Posts(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True)
    caption = models.CharField(max_length=500, blank=True)
 #   comments = models.ManyToManyField(Comments, blank=True)
    slug = models.SlugField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='post_likes')
    like = GenericRelation(Likes, related_query_name='posts')
    
    def __str__(self):
        return self.user.username
        
        

class Comments(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = GenericRelation(Likes)
    
    def __str__(self):
        return self.user.username        

      
@receiver(post_save, sender=Likes)
def send_like_notification(sender, instance, created, **kwargs):   
    if created:
        obj = instance.content_object
        if not obj.user==instance.user:
            if isinstance(obj, Posts):
                notify = Notification.objects.create(target=obj.user, from_user=instance.user, notification_types=Notification.PostLike, content_object=instance)
            
            elif isinstance(obj, Comments):
                notify = Notification.objects.create(target=obj.user, from_user=instance.user, notification_types=Notification.CommentLike, content_object=instance)
                
            else:
                pass
        
        
@receiver(pre_delete, sender=Likes)
def delete_like_notification(sender, instance, **kwargs):
    try:
        ct = ContentType.objects.get_for_model(Likes)
        if isinstance(instance.content_object, Posts):
            notify = Notification.objects.filter(notification_types=Notification.PostLike, content_type=ct, object_id=instance.id)
            notify.delete()
        elif isinstance(instance.content_object, Comments):
            notify = Notification.objects.filter(notification_types=Notification.CommentLike, content_type=ct, object_id=instance.id)
            notify.delete()
            
        else:
            pass
    except:
        pass

@receiver(post_save, sender=Comments)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        if not post.user == instance.user:
            notify = Notification.objects.create(target=post.user, from_user=instance.user, notification_types=Notification.PostComment, content_object=instance)
        

@receiver(pre_delete, sender=Comments)
def delete_comment_notification(sender, instance, **kwargs):
    try:
        ct = ContentType.objects.get_for_model(Comments)
        # deleting comment notification
        notify = Notification.objects.filter(notification_types=Notification.PostComment, content_type=ct, object_id=instance.id)
        notify.delete()
        # deleting all likes of tje comment
        likes = Likes.objects.filter(content_type=ct, object_id=instance.id)
        likes.delete()
    except:
        pass        
        
        
        