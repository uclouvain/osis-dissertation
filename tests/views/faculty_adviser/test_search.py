# ##################################################################################################
#   OSIS stands for Open Student Information System. It's an application                           #
#   designed to manage the core business of higher education institutions,                         #
#   such as universities, faculties, institutes and professional schools.                          #
#   The core business involves the administration of students, teachers,                           #
#   courses, programs and so on.                                                                   #
#   Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)             #
#   This program is free software: you can redistribute it and/or modify                           #
#   it under the terms of the GNU General Public License as published by                           #
#   the Free Software Foundation, either version 3 of the License, or                              #
#   (at your option) any later version.                                                            #
#   This program is distributed in the hope that it will be useful,                                #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                 #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                  #
#   GNU General Public License for more details.                                                   #
#   A copy of this license - GNU General Public License - is available                             #
#   at the root of the source code of this program.  If not,                                       #
#   see http://www.gnu.org/licenses/.                                                              #
# ##################################################################################################

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.entity_manager import EntityManagerFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory


class TestOfferPropositionFilterView(TestCase):
    @classmethod
    def setUpTestData(cls):
        AcademicYearFactory(current=True)
        cls.entity_manager = EntityManagerFactory()
        cls.education_group = OfferPropositionFactory()

    def setUp(self):
        self.client.force_login(self.entity_manager.person.user)

    def test_offer_proposition_search(self):
        response = self.client.get(
            reverse('offer_propositions')+'?offer_proposition={}'.format(self.education_group.pk), data={}
        )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_adviser_list(self):
        response = self.client.get(
            reverse('adviser_list')+'?offer_proposition={}'.format(self.education_group.pk), data={}
        )
        self.assertEqual(response.status_code, HttpResponse.status_code)
