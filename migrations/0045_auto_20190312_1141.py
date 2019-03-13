# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-12 11:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0044_auto_20190221_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facultyadviser',
            name='education_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='base.EducationGroup'),
        ),
        migrations.AlterField(
            model_name='facultyadviser',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Offer'),
        ),
    ]
