from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import CustomUser, Contact

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Contact)
