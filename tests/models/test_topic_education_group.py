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
from django.test import TestCase

from dissertation.tests.factories.topic_education_group import TopicEducationGroupFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory


class TestTopicEducationGroupFactory(TestCase):

    def setUp(self):

        self.education_group = EducationGroupFactory()
        self.education_group_year = EducationGroupYearFactory(education_group=self.education_group)
        self.topic_education_group = TopicEducationGroupFactory(education_group=self.education_group)

    def test_str_self(self):
        self.assertEqual(self.topic_education_group.name, u"%s - %s" % (
            self.topic_education_group.proposition_dissertation.title,
            self.topic_education_group.education_group.most_recent_acronym
        ))
