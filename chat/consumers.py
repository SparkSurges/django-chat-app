import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Chat, Message
from django.contrib.auth.models import User

class ServerConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.rooms = None
        self.groups_name = list()

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.rooms = self.user.chats.all()
            self.groups_name = [f'chat_{room.name}' for room in self.rooms]

            self.accept()

            for id in range(len(self.rooms)):
                self.send(json.dumps({
                    'type': 'users_list',
                    'users': [user.username for user in self.rooms[id].users.all()]
                }))
                self.send(json.dumps({
                    'type': 'users_list_online',
                    'users': [user.username for user in self.rooms[id].online.all()]
                }))

                await self.channel_layer.group_add(
                    self.groups_name[id],
                    self.channel_name,
                )


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Chat.objects.get(name=self.room_name)
        self.user = self.scope['user']

        self.accept()

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.username
                }
            )
            self.room.join(self.user)

        self.send(json.dumps({
            'type': 'user_list_online',
            'users': [user.username for user in self.room.online.all()],
        }))

        # Joining the channels group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.username,
                }
            )
            self.room.leave(self.user)
    
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.user.username,
                'message': message,
            }
        )

        Message.objects.create(user=self.user, chat=self.room, content=message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
    
    def user_list(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))
