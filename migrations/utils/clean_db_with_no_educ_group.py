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

from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_offer import PropositionOffer


def clean_db_with_no_educationgroup_match():

    offer_props_with_education_group_not_none = OfferProposition.objects.exclude(education_group=None)
    log = ''

    offer_props_with_education_group_none = OfferProposition.objects.filter(education_group=None).\
        prefetch_related('propositionoffer_set')

    def Return_tab_childs_offer_prop(offer_prop):
        tab_with_child = []
        for offer_prop_not_none in offer_props_with_education_group_not_none:
            if offer_prop.acronym in offer_prop_not_none.acronym:
                tab_with_child.append(offer_prop_not_none)
        return tab_with_child

    def check_if_child(propositions_offers, child_list):
        # boucle qui vérifie si il y a une autre liaison avec un enfant ou pas.
        for prop_offer_check_if_child in propositions_offers:
            if prop_offer_check_if_child.offer_proposition in child_list:
                return True
        return False

    def add_line(str_):
        return str_ + '\n'

    props_disserts = PropositionDissertation.objects.filter(offer_propositions__education_group=None).\
        prefetch_related('propositionoffer_set', 'offer_propositions').distinct()
    for proposition_dissertation in props_disserts:
        log += add_line('*********************************************************************************')
        log += add_line(proposition_dissertation.title)
        for prop_offer in proposition_dissertation.propositionoffer_set.all():
            log += add_line('   ' + prop_offer.offer_proposition.acronym)
            if prop_offer.offer_proposition in offer_props_with_education_group_none:
                log += add_line('      ' + prop_offer.offer_proposition.acronym + ' have none education group')
                child_list_offer_prop = Return_tab_childs_offer_prop(prop_offer.offer_proposition)
                if_other_proposition_offer_child = check_if_child(proposition_dissertation.propositionoffer_set.all(),
                                                                  child_list_offer_prop)
                log += add_line('      ' + prop_offer.offer_proposition.acronym + ' have none education group')
                if not if_other_proposition_offer_child:
                    log += add_line('Ne dispose pas d\'un enfant (' + str(if_other_proposition_offer_child)
                                    + ') :  child list :' + str(child_list_offer_prop))
                    for child_offer_prop in child_list_offer_prop:
                        PropositionOffer.objects.create(proposition_dissertation=proposition_dissertation,
                                                        offer_proposition=child_offer_prop)
                        log += add_line('A un enfant ou pas : ' + str(if_other_proposition_offer_child)
                                        + '  child list :' + str(child_list_offer_prop))
    print(log)
