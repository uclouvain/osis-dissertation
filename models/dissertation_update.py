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
from django.db import models
from django.utils.translation import gettext_lazy as _

from base import models as mdl
from dissertation.models.enums import dissertation_status
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from . import adviser
from . import dissertation

JUSTIFICATION_LINK = _("set to")


class DissertationUpdateAdmin(SerializableModelAdmin):
    list_display = ('dissertation', 'status_from', 'status_to', 'person', 'created')
    raw_id_fields = ('person', 'dissertation')
    search_fields = ('uuid', 'dissertation__title', 'person__last_name', 'person__first_name',
                     'dissertation__author__person__last_name', 'dissertation__author__person__first_name')


class DissertationUpdate(SerializableModel):

    status_from = models.CharField(
        max_length=12,
        choices=dissertation_status.DISSERTATION_STATUS,
        default=dissertation_status.DRAFT)
    status_to = models.CharField(
        max_length=12,
        choices=dissertation_status.DISSERTATION_STATUS,
        default=dissertation_status.DRAFT
    )
    created = models.DateTimeField(auto_now_add=True)
    justification = models.TextField(blank=True)
    person = models.ForeignKey('base.Person', on_delete=models.CASCADE)
    dissertation = models.ForeignKey(dissertation.Dissertation, on_delete=models.CASCADE)

    def __str__(self):
        desc = "%s / %s >> %s / %s" % (self.dissertation.title, self.status_from, self.status_to, str(self.created))
        return desc

    @property
    def author(self):
        return self.dissertation.author


def search_by_dissertation(dissert):
    return DissertationUpdate.objects.filter(dissertation=dissert)\
                                     .order_by('created')


def add(request, dissert, old_status, justification=None):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    update = DissertationUpdate()
    update.status_from = old_status
    update.status_to = dissert.status
    if justification:
        update.justification = justification
    else:
        update.justification = "{} {} {}".format(
            adv.type if adv else person.full_name,
            JUSTIFICATION_LINK,
            dissert.status
        )
    update.person = person
    update.dissertation = dissert
    update.save()
