# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-30 15:02
from __future__ import unicode_literals

from django.db import migrations, utils
from django.db import transaction


def copy_previous_pgrm_to_current_lunit(apps, model):
    base = apps.get_app_config('base')
    ProgramManager = base.get_model('programmanager')
    OfferYear = base.get_model('offeryear')
    previous_pgrm = ProgramManager.objects.filter(offer_year__academic_year__year=2016)\
                                          .select_related('offer_year__offer')
    for pgrm in previous_pgrm:
        new_offer_year = OfferYear.objects.filter(offer=pgrm.offer_year.offer, academic_year__year=2017).first()
        if new_offer_year:
            try:
                with transaction.atomic():
                    pgrm.pk = None
                    pgrm.offer_year = new_offer_year
                    pgrm.save()
            except utils.IntegrityError:
                print("Duplicated.")

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0197_auto_20171130_0823'),
    ]

    operations = [
        migrations.RunPython(copy_previous_pgrm_to_current_lunit),
    ]