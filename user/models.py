from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    encrypted_hashkey = models.BinaryField()
    picture = models.ImageField(upload_to='img/users/', blank=True, null=True)
    connected = models.BooleanField(default=False)

    def user_connected(self):
        if not self.connected:
            self.connected = True
            self.save()

    def user_disconnected(self):
        if self.connected:
            self.connected = False
            self.save()

class Contact(models.Model):
    contact_id = models.UUIDField(primary_key=True, db_column='contact_id')
    user = models.ForeignKey(
        to=CustomUser, 
        on_delete=models.CASCADE, 
        related_name='contacts',
        db_column='user_id'
    )
    username = models.CharField(max_length=128)
    email = models.EmailField(_("contact"), blank=False, null=False)

    def __str__(self):
        return self.contact_key

