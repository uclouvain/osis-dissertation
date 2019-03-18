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

from django.test import TestCase

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.offer_year import OfferYearFactory
from dissertation.migrations.utils.clean_db_with_no_educ_group import clean_db_with_no_educationgroup_match
from dissertation.models.proposition_offer import PropositionOffer
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.tests.factories.proposition_offer import PropositionOfferFactory


class DissertationUtilsTestCase(TestCase):
    def test_clean_db_with_no_educationgroup_match(self):
        self.last_ac_year = create_current_academic_year()
        self.last_ac_year.year = self.last_ac_year.year-1
        self.ac_year = create_current_academic_year()

        self.offer_FOPA2M = OfferFactory()
        self.offeryear_FOPA2M = OfferYearFactory(acronym='FOPA2M')
        self.education_group_FOPA2M = EducationGroupFactory()
        EducationGroupYearFactory(acronym='FOPA2M', academic_year=self.last_ac_year)
        self.education_group_year_FOPA2M = EducationGroupYearFactory(acronym='FOPA2M', academic_year=self.ac_year)
        self.offer_proposition_FOPA2M = OfferPropositionFactory(acronym='FOPA2M',
                                                                offer=self.offer_FOPA2M,
                                                                education_group=None,
                                                                )
        self.offer_FOPA2MA = OfferFactory()
        self.offeryear_FOPA2MA = OfferYearFactory(acronym='FOPA2MA')
        self.education_group_FOPA2MA = EducationGroupFactory()
        EducationGroupYearFactory(acronym='FOPA2MA', academic_year=self.last_ac_year)
        self.education_group_year_FOPA2MA = EducationGroupYearFactory(acronym='FOPA2MA', academic_year=self.ac_year)
        self.offer_proposition_FOPA2MA = OfferPropositionFactory(acronym='FOPA2MA',
                                                                 offer=self.offer_FOPA2MA,
                                                                 education_group=self.education_group_FOPA2MA)
        # self.offer_FOPA2MS = OfferFactory()
        # self.offeryear_FOPA2MS = OfferYearFactory(acronym='FOPA2MS')
        # EducationGroupYearFactory(acronym='FOPA2MS', academic_year=self.last_ac_year)
        # self.education_group_year_FOPA2MS = EducationGroupYearFactory(acronym='FOPA2MS', academic_year=self.ac_year)
        # self.offer_proposition_FOPA2MS = OfferPropositionFactory(acronym='FOPA2MS',
        #                                                          offer=self.offer_FOPA2MS,
        #                                                          education_group=None)
        # self.offer_FOPA2MSG = OfferFactory()
        #
        # self.offeryear_FOPA2MSG = OfferYearFactory(acronym='FOPA2MS/G', academic_year=self.ac_year)
        # self.education_group_FOPA2MSG = EducationGroupFactory()
        # EducationGroupYearFactory(acronym='FOPA2MS/G', academic_year=self.last_ac_year)
        # self.education_group_year_FOPA2MSG = EducationGroupYearFactory(acronym='FOPA2MS/G', academic_year=self.ac_year)
        # self.offer_proposition_FOPA2MSG = OfferPropositionFactory(acronym='FOPA2MSG',
        #                                                           offer=self.offer_FOPA2MSG,
        #                                                           education_group=self.education_group_FOPA2MSG)

        # self.offer_ANTR2M = OfferFactory()
        # self.offeryear_ANTR2M = OfferYearFactory(acronym='ANTR2M')
        # self.education_group_ANTR2M = EducationGroupFactory()
        # self.education_group_year_ANTR2M = EducationGroupYearFactory(acronym='ANTR2M', academic_year=self.ac_year)
        # self.offer_proposition_ANTR2M = OfferPropositionFactory(acronym='ANTR2M',
        #                                                         offer=self.offer_ANTR2M,
        #                                                         education_group=None,
        #                                                         global_email_to_commission=True)
        # self.offer_ANTR2MA = OfferFactory()
        # self.offeryear_ANTR2MA = OfferYearFactory(acronym='ANTR2MA')
        # self.education_group_ANTR2MA = EducationGroupFactory()
        # self.education_group_year_ANTR2MA = EducationGroupYearFactory(acronym='ANTR2MA', academic_year=self.ac_year)
        # self.offer_proposition_ANTR2MA = OfferPropositionFactory(acronym='ANTR2MA',
        #                                                          offer=self.offer_ANTR2MA,
        #                                                          education_group=self.education_group_ANTR2MA)
        # self.offer_ANTR2MB = OfferFactory()
        # self.offeryear_ANTR2MB = OfferYearFactory(acronym='ANTR2MB')
        # self.education_group_ANTR2MB = EducationGroupFactory()
        # self.education_group_year_ANTR2MB = EducationGroupYearFactory(acronym='ANTR2MB', academic_year=self.ac_year)
        # self.offer_proposition_ANTR2MB = OfferPropositionFactory(acronym='ANTR2MB',
        #                                                          offer=self.offer_ANTR2MB,
        #                                                          education_group=self.education_group_ANTR2MB)
        # self.offer_ANTR2MS = OfferFactory()
        # self.offeryear_ANTR2MS = OfferYearFactory(acronym='ANTR2MS')
        # self.education_group_year_ANTR2MS = EducationGroupYearFactory(acronym='ANTR2MS', academic_year=self.ac_year)
        # self.offer_proposition_ANTR2MS = OfferPropositionFactory(acronym='ANTR2MS',
        #                                                          offer=self.offer_ANTR2MS,
        #                                                          education_group=None)
        # self.offer_ANTR2MSID = OfferFactory()
        # self.offeryear_ANTR2MSID = OfferYearFactory(acronym='ANTR2MS/ID')
        # self.education_group_ANTR2MSID = EducationGroupFactory()
        # self.education_group_year_ANTR2MSID = EducationGroupYearFactory(acronym='ANTR2MS/ID',
        #                                                                 academic_year=self.ac_year)
        # self.offer_proposition_ANTR2MSID = OfferPropositionFactory(acronym='ANTR2MSID',
        #                                                            offer=self.offer_ANTR2MSID,
        #                                                            education_group=self.education_group_ANTR2MSID)

        self.sujet_sans_enfant_1 = PropositionDissertationFactory(title='sujet_sans_enfant_1')
        PropositionOfferFactory(proposition_dissertation=self.sujet_sans_enfant_1,
                                offer_proposition=self.offer_proposition_FOPA2M)

        # self.sujet_sans_enfant_2 = PropositionDissertationFactory(title='sujet_sans_enfant_2')
        # PropositionOfferFactory(proposition_dissertation=self.sujet_sans_enfant_2,
        #                         offer_proposition=self.offer_proposition_FOPA2M)
        # PropositionOfferFactory(proposition_dissertation=self.sujet_sans_enfant_2,
        #                         offer_proposition=self.offer_proposition_FOPA2MS)
        #
        # self.sujet_avec_enfant_1 = PropositionDissertationFactory(title='sujet_avec_enfant_3')
        # PropositionOfferFactory(proposition_dissertation=self.sujet_avec_enfant_1,
        #                         offer_proposition=self.offer_proposition_ANTR2MSID)
        #
        # PropositionOfferFactory(proposition_dissertation=self.sujet_sans_enfant_3,
        #                         offer_proposition=self.offer_proposition_ANTR2MS)
        clean_db_with_no_educationgroup_match()
        prop_offers_sujet_1 = PropositionOffer.object.get(proposition_dissertation=self.sujet_sans_enfant_1)
        # prop_offers_sujet_2 = PropositionOffer.object.get(proposition_dissertation=self.sujet_sans_enfant_2)
        # prop_offers_sujet_3 = PropositionOffer.object.get(proposition_dissertation=self.sujet_avec_enfant_1)
        self.assertIn(self.offer_proposition_FOPA2M, prop_offers_sujet_1)
        self.assertIn(self.offer_proposition_FOPA2MSG, prop_offers_sujet_1)

