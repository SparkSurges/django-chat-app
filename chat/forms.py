from django import forms
from chat.models import Chat

class CreateChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = [
            'name',
            'description',
            'picture',
            'users',
        ]