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

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase

from dissertation.tests.factories.adviser import AdviserManagerFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory


class OfferPropositionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdviserManagerFactory().person.user
        cls.offer_proposition = OfferPropositionFactory()
        cls.url = reverse("settings_by_education_group")

    def setUp(self):
        self.client.force_login(self.user)

    def test_settings_by_education_group_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_settings_by_education_group(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, "settings_by_education_group.html")
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_settings_by_education_group_edit_get(self):
        response = self.client.get(
            reverse("settings_by_education_group_edit", kwargs={'pk': self.offer_proposition.pk})
        )

        self.assertTemplateUsed(response, "settings_by_education_group_edit.html")
        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_settings_by_education_group_edit_post(self):
        form_data = {
            'offer': self.offer_proposition.offer_id,
            'acronym': self.offer_proposition.acronym,
            'education_group': self.offer_proposition.education_group_id,
            'start_visibility_proposition': self.offer_proposition.start_visibility_proposition,
            'end_visibility_proposition': self.offer_proposition.end_visibility_proposition,
            'start_visibility_dissertation': self.offer_proposition.start_visibility_dissertation,
            'end_visibility_dissertation': self.offer_proposition.end_visibility_dissertation,
            'start_jury_visibility': self.offer_proposition.start_jury_visibility,
            'end_jury_visibility': self.offer_proposition.end_jury_visibility,
            'start_edit_title': self.offer_proposition.start_edit_title,
            'end_edit_title': self.offer_proposition.end_edit_title,
            'student_can_manage_readers': not self.offer_proposition.student_can_manage_readers,
            'adviser_can_suggest_reader': not self.offer_proposition.adviser_can_suggest_reader,
            'evaluation_first_year': not self.offer_proposition.evaluation_first_year,
            'validation_commission_exists': False,
            'global_email_to_commission': False,
        }
        response = self.client.post(
            reverse(
                "settings_by_education_group_edit",
                kwargs={'pk': self.offer_proposition.pk}
            ),
            form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HttpResponse.status_code)

