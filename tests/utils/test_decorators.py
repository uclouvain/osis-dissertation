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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory, PersonWithoutUserFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.student import StudentFactory
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.utils import decorators
from dissertation.utils.decorators import autorized_dissert_promotor_or_manager


class DecoratorsTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.person_manager = PersonFactory.create()
        self.person_manager2 = PersonFactory.create()
        self.manager = AdviserManagerFactory(person=self.person_manager)
        self.manager2 = AdviserManagerFactory(person=self.person_manager2)
        self.a_person_teacher = PersonFactory.create()
        self.teacher = AdviserTeacherFactory(person=self.a_person_teacher)
        self.teacher2 = AdviserTeacherFactory()
        self.a_person_student = PersonWithoutUserFactory.create()
        self.student = StudentFactory.create(person=self.a_person_student)
        self.offer1 = OfferFactory(title="test_offer1")
        self.offer2 = OfferFactory(title="test_offer2")
        self.academic_year1 = AcademicYearFactory()
        self.offer_year_start1 = OfferYearFactory(
            acronym="test_offer1",
            offer=self.offer1,
            academic_year=self.academic_year1
        )
        self.faculty_adviser1 = FacultyAdviserFactory(adviser=self.manager, offer=self.offer1)
        self.faculty_adviser2 = FacultyAdviserFactory(adviser=self.manager2, offer=self.offer2)
        self.proposition_dissertation = PropositionDissertationFactory()
        self.dissertation1 = DissertationFactory(
            author=self.student,
            offer_year_start=self.offer_year_start1,
            proposition_dissertation=self.proposition_dissertation,
            status='DIR_SUBMIT',
            active=True,
            dissertation_role__adviser=self.teacher,
            dissertation_role__status='PROMOTEUR'
        )

    def test_adviser_is_dissertation_promotor(self):
        self.assertTrue(decorators.user_is_dissertation_promotor(self.a_person_teacher.user, self.dissertation1))
        self.assertFalse(decorators.user_is_dissertation_promotor(self.person_manager2.user, self.dissertation1))
        self.assertFalse(decorators.user_is_dissertation_promotor(self.person_manager.user, self.dissertation1))

    def test_user_autorised_dissert_author_manager(self):
        self.assertTrue(autorized_dissert_promotor_or_manager(self.a_person_teacher.user, str(self.dissertation1.id)))
        self.assertTrue(autorized_dissert_promotor_or_manager(self.manager.person.user, str(self.dissertation1.id)))
        self.assertFalse(autorized_dissert_promotor_or_manager(self.teacher2.person.user, str(self.dissertation1.id)))
        self.assertFalse(autorized_dissert_promotor_or_manager(self.manager2.person.user, str(self.dissertation1.id)))

    def test_adviser_can_manage(self):
        self.assertTrue(decorators.adviser_can_manage(self.dissertation1, self.manager))
        self.assertFalse(decorators.adviser_can_manage(self.dissertation1, self.manager2))
        self.assertFalse(decorators.adviser_can_manage(self.dissertation1, self.teacher))

    def test_user_passes_test_for_dissert(self):
        self.client.force_login(self.person_manager2.user)
        response = self.client.get('/dissertation/manager_dissertations_detail/' + str(self.dissertation1.id))
        self.assertRedirects(response, reverse('manager_dissertations_list'))
        self.client.force_login(self.person_manager.user)
        response = self.client.get('/dissertation/manager_dissertations_detail/' + '999999')
        self.assertRedirects(response, reverse('manager_dissertations_list'))

    def test_user_passes_test_for_dissert2(self):
        self.client.force_login(self.person_manager.user)
        response = self.client.get('/dissertation/manager_dissertations_detail/' + str(self.dissertation1.id))
        self.assertEqual(response.status_code, 302)

    def test_object_is_none_redirect(self):
        self.client.force_login(self.person_manager.user)
        dissert = None
        self.assertEqual(decorators.object_is_none_redirect(dissert, '/dissertation/').status_code, 302)
        dissert = self.dissertation1
        self.assertEqual(decorators.object_is_none_redirect(dissert, '/dissertation/'), None)
