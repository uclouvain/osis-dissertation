# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-20 13:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0306_auto_20180709_1334'),
        ('dissertation', '0034_offerproposition_global_email_to_commission'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicEducationGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('education_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroup')),
                ('proposition_dissertation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dissertation.PropositionDissertation')),
            ],
        ),
    ]
