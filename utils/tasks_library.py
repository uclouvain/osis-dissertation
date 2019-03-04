# ##############################################################################
#   OSIS stands for Open Student Information System. It's an application
#   designed to manage the core business of higher education institutions,
#   such as universities, faculties, institutes and professional schools.
#   The core business involves the administration of students, teachers,
#   courses, programs and so on.
#
#   Copyright (C) 2015- 2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   A copy of this license - GNU General Public License - is available
#   at the root of the source code of this program.  If not,
#   see http://www.gnu.org/licenses/.
# ##############################################################################
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Subquery, OuterRef

from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.offer_year import OfferYear
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_offer import PropositionOffer
from osis_common.tests.queue.test_callbacks import get_object


def offer_proposition_extend_dates():
    date_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    all_offer_propositions = OfferProposition.objects.all()
    logs = ''
    for offer_proposition in all_offer_propositions:
        logs += check_dates_of_offer_proposition(offer_proposition)
    if not logs:
        logs = 'no action'
    return "{} ;   task date: {}" .format(logs, date_time_now)


def check_dates_of_offer_proposition(offer_prop):
    logs = ''
    logs += check_date_end(offer_prop, start_arg="start_visibility_proposition", end_arg="end_visibility_proposition")
    logs += check_date_end(offer_prop, start_arg="start_visibility_dissertation", end_arg="end_visibility_dissertation")
    logs += check_date_end(offer_prop, start_arg="start_jury_visibility", end_arg="end_jury_visibility")
    logs += check_date_end(offer_prop, start_arg="start_edit_title", end_arg="end_edit_title")
    if logs:
        logs = str(offer_prop.recent_acronym_education_group) + " , " + logs + ' ; '
    return logs


def check_date_end(offer_prop, start_arg, end_arg):
    date_now = date.today()
    offer_start = getattr(offer_prop, start_arg)
    offer_end = getattr(offer_prop, end_arg)
    logs = ''
    if offer_end < date_now:
        logs += "{} :  {} : {}  {} : {}        ".format(
            offer_prop.recent_acronym_education_group, start_arg, offer_start, end_arg, offer_end
        )
        setattr(offer_prop, start_arg, incr_year(offer_start))
        setattr(offer_prop, end_arg, incr_year(offer_end))
        logs += "new data : {} : {} new {} : {}       ".format(start_arg, getattr(offer_prop, start_arg),
                                                               end_arg, getattr(offer_prop, end_arg))
        offer_prop.save()
    return logs


def incr_year(date_too):
    return date_too + relativedelta(years=1)


def clean_db_with_no_educationgroup_match():
    offer_props_with_education_group_none = OfferProposition.objects.filter(education_group=None).annotate(
        last_acronym=Subquery(
            OfferYear.objects.filter(
                offer__offer_proposition=OuterRef('pk'),
                academic_year=current_academic_year).values('acronym')[:1]
        ))
    offer_props_with_education_group_not_none = OfferProposition.objects.exclude(education_group=None).annotate(
        last_acronym=Subquery(
            EducationGroupYear.objects.filter(
                education_group__offer_proposition=OuterRef('pk'),
                academic_year=current_academic_year).values('acronym')[:1]
        ))
    log = ''

    def find_childs(offer_prop):
        tab_with_child_pk = []
        for offer_prop_not_none in offer_props_with_education_group_not_none:
            if offer_prop.last_acronym in offer_prop_not_none.last_acronym:
                tab_with_child_pk.append(offer_prop_not_none.pk)

    offer_props_with_education_group_none.annotate(pk_child_list=find_childs)
    props_disserts = PropositionDissertation.objects.all().prefetch_related('propositionoffer_set')
    # parcours des propositions dissertations
    for prop_dissert in props_disserts:
        # parcours des liaisons proposition_offer de chaque proposition dissertation
        for prop_offer in prop_dissert.propositionoffer_set.all():
            # si la proposition offer est une liaison avec un Offer_proposition avec education_group None
            if prop_offer.offer_proposition in offer_props_with_education_group_none:

                pk_child_list = find_childs(prop_offer.offer_proposition)
                if_other_proposition_offer_child = False
                # boucle qui vérifie si il y a une autre liaison avec un enfant ou pas.
                for prop_offer_check_if_child in prop_dissert.propositionoffer_set.all():
                    if prop_offer_check_if_child.pk in pk_child_list:
                        if_other_proposition_offer_child = True
                # si il n'y a pas d'autre liaison alors il faut les créer
                if if_other_proposition_offer_child == False:
                    # pour chaque programme enfant trouvé précédament et dont la PK est déjà stocké
                    for pk_child in pk_child_list:
                        log = log + 'création d\'un enfant : prop_dissert.id :{}, offer_proposition.id :{}'\
                            .format(prop_dissert.id, pk_child)
                        PropositionOffer.objects.create(proposition_dissertation=prop_dissert,
                                                        offer_proposition=get_object(pk=pk_child))
                else:
                    log = log + 'pas besoin de création d\'enfant pour id :{} , {}'.format(prop_dissert.id,
                                                                                           prop_dissert.title)
    print(log)

