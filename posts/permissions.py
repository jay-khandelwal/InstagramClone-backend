from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404

from profiles.models import Profile
from accounts.models import User


class PostSeeingPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        userWanted = view.kwargs.get('username')
        if user == userWanted:
            return True
        else:
            user = get_object_or_404(User, username=userWanted)
            if user.privacy==False :
                return True
            elif (user.privacy):
                profile = get_object_or_404(Profile, user=user)
                isFollower = profile.followers.filter(username=user).exists()
                
                return True
                
            else:
                return False
            
        


