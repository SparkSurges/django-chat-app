from django.db import models
from django.contrib.auth.models import User

class Status(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    status_connection = models.BooleanField(blank=False, null=True, default=False)

    def connected(self):
        self.status_connection = True
        self.save()

    def disconnect(self):
        self.status_connection = False
        self.save()

    def __str__(self):
        return self.status_connection