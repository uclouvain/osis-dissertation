# Generated by Django 2.2.5 on 2019-11-29 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0051_auto_20191129_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adviser',
            name='type',
            field=models.CharField(choices=[('PROFESSOR', 'Professor'), ('COURSE_MANAGER', 'Course manager')], default='PROFESSOR', max_length=15),
        ),
    ]
