# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-02-13 14:39
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osis_common', '0014_messagequeuecache'),
        ('dissertation', '0042_auto_20190211_1136'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adviser',
            options={},
        ),
        migrations.AddField(
            model_name='adviser',
            name='proposition_dissertation',
            field=models.ManyToManyField(related_name='advisers', through='dissertation.PropositionRole', to='dissertation.PropositionDissertation'),
        ),
        migrations.AddField(
            model_name='dissertation',
            name='dissertation_documents_files',
            field=models.ManyToManyField(through='dissertation.DissertationDocumentFile', to='osis_common.DocumentFile'),
        ),
        migrations.AlterField(
            model_name='dissertation',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='dissertation',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dissertation.DissertationLocation'),
        ),
        migrations.AlterField(
            model_name='dissertation',
            name='proposition_dissertation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dissertations', to='dissertation.PropositionDissertation', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='dissertationrole',
            name='adviser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dissertations_roles', to='dissertation.Adviser'),
        ),
        migrations.AlterField(
            model_name='offerproposition',
            name='education_group',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='offer_proposition', to='base.EducationGroup'),
        ),
    ]
