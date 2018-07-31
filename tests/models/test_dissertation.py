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
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory, PersonWithoutUserFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.offer import OfferFactory
from dissertation.tests.factories.adviser import AdviserTeacherFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from osis_common.models import message_history, message_template
from dissertation.tests.factories.dissertation import DissertationFactory

class DissertationModelTestCase(TestCase):
    fixtures = ['dissertation/fixtures/message_template.json', ]

    def setUp(self):
        a_person_teacher = PersonFactory.create(first_name='Pierre',
                                                last_name='Dupont',
                                                email='laurent.dermine@uclouvain.be')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student = PersonWithoutUserFactory.create(last_name="Durant",
                                                           email='laurent.dermine@uclouvain.be')
        self.student = StudentFactory.create(person=a_person_student)
        self.offer1 = OfferFactory(title="test_offer1")
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       creator=a_person_teacher)

        self.academic_year1 = AcademicYearFactory()

        self.offer_year_start1 = OfferYearFactory(acronym="test_offer1",
                                                  offer=self.offer1,
                                                  academic_year=self.academic_year1)
        self.dissertation_test_email = DissertationFactory(author=self.student,
                                                           title='Dissertation_test_email',
                                                           offer_year_start=self.offer_year_start1,
                                                           proposition_dissertation=self.proposition_dissertation,
                                                           status='DRAFT',
                                                           active=True,
                                                           dissertation_role__adviser=self.teacher,
                                                           dissertation_role__status='PROMOTEUR'
                                                           )

    def test_deactivate(self):
        self.dissertation = DissertationFactory(active=True)
        self.dissertation.deactivate()
        self.assertEqual(self.dissertation.active, False)

    def test_str(self):
        self.dissertation = DissertationFactory(title="dissert1")
        self.assertEqual(self.dissertation.title, str(self.dissertation))

    def test_set_status(self):
        self.dissertation = DissertationFactory(status='DRAFT')
        self.dissertation.set_status('DIR_SUBMIT')
        self.assertEqual(self.dissertation.status, 'DIR_SUBMIT')

    def test_go_forward_status(self):
        self.dissertation = DissertationFactory(status='DRAFT')
        self.dissertation.go_forward()
        self.dissertation.status = 'DIR_SUBMIT'
        self.dissertation = DissertationFactory(status='DIR_KO')
        self.dissertation.go_forward()
        self.dissertation.status = 'DIR_SUBMIT'
        self.dissertation = DissertationFactory(status='TO_RECEIVE')
        self.dissertation.go_forward()
        self.dissertation = DissertationFactory(status='TO_DEFEND')

    def test_go_forward_emails_acknowledge(self):
        self.dissertation_test_email.status = 'TO_RECEIVE'
        count_message_history_author = message_history. \
            find_my_messages(self.dissertation_test_email.author.person.id).count()
        self.dissertation_test_email.go_forward()
        message_history_result_author_after_change = message_history.find_my_messages(
            self.dissertation_test_email.author.person.id)
        count_message_history_result_author = len(message_history_result_author_after_change)
        self.assertEqual(count_message_history_author + 1, count_message_history_result_author)
        self.assertIn('bien été réceptionné', message_history_result_author_after_change.last().subject)

    def test_go_forward_emails_new_dissert_1(self):
        self.dissertation_test_email.status = 'DRAFT'
        count_messages_before_status_change = message_history.find_my_messages(self.teacher.person.id).count()
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_txt'))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_html'))
        self.assertIn('Vous avez reçu une demande d\'encadrement de mémoire', message_history_result.last().subject)

    def test_go_forward_emails_new_dissert_2(self):
        count_messages_before_status_change = message_history.find_my_messages(self.teacher.person.id).count()
        self.dissertation_test_email.status = 'DIR_KO'
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_txt'))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_html'))
        self.assertIn('Vous avez reçu une demande d\'encadrement de mémoire', message_history_result.last().subject)
