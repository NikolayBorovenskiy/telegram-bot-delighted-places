# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-11 17:38
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('corebot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='image',
        ),
        migrations.AddField(
            model_name='place',
            name='image_ref',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
