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
    def setUp(self):
        self.person_manager = PersonFactory()
        self.person_manager2 = PersonFactory()
        self.manager = AdviserManagerFactory(person=self.person_manager)
        self.manager2 = AdviserManagerFactory(person=self.person_manager2)
        self.a_person_teacher = PersonFactory(first_name='Pierre', last_name='Dupont')
        self.teacher = AdviserTeacherFactory(person=self.a_person_teacher)
        self.a_person_teacher2 = PersonFactory(first_name='Marco', last_name='Millet')
        self.teacher2 = AdviserTeacherFactory(person=self.a_person_teacher2)
        self.teacher3 = AdviserTeacherFactory()
        self.teacher4 = AdviserTeacherFactory()
        a_person_student = PersonWithoutUserFactory(last_name="Durant")
        self.student = StudentFactory(person=a_person_student)
        self.offer1 = EducationGroupFactory()
        self.offer2 = EducationGroupFactory()
        self.academic_year1 = AcademicYearFactory()
        self.academic_year2 = AcademicYearFactory(year=self.academic_year1.year - 1)
        self.offer_year_start1 = EducationGroupYearFactory(acronym="test_offer1", education_group=self.offer1,
                                                           academic_year=self.academic_year1)
        self.offer_proposition1 = OfferPropositionFactory(education_group=self.offer1,
                                                          global_email_to_commission=True,
                                                          evaluation_first_year=True)
        self.offer_proposition2 = OfferPropositionFactory(education_group=self.offer2, global_email_to_commission=False)
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       creator=self.a_person_teacher,
                                                                       title='Proposition 1212121'
                                                                       )
        self.faculty_adviser1 = FacultyAdviserFactory(adviser=self.manager, education_group=self.offer1)
        self.faculty_adviser2 = FacultyAdviserFactory(adviser=self.manager, education_group=self.offer2)
        self.dissertation1 = DissertationFactory(author=self.student,
                                                 title='Dissertation_test_email',
                                                 education_group_year_start=self.offer_year_start1,
                                                 proposition_dissertation=self.proposition_dissertation,
                                                 status='DIR_SUBMIT',
                                                 active=True,
                                                 dissertation_role__adviser=self.teacher,
                                                 dissertation_role__status='PROMOTEUR'
                                                 )
        DissertationRoleFactory(adviser=self.teacher2, status='CO_PROMOTEUR', dissertation=self.dissertation1)
        DissertationRoleFactory(adviser=self.teacher3, status='READER', dissertation=self.dissertation1)

    def test_convert_none_to_empty_str(self):
        self.assertEqual(adviser.none_to_str(None), '')
        self.assertEqual(adviser.none_to_str('toto'), 'toto')
