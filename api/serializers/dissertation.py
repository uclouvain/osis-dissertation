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
from dissertation.models.dissertation_location import DissertationLocation
from dissertation.models.enums.defend_periodes import DefendPeriodes
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
