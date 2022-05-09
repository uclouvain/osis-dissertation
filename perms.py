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
from functools import wraps

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from base.models.education_group import EducationGroup
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.enums import dissertation_role_status
from dissertation.models.proposition_role import PropositionRole


def user_is_dissertation_promotor(user, dissert):
    this_adviser = user.person.adviser
    return DissertationRole.objects.filter(dissertation=dissert). \
        filter(status=dissertation_role_status.PROMOTEUR).filter(adviser=this_adviser).exists()


def user_is_proposition_promotor(user, prop_diss):
    return PropositionRole.objects.filter(
        proposition_dissertation=prop_diss,
        status=dissertation_role_status.PROMOTEUR,
        adviser__person__user=user).exists()


def adviser_can_manage(dissert, advis):
    return advis.facultyadviser_set.filter(
        education_group=dissert.education_group_year.education_group
    ).exists() and advis.type == 'MGR'


def adviser_can_manage_proposition_dissertation(prop_diss, advis):
    education_groups_prop_diss_pk = EducationGroup.objects.filter(
        offer_proposition__offer_propositions=prop_diss
    ).values_list('id', flat=True)
    return EducationGroup.objects.filter(facultyadviser__adviser=advis, pk__in=education_groups_prop_diss_pk).exists()


def adviser_is_in_jury(user, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    return DissertationRole.objects.filter(dissertation=dissert, adviser__person__user=user).count() > 0


def autorized_dissert_promotor_or_manager(user, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related('education_group_year__education_group').
                                prefetch_related('advisers'), pk=pk)
    if user.person.adviser:
        return user_is_dissertation_promotor(user, dissert) or \
               adviser_can_manage(dissert, user.person.adviser)
    else:
        return False


def autorized_proposition_dissert_promotor_or_manager_or_author(user, proposition_dissert):
    try:
        if user.person.adviser:
            advis = user.person.adviser
            return user_is_proposition_promotor(user, proposition_dissert) or \
                   adviser_can_manage_proposition_dissertation(proposition_dissert, advis) or \
                   proposition_dissert.author == advis
    except ObjectDoesNotExist:
        return False


def check_for_dissert(test_func):
    def f_check_for_dissert_or_redirect(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(return_user_with_adviser(request.user), kwargs['pk']):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden()
        return _wrapped_view

    return f_check_for_dissert_or_redirect


def return_user_with_adviser(user):
    return get_object_or_404(User.objects.select_related('person__adviser'), pk=user.pk)
