# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-26 12:56
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0018_populate_adviser_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adviser',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
