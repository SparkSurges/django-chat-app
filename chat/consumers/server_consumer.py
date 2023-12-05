import json
import logging
import functools
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Chat, Message, get_user_contact_username, PrivateMessage
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from core.settings import ENV
from django.core.cache import cache

logger = logging.getLogger(__name__)

def check_authentication(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.user:
            self.user = self.scope['user']
        if self.user.is_authenticated:
            return await func(self, *args, **kwargs)
        return wrapper

class ServerConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.rooms = list()
        self.private_rooms = list()
        self.private_groups_name = list()
        self.groups_name = list()

    async def _initialize_connection(self):
        self.rooms = await database_sync_to_async(self.user.chats.all)()
        self.groups_name = [room.group_name for room in self.rooms]
        self.private_rooms = await database_sync_to_async(self.user.private_chats.all)()
        self.groups_name = [room.group_name for room in self.private_rooms]

        self.accept()
        user_id = self.scope['user'].id
        cache.set(f'user_status:{user_id}', 'connected')

        status = list([])
        for id in range(len(self.rooms)):
            status.append({
                self.rooms[id].name: [
                    {
                        'type': 'users_list',
                        'users': [
                            {
                                'username': user.username,
                                'status_connection': cache.get(f'user_status:{user.id}', 'disconnected')
                            } for user in self.rooms[id].users.all()
                        ]
                    },
               ],
            })

            await self.channel_layer.group_add(
                self.groups_name[id],
                self.channel_name,
            )

        for id in range(len(self.private_rooms)):
            await self.channel_layer.group_add(
                self.private_groups_name[id],
                self.channel_name,
            )

        self.send(json.dumps(status))

    @check_authentication
    async def connect(self):
        await self._initialize_connection()

    @check_authentication
    async def disconnect(self, code):
        for id in range(len(self.rooms)):
            await self.channel_layer.group_discard(
                self.groups_name[id],
                self.channel_name,
            )
        for id in range(len(self.private_rooms)):
            await self.channel_layer.group_discard(
                self.private_groups_name[id],
                self.channel_name,
            )

        user_id = self.scope['user'].id
        cache.delete(f'user_status:{user_id}')
        return super().disconnect(code)
    
    @check_authentication
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        try:
            message = text_data_json['message']
            group_name = text_data_json['group_name']

            if group_name not in self.groups_name and group_name not in self.private_groups_name:
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

        if group_name not in self.groups_name:
            private_room = await database_sync_to_async(self.user.chats.get)(name=group_name)
            await database_sync_to_async(PrivateMessage.objects.create)(
                user=self.user,
                private_chat=private_room,
                content=message 
            )

        room = await database_sync_to_async(self.user.chats.get)(name=group_name)
        await database_sync_to_async(Message.objects.create)(
            user=self.user,
            chat=room,
            content=message,
        )

    def users_list(self, event):
        self.send(text_data=json.dumps(event))

    def users_list_online(self, event):
        self.send(text_data=json.dumps(event))

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
        
    def error(self, event):
        self.send(text_data=json.dumps(event))
