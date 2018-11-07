##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.offer import OfferFactory
from dissertation.models.faculty_adviser import FacultyAdviser, search_education_group_ids_by_user
from dissertation.tests.factories.adviser import AdviserManagerFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory


def create_faculty_adviser(adviser, offer):
    faculty_adviser = FacultyAdviser(adviser=adviser, offer=offer)
    faculty_adviser.save()
    return faculty_adviser


class FacultyManagerTest(TestCase):

    def setUp(self):
        self.adviser_manager = AdviserManagerFactory()
        self.offer = OfferFactory()
        self.eduction_group = EducationGroupFactory()

    def test_str_self(self):
        faculty_adviser = FacultyAdviserFactory(adviser=self.adviser_manager, offer=self.offer)
        self.assertEqual(str(faculty_adviser), "{} - Offer {}".format(str(self.adviser_manager), str(self.offer.id)))

    def test_get_adviser_type(self):
        faculty_adviser = FacultyAdviserFactory(adviser=self.adviser_manager)
        self.assertEqual(faculty_adviser.get_adviser_type(), self.adviser_manager.type)

    def test_search_education_group_ids_by_user(self):
        education_group2 = EducationGroupFactory()
        
        FacultyAdviserFactory(adviser=self.adviser_manager, education_group=self.eduction_group)
        FacultyAdviserFactory(adviser=self.adviser_manager, education_group=education_group2)

        self.assertListEqual(
            sorted([self.eduction_group.id, education_group2.id]),
            list(search_education_group_ids_by_user(self.adviser_manager.person.user))
        )
