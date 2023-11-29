from django.urls import path
from chat.views import chat_view

urlpatterns = [
    path('', chat_view, name='chat-room')
]