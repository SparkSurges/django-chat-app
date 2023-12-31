import json
import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import Client
from chat.consumers.server_consumer import ServerConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async, async_to_sync
from channels.routing import URLRouter
from django.urls import path

@pytest.mark.django_db
@pytest.mark.asyncio
async def set_user():
    return await database_sync_to_async(get_user_model().objects.create_user)(
        username='testuser',
        password='testpass',
    )

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_connect_authenticated():
    user = await set_user() 

    client = Client()
    await sync_to_async(client.login)(
        username=user.username, 
        password='testpass',
    )
    session_id = client.cookies['sessionid'].value

    headers = [
        ('cookie', f'sessionid={session_id}'.encode('utf-8')),
    ]

    application = URLRouter([
        path('ws/server/', ServerConsumer.as_asgi())
    ]) 
    communicator = WebsocketCommunicator(application, '/ws/server/', headers=headers)

    connected, _ = await communicator.connect()
    assert connected

    response = await communicator.receive_json_from()
    assert response['type'] == 'websocket.accept'
    assert response['status'] == 'connected'

    await communicator.disconnect()

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_receive_authenticated_message():
    user = await database_sync_to_async(get_user_model().objects.create_user)(
        username='testuser',
        password='testpass'
    )

    client = Client()
    await sync_to_async(client.login)(username='testuser', password='testpass')

    session_id = client.cookies['sessionid'].value

    headers = [
        (b'cookie', f'sessionid={session_id}'.encode('utf-8')),
    ]

    communicator = WebsocketCommunicator(ServerConsumer.as_asgi(), 'ws/server', headers=headers)

    await communicator.connect()

    # Simulate a message from the frontend
    message_data = {'type': 'receive', 'message': 'Test message', 'group_name': 'test_group'}
    await communicator.send_json_to(message_data)

    # Check if the message is received by the group
    response = await communicator.receive_json_from()
    assert response['type'] == 'chat_message'
    assert response['user'] == user.username
    assert response['message'] == 'Test message'

    await communicator.disconnect()

@pytest.mark.asyncio
async def test_receive_unauthenticated_message():
    communicator = WebsocketCommunicator(ServerConsumer.as_asgi(), 'ws/server')

    # Try to receive a message without connecting first
    message_data = {'type': 'receive', 'message': 'Test message', 'group_name': 'test_group'}
    await communicator.send_json_to(message_data)

    # Check if an error message is received
    response = await communicator.receive_json_from()
    assert response['type'] == 'error'
    assert response['message'] == 'Invalid message'

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_receive_invalid_group_name():
    await database_sync_to_async(get_user_model().objects.create_user)(
        username='testuser',
        password='testpass'
    )

    client = Client()
    await sync_to_async(client.login)(username='testuser', password='testpass')

    session_id = client.cookies['sessionid'].value

    headers = [
        (b'cookie', f'sessionid={session_id}'.encode('utf-8')),
    ]

    communicator = WebsocketCommunicator(ServerConsumer.as_asgi(), 'ws/server', headers=headers)

    await communicator.connect()

    message_data = {'type': 'receive', 'message': 'Test message', 'group_name': 'invalid_group'}
    await communicator.send_json_to(message_data)

    # Check if an error message is received
    response = await communicator.receive_json_from()
    assert response['type'] == 'error'
    assert response['message'] == 'Invalid group_name'

    await communicator.disconnect()
