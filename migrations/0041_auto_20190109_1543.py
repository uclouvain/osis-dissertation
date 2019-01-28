# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-09 15:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0040_populate_educationgroup_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dissertation',
            name='offer_year_start',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear'),
        ),
    ]