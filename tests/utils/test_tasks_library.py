##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime

from coverage.backunittest import TestCase

from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.utils.tasks_library import offer_proposition_extend_dates, check_dates_of_offer_proposition, \
    incr_year, check_date_end


class UtilsTestCase(TestCase):
    def setUp(self):
        self.date_before_today = datetime.date(2017, 9, 1)
        self.date_end_before_today = datetime.date(2018, 9, 1)
        self.date_start_after_today = datetime.date(2099, 9, 1)
        self.date_end_after_today = datetime.date(2100, 9, 1)
        self.education_group_outdated = EducationGroupFactory()
        self.education_group_year_outdated = EducationGroupYearFactory \
            (education_group=self.education_group_outdated)

        self.education_group2_outdated = EducationGroupFactory()
        self.education_group2_year_outdated = EducationGroupYearFactory(
            education_group=self.education_group2_outdated)

        self.education_group_future_dates = EducationGroupFactory()
        self.education_group_year__future_dates = EducationGroupYearFactory(
            education_group=self.education_group_future_dates)

        self.offer_proposition_outdated = OfferPropositionFactory(
            start_visibility_proposition=self.date_before_today,
            end_visibility_proposition=self.date_end_before_today,
            start_visibility_dissertation=self.date_before_today,
            end_visibility_dissertation=self.date_end_before_today,
            start_jury_visibility=self.date_before_today,
            end_jury_visibility=self.date_end_before_today,
            start_edit_title=self.date_before_today,
            end_edit_title=self.date_end_before_today,
            education_group=self.education_group_outdated
        )
        self.offer_proposition2_outdated = OfferPropositionFactory(
            start_visibility_proposition=self.date_before_today,
            end_visibility_proposition=self.date_end_before_today,
            start_visibility_dissertation=self.date_before_today,
            end_visibility_dissertation=self.date_end_before_today,
            start_jury_visibility=self.date_before_today,
            end_jury_visibility=self.date_end_before_today,
            start_edit_title=self.date_before_today,
            end_edit_title=self.date_end_before_today,
            education_group=self.education_group2_outdated
        )
        self.offer_proposition_future_dates = OfferPropositionFactory(
            start_visibility_proposition=self.date_start_after_today,
            end_visibility_proposition=self.date_end_after_today,
            start_visibility_dissertation=self.date_start_after_today,
            end_visibility_dissertation=self.date_end_after_today,
            start_jury_visibility=self.date_start_after_today,
            end_jury_visibility=self.date_end_after_today,
            start_edit_title=self.date_start_after_today,
            end_edit_title=self.date_end_after_today,
            education_group=self.education_group_future_dates
        )

    def test_add_year_to_date(self):
        self.assertEqual(incr_year(self.date_before_today), self.date_end_before_today)

    def test_check_dates_of_offer_proposition(self):
        result = check_dates_of_offer_proposition(self.offer_proposition_outdated)
        self.assertIn(self.education_group_year_outdated.acronym, result)
        expected_start_year = incr_year(self.date_before_today)
        expected_end_year = incr_year(self.date_end_before_today)

        self.assertEqual(self.offer_proposition_outdated.start_visibility_proposition, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_visibility_proposition, expected_end_year)
        self.assertEqual(self.offer_proposition_outdated.start_visibility_dissertation, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_visibility_dissertation, expected_end_year)
        self.assertEqual(self.offer_proposition_outdated.start_jury_visibility, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_jury_visibility, expected_end_year)
        self.assertEqual(self.offer_proposition_outdated.start_edit_title, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_edit_title, expected_end_year)

    def test_check_date_end(self):
        expected_start_year = incr_year(self.date_before_today)
        expected_end_year = incr_year(self.date_end_before_today)
        check_date_end(self.offer_proposition_outdated, 'start_visibility_proposition', 'end_visibility_proposition')
        self.assertEqual(self.offer_proposition_outdated.start_visibility_proposition, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_visibility_proposition, expected_end_year)

    def test_offer_proposition_extend_dates(self):
        result = offer_proposition_extend_dates()
        self.assertIn(self.education_group_year_outdated.acronym, result)
        self.assertIn(self.education_group2_year_outdated.acronym, result)
        self.offer_proposition_outdated.refresh_from_db()
        expected_start_year = incr_year(self.date_before_today)
        expected_end_year = incr_year(self.date_end_before_today)

        self.assertEqual(self.offer_proposition_outdated.start_visibility_proposition, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_visibility_proposition, expected_end_year)
        self.assertEqual(self.offer_proposition_outdated.start_visibility_dissertation, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_visibility_dissertation, expected_end_year)
        self.assertEqual(self.offer_proposition_outdated.start_jury_visibility, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_jury_visibility, expected_end_year)
        self.assertEqual(self.offer_proposition_outdated.start_edit_title, expected_start_year)
        self.assertEqual(self.offer_proposition_outdated.end_edit_title, expected_end_year)

        self.offer_proposition2_outdated.refresh_from_db()
        self.assertEqual(self.offer_proposition2_outdated.start_visibility_proposition, expected_start_year)
        self.assertEqual(self.offer_proposition2_outdated.end_visibility_proposition, expected_end_year)
        self.assertEqual(self.offer_proposition2_outdated.start_visibility_dissertation, expected_start_year)
        self.assertEqual(self.offer_proposition2_outdated.end_visibility_dissertation, expected_end_year)
        self.assertEqual(self.offer_proposition2_outdated.start_jury_visibility, expected_start_year)
        self.assertEqual(self.offer_proposition2_outdated.end_jury_visibility, expected_end_year)
        self.assertEqual(self.offer_proposition2_outdated.start_edit_title, expected_start_year)
        self.assertEqual(self.offer_proposition2_outdated.end_edit_title, expected_end_year)

        self.offer_proposition_future_dates.refresh_from_db()
        self.assertEqual(self.offer_proposition_future_dates.start_visibility_proposition, self.date_start_after_today)
        self.assertEqual(self.offer_proposition_future_dates.end_visibility_proposition, self.date_end_after_today)
        self.assertEqual(self.offer_proposition_future_dates.start_visibility_dissertation, self.date_start_after_today)
        self.assertEqual(self.offer_proposition_future_dates.end_visibility_dissertation, self.date_end_after_today)
        self.assertEqual(self.offer_proposition_future_dates.start_jury_visibility, self.date_start_after_today)
        self.assertEqual(self.offer_proposition_future_dates.end_jury_visibility, self.date_end_after_today)
        self.assertEqual(self.offer_proposition_future_dates.start_edit_title, self.date_start_after_today)
        self.assertEqual(self.offer_proposition_future_dates.end_edit_title, self.date_end_after_today)
