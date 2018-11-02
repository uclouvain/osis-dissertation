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

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from base.views import layout
from dissertation.forms import ManagerOfferPropositionForm
from dissertation.models import adviser
from dissertation.models import faculty_adviser
from dissertation.models import offer_proposition
from dissertation.views.utils.redirect_if_form_is_valid import redirect_if_form_is_valid


@login_required
@user_passes_test(adviser.is_manager)
def settings_by_education_group(request):
    education_group_ids = faculty_adviser.search_education_group_ids_by_user(request.user)
    offers_propositions = offer_proposition.get_by_education_group_ids(education_group_ids)

    return layout.render(request, 'settings_by_education_group.html', {'offer_propositions': offers_propositions})


@login_required
@user_passes_test(adviser.is_manager)
def settings_by_education_group_edit(request, pk):
    offer_prop = get_object_or_404(offer_proposition.OfferProposition, pk=pk)
    form = ManagerOfferPropositionForm(request.POST or None, instance=offer_prop)
    redirect_if_form_is_valid(form, 'settings_by_education_group')

    return layout.render(request, "settings_by_education_group_edit.html",
                         {'offer_proposition': offer_prop, 'form': form})
