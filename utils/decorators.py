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
from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from rest_framework.exceptions import PermissionDenied
from base import models as mdl
from base.models import person
from dissertation.models import dissertation_role, dissertation, adviser
from dissertation.models.adviser import search_by_person
from dissertation.models.enums import status_types


def user_is_dissertation_promotor(user, dissert):
    pers = person.find_by_user(user)
    this_adviser = search_by_person(pers)
    return dissertation_role._find_by_dissertation(dissert).\
        filter(status=status_types.PROMOTEUR).filter(adviser=this_adviser).exists()


def autorized_dissert_promotor_or_manager(user, pk, template_redirect='dissertations'):
    from dissertation.views.dissertation import adviser_can_manage
    dissert = dissertation.find_by_id(pk)
    perso = mdl.person.find_by_user(user)
    advis = adviser.search_by_person(perso)
    if template_redirect is None:
        template_redirect = 'dissertations'
    if dissert is None:
        return redirect(template_redirect)
    elif user_is_dissertation_promotor(user, dissert) or adviser_can_manage(dissert, advis):
        return True
    else:
        return False


def check_for_dissert_or_redirect(test_func, template_redirect=None):
    def f_check_for_dissert_or_redirect(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user, kwargs['pk'], template_redirect):
                return view_func(request, *args, **kwargs)
            else:
                return template_none_denied_or_redirect(template_redirect)
        return _wrapped_view
    return f_check_for_dissert_or_redirect


def template_none_denied_or_redirect(template):
    if template is None:
        raise PermissionDenied()
    else:
        return redirect(template)
