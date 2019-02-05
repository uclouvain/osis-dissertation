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
from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.decorators import available_attrs

from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.enums import dissertation_role_status


def user_is_dissertation_promotor(user, dissert):
    this_adviser = user.person.adviser
    return DissertationRole.objects.filter(dissertation=dissert). \
        filter(status=dissertation_role_status.PROMOTEUR).filter(adviser=this_adviser).exists()


def adviser_can_manage(dissert, advis):
   return advis.facultyadviser_set.filter(
       education_group=dissert.education_group_year_start.education_group
   ).exists() and advis.type == 'MGR'


def adviser_is_in_jury(user, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    if user.person.adviser:
        return DissertationRole.objects.filter(dissertation=dissert).filter(user.person.adviser).count() > 0
    else:
        return False


def autorized_dissert_promotor_or_manager(user, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related('education_group_year_start__education_group').
                                prefetch_related('advisers'), pk=pk)
    if user.person.adviser:
        return user_is_dissertation_promotor(user, dissert) or adviser_can_manage(dissert, user.person.adviser)
    else:
        return False


def check_for_dissert(test_func):
    def f_check_for_dissert_or_redirect(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user, kwargs['pk']):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        return _wrapped_view

    return f_check_for_dissert_or_redirect
