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
from dissertation.models.offer_proposition_group import OfferPropositionGroup
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from base.models import offer
from datetime import date


class OfferPropositionAdmin(SerializableModelAdmin):
    list_display = ('acronym', 'offer', 'offer_proposition_group')
    raw_id_fields = ('offer',)
    search_fields = ('uuid',)


class OfferProposition(SerializableModel):
    acronym = models.CharField(max_length=200)
    offer = models.ForeignKey(offer.Offer)
    student_can_manage_readers = models.BooleanField(default=True)
    adviser_can_suggest_reader = models.BooleanField(default=False)
    evaluation_first_year = models.BooleanField(default=False)
    validation_commission_exists = models.BooleanField(default=False)
    start_visibility_proposition = models.DateField(default=timezone.now)
    end_visibility_proposition = models.DateField(default=timezone.now)
    start_visibility_dissertation = models.DateField(default=timezone.now)
    end_visibility_dissertation = models.DateField(default=timezone.now)
    start_jury_visibility = models.DateField(default=timezone.now)
    end_jury_visibility = models.DateField(default=timezone.now)
    start_edit_title = models.DateField(default=timezone.now)
    end_edit_title = models.DateField(default=timezone.now)
    offer_proposition_group = models.ForeignKey(OfferPropositionGroup, null=True, blank=True)
    global_email_to_commission = models.BooleanField(default=False)

    @property
    def in_periode_visibility_proposition(self):
        start = self.start_visibility_proposition
        end = self.end_visibility_proposition

        return start <= date.today() <= end

    @property
    def in_periode_visibility_dissertation(self):
        start = self.start_visibility_dissertation
        end = self.end_visibility_dissertation

        return start <= date.today() <= end

    @property
    def in_periode_jury_visibility(self):
        start = self.start_jury_visibility
        end = self.end_jury_visibility

        return start <= date.today() <= end

    @property
    def in_periode_edit_title(self):
        start = self.start_edit_title
        end = self.end_edit_title

        return start <= date.today() <= end

    def __str__(self):
        return self.acronym

    class Meta:
        ordering = ['offer_proposition_group', 'acronym']


def get_by_offer(an_offer):
    try:
        offer_proposition = OfferProposition.objects.get(offer=an_offer)
    except ObjectDoesNotExist:
        offer_proposition = None

    return offer_proposition


def search_by_offer(offers):
    return OfferProposition.objects.filter(offer__in=offers) \
        .distinct() \
        .order_by('acronym')


def show_validation_commission(offer_props):
    # True si validation_commission_exists est True pour au moins une offer_prop dans offer_props
    # False sinon
    return any([offer_prop.validation_commission_exists for offer_prop in offer_props])


def show_evaluation_first_year(offer_props):
    # True si evaluation_first_year est True pour au moins une offer_prop dans offer_props
    # False sinon
    return any([offer_prop.evaluation_first_year for offer_prop in offer_props])


def get_by_dissertation(dissert):
    return get_by_offer(dissert.offer_year_start.offer)


def find_by_id(offer_proposition_id):
    try:
        return OfferProposition.objects.get(pk=offer_proposition_id)
    except ObjectDoesNotExist:
        return None


def find_all_ordered_by_acronym():
    return OfferProposition.objects.order_by('acronym')


def get_by_offer_proposition_group(offer_proposition_group):
    try:
        offer_proposition = OfferProposition.objects.get(offer_proposition_group=offer_proposition_group)
    except ObjectDoesNotExist:
        offer_proposition = None
    return offer_proposition
