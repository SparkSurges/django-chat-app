from django.urls import re_path
from chat.consumers.server_consumer import ServerConsumer

websockets_urlpatterns = [
    re_path(r'ws/server/$', ServerConsumer.as_asgi()),
]