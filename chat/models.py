import json
import datetime
from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from chat.utils import generate_key, generate_link

class Chat(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, blank=True)
    picture = models.ImageField(upload_to='img/', default='img/default_chat.jpg')
    users = models.ManyToManyField(to=User, blank=True, related_name='chats')
    private_link = models.JSONField(default=dict)
    group_name = models.CharField(max_length=64, blank=False, null=False, default=str) 

    def delete_image(self):
        self.picture.delete(save=False)
        self.picture = 'img/default_chat.jpg'
        self.save()

    def get_online_count(self):
        return self.online.count()
    
    def join_online(self, user):
        if user not in self.online.all():
            self.online.add(user)
            self.save()

    def leave_online(self, user):
        if user in self.online.all():
            self.online.remove(user)
            self.save()

    def join(self, user):
        if user not in self.users.all():
            self.users.add(user)
            self.save()
    
    def leave(self, user):
        if user in self.users.all():
            self.users.remove(user)
            self.save()

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'chat'

def generate_group_name(instance):
    return f'chat_{instance.name}_{generate_key()}'

def generate_link():
    token = generate_key()
    link_data = {
        'created_at': datetime.now().isoformat(),
        'link': f'chat/{token}',
    }

    return link_data

@receiver(pre_save, sender=Chat)
def set_initial_link(sender, instance, **kwargs):
    if not instance.private_link:
        instance.private_link = json.dumps(generate_link())

@receiver(pre_save, sender=Chat)
def set_default_group_name(sender, instance, **kwargs):
    if not instance.group_name:
        instance.group_name = generate_group_name(instance)

class Message(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    content = models.TextField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
    class Meta:
        db_table = 'message'
