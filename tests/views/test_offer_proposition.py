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
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from dissertation.models import faculty_adviser, offer_proposition
from dissertation.tests.factories.adviser import AdviserManagerFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory


class OfferPropositionViewTestCase(TestCase):

    def setUp(self):
        self.person = PersonFactory()
        self.manager = AdviserManagerFactory(person=self.person)
        self.education_group = EducationGroupFactory()
        self.education_group2 = EducationGroupFactory()
        self.education_group_year = EducationGroupYearFactory(education_group=self.education_group)
        self.education_group_year2 = EducationGroupYearFactory(education_group=self.education_group2)
        self.faculty_manager = FacultyAdviserFactory(adviser=self.manager, education_group=self.education_group2)
        self.faculty_manager2 = FacultyAdviserFactory(adviser=self.manager, education_group=self.education_group)
        self.offer_proposition = OfferPropositionFactory(pk=12,
                                                         education_group=self.education_group,
                                                         start_visibility_proposition="2018-12-12",
                                                         end_visibility_proposition="2019-12-12",
                                                         start_visibility_dissertation="2018-12-12",
                                                         end_visibility_dissertation="2019-12-12",
                                                         start_jury_visibility="2018-12-12",
                                                         end_jury_visibility="2019-12-12",
                                                         start_edit_title="2018-12-12",
                                                         end_edit_title="2019-12-12",
                                                         )
        self.offer_proposition2 = OfferPropositionFactory(pk=15,
                                                         education_group=self.education_group2,
                                                         start_visibility_proposition="2018-12-12",
                                                         end_visibility_proposition="2019-12-12",
                                                         start_visibility_dissertation="2018-12-12",
                                                         end_visibility_dissertation="2019-12-12",
                                                         start_jury_visibility="2018-12-12",
                                                         end_jury_visibility="2019-12-12",
                                                         start_edit_title="2018-12-12",
                                                         end_edit_title="2019-12-12",
                                                         )

    def test_manager_offer_parameters(self):
        self.client.force_login(self.manager.person.user)
        offer_propositions = [self.offer_proposition, self.offer_proposition2]
        response = self.client.post(reverse("manager_offer_parameters"))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        education_groups = faculty_adviser.find_education_groups_by_adviser(self.manager)
        offer_props = offer_proposition.search_by_education_group(education_groups)
        self.assertCountEqual(offer_props, offer_propositions)

    def test_manager_offer_parameters_edit(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.post(reverse("manager_offer_parameters_edit")+"?pk=12&pk=15", {
            "start_visibility_proposition" : "2018-12-12",
            "end_visibility_proposition" : "2019-12-12",
            "start_visibility_dissertation" : "2018-12-12",
            "end_visibility_dissertation" : "2019-12-12",
            "start_jury_visibility" : "2018-12-12",
            "end_jury_visibility" : "2019-12-12",
            "start_edit_title" : "2018-12-12",
            "end_edit_title" : "2019-12-12"
        })
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        response = self.client.post(reverse("manager_offer_parameters_edit") + "?pk=12&pk=15", {
            "start_visibility_proposition": "2018-12-12",
            "end_visibility_proposition": "2016-12-12",
            "start_visibility_dissertation": "2018-12-12",
            "end_visibility_dissertation": "2019-12-12",
            "start_jury_visibility": "2018-12-12",
            "end_jury_visibility": "2019-12-12",
            "start_edit_title": "2018-12-12",
            "end_edit_title": "2019-12-12"
        })
        self.assertEqual(response.status_code, HttpResponse.status_code)
        response = self.client.get(reverse("manager_offer_parameters_edit") + "?pk=12")
        self.assertEqual(response.status_code, HttpResponse.status_code)
