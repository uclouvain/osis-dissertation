# Generated by Django 2.2.5 on 2019-11-29 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0050_auto_20191129_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dissertation',
            name='defend_periode',
            field=models.CharField(choices=[('UNDEFINED', 'Undefined'), ('JANUARY', 'January'), ('JUNE', 'June'), ('SEPTEMBER', 'September')], default='UNDEFINED', max_length=12, null=True, verbose_name='Defense period'),
        ),
    ]
