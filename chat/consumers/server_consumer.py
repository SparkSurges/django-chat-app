import json
import logging
import functools
from channels.generic.websocket import WebsocketConsumer
from chat.models import Chat, Message
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

def check_authentication(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self.user and self.user.is_authenticated:
            return await func(self, *args, **kwargs)
        return wrapper

class ServerConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.rooms = None
        self.groups_name = None 

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.rooms = self.user.chats.all()
            self.groups_name = [f'chat_{room.name}' for room in self.rooms]

            self.accept()
            self.user.status.connected()

            status = list([])
            for id in range(len(self.rooms)):
                self.rooms[id].join_online(self.user)
                status.append({
                    self.rooms[id].name: [
                        {
                            'type': 'users_list',
                            'users': [user.username for user in self.rooms[id].users.all()]
                        },
                        {
                            'type': 'users_list_online',
                            'users': [user.username for user in self.rooms[id].online.all()]
                        }
                   ],
                })

                await self.channel_layer.group_add(
                    self.groups_name[id],
                    self.channel_name,
                )

            self.send(json.dumps(status))

    @check_authentication
    async def disconnect(self, code):
        for id in range(len(self.rooms)):
            await self.channel_layer.group_discard(
                self.groups_name[id],
                self.channel_name,
            )

            self.rooms[id].leave_online(self.user)

        return super().disconnect(code)
    
    @check_authentication
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        try:
            message = text_data_json['message']
            group_name = text_data_json['group_name']

            if group_name not in self.groups_name:
                logger.warning('Invalid group_name')
                self.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid group_name'
                }))
                return
        except KeyError as err:
            logger.error(f'An error ocurred: {err}')
            self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid message'
            }))
            return

        await self.channel_layer.group_send(
            f'chat_{group_name}',
            {
                'type': 'chat_message',
                'user': self.user.username,
                'message': message,
            }
        )

        room = self.user.chats.get(name=group_name) 
        Message.objects.create(user=self.user, chat=room, content=message)

    def users_list(self, event):
        self.send(text_data=json.dumps(event))

    def users_list_online(self, event):
        self.send(text_data=json.dumps(event))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
        
    def error(self, event):
        self.send(text_data=json.dumps(event))
