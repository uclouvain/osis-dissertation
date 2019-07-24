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
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.test import TestCase

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory, PersonWithoutUserFactory
from base.tests.factories.student import StudentFactory
from dissertation.forms import AdviserForm, ManagerAddAdviserPerson, ManagerAddAdviserForm, \
    AddAdviserForm
from dissertation.models import dissertation_role
from dissertation.models.enums import dissertation_role_status, dissertation_status
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory


class InformationTeacherViewTestCase(TestCase):

    def setUp(self):
        self.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory(first_name='Pierre', last_name='Dupont')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        self.person = PersonFactory()
        self.manager2 = AdviserManagerFactory()
        self.client.force_login(self.teacher.person.user)

    def test_informations(self):
        response = self.client.post(reverse('informations'),
                                    {
                                        'adviser': self.teacher,
                                        'first_name': self.teacher.person.first_name.title(),
                                        'last_name': self.teacher.person.last_name.title()
                                    }
                                    )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_detail_stats(self):
        advisers_pro = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.PROMOTEUR)
        advisers_copro = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.CO_PROMOTEUR)
        advisers_reader = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.READER)
        response = self.client.post(reverse('informations_detail_stats'),
                                    {
                                        'adviser': self.teacher,
                                        'count_advisers_copro': dissertation_role.count_by_adviser_and_role_stats(self.teacher, dissertation_role_status.CO_PROMOTEUR),
                                        'count_advisers_pro': dissertation_role.count_by_adviser_and_role_stats(self.teacher, dissertation_role_status.PROMOTEUR),
                                        'count_advisers_reader': dissertation_role.count_by_adviser_and_role_stats(self.teacher, dissertation_role_status.READER),
                                        'count_advisers_pro_request': dissertation_role.count_by_adviser(self.teacher, dissertation_role_status.PROMOTEUR, 'DIR_SUBMIT'),
                                        'tab_offer_count_pro': dissertation_role.get_tab_count_role_by_education_group(advisers_pro),
                                        'tab_offer_count_read': dissertation_role.get_tab_count_role_by_education_group(advisers_reader),
                                        'tab_offer_count_copro': dissertation_role.get_tab_count_role_by_education_group(advisers_copro)
                                    }
                                    )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_edit(self):
        form = AdviserForm()
        response = self.client.post(reverse('informations_edit'),
                                    {
                                        'form': form,
                                        'first_name': self.teacher.person.first_name.title(),
                                        'last_name': self.teacher.person.last_name.title(),
                                        'email': self.teacher.person.email,
                                        'phone': self.teacher.person.phone,
                                        'phone_mobile': self.teacher.person.phone_mobile
                                    }
                                    )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        response = self.client.get(reverse('informations_edit'),
                                    {
                                        'form': form,
                                        'first_name': self.teacher.person.first_name.title(),
                                        'last_name': self.teacher.person.last_name.title(),
                                        'email': self.teacher.person.email,
                                        'phone': self.teacher.person.phone,
                                        'phone_mobile': self.teacher.person.phone_mobile
                                    }
                                    )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_add(self):
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'search_form': self.person.email,
                                        'email': self.person.email
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_add_without_email(self):
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'search_form': self.person.email
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_add_with_already_adviser(self):
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'search_form': self.manager2.person.email,
                                        'email': self.manager2.person.email
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_add_with_invalid_person(self):
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'search_form': "bobo.hibou@uclouvain.be",
                                        'email': "bobo.hibou@uclouvain.be"
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_add_with_invalid_email(self):
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'search_form': "fake_email",
                                        'email': "fake_email"
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_informations_add_without_search_form(self):
        form = AddAdviserForm()
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'email': self.person.email,
                                        'form': form,
                                        'person': self.person.id
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)
        response = self.client.post(reverse("informations_add"),
                                    {
                                        'email': self.person.email,
                                    })
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_informations_add_with_get_method(self):
        response = self.client.get(reverse("informations_add"))
        self.assertEqual(response.status_code, HttpResponse.status_code)


