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
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.response import Response

from dissertation.api.serializers.dissertation import DissertationListSerializer, DissertationCreateSerializer, \
    DissertationDetailSerializer, DissertationHistoryListSerializer, DissertationUpdateSerializer
from dissertation.models import dissertation_update
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_update import DissertationUpdate
from dissertation.models.enums.dissertation_status import DissertationStatus


class DissertationListCreateView(generics.ListCreateAPIView):
    """
       POST: Create a dissertation
       GET: Return all dissertations available of the user currently connected
    """
    name = 'dissertation-list-create'
    serializer_class = DissertationListSerializer
    search_fields = ('title',)

    @cached_property
    def student(self):
        return self.request.user.person.student_set.first()

    # TODO: Implement filter on active tag !
    def get_queryset(self):
        return Dissertation.objects.filter(
            author__person__user=self.request.user
        ).select_related(
            'author__person',
            'proposition_dissertation__author__person',
            'education_group_year__academic_year'
        )

    def create(self, request, *args, **kwargs):
        serializer = DissertationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dissertation_uuid = self.perform_create(serializer)
        return Response({'dissertation_uuid': dissertation_uuid}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer) -> str:
        obj_created = Dissertation.objects.create(
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            defend_year=serializer.validated_data['defend_year'],
            defend_periode=serializer.validated_data['defend_period'],
            author=self.student,

            # Conversion uuid to id is made in Serializer
            location_id=serializer.validated_data['location_uuid'],
            education_group_year_id=serializer.validated_data['education_group_year_uuid'],
            proposition_dissertation_id=serializer.validated_data['proposition_dissertation_uuid'],
        )

        dissertation_update.add(
            self.request,
            obj_created,
            obj_created.status,
            justification="Student created the dissertation : {}".format(obj_created.title)
        )
        return obj_created.uuid


class DissertationDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
       GET: Return dissertation's detail of the user currently connected
       DELETE: Deactivate user's dissertation
       PUT: Update user's dissertation
    """
    name = 'dissertation-get-delete'
    serializer_class = DissertationDetailSerializer

    def patch(self, request, *args, **kwargs):
        allowed_http_methods = ["get", "post", "delete"]
        return HttpResponseNotAllowed(allowed_http_methods)

    def update(self, request, *args, **kwargs):
        serializer = DissertationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

    def perform_update(self, serializer):
        disseration = self.get_object()
        if disseration.status in [DissertationStatus.DRAFT.name, DissertationStatus.DIR_KO.name, ]:
            self._perform_only_title_update(serializer, disseration)
        else:
            self._perform_full_update(serializer, disseration)

    def _perform_only_title_update(self, serializer, instance: Dissertation):
        if instance.title != serializer.validated_data['title']:
            justification_str = "student_edit_title: {} : {}, {} : {}".format(
                _("original title"),
                instance.title,
                _("new title"),
                serializer.validated_data['title']
            )

            instance.title = serializer.validated_data['title']
            instance.save()
            dissertation_update.add(self.request, instance, instance.status, justification=justification_str)

    def _perform_full_update(self, serializer, instance: Dissertation):
        instance.title = serializer.validated_data['title']
        instance.description = serializer.validated_data['description'],
        instance.defend_year = serializer.validated_data['defend_year'],
        instance.defend_period = serializer.validated_data['defend_period'],
        instance.location_id = serializer.validated_data['location'],
        instance.save()
        dissertation_update.add(
            self.request,
            instance,
            instance.status,
            justification="student edited the dissertation",
        )

    def get_object(self) -> Dissertation:
        return Dissertation.objects.select_related(
            'author__person',
            'location'
        ).prefetch_related(
            'dissertationrole_set__adviser__person',
            'proposition_dissertation__propositionrole_set__adviser__person'
        ).get(
            author__person__user=self.request.user,
            uuid=self.kwargs['uuid']
        )

    def perform_destroy(self, instance: Dissertation):
        instance.deactivate()
        dissertation_update.add(
            self.request,
            instance,
            instance.status,
            justification="Student set dissertation inactive",
        )


class DissertationHistoryListView(generics.ListAPIView):
    """
       GET: Return dissertation's modification history
    """
    name = 'dissertation-history-list'
    serializer_class = DissertationHistoryListSerializer

    def get_queryset(self):
        return DissertationUpdate.objects.filter(
            dissertation__uuid=self.kwargs['uuid'],
            dissertation__author__person__user=self.request.user
        ).exclude(
            Q(justification__contains='auto_add_jury') |
            Q(justification__contains='Auto add jury') |
            Q(justification__contains='manager_add_jury') |
            Q(justification__contains='Manager add jury') |
            Q(justification__contains='Le manager a ajouté un membre du jury') |
            Q(justification__contains='manager_creation_dissertation') |
            Q(justification__contains='manager_delete_jury') |
            Q(justification__contains='Manager deleted jury') |
            Q(justification__contains='manager_edit_dissertation') |
            Q(justification__contains='manager has edited the dissertation') |
            Q(justification__contains='manager_set_active_false') |
            Q(justification__contains='teacher_add_jury') |
            Q(justification__contains='Teacher added jury') |
            Q(justification__contains='teacher_delete_jury') |
            Q(justification__contains='Teacher deleted jury') |
            Q(justification__contains='teacher_set_active_false')
        ).select_related('person',)
