# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-13 14:38
from __future__ import unicode_literals

import base.models.enums.diploma_coorganization
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0165_auto_20171009_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationGroupOrganization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('all_students', models.BooleanField(default=False)),
                ('enrollment_place', models.BooleanField(default=False)),
                ('diploma', models.CharField(choices=[('UNIQUE', 'UNIQUE'), ('SEPARATE', 'SEPARATE'), ('NOT_CONCERNED', 'NOT_CONCERNED')], default=base.models.enums.diploma_coorganization.DiplomaCoorganizationTypes('NOT_CONCERNED'), max_length=40)),
                ('education_group_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Organization')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='organization_logos'),
        ),
    ]