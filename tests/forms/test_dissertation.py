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
from django.test import TestCase

from dissertation.forms import ManagerDissertationEditForm
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.tests.factories.adviser import AdviserManagerFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.faculty_adviser import FacultyAdviserFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory


class DissertationFormsTestCase(TestCase):

    def setUp(self):
        self.manager = AdviserManagerFactory()
        self.proposition = PropositionDissertationFactory()
        self.dissertation = DissertationFactory(proposition_dissertation=self.proposition)
        self.proposition_offer = PropositionOfferFactory(
            proposition_dissertation=self.proposition
        )
        FacultyAdviserFactory(
            adviser=self.manager,
            education_group=self.proposition_offer.offer_proposition.education_group
        )

    def test_dissertation_manager_edit_form(self):
        form = ManagerDissertationEditForm(None, instance=self.dissertation, user=self.manager.person.user)
        self.assertCountEqual(
            form.fields['proposition_dissertation'].queryset,
            PropositionDissertation.objects.all()
        )
