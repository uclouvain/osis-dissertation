# ##############################################################################
#   OSIS stands for Open Student Information System. It's an application
#   designed to manage the core business of higher education institutions,
#   such as universities, faculties, institutes and professional schools.
#   The core business involves the administration of students, teachers,
#   courses, programs and so on.
#
#   Copyright (C) 2015- 2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   A copy of this license - GNU General Public License - is available
#   at the root of the source code of this program.  If not,
#   see http://www.gnu.org/licenses/.
# ##############################################################################
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from dissertation.tests.factories.adviser import AdviserManagerFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.dissertation_document_file import DissertationDocumentFileFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory


class TestDissertationDocumentFileView(TestCase):

    def setUp(self):

        self.manager = AdviserManagerFactory()
        self.education_group = EducationGroupFactory()
        self.academic_year = create_current_academic_year()
        self.education_group_year = EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.faculty_adviser = FacultyAdviserFactory(adviser=self.manager, education_group=self.education_group)
        self.dissertation = DissertationFactory(education_group_year_start=self.education_group_year)
        self.dissertation_document = DissertationDocumentFileFactory(dissertation=self.dissertation)

    def test_DeleteDissertationFileView(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.post(
            reverse('dissertation_file_delete', args=[self.dissertation.pk])
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
