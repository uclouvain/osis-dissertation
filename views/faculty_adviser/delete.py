# ##################################################################################################
#   OSIS stands for Open Student Information System. It's an application                           #
#   designed to manage the core business of higher education institutions,                         #
#   such as universities, faculties, institutes and professional schools.                          #
#   The core business involves the administration of students, teachers,                           #
#   courses, programs and so on.                                                                   #
#   Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)             #
#   This program is free software: you can redistribute it and/or modify                           #
#   it under the terms of the GNU General Public License as published by                           #
#   the Free Software Foundation, either version 3 of the License, or                              #
#   (at your option) any later version.                                                            #
#   This program is distributed in the hope that it will be useful,                                #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                 #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                  #
#   GNU General Public License for more details.                                                   #
#   A copy of this license - GNU General Public License - is available                             #
#   at the root of the source code of this program.  If not,                                       #
#   see http://www.gnu.org/licenses/.                                                              #
# ##################################################################################################
from django.db.models import Subquery, OuterRef
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.views.mixins import AjaxTemplateMixin
from dissertation.models.adviser import Adviser
from dissertation.models.faculty_adviser import FacultyAdviser
from dissertation.models.offer_proposition import OfferProposition


class FacultyAdviserDeleteView(AjaxTemplateMixin, DeleteView):
    model = FacultyAdviser
    success_url = reverse_lazy('adviser_list')
    template_name = 'dissertation/facultyadviser_confirm_delete_inner.html'
    partial_reload = '#tb_faculty_adviser'

    @property
    def offer_propositions(self) -> list:
        return self.request.GET['offer_proposition'].split(',')

    def get_success_url(self):
        url = super().get_success_url() + "?"
        for offer_prop in self.offer_propositions:
            url += "offer_proposition={}&".format(offer_prop)

        return url

    def get_object(self, queryset=None):
        return FacultyAdviser.objects.filter(
            adviser__pk=self.kwargs['pk'],
            education_group__offer_proposition__pk__in=self.offer_propositions
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        for obj in self.object.all():
            obj.delete()
        return self._ajax_response()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        adviser = Adviser.objects.get(pk=self.kwargs['pk'])
        context['adviser'] = adviser
        context['offer_propositions'] = OfferProposition.objects.filter(pk__in=self.offer_propositions).annotate(
            last_acronym=Subquery(
                EducationGroupYear.objects.filter(
                    education_group__offer_proposition=OuterRef('pk'),
                    academic_year=current_academic_year()).values('acronym')[:1]
            )).values_list('last_acronym', flat=True)
        context['other_offer_propositions'] = OfferProposition.objects.filter(education_group__advisers=adviser)\
            .exclude(pk__in=self.offer_propositions).annotate(
            last_acronym=Subquery(
                EducationGroupYear.objects.filter(
                    education_group__offer_proposition=OuterRef('pk'),
                    academic_year=current_academic_year()).values('acronym')[:1]
            )).values_list('last_acronym', flat=True)
        return context
