# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-02 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0037_auto_20160427_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribution',
            name='function',
            field=models.CharField(blank=True, choices=[('COORDINATOR', 'Coordinator'), ('PROFESSOR', 'Professor')], db_index=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='acronym',
            field=models.CharField(db_index=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='offeryear',
            name='acronym',
            field=models.CharField(db_index=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='offeryearcalendar',
            name='end_date',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='offeryearcalendar',
            name='start_date',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='first_name',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(blank=True, db_index=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='registration_id',
            field=models.CharField(max_length=10, unique=True),
        )
    ]
