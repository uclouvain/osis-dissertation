# ##################################################################################################
#  OSIS stands for Open Student Information System. It's an application                            #
#  designed to manage the core business of higher education institutions,                          #
#  such as universities, faculties, institutes and professional schools.                           #
#  The core business involves the administration of students, teachers,                            #
#  courses, programs and so on.                                                                    #
#                                                                                                  #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)              #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify                            #
#  it under the terms of the GNU General Public License as published by                            #
#  the Free Software Foundation, either version 3 of the License, or                               #
#  (at your option) any later version.                                                             #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful,                                 #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                                  #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                   #
#  GNU General Public License for more details.                                                    #
#                                                                                                  #
#  A copy of this license - GNU General Public License - is available                              #
#  at the root of the source code of this program.  If not,                                        #
#  see http://www.gnu.org/licenses/.                                                               #
# ##################################################################################################
from datetime import date

from dateutil.relativedelta import relativedelta

from base.models.education_group_year import EducationGroupYear
from base.models.offer import Offer
from dissertation.models.dissertation import Dissertation
from dissertation.models.faculty_adviser import FacultyAdviser
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_offer import PropositionOffer


def offer_proposition_extend_dates():
    all_offer_propositions = OfferProposition.objects.all()
    logs = ''
    for offer_proposition in all_offer_propositions:
        logs += check_dates_of_offer_proposition(offer_proposition)
    if not logs:
        logs = 'no action'
    return logs


def check_dates_of_offer_proposition(offer_prop):
    logs = ''
    logs += check_date_end(offer_prop, start_arg="start_visibility_proposition", end_arg="end_visibility_proposition")
    logs += check_date_end(offer_prop, start_arg="start_visibility_dissertation", end_arg="end_visibility_dissertation")
    logs += check_date_end(offer_prop, start_arg="start_jury_visibility", end_arg="end_jury_visibility")
    logs += check_date_end(offer_prop, start_arg="start_edit_title", end_arg="end_edit_title")
    if logs:
        logs = str(offer_prop.education_group.most_recent_acronym) + "\n" + logs
    return logs


def check_date_end(offer_prop, start_arg, end_arg):
    date_now = date.today()
    offer_start = getattr(offer_prop, start_arg)
    offer_end = getattr(offer_prop, end_arg)
    logs = ''
    if offer_end < date_now:
        logs += "{} : {}  {} : {}".format(
            start_arg, offer_start, end_arg, offer_end
        )
        setattr(offer_prop, start_arg, incr_year(offer_start))
        setattr(offer_prop, end_arg, incr_year(offer_end))
        logs += "new data : {} : {} new {} : {} \n".format(start_arg, offer_start, end_arg, offer_end)
        offer_prop.save()
    return logs


def incr_year(date_too):
    return date_too + relativedelta(years=1)


def clean_db_with_no_educationgroup_match():
    offer_propositions = OfferProposition.objects.filter(education_group=None)
    faculty_advisers = FacultyAdviser.objects.all()
    dissertations = Dissertation.objects.all()
    offer_ids = set([op.offer_id for op in offer_propositions])
    offer_year_ids = set([dissert.offer_year_start_id for dissert in dissertations])

    def get_map_offer_id_with_educ_grp(offer_ids):
        education_group_years = EducationGroupYear.objects.all().select_related('education_group') \
            .values('education_group_id', 'acronym')
        map_acronym_with_educ_group_id = {rec['acronym']: rec['education_group_id'] for rec in education_group_years}
        map_offer_id_with_educ_group_id = {}
        for offer in Offer.objects.filter(pk__in=offer_ids).prefetch_related('offeryear_set'):
            if offer.offeryear_set.count() < 1:
                print('WARNING :: No OfferYear found for offer = {}'.format(offer.id))
                continue
            off_year = offer.offeryear_set.order_by('-academic_year__year').first()
            try:
                educ_group_id = map_acronym_with_educ_group_id[off_year.acronym]
                map_offer_id_with_educ_group_id[offer.id] = educ_group_id
            except KeyError as e:
                print('WARNING :: acronym {} does not have matching education group id.'.format(off_year.acronym))
        return map_offer_id_with_educ_group_id

    def find_childs_of_offer_prop(offer_prop):
        offer_prop.offer.offeryear_set.order_by('-academic_year__year').first()

        child_offer_prop = OfferProposition.objects.filter(offer__offeryear_set__academic_year__acronym__
                                                           ).exclude(offer_prop)

    map_offer_with_matching_education_group = get_map_offer_id_with_educ_grp(offer_ids)

    for off_prop in offer_propositions:
        educ_group_id = map_offer_with_matching_education_group.get(off_prop.offer_id, None)
        if educ_group_id:
            off_prop.education_group_id = educ_group_id
            off_prop.save()
        else:
            porposition_offers_this_off_prop = PropositionOffer.objects.filters(offer_proposition=off_prop)
