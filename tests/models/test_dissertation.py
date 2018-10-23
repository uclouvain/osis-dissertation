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
import datetime
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory, PersonWithoutUserFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.offer import OfferFactory
from dissertation.models import dissertation
from dissertation.tests.factories.adviser import AdviserTeacherFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from osis_common.models import message_history, message_template
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.models.enums import dissertation_status

NOW = datetime.datetime.now()


class DissertationModelTestCase(TestCase):
    fixtures = ['dissertation/fixtures/message_template.json', ]

    def setUp(self):
        a_person_teacher = PersonFactory.create(first_name='Pierre',
                                                last_name='Dupont',
                                                email='laurent.dermine@uclouvain.be')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student = PersonWithoutUserFactory.create(last_name="Durant", first_name='jean',
                                                           email='laurent@uclouvain.be')
        self.student = StudentFactory.create(person=a_person_student)
        self.offer1 = OfferFactory(title="test_offer1")
        self.offer_prop = OfferPropositionFactory(offer=self.offer1, acronym="test_offer1",
                                                  validation_commission_exists=True)
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       title='proposition_x',
                                                                       creator=a_person_teacher)

        self.academic_year1 = AcademicYearFactory()

        self.offer_year_start1 = OfferYearFactory(acronym="test_offer1",
                                                  offer=self.offer1,
                                                  academic_year=self.academic_year1)
        self.dissertation_test_email = DissertationFactory(author=self.student,
                                                           title='Dissertation_test_email',
                                                           offer_year_start=self.offer_year_start1,
                                                           proposition_dissertation=self.proposition_dissertation,
                                                           status=dissertation_status.DRAFT,
                                                           active=True,
                                                           dissertation_role__adviser=self.teacher,
                                                           dissertation_role__status='PROMOTEUR'
                                                           )
        self.dissertation = DissertationFactory(author=self.student,
                                                title='Dissertation_1',
                                                offer_year_start=self.offer_year_start1,
                                                proposition_dissertation=self.proposition_dissertation,
                                                status=dissertation_status.DIR_SUBMIT,
                                                active=True,
                                                description='les phobies',
                                                dissertation_role__adviser=self.teacher,
                                                dissertation_role__status='PROMOTEUR')

    def test_deactivate(self):
        self.dissertation = DissertationFactory(active=True)
        self.dissertation.deactivate()
        self.assertEqual(self.dissertation.active, False)

    def test_str(self):
        self.dissertation = DissertationFactory(title="dissert1")
        self.assertEqual(self.dissertation.title, str(self.dissertation))

    def test_set_status(self):
        self.dissertation = DissertationFactory(status=dissertation_status.DRAFT)
        self.dissertation.set_status(dissertation_status.DIR_SUBMIT)
        self.assertEqual(self.dissertation.status, dissertation_status.DIR_SUBMIT)

    def test_go_forward_status(self):
        self.dissertation = DissertationFactory(status=dissertation_status.DRAFT, active=True)
        self.dissertation.go_forward()
        self.assertEqual(dissertation_status.DIR_SUBMIT, self.dissertation.status)
        self.dissertation = DissertationFactory(status=dissertation_status.DIR_KO)
        self.dissertation.go_forward()
        self.assertEqual(dissertation_status.DIR_SUBMIT, self.dissertation.status)
        self.dissertation = DissertationFactory(status=dissertation_status.TO_RECEIVE)
        self.dissertation.go_forward()
        self.assertEqual(dissertation_status.TO_DEFEND, self.dissertation.status)

    def test_go_forward_emails_acknowledge(self):
        self.dissertation_test_email.status = dissertation_status.TO_RECEIVE
        count_message_history_author = message_history. \
            find_my_messages(self.dissertation_test_email.author.person.id).count()
        self.dissertation_test_email.go_forward()
        message_history_result_author_after_change = message_history.find_my_messages(
            self.dissertation_test_email.author.person.id)
        count_message_history_result_author = len(message_history_result_author_after_change)
        self.assertEqual(count_message_history_author + 1, count_message_history_result_author)
        self.assertIn('bien été réceptionné', message_history_result_author_after_change.last().subject)

    def test_go_forward_emails_new_dissert_1(self):
        self.dissertation_test_email.status = dissertation_status.DRAFT
        count_messages_before_status_change = message_history.find_my_messages(self.teacher.person.id).count()
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_txt'))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_html'))
        self.assertIn('Vous avez reçu une demande d\'encadrement de mémoire', message_history_result.last().subject)

    def test_go_forward_emails_new_dissert_2(self):
        count_messages_before_status_change = message_history.find_my_messages(self.teacher.person.id).count()
        self.dissertation_test_email.status = dissertation_status.DIR_KO
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_txt'))
        self.assertIsNotNone(message_template.find_by_reference('dissertation_adviser_new_project_dissertation_html'))
        self.assertIn('Vous avez reçu une demande d\'encadrement de mémoire', message_history_result.last().subject)

    def test_manager_accept_commission_exist(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                 offer_year_start=self.offer_year_start2)
        self.dissertation1.manager_accept()
        self.assertEqual(self.dissertation1.status, dissertation_status.COM_SUBMIT)

    def test_manager_accept_commission_exist_2(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=True,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.COM_KO,
                                                 offer_year_start=self.offer_year_start2)
        self.dissertation1.manager_accept()
        self.assertEqual(self.dissertation1.status, dissertation_status.EVA_SUBMIT)

    def test_manager_accept_not_commission_exist(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=False)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                 offer_year_start=self.offer_year_start2)
        self.dissertation1.manager_accept()
        self.assertEqual(self.dissertation1.status, dissertation_status.TO_RECEIVE)

    def test_manager_accept_not_commission_yes_eval(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                 offer_year_start=self.offer_year_start2)
        self.dissertation1.manager_accept()
        self.assertEqual(self.dissertation1.status, dissertation_status.EVA_SUBMIT)

    def test_manager_accept_eval_submit(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.EVA_SUBMIT,
                                                 offer_year_start=self.offer_year_start2)
        self.dissertation1.manager_accept()
        self.assertEqual(self.dissertation1.status, dissertation_status.TO_RECEIVE)

    def test_manager_accept_eval_KO(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.EVA_KO,
                                                 offer_year_start=self.offer_year_start2)
        self.dissertation1.manager_accept()
        self.assertEqual(self.dissertation1.status, dissertation_status.TO_RECEIVE)

    def test_teacher_accept_1(self):
        self.offer2 = OfferFactory()
        count_messages_before_status_change = message_history.find_my_messages(self.student.person.id).count()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=True,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                 offer_year_start=self.offer_year_start2,
                                                 author=self.student)
        self.dissertation1.teacher_accept()
        message_history_result = message_history.find_my_messages(self.student.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertEqual(self.dissertation1.status, dissertation_status.COM_SUBMIT)
        self.assertIn('Votre projet de mémoire est validé par votre promoteur', message_history_result.last().subject)

    def test_teacher_accept_2(self):
        self.dissertation1 = DissertationFactory(status=dissertation_status.DRAFT)
        self.assertEqual(self.dissertation1.teacher_accept(), None)

    def test_refuse_DIR_SUBMIT(self):
        self.offer2 = OfferFactory()
        count_messages_before_status_change = message_history.find_my_messages(self.student.person.id).count()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                 offer_year_start=self.offer_year_start2,
                                                 author=self.student)
        self.dissertation1.refuse()
        message_history_result = message_history.find_my_messages(self.student.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertEqual(self.dissertation1.status, dissertation_status.DIR_KO)
        self.assertIn('Votre projet de mémoire n\'a pas été validé par votre promoteur',
                      message_history_result.last().subject)

    def test_refuse_COM_SUBMIT(self):
        self.offer2 = OfferFactory()
        count_messages_before_status_change = message_history.find_my_messages(self.student.person.id).count()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=True,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.COM_SUBMIT,
                                                 offer_year_start=self.offer_year_start2,
                                                 author=self.student)
        self.dissertation1.refuse()
        message_history_result = message_history.find_my_messages(self.student.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertEqual(self.dissertation1.status, dissertation_status.COM_KO)
        self.assertIn('n\'a pas validé',
                      message_history_result.last().subject)

    def test_refuse_COM_SUBMIT_2(self):
        self.offer2 = OfferFactory()
        count_messages_before_status_change = message_history.find_my_messages(self.teacher.person.id).count()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=True,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation1 = DissertationFactory(status=dissertation_status.COM_SUBMIT,
                                                 offer_year_start=self.offer_year_start2,
                                                 author=self.student,
                                                 dissertation_role__adviser=self.teacher,
                                                 dissertation_role__status='PROMOTEUR'
                                                 )
        self.dissertation1.refuse()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertEqual(self.dissertation1.status, dissertation_status.COM_KO)
        self.assertIn('n\'a pas validé le projet de mémoire',
                      message_history_result.last().subject)

    def test_search_1(self):
        result = dissertation.search('Dissertation_1')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], self.dissertation)
        result = dissertation.search(dissertation_status.DIR_SUBMIT)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], self.dissertation)
        result = dissertation.search('jean')
        self.assertEqual(result.count(), 2)
        result = dissertation.search('Durant')
        self.assertEqual(result.count(), 2)
        result = dissertation.search('Pierre')
        self.assertEqual(result.count(), 2)

    def test_search_2(self):
        result = dissertation.search('les phobies')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], self.dissertation)
        result = dissertation.search('Dissertation_1')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], self.dissertation)
        result = dissertation.search('proposition_x')
        self.assertEqual(result.count(), 2)
        self.assertEqual(result[0], self.dissertation)
        result = dissertation.search('proposition_x')
        self.assertEqual(result.count(), 2)
        result = dissertation.search('test_offer1')
        self.assertEqual(result.count(), 2)

    def test_search_by_proposition_author(self):
        result = dissertation.search_by_proposition_author(None, True, self.teacher)
        self.assertEqual(result.count(), 2)

    def test_search_by_offer(self):
        result = dissertation.search_by_offer([self.offer1])
        self.assertEqual(result.count(), 2)

    def test_search_by_offer_and_status(self):
        result = dissertation.search_by_offer_and_status([self.offer1], dissertation_status.DIR_SUBMIT)
        self.assertEqual(result.count(), 1)
        self.assertEqual(result[0], self.dissertation)

    def test_get_next_status_goforward(self):
        self.dissertation_x = DissertationFactory(status=dissertation_status.DRAFT, active=True)
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "go_forward"),
                         dissertation_status.DIR_SUBMIT)
        self.dissertation_x.status = dissertation_status.DIR_KO
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "go_forward"),
                         dissertation_status.DIR_SUBMIT)
        self.dissertation_x.status = dissertation_status.TO_RECEIVE
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "go_forward"),
                         dissertation_status.TO_DEFEND)
        self.dissertation_x.status = dissertation_status.TO_DEFEND
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "go_forward"),
                         dissertation_status.DEFENDED)
        self.dissertation_x.status = dissertation_status.DIR_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "go_forward"),
                         dissertation_status.DIR_SUBMIT)

    def test_get_next_status_accept_1(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=True,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation_x = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                  offer_year_start=self.offer_year_start2)
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"),
                         dissertation_status.COM_SUBMIT)

    def test_get_next_status_accept_2(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation_x = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                  offer_year_start=self.offer_year_start2)
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"),
                         dissertation_status.EVA_SUBMIT)
        self.dissertation_x.status = dissertation_status.COM_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"),
                         dissertation_status.EVA_SUBMIT)
        self.dissertation_x.status = dissertation_status.COM_KO
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"),
                         dissertation_status.EVA_SUBMIT)

    def test_get_next_status_accept_3(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=True)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation_x = DissertationFactory(status=dissertation_status.EVA_SUBMIT,
                                                  offer_year_start=self.offer_year_start2)
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"),
                         dissertation_status.TO_RECEIVE)
        self.dissertation_x.status = dissertation_status.DEFENDED
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"), dissertation_status.ENDED_WIN)

        self.dissertation_x.status = dissertation_status.DIR_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"), dissertation_status.EVA_SUBMIT)

    def test_get_next_status_accept_4(self):
        self.offer2 = OfferFactory()
        self.offer_prop2 = OfferPropositionFactory(offer=self.offer2,
                                                   validation_commission_exists=False,
                                                   evaluation_first_year=False)
        self.offer_year_start2 = OfferYearFactory(offer=self.offer2,
                                                  academic_year=self.academic_year1)
        self.dissertation_x = DissertationFactory(status=dissertation_status.DIR_SUBMIT,
                                                  offer_year_start=self.offer_year_start2)
        self.dissertation_x.status = dissertation_status.DIR_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "accept"),
                         dissertation_status.TO_RECEIVE)
        self.dissertation_x.status = dissertation_status.DIR_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_x, "go"), dissertation_status.DIR_SUBMIT)

    def test_get_next_status_refuse(self):
        self.dissertation_a = DissertationFactory(status=dissertation_status.DIR_SUBMIT)
        self.assertEqual(dissertation.get_next_status(self.dissertation_a, "refuse"), dissertation_status.DIR_KO)
        self.dissertation_a.status = dissertation_status.COM_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_a, "refuse"), dissertation_status.COM_KO)
        self.dissertation_a.status = dissertation_status.EVA_SUBMIT
        self.assertEqual(dissertation.get_next_status(self.dissertation_a, "refuse"), dissertation_status.EVA_KO)
        self.dissertation_a.status = dissertation_status.DEFENDED
        self.assertEqual(dissertation.get_next_status(self.dissertation_a, "refuse"), dissertation_status.ENDED_LOS)
        self.dissertation_a.status = dissertation_status.DRAFT
        self.assertEqual(dissertation.get_next_status(self.dissertation_a, "refuse"), dissertation_status.DRAFT)
        self.dissertation_a.status = dissertation_status.TO_DEFEND
        self.assertEqual(dissertation.get_next_status(self.dissertation_a, "refuse"), dissertation_status.TO_DEFEND)

    def test_find_by_id(self):
        self.dissertation_a = DissertationFactory(id=666)
        result = dissertation.find_by_id(666)
        self.assertEqual(self.dissertation_a, result)
        result = dissertation.find_by_id(999)
        self.assertEqual(None, result)

    def test_count_by_proposition(self):
        self.proposition_dissertation_x = PropositionDissertationFactory()
        self.current_academic_yr = AcademicYearFactory(year=NOW.year,
                                                       start_date=datetime.datetime(NOW.year, NOW.month, 1),
                                                       end_date=datetime.datetime(NOW.year + 1, NOW.month, 28))
        self.dissertation_active = DissertationFactory(active=True,
                                                       status=dissertation_status.COM_SUBMIT,
                                                       proposition_dissertation=self.proposition_dissertation_x,
                                                       offer_year_start__academic_year=self.current_academic_yr)
        self.dissertation_false = DissertationFactory(active=False,
                                                      proposition_dissertation=self.proposition_dissertation_x)
        self.dissertation_active_draft = DissertationFactory(active=True,
                                                             status=dissertation_status.DRAFT,
                                                             proposition_dissertation=self.proposition_dissertation_x)
        self.dissertation_active_draft = DissertationFactory(active=True,
                                                             status=dissertation_status.DIR_KO,
                                                             proposition_dissertation=self.proposition_dissertation_x)
        self.assertEqual(dissertation.count_by_proposition(self.proposition_dissertation_x), 1)
