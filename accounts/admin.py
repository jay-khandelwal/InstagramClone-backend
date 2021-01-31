from django.contrib import admin
from .models import User, ConnectedUsers

admin.site.register(User)
admin.site.register(ConnectedUsers)
