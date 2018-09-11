# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-11 17:42
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('corebot', '0002_auto_20180911_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='image_ref',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
