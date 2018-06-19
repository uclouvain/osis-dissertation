##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from base.models import person
from dissertation.models import dissertation_role


class AdviserAdmin(SerializableModelAdmin):
    list_display = ('person', 'type')
    raw_id_fields = ('person',)
    search_fields = ('uuid', 'person__last_name', 'person__first_name')


class Adviser(SerializableModel):
    TYPES_CHOICES = (
        ('PRF', _('professor')),
        ('MGR', _('manager')),
    )

    person = models.OneToOneField('base.Person', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TYPES_CHOICES, default='PRF')
    available_by_email = models.BooleanField(default=False)
    available_by_phone = models.BooleanField(default=False)
    available_at_office = models.BooleanField(default=False)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        first_name = ""
        middle_name = ""
        last_name = ""
        if self.person.first_name:
            first_name = self.person.first_name
        if self.person.middle_name:
            middle_name = self.person.middle_name
        if self.person.last_name:
            last_name = self.person.last_name + ","
        return u"%s %s %s" % (last_name.upper(), first_name, middle_name)

    @property
    def get_stat_dissertation_role(self):
        list_stat = [0] * 5
        # list_stat[0]= count dissertation_role active of adviser
        # list_stat[1]= count dissertation_role Promoteur active of adviser
        # list_stat[2]= count dissertation_role coPromoteur active of adviser
        # list_stat[3]= count dissertation_role reader active of adviser
        # list_stat[4]= count dissertation_role need request active of adviser
        list_stat[0] = 0
        list_stat[1] = 0
        list_stat[2] = 0
        list_stat[3] = 0
        list_stat[4] = 0

        queryset = dissertation_role.DissertationRole.objects.all().filter(Q(adviser=self))
        list_stat[0] = queryset.filter(dissertation__active=True) \
            .count()

        list_stat[1] = queryset.filter(status='PROMOTEUR') \
            .filter(Q(dissertation__active=True)) \
            .exclude(Q(dissertation__status='DRAFT') |
                     Q(dissertation__status='ENDED') |
                     Q(dissertation__status='DEFENDED')) \
            .count()

        list_stat[4] = queryset.filter(status='PROMOTEUR') \
            .filter(dissertation__status='DIR_SUBMIT') \
            .filter(dissertation__active=True) \
            .count()

        advisers_copro = queryset.filter(status='CO_PROMOTEUR') \
            .filter(dissertation__active=True) \
            .exclude(Q(dissertation__status='DRAFT') |
                     Q(dissertation__status='ENDED') |
                     Q(dissertation__status='DEFENDED'))

        list_stat[2] = advisers_copro.count()
        tab_offer_count_copro = dissertation_role.get_tab_count_role_by_offer(advisers_copro)

        advisers_reader = queryset.filter(Q(adviser=self) &
                                          Q(status='READER') &
                                          Q(dissertation__active=True)) \
            .exclude(Q(dissertation__status='DRAFT') |
                     Q(dissertation__status='ENDED') |
                     Q(dissertation__status='DEFENDED'))

        list_stat[3] = advisers_reader.count()
        tab_offer_count_read = dissertation_role.get_tab_count_role_by_offer(advisers_reader)

        advisers_pro = queryset.filter(status='PROMOTEUR') \
            .filter(Q(dissertation__active=True)) \
            .exclude(Q(dissertation__status='DRAFT') |
                     Q(dissertation__status='ENDED') |
                     Q(dissertation__status='DEFENDED'))

        tab_offer_count_pro = dissertation_role.get_tab_count_role_by_offer(advisers_pro)

        return list_stat, tab_offer_count_read, tab_offer_count_copro, tab_offer_count_pro

    class Meta:
        ordering = ["person__last_name", "person__middle_name", "person__first_name"]


def search_by_person(a_person):
    try:
        adviser = Adviser.objects.get(person=a_person)
        return adviser
    except ObjectDoesNotExist:
        return None


def find_by_person(a_person):
    adviser = Adviser.objects.filter(person=a_person)
    return adviser


def search_adviser(terms):
    queryset = Adviser.objects.all().filter(type='PRF')
    if terms:
        queryset = queryset.filter(
            (
                Q(person__first_name__icontains=terms) |
                Q(person__last_name__icontains=terms)
            ) &
            Q(type='PRF')).distinct()
    return queryset


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
    pers = person.find_by_user(user)
    this_adviser = search_by_person(pers)
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
