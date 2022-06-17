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
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from base.models.education_group_year import EducationGroupYear
from dissertation.api.serializers.dissertation import DissertationListSerializer, DissertationCreateSerializer, \
    DissertationDetailSerializer, DissertationHistoryListSerializer, DissertationUpdateSerializer, \
    DissertationJuryAddSerializer, DissertationSubmitSerializer, DissertationBackToDraftSerializer, \
    DissertationCanManageJurySerializer, DissertationCanEditDissertationSerializer, DissertationFileSerializer
from dissertation.models import dissertation_update
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.dissertation_update import DissertationUpdate
from dissertation.models.enums.dissertation_role_status import DissertationRoleStatus
from dissertation.models.enums.dissertation_status import DissertationStatus
from dissertation.models.offer_proposition import OfferProposition


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

    def get_education_group_year(self, acronym, year):
        return EducationGroupYear.objects.get(
            acronym=acronym,
            academic_year__year=year
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
            education_group_year=self.get_education_group_year(
                serializer.validated_data['acronym'],
                serializer.validated_data['year']
            ),
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
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        disseration = self.get_object()
        if disseration.status in [DissertationStatus.DRAFT.name, DissertationStatus.DIR_KO.name, ]:
            self._perform_full_update(serializer, disseration)
        else:
            self._perform_only_title_update(serializer, disseration)

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
        instance.description = serializer.validated_data['description']
        instance.defend_year = serializer.validated_data['defend_year']
        instance.defend_periode = serializer.validated_data['defend_period']
        # Conversion uuid to id is made in Serializer
        instance.location_id = serializer.validated_data['location_uuid']
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
        ).select_related('person', )


class DissertationJuryAddView(generics.CreateAPIView):
    """
       POST: Add a reader jury member on dissertation
    """
    name = 'dissertation-jury-add'
    serializer_class = DissertationJuryAddSerializer

    @cached_property
    def dissertation(self):
        return Dissertation.objects.prefetch_related(
            'dissertationrole_set'
        ).select_related(
            'education_group_year__education_group__offer_proposition'
        ).get(
            author__person__user=self.request.user,
            uuid=self.kwargs['uuid']
        )

    def create(self, request, *args, **kwargs):
        if not self._can_create():
            raise PermissionDenied()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dissertation_jury_uuid = self.perform_create(serializer)
        return Response({'dissertation_jury_uuid': dissertation_jury_uuid}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer) -> str:
        # Conversion uuid to id done in serializer
        adviser = Adviser.objects.select_related('person').get(pk=serializer.validated_data['adviser_uuid'])
        obj_created = DissertationRole.objects.create(
            adviser_id=adviser.pk,
            dissertation_id=self.dissertation.pk,
            status=DissertationRoleStatus.READER.name,
        )

        justification = "{} {}".format("Student added reader", adviser)
        dissertation_update.add(
            self.request,
            self.dissertation,
            self.dissertation.status,
            justification=justification
        )
        return obj_created.uuid

    def _can_create(self) -> bool:
        all_jury_members = self.dissertation.dissertationrole_set.all()
        all_jury_readers_members = [
            jury_member for jury_member in all_jury_members if jury_member.status == DissertationRoleStatus.READER.name
        ]

        return len(all_jury_members) < 4 and \
            len(all_jury_readers_members) < 2 and \
            self.dissertation.education_group_year.education_group.offer_proposition.student_can_manage_readers


class DissertationJuryDeleteView(generics.DestroyAPIView):
    """
       DELETE: Delete a jury member of dissertation
    """
    name = 'dissertation-jury-delete'

    def get_object(self):
        return DissertationRole.objects.select_related(
            'dissertation__education_group_year__education_group__offer_proposition'
        ).get(
            dissertation__uuid=self.kwargs['uuid'],
            uuid=self.kwargs['uuid_jury_member'],
        )

    def perform_destroy(self, instance: DissertationRole):
        if not self._can_delete(instance):
            raise PermissionDenied()

        justification = "Student deleted reader {}".format(instance)
        dissertation_update.add(
            self.request,
            instance.dissertation,
            instance.dissertation.status,
            justification=justification,
        )
        instance.delete()

    def _can_delete(self, instance: DissertationRole) -> bool:
        return instance.dissertation.status == DissertationStatus.DRAFT.name and \
               instance.status == DissertationRoleStatus.READER.name and \
               instance.dissertation.education_group_year.education_group.offer_proposition.student_can_manage_readers


class DissertationSubmitView(generics.ListCreateAPIView):
    """
       POST: Return dissertation's detail of the user currently connected
    """
    name = 'dissertation-submit'
    serializer_class = DissertationSubmitSerializer

    @cached_property
    def dissertation(self):
        return Dissertation.objects.prefetch_related(
            'dissertationrole_set'
        ).select_related(
            'education_group_year__education_group__offer_proposition'
        ).get(
            author__person__user=self.request.user,
            uuid=self.kwargs['uuid']
        )

    def create(self, request, *args, **kwargs):
        self.dissertation.status = DissertationStatus.DIR_SUBMIT.name
        self.dissertation.save()

        dissertation_update.add(
            self.request,
            self.dissertation,
            self.dissertation.status,
            justification=request.data["justification"]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DissertationBackToDraftView(generics.ListCreateAPIView):
    """
       POST: Return dissertation's detail of the user currently connected
    """
    name = 'dissertation-submit'
    serializer_class = DissertationBackToDraftSerializer

    @cached_property
    def dissertation(self):
        return Dissertation.objects.prefetch_related(
            'dissertationrole_set'
        ).select_related(
            'education_group_year__education_group__offer_proposition'
        ).get(
            author__person__user=self.request.user,
            uuid=self.kwargs['uuid']
        )

    def create(self, request, *args, **kwargs):
        self.dissertation.status = DissertationStatus.DRAFT.name
        self.dissertation.save()

        dissertation_update.add(
            self.request,
            self.dissertation,
            self.dissertation.status,
            justification=request.data["justification"]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DissertationCanManageJuryView(generics.RetrieveAPIView):
    """
       GET: Return if student can manage jury
    """
    name = 'dissertation-can-manage-jury'
    serializer_class = DissertationCanManageJurySerializer

    def get_object(self):
        dissertation = Dissertation.objects.get(
            uuid=self.kwargs['uuid'],
        )
        return OfferProposition.objects.get(
            education_group=dissertation.education_group_year.education_group
        )


class DissertationCanEditDissertationView(generics.RetrieveAPIView):
    """
       GET: Return if student can manage jury
    """
    name = 'dissertation-can-manage-jury'
    serializer_class = DissertationCanEditDissertationSerializer

    def get_object(self):
        dissertation = Dissertation.objects.get(
            uuid=self.kwargs['uuid'],
        )
        return OfferProposition.objects.get(
            education_group=dissertation.education_group_year.education_group
        )


class DissertationFileView(UpdateModelMixin, RetrieveAPIView):
    name = "dissertation_file"
    pagination_class = None
    filter_backends = []
    serializer_class = DissertationFileSerializer

    def get_object(self):
        return get_object_or_404(Dissertation, uuid=self.kwargs.get('uuid'))

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        return response
