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
from rest_framework import serializers

from base.models.education_group_year import EducationGroupYear
from dissertation.models import dissertation_role
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_location import DissertationLocation
from dissertation.models.enums.defend_periodes import DefendPeriodes
from dissertation.models.enums.dissertation_role_status import DissertationRoleStatus
from dissertation.models.proposition_dissertation import PropositionDissertation


class DissertationListSerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    title = serializers.CharField(default='', read_only=True)
    author = serializers.CharField(default='', read_only=True)
    status = serializers.CharField(read_only=True)
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    offer_acronym = serializers.CharField(source='education_group_year.acronym', read_only=True)
    start_year = serializers.IntegerField(source='education_group_year.academic_year.year', read_only=True)
    dissertation_subject = serializers.CharField(source='proposition_dissertation', read_only=True)


class DissertationCreateSerializer(serializers.Serializer):
    proposition_dissertation_uuid = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    defend_year = serializers.IntegerField(required=True)
    defend_period = serializers.ChoiceField(required=True, choices=DefendPeriodes.choices())
    location_uuid = serializers.CharField(required=True)
    education_group_year_uuid = serializers.CharField(required=True)

    def validate_proposition_dissertation_uuid(self, proposition_dissertation_uuid: str):
        try:
            obj = PropositionDissertation.objects.get(uuid=proposition_dissertation_uuid)
            return obj.pk
        except PropositionDissertation.DoesNotExist:
            raise serializers.ValidationError("Not found")

    def validate_location_uuid(self, location_uuid: str):
        try:
            obj = DissertationLocation.objects.get(uuid=location_uuid)
            return obj.pk
        except DissertationLocation.DoesNotExist:
            raise serializers.ValidationError("Not found")

    def validate_education_group_year_uuid(self, education_group_year_uuid: str):
        try:
            obj = EducationGroupYear.objects.get(uuid=education_group_year_uuid)
            return obj.pk
        except EducationGroupYear.DoesNotExist:
            raise serializers.ValidationError("Not found")


class DissertationAuthorSerializer(serializers.Serializer):
    first_name = serializers.CharField(default='', read_only=True)
    last_name = serializers.CharField(default='', read_only=True)
    middle_name = serializers.CharField(default='', read_only=True)


class DissertationLocation(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)


class DissertationJurySerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    adviser = serializers.CharField(default='', read_only=True)


class DissertationLinkSerializer(serializers.Serializer):
    document_url = serializers.SerializerMethodField()
    delete_document_url = serializers.SerializerMethodField()

    def get_document_url(self, obj) -> str:
        return ''

    def get_delete_document_url(self, obj) -> str:
        return ''


class DissertationDetailSerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    proposition_uuid = serializers.CharField(read_only=True, source="proposition_dissertation.uuid")
    title = serializers.CharField(default='', read_only=True)
    description = serializers.CharField(default='', read_only=True)
    author = DissertationAuthorSerializer(source='author.person')
    status = serializers.CharField(read_only=True)
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    defend_period = serializers.CharField(read_only=True, source='defend_periode')
    defend_period_text = serializers.CharField(source='get_defend_periode_display', read_only=True)
    defend_year = serializers.IntegerField(read_only=True)
    location = DissertationLocation()
    jury = serializers.SerializerMethodField()
    link = DissertationLinkSerializer(source='*')

    def get_jury(self, obj: Dissertation):
        results = DissertationJurySerializer(obj.dissertationrole_set.all(), many=True).data
        if results:
            return results

        results = DissertationJurySerializer(obj.proposition_dissertation.propositionrole_set.all(), many=True).data
        if results:
            # TODO: Remove logic inside - must be done at creation
            for role in obj.proposition_dissertation.propositionrole_set.all():
                dissertation_role.add(role.status, role.adviser, obj)
            return results

        if not results:
            # TODO: Remove logic inside - must be done at creation
            dissertation_role.add(DissertationRoleStatus.PROMOTEUR.name, obj.proposition_dissertation.author, obj)
            return [{
                'status': DissertationRoleStatus.PROMOTEUR.name,
                'status_text': DissertationRoleStatus.PROMOTEUR.value,
                'adviser': str(obj.author)
            }]
        return results


class DissertationHistoryListSerializer(serializers.Serializer):
    status_from = serializers.CharField(read_only=True)
    status_from_text = serializers.CharField(read_only=True, source="get_status_from_display")
    status_to = serializers.CharField(read_only=True)
    status_to_text = serializers.CharField(read_only=True, source="get_status_to_display")
    author = serializers.CharField(read_only=True, source="person")
    created_at = serializers.DateTimeField(read_only=True, format="%d-%m-%Y %H:%M:%S", source="created")
    justification = serializers.CharField(read_only=True)
