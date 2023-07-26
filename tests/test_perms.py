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
from rest_framework import status

import dissertation.perms
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory, PersonWithoutUserFactory
from base.tests.factories.student import StudentFactory
from dissertation.models.enums.dissertation_role_status import DissertationRoleStatus
from dissertation.perms import adviser_can_manage, \
    autorized_dissert_promotor_or_manager, \
    adviser_can_manage_proposition_dissertation, \
    autorized_proposition_dissert_promotor_or_manager_or_author
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.dissertation_role import DissertationRoleFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory


class DecoratorsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_manager = PersonFactory()
        cls.person_no_manager = PersonFactory()
        cls.person_manager2 = PersonFactory()
        cls.manager = AdviserManagerFactory(person=cls.person_manager)
        cls.manager2 = AdviserManagerFactory(person=cls.person_manager2)
        cls.a_person_teacher = PersonFactory()
        cls.teacher = AdviserTeacherFactory(person=cls.a_person_teacher)
        cls.teacher2 = AdviserTeacherFactory()
        cls.teacher3 = AdviserTeacherFactory()
        cls.a_person_student = PersonWithoutUserFactory()
        cls.student = StudentFactory(person=cls.a_person_student)
        cls.education_group = EducationGroupFactory()
        cls.education_group2 = EducationGroupFactory()
        cls.academic_year1 = AcademicYearFactory()
        cls.education_group_year = EducationGroupYearFactory(
            acronym="test_offer1",
            title="test_offer1",
            education_group=cls.education_group,
            academic_year=cls.academic_year1
        )
        cls.faculty_adviser1 = FacultyAdviserFactory(
            adviser=cls.manager,
            education_group=cls.education_group
        )
        cls.faculty_adviser2 = FacultyAdviserFactory(
            adviser=cls.manager2,
            education_group=cls.education_group2
        )
        cls.proposition_dissertation = PropositionDissertationFactory(author=cls.teacher,
                                                                      creator=cls.teacher3.person)
        cls.offer_propo = OfferPropositionFactory(education_group=cls.education_group)
        cls.proposition_offer = PropositionOfferFactory(
            proposition_dissertation=cls.proposition_dissertation,
            offer_proposition=cls.offer_propo
        )
        cls.dissertation1 = DissertationFactory(
            author=cls.student,
            education_group_year=cls.education_group_year,
            proposition_dissertation=cls.proposition_dissertation,
            status='DIR_SUBMIT',
            active=True,
            dissertation_role__adviser=cls.teacher,
            dissertation_role__status=DissertationRoleStatus.PROMOTEUR.name
        )
        cls.dissertation_role = DissertationRoleFactory(
            adviser=cls.teacher3,
            status=DissertationRoleStatus.READER.name,
            dissertation=cls.dissertation1
        )

    def test_adviser_is_dissertation_promotor(self):
        self.assertTrue(
            dissertation.perms.user_is_dissertation_promotor(self.a_person_teacher.user, self.dissertation1))
        self.assertFalse(
            dissertation.perms.user_is_dissertation_promotor(self.person_manager2.user, self.dissertation1))
        self.assertFalse(dissertation.perms.user_is_dissertation_promotor(self.person_manager.user, self.dissertation1))

    def test_user_autorised_dissert_author_manager(self):
        self.assertTrue(autorized_dissert_promotor_or_manager(self.a_person_teacher.user, str(self.dissertation1.id)))
        self.assertTrue(autorized_dissert_promotor_or_manager(self.manager.person.user, str(self.dissertation1.id)))
        self.assertFalse(autorized_dissert_promotor_or_manager(self.teacher2.person.user, str(self.dissertation1.id)))
        self.assertFalse(autorized_dissert_promotor_or_manager(self.manager2.person.user, str(self.dissertation1.id)))

    def test_adviser_can_manage(self):
        self.assertTrue(adviser_can_manage(self.dissertation1, self.manager))
        self.assertFalse(adviser_can_manage(self.dissertation1, self.manager2))
        self.assertFalse(adviser_can_manage(self.dissertation1, self.teacher))

    def test_user_manager_passes_test_for_dissert(self):
        self.client.force_login(self.person_manager.user)
        response = self.client.get('/dissertation/manager_dissertations_detail/' + '999999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get('/dissertation/manager_dissertations_detail/' + str(self.dissertation1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_login(self.person_manager2.user)
        response = self.client.get('/dissertation/manager_dissertations_detail/' + str(self.dissertation1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_teacher_passes_test_for_dissert(self):
        self.client.force_login(self.a_person_teacher.user)
        response = self.client.get('/dissertation/dissertations_detail/' + '999999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get('/dissertation/dissertations_detail/' + str(self.dissertation1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_login(self.teacher2.person.user)
        response = self.client.get('/dissertation/dissertations_detail/' + str(self.dissertation1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_login(self.teacher3.person.user)
        response = self.client.get('/dissertation/dissertations_detail/' + str(self.dissertation1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_adviser_is_in_jury(self):
        self.assertTrue(autorized_dissert_promotor_or_manager(self.a_person_teacher.user, str(self.dissertation1.id)))
        self.assertFalse(autorized_dissert_promotor_or_manager(self.teacher2.person.user, str(self.dissertation1.id)))

    def test_adviser_can_manage_proposition_dissertation(self):
        self.client.force_login(self.manager.person.user)
        self.assertEqual(adviser_can_manage_proposition_dissertation(
            self.proposition_dissertation,
            self.manager), True)
        self.assertNotEqual(adviser_can_manage_proposition_dissertation(
            self.proposition_dissertation,
            self.manager2), True)

    def test_autorized_proposition_dissert_promotor_or_manager_or_author(self):
        self.assertTrue(autorized_proposition_dissert_promotor_or_manager_or_author(
            self.manager.person.user,
            self.proposition_dissertation
        ))
        self.assertTrue(autorized_proposition_dissert_promotor_or_manager_or_author(
            self.teacher.person.user,
            self.proposition_dissertation
        ))
        self.assertFalse(autorized_proposition_dissert_promotor_or_manager_or_author(
            self.teacher2.person.user,
            self.proposition_dissertation
        ))
        self.assertFalse(autorized_proposition_dissert_promotor_or_manager_or_author(
            self.teacher3.person.user,
            self.proposition_dissertation
        ))
        self.assertFalse(autorized_proposition_dissert_promotor_or_manager_or_author(
            self.manager2.person.user,
            self.proposition_dissertation
        ))
        self.assertFalse(autorized_proposition_dissert_promotor_or_manager_or_author(
            self.person_no_manager.user,
            self.proposition_dissertation
        ))
