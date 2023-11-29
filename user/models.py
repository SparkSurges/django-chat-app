from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='img/user/', default='img/default_user.jpg')

    def __str__(self):
        return self.user.username
