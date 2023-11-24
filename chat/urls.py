from django.urls import path
from chat.views import index_view, chat_view

urlpatterns = [
    path('', index_view, name='chat-list'),
    path('<str:chat_name>/', chat_view, name='chat-room')
]