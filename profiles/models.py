from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Posts
from chatSystem.models import ChatProfile

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='profile_follower', blank=True)
    followings = models.ManyToManyField(User, related_name='profile_followings', blank=True)
    posts = models.ManyToManyField(Posts, blank=True)
 #   saved_posts = models.ManyToManyField(Posts, blank=True)
    
    def __str__(self):
        return self.user.username

class SavedPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username
        
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    try:
        if created:
            Profile.objects.create(user=instance)
            ChatProfile.objects.create(user=instance)
    except:
        instance.delete()
