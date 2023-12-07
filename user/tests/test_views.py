from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import Client
import pytest
from user.models import CustomUser
from mixer.backend.django import mixer

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_login_view(client, mocker):
    CustomUser.objects.create_user(username='testuser', password='testpassword')

    mocker.patch('django.contrib.auth.authenticate', return_value=mixer.blend(CustomUser))

    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})

    assert response.status_code == 302  # Should redirect after successful login
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert 'Login successful.' in messages

@pytest.mark.django_db
def test_logout_view(client):
    user = CustomUser.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')

    response = client.get(reverse('logout'))

    assert response.status_code == 302
    messages_cookie = response.client.cookies.get('messages')
    assert messages_cookie is not None 

@pytest.mark.django_db
def test_registration_view(client, mocker):
    mocker.patch('user.views.login', return_value=None)

    response = client.post(reverse('register'), {'username': 'newuser', 'email': 'new@email.com', 'password1': '@newpassnotsimilar567', 'password2': '@newpassnotsimilar567'})

    assert response.status_code == 302
    messages_cookie = response.client.cookies.get('messages')
    assert messages_cookie is not None 
