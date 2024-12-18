##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

from base.models.education_group import EducationGroup
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.enums.adviser_types import AdviserTypes, ADVISER_TYPES
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_role import PropositionRole
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from osis_common.utils.models import get_object_or_none


class AdviserAdmin(SerializableModelAdmin):
    list_display = (
        'uuid',
        'person',
        'type'
    )
    raw_id_fields = (
        'person',
    )
    search_fields = (
        'uuid',
        'person__last_name',
        'person__first_name'
    )


class Adviser(SerializableModel):
    person = models.OneToOneField(
        'base.Person',
        on_delete=models.CASCADE
    )
    type = models.CharField(
        max_length=3,
        choices=ADVISER_TYPES,
        default=AdviserTypes.PRF.value
    )
    available_by_email = models.BooleanField(
        default=False
    )
    available_by_phone = models.BooleanField(
        default=False
    )
    available_at_office = models.BooleanField(
        default=False
    )
    comment = models.TextField(
        default='',
        blank=True
    )
    education_groups = models.ManyToManyField(
        EducationGroup,
        through="FacultyAdviser",
        related_name="advisers"
    )
    dissertations = models.ManyToManyField(
        Dissertation,
        through=DissertationRole,
        related_name='advisers'
    )
    proposition_dissertation = models.ManyToManyField(
        PropositionDissertation,
        through=PropositionRole,
        related_name='advisers'
    )

    def __str__(self):
        first_name = ""
        last_name = ""
        if self.person.first_name:
            first_name = self.person.first_name
        if self.person.last_name:
            last_name = self.person.last_name + ","
        return u"%s %s" % (last_name.upper(), first_name)


def search_by_person(a_person):
    try:
        adviser = Adviser.objects.get(person=a_person)
        return adviser
    except ObjectDoesNotExist:
        return None


def find_by_person(a_person):
    adviser = Adviser.objects.filter(person=a_person)
    return adviser


def list_teachers():
    return Adviser.objects.filter(type='PRF') \
        .order_by('person__last_name', 'person__first_name')


def find_all_advisers():
    return Adviser.objects.all()


def add(person, type_arg, available_by_email, available_by_phone, available_at_office, comment):
    adv = Adviser(person=person,
                  type=type_arg,
                  available_by_email=available_by_email,
                  available_by_phone=available_by_phone,
                  available_at_office=available_at_office,
                  comment=comment)
    adv.save()
    return adv


def _has_role(user, role):
    this_adviser = get_object_or_none(Adviser, person__user=user)
    return this_adviser.type == role if this_adviser else False


def is_manager(user):
    return _has_role(user, 'MGR')


def is_teacher(user):
    return _has_role(user, 'PRF')


def get_by_id(adviser_id):
    try:
        return Adviser.objects.get(pk=adviser_id)
    except ObjectDoesNotExist:
        return None


def find_advisers_last_name_email(term, maximum_in_request):
    if term is None:
        return []
    else:
        return Adviser.objects.filter(Q(person__email__icontains=term) |
                                      Q(person__last_name__icontains=term))[:maximum_in_request]


def convert_advisers_to_array(advisers):
    return_data = [
        {
            'value': "{}, {} ({})".format(none_to_str(adviser.person.last_name),
                                          none_to_str(adviser.person.first_name),
                                          none_to_str(adviser.person.email)),
            'first_name': none_to_str(adviser.person.first_name),
            'last_name': none_to_str(adviser.person.last_name),
            'id': adviser.id
        }
        for adviser in advisers
    ]
    return return_data


def none_to_str(value):
    return value or ''
