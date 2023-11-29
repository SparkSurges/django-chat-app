from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    status_connection = models.BooleanField(blank=False, null=True, default=False)
    picture = models.ImageField(upload_to='img/user/', default='img/default_user.jpg')

    def connected(self):
        self.status_connection = True
        self.save()

    def disconnect(self):
        self.status_connection = False
        self.save()

    def check_connection(self):
        return self.status_connection

    def __str__(self):
        return self.user.username
