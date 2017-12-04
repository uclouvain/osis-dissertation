# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-20 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0186_message_templates_learning_unit_deletion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='learningunit',
            options={'permissions': (('can_access_learningunit', 'Can access learning unit'), ('can_edit_learningunit_pedagogy', 'Can edit learning unit pedagogy'), ('can_edit_learningunit_specification', 'Can edit learning unit specification'), ('can_delete_learningunit', 'Can delete learning unit'))},
        ),
        migrations.AlterField(
            model_name='academiccalendar',
            name='reference',
            field=models.CharField(blank=True, choices=[('DELIBERATION', 'DELIBERATION'), ('DISSERTATION_SUBMISSION', 'DISSERTATION_SUBMISSION'), ('EXAM_ENROLLMENTS', 'EXAM_ENROLLMENTS'), ('SCORES_EXAM_DIFFUSION', 'SCORES_EXAM_DIFFUSION'), ('SCORES_EXAM_SUBMISSION', 'SCORES_EXAM_SUBMISSION'), ('TEACHING_CHARGE_APPLICATION', 'TEACHING_CHARGE_APPLICATION'), ('COURSE_ENROLLMENT', 'COURSE_ENROLLMENT')], max_length=50, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='offeryearcalendar',
            unique_together=set([('academic_calendar', 'education_group_year')]),
        ),
    ]
