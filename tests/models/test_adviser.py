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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import User
from django.test import TestCase

from base.models.person import Person
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory, PersonWithoutUserFactory
from base.tests.factories.student import StudentFactory
from dissertation.models import adviser
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.dissertation_role import DissertationRoleFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory


def create_adviser(person, type="PRF"):
    adv = adviser.Adviser.objects.create(person=person, type=type)
    return adv


def create_adviser_from_user(user, type="PRF"):
    person = Person.objects.create(user=user, first_name=user.username, last_name=user.username)
    return create_adviser(person, type)


def create_adviser_from_scratch(username, email, password, type="PRF"):
    user = User.objects.create_user(username=username, email=email, password=password)
    return create_adviser_from_user(user, type)


class UtilsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_manager = PersonFactory()
        cls.person_manager2 = PersonFactory()
        cls.manager = AdviserManagerFactory(person=cls.person_manager)
        cls.manager2 = AdviserManagerFactory(person=cls.person_manager2)
        cls.a_person_teacher = PersonFactory(first_name='Pierre', last_name='Dupont')
        cls.teacher = AdviserTeacherFactory(person=cls.a_person_teacher)
        cls.a_person_teacher2 = PersonFactory(first_name='Marco', last_name='Millet')
        cls.teacher2 = AdviserTeacherFactory(person=cls.a_person_teacher2)
        cls.teacher3 = AdviserTeacherFactory()
        cls.teacher4 = AdviserTeacherFactory()
        a_person_student = PersonWithoutUserFactory(last_name="Durant")
        cls.student = StudentFactory(person=a_person_student)
        cls.offer1 = EducationGroupFactory()
        cls.offer2 = EducationGroupFactory()
        cls.academic_year1 = AcademicYearFactory()
        cls.academic_year2 = AcademicYearFactory(year=cls.academic_year1.year - 1)
        cls.education_group_year1 = EducationGroupYearFactory(acronym="test_offer1", education_group=cls.offer1,
                                                              academic_year=cls.academic_year1)
        cls.offer_proposition1 = OfferPropositionFactory(education_group=cls.offer1,
                                                         global_email_to_commission=True,
                                                         evaluation_first_year=True)
        cls.offer_proposition2 = OfferPropositionFactory(education_group=cls.offer2, global_email_to_commission=False)
        cls.proposition_dissertation = PropositionDissertationFactory(author=cls.teacher,
                                                                      creator=cls.a_person_teacher,
                                                                      title='Proposition 1212121'
                                                                      )
        cls.faculty_adviser1 = FacultyAdviserFactory(adviser=cls.manager, education_group=cls.offer1)
        cls.faculty_adviser2 = FacultyAdviserFactory(adviser=cls.manager, education_group=cls.offer2)
        cls.dissertation1 = DissertationFactory(author=cls.student,
                                                title='Dissertation_test_email',
                                                education_group_year=cls.education_group_year1,
                                                proposition_dissertation=cls.proposition_dissertation,
                                                status='DIR_SUBMIT',
                                                active=True,
                                                dissertation_role__adviser=cls.teacher,
                                                dissertation_role__status='PROMOTEUR'
                                                )
        DissertationRoleFactory(adviser=cls.teacher2, status='CO_PROMOTEUR', dissertation=cls.dissertation1)
        DissertationRoleFactory(adviser=cls.teacher3, status='READER', dissertation=cls.dissertation1)

    def test_convert_none_to_empty_str(self):
        self.assertEqual(adviser.none_to_str(None), '')
        self.assertEqual(adviser.none_to_str('toto'), 'toto')
