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

from django.shortcuts import redirect, get_list_or_404, render
from django.contrib.auth.decorators import login_required

from base import models as mdl
from base.views.common import display_error_messages
from dissertation.models import adviser
from dissertation.models import faculty_adviser
from dissertation.models import offer_proposition
from dissertation.forms import ManagerOfferPropositionForm
from django.contrib.auth.decorators import user_passes_test

###########################
#      MANAGER VIEWS      #
###########################
from dissertation.models.offer_proposition import OfferProposition


@login_required
@user_passes_test(adviser.is_manager)
def manager_offer_parameters(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    return render(request, 'manager_offer_parameters.html', {'offer_propositions': offer_props})


@login_required
@user_passes_test(adviser.is_manager)
def manager_offer_parameters_edit(request):
    if not request.GET['pk']:
        return redirect('manager_offer_parameters')
    list_offer_prop = get_list_or_404(OfferProposition, pk__in=request.GET.getlist('pk'))
    list_form_valid = []
    forms = []
    for offer_prop in list_offer_prop:
        form = ManagerOfferPropositionForm(request.POST or None, instance=offer_prop)
        forms.append(form)
        list_form_valid.append(form.is_valid())
        if form.errors:
            errors = form.non_field_errors().as_ul()
            display_error_messages(request, errors, extra_tags='safe')

    if all(list_form_valid):
        for form in forms:
            form.save()
        return redirect('manager_offer_parameters')
    return render(request, "manager_offer_parameters_edit.html", {
        'list_offer_proposition': list_offer_prop,
        'form': forms[0]
    })