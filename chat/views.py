from django.shortcuts import render
from chat.models import Chat

def index_view(request):
    return render(request, 'chat/index.html', {'chat_list': Chat.objects.all()})

def chat_view(request, chat_name):
    chat, created = Chat.objects.get_or_create(name=chat_name)
    return render(request, 'chat/chat.html', {'chat': chat})
