from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, unique=True)

class Profile(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.OneToOneField(to=CustomUser, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='img/user/', default='img/default_user.jpg')

    def __str__(self):
        return self.user.username

class Contact(models.Model):
    id = models.UUIDField(primary_key=True)
    username = models.CharField(max_length=128)
    email = models.EmailField(_("contact"), blank=False)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='contacts')

    def __str__(self):
        return self.contact_key
        