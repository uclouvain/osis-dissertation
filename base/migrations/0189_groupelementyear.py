# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-21 08:56
from __future__ import unicode_literals

import base.models.enums.sessions_derogation
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0188_auto_20171121_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupelementyear',
            name='own_comment',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='current_order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='is_mandatory',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='max_credits',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='min_credits',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='relative_credits',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='sessions_derogation',
            field=models.CharField(choices=[('SESSION_1', 'SESSION_1'), ('SESSION_2', 'SESSION_2'), ('SESSION_3', 'SESSION_3'), ('SESSION_1_2', 'SESSION_1_2'), ('SESSION_1_3', 'SESSION_1_3'), ('SESSION_2_3', 'SESSION_2_3'), ('SESSION_1_2_3', 'SESSION_1_2_3'), ('SESSION_UNDEFINED', 'SESSION_UNDEFINED'), ('SESSION_PARTIAL_2_3', 'SESSION_PARTIAL_2_3')], default=base.models.enums.sessions_derogation.SessionsDerogationTypes('SESSION_UNDEFINED'), max_length=65),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='absolute_credits',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='groupelementyear',
            name='block',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
