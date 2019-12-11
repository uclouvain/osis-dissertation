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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from base.models.education_group_year import EducationGroupYear
from base.models.student import Student
from dissertation.models import adviser

MAX_RETURN = 50


@login_required
@user_passes_test(adviser.is_manager)
def get_students_list_in_education_group_year(request, education_group_year_id):
    education_group_year = get_object_or_404(EducationGroupYear, pk=education_group_year_id)
    students_list = Student.objects.filter(offerenrollment__education_group_year=education_group_year)
    data = []
    if students_list:
        for student in students_list:
            data.append({'person_id': student.id,
                         'first_name': student.person.first_name,
                         'last_name': student.person.last_name,
                         'registration_id': student.registration_id})

    else:
        data = False

    return JsonResponse({'res': data})


@login_required
@user_passes_test(adviser.is_manager)
def find_adviser_list_json(request):
    term_search = request.GET.get('term')
    advisers = adviser.find_advisers_last_name_email(term_search, MAX_RETURN)
    response_data = adviser.convert_advisers_to_array(advisers)
    return JsonResponse(response_data, safe=False)
