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

from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_document_file import PropositionDocumentFileFactory


class TestPropositionDocumentFileView(TestCase):

    def setUp(self):

        self.manager = AdviserManagerFactory()
        self.teacher1 = AdviserTeacherFactory()
        self.teacher2 = AdviserTeacherFactory()
        self.proposition = PropositionDissertationFactory(author=self.teacher1)
        self.proposition_document = PropositionDocumentFileFactory(proposition=self.proposition)

    def test_DeletePropositionFileView(self):
        self.client.force_login(self.teacher1.person.user)
        response = self.client.post(
            reverse('proposition_file_delete', args=[self.proposition.pk])
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
