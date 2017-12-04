# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-24 08:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0192_auto_20171123_0827'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationGroupType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('category', models.CharField(choices=[('TRAINING', 'TRAINING'), ('MINI_TRAINING', 'MINI_TRAINING'), ('GROUP', 'GROUP')], default='TRAINING', max_length=25)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='category',
        ),
        migrations.RemoveField(
            model_name='educationgroupyear',
            name='education_group_type',
        ),
    ]
