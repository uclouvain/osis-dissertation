# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-11 12:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0211_auto_20180109_1436'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offeryearcalendar',
            name='customized',
        ),
    ]