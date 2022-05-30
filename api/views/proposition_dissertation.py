##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.db import models
from django.db.models import Sum, Case, When, Q, ExpressionWrapper, F, Prefetch, Subquery, OuterRef
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework import generics

from base.models.academic_year import AcademicYear
from base.models.education_group_year import EducationGroupYear
from base.models.enums import offer_enrollment_state
from base.models.offer_enrollment import OfferEnrollment
from dissertation.api.serializers.proposition_dissertation import PropositionDissertationListSerializer, \
    PropositionDissertationDetailSerializer
from dissertation.models.enums.dissertation_status import DissertationStatus
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation


class PropositionDissertationViewMixin:
    @cached_property
    def academic_year(self):
        return AcademicYear.objects.current()

    @cached_property
    def offer_enrollment_ids(self):
        offer_enrollments = list(OfferEnrollment.objects.filter(
            student__person__user=self.request.user,
            education_group_year__academic_year=self.academic_year,
            enrollment_state__in=[
                offer_enrollment_state.SUBSCRIBED,
                offer_enrollment_state.PROVISORY
            ]
        ))
        offer_propositions = OfferProposition.objects.filter(
            education_group__in=[
                offer_enrollment.education_group_year.education_group for offer_enrollment in offer_enrollments
            ]
        )
        date_now = timezone.now().date()
        offer_enrollment_ids = [
            o.id for o in offer_propositions
            if o.start_visibility_proposition <= date_now <= o.end_visibility_proposition
        ]
        return offer_enrollment_ids

    def get_queryset(self):
        prefetch_propositions = Prefetch(
            "offer_propositions",
            queryset=OfferProposition.objects.filter(
                education_group__educationgroupyear__offerenrollment__in=self.offer_enrollment_ids
            ).annotate(last_acronym=Subquery(
                EducationGroupYear.objects.filter(
                    education_group__offer_proposition=OuterRef('pk'),
                    academic_year=self.academic_year
                ).values('acronym')[:1]
            )).distinct()
        )

        return PropositionDissertation.objects.select_related('author__person').prefetch_related(prefetch_propositions)


class PropositionDissertationListView(PropositionDissertationViewMixin, generics.ListAPIView):
    """
       Return all dissertation's propositions available for the user currently connected
    """
    name = 'propositions'
    serializer_class = PropositionDissertationListSerializer
    search_fields = ('title',)

    def get_queryset(self):
        qs = super().get_queryset().filter(
            active=True,
            visibility=True,
            offer_propositions__in=self.offer_enrollment_ids
        ).annotate(
            dissertations_count=Sum(
                Case(
                    When(
                        Q(
                            Q(
                                dissertations__active=True,
                                dissertations__education_group_year__academic_year=self.academic_year
                            ),
                            ~Q(
                                dissertations__status__in=(
                                    DissertationStatus.DRAFT.name,
                                    DissertationStatus.DIR_KO.name,
                                )
                            )
                        ), then=1
                    ),
                    default=0,
                    output_field=models.IntegerField()
                )
            )
        ).annotate(
            remaining_places=ExpressionWrapper(
                F('max_number_student') - F('dissertations_count'),
                output_field=models.IntegerField()
            ),
        )
        return qs.only('title', 'max_number_student', 'author', 'offer_propositions', )


class PropositionDissertationDetailView(PropositionDissertationViewMixin, generics.RetrieveAPIView):
    """
        Return detail of a proposition dissertation available for the user currently connected
    """
    name = 'proposition_detail'
    serializer_class = PropositionDissertationDetailSerializer

    def get_object(self):
        qs = self.get_queryset(). \
            prefetch_related(
            'propositionrole_set__adviser__person',
            'propositiondocumentfile_set__document_file'
        )
        return qs.get(uuid=self.kwargs['uuid'])
