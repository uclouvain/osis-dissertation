# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-15 15:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0003_auto_20161215_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='score_responsible',
            field=models.BooleanField(default=False),
        ),
    ]