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
from django.utils.functional import cached_property
from rest_framework import generics, status
from rest_framework.response import Response

from dissertation.api.serializers.dissertation import DissertationListSerializer, DissertationCreateSerializer
from dissertation.models.dissertation import Dissertation


class DissertationListCreateView(generics.ListCreateAPIView):
    """
       POST: Create a dissertation
       GET: Return all dissertations available of the user currently connected
   """
    name = 'dissertation-list-create'
    serializer_class = DissertationListSerializer

    @cached_property
    def student(self):
        return self.request.user.person.student_set.first()

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
            defend_period=serializer.validated_data['defend_period'],
            author=self.student,

            # Conversion uuid to id is made in Serializer
            location_id=serializer.validated_data['location_uuid'],
            education_group_year_id=serializer.validated_data['education_group_year_uuid'],
            proposition_dissertation_id=serializer.validated_data['proposition_dissertation_uuid'],
        )
        return obj_created.uuid
