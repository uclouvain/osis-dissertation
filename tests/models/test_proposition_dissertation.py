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
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_offer import PropositionOffer
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.models import test_proposition_role


def create_proposition_dissertation(title, adviser, person, offer_proposition = None, collaboration="FORBIDDEN", type="OTH",
                                    level="SPECIFIC", max_number_student=1 ):
    proposition = PropositionDissertation.objects.create(title=title, author= adviser,
                                                         collaboration=collaboration, type=type,
                                                         level=level, max_number_student=max_number_student,
                                                         creator=person)
    #Assign adviser as "PROMOTEUR"
    test_proposition_role.create_proposition_role(proposition=proposition, adviser=adviser)

    #Make link in many-to-many table
    if offer_proposition is not None:
        PropositionOffer.objects.create(proposition_dissertation=proposition, offer_proposition=offer_proposition)

    return proposition

def test_count_dissertations(self):
    self.client.force_login(self.manager.person.user)
    self.dissertation_test_count2015 = DissertationFactory(author=self.student1,
                                                           offer_year_start=self.offer_year_start2015,
                                                           proposition_dissertation=self.proposition_dissertation,
                                                           status='COM_SUBMIT',
                                                           active=True,
                                                           dissertation_role__adviser=self.teacher,
                                                           dissertation_role__status='PROMOTEUR')

    self.dissertation_test_count2017 = DissertationFactory(author=self.student2,
                                                           offer_year_start=self.offer_year_start2017,
                                                           proposition_dissertation=self.proposition_dissertation,
                                                           status='COM_SUBMIT',
                                                           active=True,
                                                           dissertation_role__adviser=self.teacher,
                                                           dissertation_role__status='PROMOTEUR')

    self.assertEqual(PropositionDissertation.count_dissertations(self.proposition_dissertation),1)