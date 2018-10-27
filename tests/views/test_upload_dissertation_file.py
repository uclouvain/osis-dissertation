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

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase

from dissertation.models import dissertation_document_file

from dissertation.tests.factories.adviser import AdviserManagerFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.dissertation_document_file import DissertationDocumentFileFactory


class UploadDissertationFileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdviserManagerFactory().person.user
        cls.dissertation = DissertationFactory()
        cls.document = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        cls.dissertation_document = DissertationDocumentFileFactory(dissertation=cls.dissertation)
        cls.download_url = reverse("dissertation_download", args=[cls.dissertation.pk])
        cls.upload_url = reverse("dissertation_save_upload")

    def setUp(self):
        self.client.force_login(self.user)

    def test_download_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.download_url)

        self.assertRedirects(response, "/login/?next={}".format(self.download_url))

    def test_download(self):
        self.client.force_login(self.user)
        response = self.client.get(self.download_url)

        self.assertEqual(response.status_code, HttpResponse.status_code)

    def test_download_dissertation_without_document(self):
        self.client.force_login(self.user)
        dissertation = DissertationFactory()
        response = self.client.get(reverse("dissertation_download", args=[dissertation.pk]))

        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_save_uploaded_file_when_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.upload_url)

        self.assertRedirects(response, "/login/?next={}".format(self.upload_url))

    def test_save_uploaded_file(self):
        self.client.force_login(self.user)
        form_data = {'file': self.document, 'dissertation_id': self.dissertation.id, 'description': 'description'}
        response = self.client.post(self.upload_url, form_data, follow=True)

        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(1, len(dissertation_document_file.find_by_dissertation(self.dissertation)))
