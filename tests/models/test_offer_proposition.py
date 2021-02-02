##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.offer_proposition import get_by_dissertation, get_by_offer_proposition_group, \
    find_by_id
from dissertation.models.offer_proposition_group import OfferPropositionGroup
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.offer_proposition_group import OfferPropositionGroupFactory


def create_offer_proposition(acronym, education_group, offer_proposition_group=None):
    offer_proposition = OfferPropositionFactory.create(
        acronym=acronym,
        education_group=education_group,
        offer_proposition_group=offer_proposition_group)
    EducationGroupYearFactory(education_group=offer_proposition.education_group)
    return offer_proposition


class OfferPropositionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.offer_proposition_with_good_dates = OfferPropositionFactory()
        cls.education_group_with_offer_proposition = EducationGroupFactory()
        cls.offer_proposition_group = OfferPropositionGroupFactory()
        cls.offer_proposition = OfferPropositionFactory(
            education_group=cls.education_group_with_offer_proposition,
            offer_proposition_group=cls.offer_proposition_group
        )
        cls.education_group_year = EducationGroupYearFactory(
            education_group=cls.education_group_with_offer_proposition
        )
        cls.dissertation = DissertationFactory(
            education_group_year=cls.education_group_year
        )

    def test_offer_proposition_exist(self):
        OfferPropositionGroupFactory.create(name_short="PSP", name_long="Faculté de Psychologie")
        offer_proposition_g = OfferPropositionGroup.objects.get(name_short='PSP')
        OfferProposition.objects.create(acronym="PSP2MSG",
                                        offer_proposition_group=offer_proposition_g)
        offer_proposition_psp = OfferProposition.objects.get(acronym='PSP2MSG')
        self.assertEqual(offer_proposition_psp.offer_proposition_group,
                         OfferPropositionGroup.objects.get(name_short='PSP'))

    def test_periode_visibility_proposition(self):
        visibility = self.offer_proposition_with_good_dates.in_periode_visibility_proposition
        self.assertTrue(visibility)

    def test_periode_visibility_dissertation(self):
        visibility = self.offer_proposition_with_good_dates.in_periode_visibility_dissertation
        self.assertTrue(visibility)

    def test_periode_jury_visibility(self):
        visibility = self.offer_proposition_with_good_dates.in_periode_jury_visibility
        self.assertTrue(visibility)

    def test_periode_edit_title(self):
        visibility = self.offer_proposition_with_good_dates.in_periode_edit_title
        self.assertTrue(visibility)

    def test_find_by_id_with_bad_values(self):
        offer_proposition = find_by_id(None)
        self.assertIsNone(offer_proposition)

    def test_get_by_dissertation(self):
        dissert = get_by_dissertation(self.dissertation)
        self.assertEqual(dissert, self.offer_proposition)

    def test_get_by_offer_proposition_group(self):
        self.assertEqual(get_by_offer_proposition_group(self.offer_proposition_group), self.offer_proposition)

    def test_get_by_offer_proposition_group_0(self):
        offer_proposition_group = 0
        self.assertEqual(get_by_offer_proposition_group(offer_proposition_group), None)
