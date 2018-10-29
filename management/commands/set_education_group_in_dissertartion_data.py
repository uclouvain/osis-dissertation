#!/usr/bin/env python
from django.core.management.base import BaseCommand
from base.models.education_group_year import EducationGroupYear
from base.models.offer import Offer
from dissertation.models.offer_proposition import OfferProposition


def _build_map_offer_with_matching_education_group(offer_ids):
    education_group_years = EducationGroupYear.objects.all().select_related('education_group')\
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
            raise e
        map_offer_id_with_educ_group_id[offer.id] = educ_group_id
    return map_offer_id_with_educ_group_id


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Setting education_group in offer_proposition
        """
        offer_propositions = OfferProposition.objects.filter(education_group__isnull=True).all()
        offer_ids = set([op.offer_id for op in offer_propositions])
        map_offer_with_matching_education_group = _build_map_offer_with_matching_education_group(offer_ids)
        for off_prop in offer_propositions:
            off_prop.education_group_id = map_offer_with_matching_education_group[off_prop.offer_id]
            off_prop.save()