from django.contrib import admin
from .models import Posts, Likes, Comments

admin.site.register(Posts)
admin.site.register(Likes)
admin.site.register(Comments)
