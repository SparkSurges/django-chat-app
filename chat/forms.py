from django import forms
from chat.models import Chat

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = [
            'name',
            'description',
            'picture',
            'users',
        ]

class PrivateChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = [
            'name',
            'users',
        ]
