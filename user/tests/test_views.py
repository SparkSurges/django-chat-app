# Fix issues
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import Client
import pytest
from user.forms import LoginForm, RegistrationForm
from user.utils import anonymous_required
from mixer.backend.django import mixer

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_login_view(client, mocker):
    # Mock the authenticate method to return a user
    mocker.patch('django.contrib.auth.authenticate', return_value=mixer.blend(User))

    response = client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'})

    assert response.status_code == 302  # Should redirect after successful login
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert 'Login successful.' in messages

@pytest.mark.django_db
def test_logout_view(client):
    response = client.get(reverse('logout'))

    assert response.status_code == 302  # Should redirect after logout
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert 'Logout successfully.' in messages

@pytest.mark.django_db
def test_registration_view(client, mocker):
    mocker.patch('user.views.login', return_value=None)  # Mock the login method

    response = client.post(reverse('registration'), {'username': 'newuser', 'password1': 'password123', 'password2': 'password123'})

    assert response.status_code == 302  # Should redirect after successful registration
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert 'You have signed up successfully.' in messages

# Add more tests as needed
