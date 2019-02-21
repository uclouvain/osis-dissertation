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
from django.core.exceptions import ValidationError
from django.test import TestCase

from dissertation.models.proposition_role import PropositionRole
from dissertation.tests.factories.adviser import AdviserTeacherFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_role import PropositionRoleFactory


def create_proposition_role(proposition, adviser, status="PROMOTEUR"):
   proposition_role = PropositionRole.objects.create(proposition_dissertation=proposition, adviser=adviser,
                                                     status=status)
   return proposition_role


class PropositionRoleModelTestCase(TestCase):
    def setUp(self):
        self.adviser = AdviserTeacherFactory()
        self.proposition_role = []
        self.proposition_dissertation = PropositionDissertationFactory()
        for x in range(0, 3):
            proposition_role = PropositionRoleFactory(proposition_dissertation=self.proposition_dissertation)
            self.proposition_role.append(proposition_role)

    def test_maximum_jury_reached_exception(self):
        with self.assertRaises(ValidationError):
            a = PropositionRoleFactory(proposition_dissertation=self.proposition_dissertation, adviser=self.adviser)
            a.clean()

