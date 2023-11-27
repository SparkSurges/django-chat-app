from django.urls import re_path, path
from chat.consumers.server_consumer import ServerConsumer

websockets_urlpatterns = [
    path('ws/server/', ServerConsumer.as_asgi()),
]