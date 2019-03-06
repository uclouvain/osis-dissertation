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
import django_filters
from django.db.models import Subquery, OuterRef
from django.utils.translation import gettext_lazy
from django.views.generic import ListView
from django_filters.views import FilterView

from base.forms.education_groups import EntityManagementModelChoiceField
from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.utils.cache import cache_filter
from dissertation.models.adviser import Adviser
from dissertation.models.faculty_adviser import FacultyAdviser
from dissertation.models.offer_proposition import OfferProposition


class EducationGroupModelChoiceFilter(django_filters.ModelChoiceFilter):
    field_class = EntityManagementModelChoiceField


class OfferPropositionFilterSet(django_filters.FilterSet):
    education_group__educationgroupyear = EducationGroupModelChoiceFilter(queryset=EducationGroupYear.objects.filter(
        academic_year=current_academic_year(), education_group__facultyadviser__isnull=False
    ).order_by('acronym'), label=gettext_lazy("Education Group"))
    education_group__facultyadviser__adviser = django_filters.ModelChoiceFilter(
        queryset=Adviser.objects.filter(type='MGR').select_related('person'), label=gettext_lazy("Faculty Adviser")
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        qs = self.filters['education_group__educationgroupyear'].queryset
        qs = qs.filter(management_entity__in=request.user.person.linked_entities).distinct()
        self.filters['education_group__educationgroupyear'].queryset = qs

    class Meta:
        model = OfferProposition
        fields = ('education_group__educationgroupyear', 'education_group__facultyadviser__adviser')


class OfferPropositionFilterView(FilterView):
    model = OfferProposition
    filterset_class = OfferPropositionFilterSet

    def get_queryset(self):
        person = self.request.user.person
        return super().get_queryset().filter(
            education_group__educationgroupyear__management_entity__in=person.linked_entities
        ).prefetch_related(
            'education_group__educationgroupyear_set', 'education_group__facultyadviser_set__adviser__person'
        ).annotate(
            last_acronym=Subquery(
                EducationGroupYear.objects.filter(
                    education_group__offer_proposition=OuterRef('pk'),
                    academic_year=current_academic_year()).values('acronym')[:1]
            )).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['managed_entities_acronym'] = self.request.user.person.managed_entities.annotate(
            acronym=Subquery(
                EntityVersion.objects.filter(
                    entity=OuterRef('pk')
                ).current(
                    current_academic_year().start_date
                ).values('acronym')[:1]
            )).values_list('acronym', flat=True)
        return context


class AdviserList(ListView):
    model = Adviser

    def get_queryset(self):
        qs = super().get_queryset()
        offer_propositions = self.request.GET.getlist('offer_proposition')
        if not offer_propositions:
            return qs.none()
        for op in offer_propositions:
            qs = qs.filter(education_groups__offer_proposition=op)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer_propositions'] = self.request.GET.getlist('offer_proposition')
        return context


