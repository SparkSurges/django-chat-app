import json
import datetime
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from chat.utils import generate_key
from user.models import CustomUser

class Chat(models.Model):
    id = models.UUIDField(primary_key=True)
    creator = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='own_chats')
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, blank=True, null=True)
    picture = models.ImageField(upload_to='img/', default='img/default_chat.jpg')
    users = models.ManyToManyField(to=CustomUser, blank=True, null=True, related_name='chats')
    link = models.JSONField(default=dict)
    group_name = models.CharField(max_length=64) 

    def delete_image(self):
        self.picture.delete(save=False)
        self.picture = 'img/default_chat.jpg'
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
def set_creator_as_user(sender, instance, **kwargs):
    if not instance.users.filter(user=instance.creator).exists():
        instance.users.add(instance.creator)

@receiver(pre_save, sender=Chat)
def set_initial_link(sender, instance, **kwargs):
    if not instance.private_link:
        instance.link = json.dumps(generate_link())

@receiver(pre_save, sender=Chat)
def set_default_group_name(sender, instance, **kwargs):
    if not instance.group_name:
        instance.group_name = generate_group_name(instance)

class Message(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    content = models.TextField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
    class Meta:
        db_table = 'message'

class PrivateChat(models.Model):
    id = models.UUIDField(primary_key=True)
    users = models.ManyToManyField(to=CustomUser, related_name='private_chats')
    group_name = models.CharField(max_length=64)

    class Meta:
        db_table = 'private_chat'

def get_user_contact(instance, user):
    try:
        user_contact = instance.users.exclude(id=user.id).first()
        return user_contact
    except CustomUser.DoesNotExist:
        return None
    
def get_user_contact_username(instance, user):
    user_contact = get_user_contact(instance, user)
    return user.contacts.get(email=user_contact.email).username

def generate_group_name(instance):
    return f'chat_private_{generate_key()}'

@receiver(pre_save, sender=PrivateChat)
def set_default_private_group_name(sender, instance, **kwargs):
    if not instance.group_name:
        instance.group_name = generate_group_name(instance)

class PrivateMessage(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    private_chat = models.ForeignKey(to=PrivateChat, on_delete=models.CASCADE)
    content = models.TextField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'private_message'
