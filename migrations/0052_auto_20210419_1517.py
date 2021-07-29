# Generated by Django 2.2.13 on 2021-04-19 15:17

from django.db import migrations


def remove_unused_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name="dissertation_administrators").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0051_auto_20191211_1458'),
    ]

    operations = [
        migrations.RunPython(remove_unused_groups, migrations.RunPython.noop, elidable=True)
    ]
