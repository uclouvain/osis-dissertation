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

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from .enums.dissertation_role_status import DissertationRoleStatus

MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION = 4


class DissertationRoleAdmin(SerializableModelAdmin):
    list_display = ('adviser', 'status', 'dissertation', 'author', 'dissertation_status')
    raw_id_fields = ('adviser', 'dissertation')
    search_fields = ('uuid', 'dissertation__author__person__last_name', 'dissertation__author__person__first_name',
                     'dissertation__title', 'adviser__person__last_name', 'adviser__person__first_name')


class DissertationRole(SerializableModel):
    status = models.CharField(max_length=12, choices=DissertationRoleStatus.choices())
    adviser = models.ForeignKey('Adviser', related_name='dissertations_roles', on_delete=models.CASCADE)
    dissertation = models.ForeignKey('Dissertation', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('status', 'adviser', 'dissertation')

    def __str__(self):
        return u"%s %s" % (self.status if self.status else "",
                           self.adviser if self.adviser else "")

    @property
    def author(self):
        return self.dissertation.author

    @property
    def dissertation_status(self):
        return self.dissertation.status


def count_by_adviser(adviser, role=None, dissertation_status=None):
    query = DissertationRole.objects.filter(adviser=adviser)

    if role:
        query = query.filter(status=role)

    if dissertation_status:
        query = query.filter(dissertation__status=dissertation_status)

    query = query.filter(dissertation__active=True) \
        .count()

    return query


def find_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation)


def count_by_dissertation(dissertation):
    return find_by_dissertation(dissertation).count()


def count_by_status_dissertation(status, dissertation):
    return find_by_dissertation(dissertation).filter(status=status).count()


def count_by_adviser_dissertation(adviser, dissertation):
    return find_by_dissertation(dissertation).filter(adviser=adviser).count()


def count_by_status_adviser_dissertation(status, adviser, dissertation):
    return find_by_dissertation(dissertation).filter(adviser=adviser).filter(status=status).count()


def search_by_adviser_and_role_stats(adviser, role):
    return DissertationRole.objects.filter(adviser=adviser) \
        .filter(status=role) \
        .filter(dissertation__active=True) \
        .exclude(
        Q(dissertation__status='DRAFT') |
        Q(dissertation__status='ENDED') |
        Q(dissertation__status='DEFENDED')
    )


def search_by_adviser_and_role_and_waiting(adviser, education_groups):
    return list_teachers_action_needed(education_groups).filter(adviser=adviser)


def count_by_adviser_and_role_stats(adviser, role):
    return search_by_adviser_and_role_stats(adviser, role).count()


def add(status, adviser, dissertation):
    if count_by_status_adviser_dissertation(status, adviser, dissertation) == 0:
        role = DissertationRole(status=status,
                                adviser=adviser,
                                dissertation=dissertation)
        role.save()


def search_by_dissertation(dissertation):
    return DissertationRole.objects.filter(dissertation=dissertation).order_by('status')


def search_by_dissertation_and_role(dissertation, role):
    return search_by_dissertation(dissertation).filter(status=role)


def search_by_adviser_and_role(adviser, role):
    return DissertationRole.objects.filter(status=role) \
        .filter(adviser=adviser) \
        .filter(dissertation__active=True) \
        .exclude(dissertation__status='DRAFT') \
        .order_by(
        'dissertation__status',
        'dissertation__author__person__last_name',
        'dissertation__author__person__first_name'
    )


def search_by_adviser_and_role_and_education_groups(adviser, role, education_groups):
    return search_by_adviser_and_role(adviser, role).filter(
        dissertation__education_group_year__education_group__in=education_groups
    )


def search_by_adviser_and_role_and_status(adviser, role, status):
    return DissertationRole.objects.filter(status=role) \
        .filter(adviser=adviser) \
        .filter(dissertation__active=True) \
        .filter(dissertation__status=status) \
        .order_by(
        'dissertation__author__person__last_name',
        'dissertation__author__person__first_name'
    )


def list_teachers_action_needed(education_groups):
    return DissertationRole.objects.filter(
        status='PROMOTEUR'
    ).filter(
        dissertation__status='DIR_SUBMIT'
    ).filter(
        dissertation__education_group_year__education_group__in=education_groups
    ).filter(
        dissertation__active=True
    ).distinct('adviser')


def find_all_promotor_by_dissertation(dissert):
    return search_by_dissertation_and_role(dissert, 'PROMOTEUR')


def get_tab_count_role_by_education_group(list_roles):
    tab = {}
    for role in list_roles:
        if role.dissertation.education_group_year.education_group in tab:
            tab[role.dissertation.education_group_year.education_group] += 1
        else:
            tab[role.dissertation.education_group_year.education_group] = 1

    return tab


def find_by_id(dissertrole_id):
    try:
        return DissertationRole.objects.get(id=dissertrole_id)
    except ObjectDoesNotExist:
        return None
