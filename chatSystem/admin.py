from django.contrib import admin
from .models import ChatProfile, ChatRequest, ChatRoom,ChatMessages, UserMessages

admin.site.register(ChatProfile)
admin.site.register(ChatRequest)
admin.site.register(ChatRoom)
admin.site.register(ChatMessages)
admin.site.register(UserMessages)
