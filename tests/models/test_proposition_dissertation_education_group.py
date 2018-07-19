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
import factory
from django.test import TestCase

from assistant.tests.factories.assistant_mandate import AssistantMandateFactory
from assistant.tests.factories import review
from assistant.models.enums import assistant_mandate_state
from assistant.models.enums import review_status
from assistant.models.review import find_by_reviewer_for_mandate
from assistant.models.review import get_in_progress_for_mandate

class TestReviewFactory(TestCase):

    def setUp(self):

        self.mandate = AssistantMandateFactory(state=assistant_mandate_state.RESEARCH)
        self.review = review.ReviewFactory(status=review_status.DONE, mandate=self.mandate)

    def test_review_by_reviewer_for_mandate(self):
        self.assertEqual(self.review, find_by_reviewer_for_mandate(self.review.reviewer, self.review.mandate))

    def test_find_in_progress_for_mandate(self):
        self.assertFalse(get_in_progress_for_mandate(self.review.mandate))
        self.review.status = review_status.IN_PROGRESS
        self.review.save()
        self.assertEqual(get_in_progress_for_mandate(self.review.mandate), self.review)
        self.review.delete()
        self.mandate.state = assistant_mandate_state.TRTS
        self.assertFalse(get_in_progress_for_mandate(self.review.mandate))


