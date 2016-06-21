# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-02 15:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0039_auto_20160502_0055'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoresEncoding',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('total_exam_enrollments', models.IntegerField()),
                ('exam_enrollments_encoded', models.IntegerField()),
            ],
            options={
                'managed': False,
                'db_table': 'app_scores_encoding',
            },
        ),
        migrations.RunSQL(
            """
            DROP VIEW IF EXISTS app_scores_encoding;

            CREATE OR REPLACE VIEW app_scores_encoding AS
            SELECT row_number() OVER () as id,

                base_programmanager.id as program_manager_id,
                program_manager_person.id as pgm_manager_person_id,
                tutor_person.id as tutor_person_id,
                base_offeryear.id as offer_year_id,
                base_learningunityear.id as learning_unit_year_id,

                count(base_examenrollment.id) as total_exam_enrollments,
                sum(case when base_examenrollment.score_final is not null or base_examenrollment.justification_final is not null then 1 else 0 end) exam_enrollments_encoded


            from base_person tutor_person
            join base_tutor on tutor_person.id = base_tutor.person_id
            join base_attribution on base_attribution.tutor_id = base_tutor.id
            join base_learningunit on base_learningunit.id = base_attribution.learning_unit_id
            join base_learningunityear on base_learningunityear.learning_unit_id = base_learningunit.id
            join base_sessionexam on base_sessionexam.learning_unit_year_id = base_learningunityear.id
            join base_examenrollment on base_sessionexam.id = base_examenrollment.session_exam_id
            join base_offeryearcalendar on base_offeryearcalendar.id = base_sessionexam.offer_year_calendar_id
            join base_offeryear on base_offeryear.id = base_offeryearcalendar.offer_year_id
            join base_programmanager on base_programmanager.offer_year_id = base_offeryear.id
            join base_person program_manager_person on program_manager_person.id = base_programmanager.person_id

            where base_offeryearcalendar.start_date < CURRENT_TIMESTAMP
            and base_offeryearcalendar.end_date >  CURRENT_TIMESTAMP

            group by
            base_programmanager.id,
            program_manager_person.id,
            tutor_person.id,
            base_offeryear.id,
            base_learningunityear.id
            ;
            """
        ),
    ]
