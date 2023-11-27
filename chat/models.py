import json
import datetime
from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Chat(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, blank=True)
    picture = models.ImageField(upload_to='img/', default='img/default_chat.jpg')
    users = models.ManyToManyField(to=User, blank=True, related_name='chats')
    online = models.ManyToManyField(to=User, blank=True, related_name='online_users')
    is_private = models.BooleanField(blank=False, null=False, default=False)
    private_links = models.JSONField(default=list)

    def generate_link(self):
        if self.is_private:
            try:
                links = json.loads(self.private_links)
            except json.JSONDecodeError:
                links = []

            token = Token.generate_key()
            link_data = {
                'created_at': datetime.now().isoformat(),
                'link': f'chat/{token}',
            }
            links.append(link_data)

            self.private_links = json.dumps(links)
            self.save()

            return link_data['link']

        return f'{self.name}'

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

    def save(self, *args, **kwargs):
        self.generate_link()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        db_table = 'chat'

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
