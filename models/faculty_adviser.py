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
from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models import offer
from base.models import offer_year
from base.models.education_group import EducationGroup
from dissertation.models.adviser import Adviser


class FacultyAdviserAdmin(admin.ModelAdmin):
    list_display = ('adviser', 'offer_most_recent_offer_year', 'get_adviser_type', 'education_group',
                    'recent_acronym_education_group')
    raw_id_fields = ('adviser', 'offer', 'education_group')
    search_fields = ('adviser__person__last_name', 'adviser__person__first_name', 'offer__id',
                     'education_group__id')
    readonly_fields = ('recent_acronym_education_group',)


class FacultyAdviser(models.Model):
    adviser = models.ForeignKey(Adviser, verbose_name=_('Adviser'), on_delete=models.CASCADE)
    offer = models.ForeignKey(
        offer.Offer,
        null=True, blank=True,
        on_delete=models.CASCADE
    )
    education_group = models.ForeignKey(EducationGroup, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return "{} - EducationGroup {}".format(str(self.adviser), str(self.education_group))

    def get_adviser_type(self):
        return self.adviser.type

    def offer_most_recent_offer_year(self):
        most_recent_offer_year = offer_year.get_last_offer_year_by_offer(self.offer)
        most_recent_offer_year_title = most_recent_offer_year.title if most_recent_offer_year is not None else ""
        return "{} - {}".format(str(most_recent_offer_year), most_recent_offer_year_title)

    @property
    def recent_acronym_education_group(self):
        if self.education_group:
            return self.education_group.most_recent_acronym
        return None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.adviser.type != 'MGR':
            self.adviser.type = 'MGR'
            self.adviser.save()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.adviser.facultyadviser_set.exclude(pk=self.pk).count() == 0:
            self.adviser.type = 'PRF'
            self.adviser.save()
        return super().delete(using, keep_parents)


def find_education_groups_by_adviser(a_adviser):
    return FacultyAdviser.objects.filter(adviser=a_adviser).select_related('education_group'). \
        values_list('education_group', flat=True)