class InformationManagerViewTestCase(TestCase):
    def setUp(self):
        self.manager = AdviserManagerFactory()
        self.client.force_login(self.manager.person.user)
        a_person_teacher = PersonFactory(first_name='Pierre', last_name='Dupont')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        self.person = PersonFactory()
        self.manager2 = AdviserManagerFactory()
        a_person_student = PersonWithoutUserFactory(last_name="Durant")
        student = StudentFactory(person=a_person_student)
        offer_year_start = OfferYearFactory(acronym="test_offer")
        offer = offer_year_start.offer
        offer_proposition = OfferPropositionFactory(offer=offer)
        self.education_group_year = EducationGroupYearFactory(education_group=offer_proposition.education_group)
        FacultyAdviserFactory(adviser=self.manager, offer=offer,
                              education_group=self.education_group_year.education_group)
        roles = [dissertation_role_status.PROMOTEUR, dissertation_role_status.CO_PROMOTEUR, dissertation_role_status.READER, dissertation_role_status.PROMOTEUR, dissertation_role_status.ACCOMPANIST, dissertation_role_status.PRESIDENT]
        status = [dissertation_status.DRAFT, dissertation_status.COM_SUBMIT, dissertation_status.EVA_SUBMIT, dissertation_status.TO_RECEIVE, dissertation_status.DIR_SUBMIT, dissertation_status.DIR_SUBMIT]
        for x in range(0, 6):
            proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                      creator=a_person_teacher,
                                                                      title='Proposition {}'.format(x)
                                                                      )
            PropositionOfferFactory(proposition_dissertation=proposition_dissertation,
                                    offer_proposition=offer_proposition)

            DissertationFactory(author=student,
                                title='Dissertation {}'.format(x),
                                offer_year_start=offer_year_start,
                                education_group_year_start=self.education_group_year,
                                proposition_dissertation=proposition_dissertation,
                                status=status[x],
                                active=True,
                                dissertation_role__adviser=self.teacher,
                                dissertation_role__status=roles[x]
                                )

    def test_manager_informations(self):
        response = self.client.get(reverse("manager_informations"))
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add(self):
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'search_form': self.person.email,
                                        'email': self.person.email
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_without_email(self):
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'search_form': self.person.email
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_with_already_adviser(self):
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'search_form': self.manager2.person.email,
                                        'email': self.manager2.person.email
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_with_invalid_person(self):
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'search_form': "bobo.hibou@uclouvain.be",
                                        'email': "bobo.hibou@uclouvain.be"
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_with_invalid_email(self):
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'search_form': "fake_email",
                                        'email': "fake_email"
                                    })
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_without_search_form(self):
        form = ManagerAddAdviserForm()
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'email': self.person.email,
                                        'form': form,
                                        'person': self.person.id
                                    })
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        response = self.client.post(reverse("manager_informations_add"),
                                    {
                                        'email': self.person.email,
                                    })
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_manager_informations_add_with_get_method(self):
        response = self.client.get(reverse("manager_informations_add"))
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_person(self):
        form = {
                   'email': self.person.email,
                   'last_name': self.person.last_name,
                   'first_name': self.person.first_name,
                   'phone': self.person.phone,
                   'phone_mobile': self.person.phone
               }
        response = self.client.post(reverse("manager_informations_add_person"), form)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_manager_informations_add_person_with_invalid_data(self):
        form = {
                   'email': self.person.email,
                   'last_name': self.person.last_name,
               }
        response = self.client.post(reverse("manager_informations_add_person"), form)
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_person_with_get_method(self):
        form = {
                   'email': self.person.email,
                   'last_name': self.person.last_name,
                   'first_name': self.person.first_name,
                   'phone': self.person.phone,
                   'phone_mobile': self.person.phone
               }
        response = self.client.get(reverse("manager_informations_add_person"), form)
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_add_person_with_invalid_form(self):
        data = { 'email': "fake_email" }
        form = ManagerAddAdviserPerson(data)
        self.assertFalse(form.is_valid())
        response = self.client.post(reverse("manager_informations_add_person"), data)
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_detail(self):
        response = self.client.get(reverse("manager_informations_detail", args=[self.teacher.pk]))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        response = self.client.get(reverse("manager_informations_detail", args=[self.teacher.person.user.pk]))
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_manager_informations_edit(self):
        response = self.client.get(reverse("manager_informations_edit", args=[self.teacher.person.user.pk]))
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        form = AdviserForm(instance=self.teacher.person.user)
        response = self.client.post(reverse("manager_informations_edit", args=[self.teacher.pk]),
                                    {
                                        'form': form,
                                    })
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_manager_informations_list_request(self):
        response = self.client.post(reverse("manager_informations_list_request"))
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_edit_with_get_method(self):
        response = self.client.get(reverse("manager_informations_edit", args=[self.teacher.pk]))
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_detail_list(self):
        url = reverse('manager_informations_detail_list', kwargs={'pk': self.teacher.id})
        response = self.client.get(url)
        self.assertEqual(response.context[-1].get('adv_list_disserts_pro').count(), 1) # only 1 because 1st is DRAFT
        self.assertEqual(response.context[-1].get('adv_list_disserts_copro').count(), 1)
        self.assertEqual(response.context[-1].get('adv_list_disserts_reader').count(), 1)
        self.assertEqual(response.context[-1].get('adv_list_disserts_accompanist').count(), 1)
        self.assertEqual(response.context[-1].get('adv_list_disserts_president').count(), 1)
        response = self.client.get(reverse("manager_informations_detail_list", args=[self.teacher.person.user.pk]))
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_manager_informations_detail_list_wait(self):
        response = self.client.get(reverse("manager_informations_detail_list_wait", args=[self.teacher.pk]))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        response = self.client.get(reverse("manager_informations_detail_list_wait", args=[self.teacher.person.user.pk]))
        self.assertEqual(response.status_code, HttpResponseNotFound.status_code)

    def test_manager_informations_detail_stats(self):
        advisers_pro = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.PROMOTEUR)
        advisers_copro = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.CO_PROMOTEUR)
        advisers_reader = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.READER)
        response = self.client.post(reverse('manager_informations_detail_stats', args=[self.teacher.pk]),
                                    {
                                        'adviser': self.teacher,
                                        'count_advisers_copro': dissertation_role.count_by_adviser_and_role_stats(
                                            self.teacher, dissertation_role_status.CO_PROMOTEUR),
                                        'count_advisers_pro': dissertation_role.count_by_adviser_and_role_stats(
                                            self.teacher, dissertation_role_status.PROMOTEUR),
                                        'count_advisers_reader': dissertation_role.count_by_adviser_and_role_stats(
                                            self.teacher, dissertation_role_status.READER),
                                        'count_advisers_pro_request': dissertation_role.count_by_adviser(self.teacher,
                                                                                                         dissertation_role_status.PROMOTEUR,
                                                                                                         'DIR_SUBMIT'),
                                        'tab_offer_count_pro': dissertation_role.get_tab_count_role_by_education_group(
                                            advisers_pro),
                                        'tab_offer_count_read': dissertation_role.get_tab_count_role_by_education_group(
                                            advisers_reader),
                                        'tab_offer_count_copro': dissertation_role.get_tab_count_role_by_education_group(
                                            advisers_copro)
                                    }
                                    )
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_manager_informations_detail_stats_without_teacher(self):
        advisers_pro = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.PROMOTEUR)
        advisers_copro = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.CO_PROMOTEUR)
        advisers_reader = dissertation_role.search_by_adviser_and_role_stats(self.teacher, dissertation_role_status.READER)
        response = self.client.post(reverse('manager_informations_detail_stats', args=[self.manager.person.user.pk]),
                                    {
                                        'adviser': self.teacher,
                                        'count_advisers_copro': dissertation_role.count_by_adviser_and_role_stats(
                                            self.teacher, dissertation_role_status.CO_PROMOTEUR),
                                        'count_advisers_pro': dissertation_role.count_by_adviser_and_role_stats(
                                            self.teacher, dissertation_role_status.PROMOTEUR),
                                        'count_advisers_reader': dissertation_role.count_by_adviser_and_role_stats(
                                            self.teacher, dissertation_role_status.READER),
                                        'count_advisers_pro_request': dissertation_role.count_by_adviser(self.teacher,
                                                                                                         dissertation_role_status.PROMOTEUR,
                                                                                                         'DIR_SUBMIT'),
                                        'tab_offer_count_pro': dissertation_role.get_tab_count_role_by_education_group(
                                            advisers_pro),
                                        'tab_offer_count_read': dissertation_role.get_tab_count_role_by_education_group(
                                            advisers_reader),
                                        'tab_offer_count_copro': dissertation_role.get_tab_count_role_by_education_group(
                                            advisers_copro)
                                    }
                                    )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)