import json
import logging
from datetime import datetime
from cryptography import fernet
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from chat.utils import generate_key
from user.models import CustomUser

logger = logging.getLogger(__name__)

class Chat(models.Model):
    id = models.UUIDField(primary_key=True)
    admins = models.ManyToManyField(
        to=CustomUser, 
        through='ChatAdmin',
        related_name='owned_chats'
    )
    users = models.ManyToManyField(
        to=CustomUser, 
        through='ChatUser',
        related_name='chats'
    )
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    picture = models.ImageField(
        upload_to='img/chats/', 
        null=True, 
        blank=True
    )
    is_private = models.BooleanField(default=False)
    link = models.JSONField(default=dict, blank=True, null=True)
    group_name = models.CharField(max_length=64, editable=False) 
    created_at = models.DateTimeField(
        editable=False, 
        default=datetime.now
    )

    def delete_image(self):
        self.picture.delete(save=False)
        self.save()

    def join(self, user):
        if user not in self.users.all() and user not in self.admins.all():
            self.users.add(user)
            self.save()
    
    def leave(self, user):
        if user in self.users.all(): 
            self.users.remove(user)
            self.save()

        if user in self.admins.all():
            self.admins.remove(user)
            if self.admins.count() == 0:
                self.delete()
            self.save()

    def __str__(self):
        return self.name if self.name else str(self.id)
    
    class Meta:
        db_table = 'chat'

def generate_group_name():
    return f'chat_{generate_key(size=40)}'

def generate_link():
    token = generate_key()
    link_data = {
        'created_at': datetime.now().isoformat(),
        'link': f'chat/{token}',
    }

    return link_data

@receiver(pre_save, sender=Chat)
def set_initial_link(sender, instance, **kwargs):
    if not instance.link and instance.is_private:
        instance.link = json.dumps(generate_link())

@receiver(pre_save, sender=Chat)
def set_default_group_name(sender, instance, **kwargs):
    if not instance.group_name:
        instance.group_name = generate_group_name(instance)

class ChatAdmin(models.Model):
    user = models.ForeignKey(
        to=CustomUser, 
        on_delete=models.CASCADE, 
        db_column='admin_id'
    )
    chat = models.ForeignKey(
        to=Chat, 
        on_delete=models.CASCADE, 
        db_column='chat_id'
    )

    class Meta:
        db_table = 'chat_admin'
        
class ChatUser(models.Model):
    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        db_column='user_id',
    )
    chat = models.ForeignKey(
        to=Chat,
        on_delete=models.CASCADE,
        db_column='chat_id'
    )

    class Meta:
        db_table = 'chat_user'

class Message(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    chat = models.ForeignKey(to=Chat, on_delete=models.CASCADE)
    encrypted_content = models.BinaryField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
   
    def decrypt(self, hashkey):
        try:
            fer = fernet.Fernet(hashkey)
            decrypted_content = fer.decrypt(self.encrypted_content).decode()
            return decrypted_content
        except Exception as err:
            logger.error(f'Decryption failed: {err}')
    
    def encrypt(self, hashkey, content):
        try:
            fer = fernet.Fernet(hashkey)
            encrypted_content = fer.encrypt(content.encode())
            return encrypted_content
        except Exception as err:
            logger.error(f'Encryption failed: {err}') 

    def get_content(self, hashkey):
        return self.decrypt(hashkey)
   
    class Meta:
        db_table = 'message'
