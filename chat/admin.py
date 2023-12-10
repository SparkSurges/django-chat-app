from django.contrib import admin
from chat.models import Chat, Message, ChatAdmin, ChatUser

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(ChatAdmin)
admin.site.register(ChatUser)
