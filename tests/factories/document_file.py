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
import factory.fuzzy

from django.utils import timezone
from osis_common.models.enum import storage_duration


class DocumentFileFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'osis_common.DocumentFile'

    file_name = factory.Sequence(lambda n: "file %03d" % n)
    content_type = 'application/csv'
    creation_date = factory.Faker('date_time_this_year', before_now=True, after_now=False,
                                  tzinfo=timezone.get_current_timezone())
    storage_duration = storage_duration.FIVE_YEARS
    file = factory.django.FileField(filename='the_file.dat')
    description = factory.Sequence(lambda n: "Description %03d" % n)
    update_by = 'system'
    application_name = factory.Faker('text', max_nb_chars=100)
    size = factory.fuzzy.FuzzyInteger(45, 200)
