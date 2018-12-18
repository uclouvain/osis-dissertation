from __future__ import unicode_literals

from django.db import migrations


def populate_educationgroup_fields(apps, shema_editor):
    EducationGroupYear = apps.get_model('base', 'educationgroupyear')
    Offer = apps.get_model('base', 'offer')
    OfferYear = apps.get_model('base', 'offeryear')
    Dissertation = apps.get_model('dissertation', 'dissertation')
    OfferProposition = apps.get_model('dissertation', 'offerproposition')
    FacultyAdviser = apps.get_model('dissertation', 'facultyadviser')

    offer_propositions = OfferProposition.objects.filter(education_group__isnull=True).all()
    faculty_advisers = FacultyAdviser.objects.filter(education_group__isnull=True).all()
    dissertations = Dissertation.objects.filter(education_group_year_start__isnull=True).all()
    offer_ids = set([op.offer_id for op in offer_propositions])
    offer_year_ids = set([dissert.offer_year_start_id for dissert in dissertations])

    def get_map_offer_id_with_educ_grp(offer_ids):
        education_group_years = EducationGroupYear.objects.all().select_related('education_group') \
            .values('education_group_id', 'acronym')
        map_acronym_with_educ_group_id = {rec['acronym']: rec['education_group_id'] for rec in education_group_years}
        map_offer_id_with_educ_group_id = {}
        for offer in Offer.objects.filter(pk__in=offer_ids).prefetch_related('offeryear_set'):
            if offer.offeryear_set.count() < 1:
                raise Exception('WARNING :: No OfferYear found for offer = {}'.format(offer.id))
            off_year = offer.offeryear_set.order_by('-academic_year__year').first()
            try:
                educ_group_id = map_acronym_with_educ_group_id[off_year.acronym]
            except KeyError as e:
                print('WARNING :: acronym {} does not have matching education group id.'.format(off_year.acronym))

            map_offer_id_with_educ_group_id[offer.id] = educ_group_id

        return map_offer_id_with_educ_group_id

    map_offer_with_matching_education_group = get_map_offer_id_with_educ_grp(offer_ids)

    def get_map_education_group_year_id_with_offer_year(offer_year_ids):
        education_group_years = EducationGroupYear.objects.all().values('id', 'acronym')
        map_acronym_with_educ_group_year_id = {rec['acronym']: rec['id'] for rec in education_group_years}
        map_offer_year_id_with_educ_group_year_id = {}
        for offer_year in OfferYear.objects.filter(pk__in=offer_year_ids):
            try:
                educ_group_year_id = map_acronym_with_educ_group_year_id[offer_year.acronym]
            except KeyError as e:
                print('WARNING :: acronym {} does not have matching education group id.'.format(offer_year.acronym))

            map_offer_year_id_with_educ_group_year_id[offer_year.id] = educ_group_year_id
        return map_offer_year_id_with_educ_group_year_id

    for off_prop in offer_propositions:
        off_prop.education_group_id = map_offer_with_matching_education_group[off_prop.offer_id]
        off_prop.save()

    for fac_adv in faculty_advisers:
        fac_adv.education_group_id = map_offer_with_matching_education_group[fac_adv.offer_id]
        fac_adv.save()

    map_offer_year_with_matching_education_group_year = get_map_education_group_year_id_with_offer_year(offer_year_ids)

    for dissert in dissertations:
        dissert.education_group_year_id = map_offer_year_with_matching_education_group_year[dissert.offer_year_start_id]
        dissert.save()


class Migration(migrations.Migration):
    dependencies = [
        ('dissertation', '0039_auto_20181217_1442'),
    ]

    operations = [
        migrations.RunPython(populate_educationgroup_fields),
    ]
