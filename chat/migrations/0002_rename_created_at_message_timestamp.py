# Generated by Django 4.2.7 on 2023-12-08 21:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='created_at',
            new_name='timestamp',
        ),
    ]
