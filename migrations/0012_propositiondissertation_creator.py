# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-25 14:24
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0059_auto_20160718_1435'),
        ('dissertation', '0011_auto_20160824_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='propositiondissertation',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person'),
        ),
    ]
