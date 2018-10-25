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

from django.core.urlresolvers import reverse
from django.test import TestCase
from dissertation.tests.factories.adviser import AdviserManagerFactory


HTTP_OK = 200
HTTP_ERROR_403_NOT_AUTORIZED = 403
HTTP_ERROR_404_PAGE_NO_FOUND = 404
HTTP_ERROR_405_BAD_REQUEST = 405


class UrlTestCase(TestCase):
    def setUp(self):
        self.manager = AdviserManagerFactory()

    def test_settings_by_education_group_url(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.get(reverse('settings_by_education_group'), {})
        self.assertEqual(response.status_code, HTTP_OK)
