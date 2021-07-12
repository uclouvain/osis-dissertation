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
from typing import List

from rest_framework import serializers

from dissertation.models.adviser import Adviser
from dissertation.models.enums.dissertation_role_status import DissertationRoleStatus
from dissertation.models.proposition_dissertation import PropositionDissertation


class PropositionDissertationListSerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    title = serializers.CharField(default='', read_only=True)
    offers = serializers.SerializerMethodField()
    remaining_places = serializers.SerializerMethodField()
    max_number_student = serializers.IntegerField(default=0, read_only=True)
    author = serializers.CharField(default='', read_only=True)

    def get_offers(self, obj: PropositionDissertation) -> List[str]:
        # At this stage, PropositionDissertation has been prefetch last_acronym
        return [
            offer_proposition.last_acronym for offer_proposition in obj.offer_propositions.all() if
            offer_proposition.last_acronym
        ]

    def get_remaining_places(self, obj: PropositionDissertation) -> int:
        # At this stage, PropositionDissertation is annotated in queryset
        return obj.remaining_places if obj.remaining_places >= 0 else 0


class PropositionDissertationAuthorSerializer(serializers.Serializer):
    first_name = serializers.CharField(default='', source='person.first_name', read_only=True)
    last_name = serializers.CharField(default='', source='person.last_name', read_only=True)
    middle_name = serializers.CharField(default='', source='person.middle_name', read_only=True)
    available_by_email = serializers.BooleanField(read_only=True)
    email = serializers.SerializerMethodField()
    available_by_phone = serializers.BooleanField(read_only=True)
    phone = serializers.SerializerMethodField()
    mobile_phone = serializers.SerializerMethodField()
    comment = serializers.CharField(default='', read_only=True)

    def get_email(self, obj: Adviser) -> str:
        if obj.available_by_email:
            return obj.person.email or ''
        return ''

    def get_phone(self, obj: Adviser) -> str:
        if obj.available_by_phone:
            return obj.person.phone or ''
        return ''

    def get_mobile_phone(self, obj: Adviser) -> str:
        if obj.available_by_phone:
            return obj.person.phone_mobile or ''
        return ''


class PropositionDissertationJurySerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    status_text = serializers.CharField(source='get_status_display', read_only=True)
    adviser = serializers.CharField(default='', read_only=True)


class PropositionDissertationLinkSerializer(serializers.Serializer):
    document_url = serializers.SerializerMethodField()

    def get_document_url(self, obj) -> str:
        return ''


class PropositionDissertationDetailSerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    title = serializers.CharField(default='', read_only=True)
    offers = serializers.SerializerMethodField()
    max_number_student = serializers.IntegerField(default=0, read_only=True)
    dissertations_count = serializers.IntegerField(default=0, read_only=True)
    author = PropositionDissertationAuthorSerializer()
    jury = serializers.SerializerMethodField()
    link = PropositionDissertationLinkSerializer(source='*')

    def get_offers(self, obj: PropositionDissertation) -> List[str]:
        # At this stage, PropositionDissertation has been prefetch last_acronym
        return [
            offer_proposition.last_acronym for offer_proposition in obj.offer_propositions.all() if
            offer_proposition.last_acronym
        ]

    def get_jury(self, obj: PropositionDissertation):
        results = PropositionDissertationJurySerializer(obj.propositionrole_set.all(), many=True).data
        if not results:
            return [{
                'status': DissertationRoleStatus.PROMOTEUR.name,
                'status_text': DissertationRoleStatus.PROMOTEUR.value,
                'adviser': str(obj.author)
            }]
        return results
