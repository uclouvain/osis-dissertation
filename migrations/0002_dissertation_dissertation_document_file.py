# Generated by Django 3.2.12 on 2022-06-08 15:05

from django.db import migrations, models
import osis_document.contrib.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0001_squashed_0052_auto_20210419_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='dissertation',
            name='dissertation_document_file',
            field=osis_document.contrib.fields.FileField(base_field=models.UUIDField(), default=list, null=True, size=2),
        ),
    ]
