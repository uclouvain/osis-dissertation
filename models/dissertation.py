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


from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from base.models import academic_year
from base.models import offer_year, student
from dissertation.models import proposition_dissertation, offer_proposition, dissertation_location
from dissertation.utils import emails_dissert
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class DissertationAdmin(SerializableModelAdmin):
    list_display = ('uuid', 'title', 'author', 'status', 'active', 'proposition_dissertation', 'modification_date')
    raw_id_fields = ('author', 'offer_year_start', 'proposition_dissertation', 'location')
    search_fields = ('uuid', 'title', 'author__person__last_name', 'author__person__first_name',
                     'proposition_dissertation__title', 'proposition_dissertation__author__person__last_name',
                     'proposition_dissertation__author__person__first_name')


STATUS_CHOICES = (
    ('DRAFT', _('draft')),
    ('DIR_SUBMIT', _('submitted_to_director')),
    ('DIR_OK', _('accepted_by_director')),
    ('DIR_KO', _('refused_by_director')),
    ('COM_SUBMIT', _('submitted_to_commission')),
    ('COM_OK', _('accepted_by_commission')),
    ('COM_KO', _('refused_by_commission')),
    ('EVA_SUBMIT', _('submitted_to_first_year_evaluation')),
    ('EVA_OK', _('accepted_by_first_year_evaluation')),
    ('EVA_KO', _('refused_by_first_year_evaluation')),
    ('TO_RECEIVE', _('to_be_received')),
    ('TO_DEFEND', _('to_be_defended')),
    ('DEFENDED', _('defended')),
    ('ENDED', _('ended')),
    ('ENDED_WIN', _('ended_win')),
    ('ENDED_LOS', _('ended_los')),
)

DEFEND_PERIODE_CHOICES = (
    ('UNDEFINED', _('undefined')),
    ('JANUARY', _('january')),
    ('JUNE', _('june')),
    ('SEPTEMBER', _('september')),
)


class Dissertation(SerializableModel):
    title = models.CharField(max_length=500)
    author = models.ForeignKey(student.Student)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='DRAFT')
    defend_periode = models.CharField(max_length=12, choices=DEFEND_PERIODE_CHOICES, blank=True, null=True)
    defend_year = models.IntegerField(blank=True, null=True)
    offer_year_start = models.ForeignKey(offer_year.OfferYear)
    proposition_dissertation = models.ForeignKey(proposition_dissertation.PropositionDissertation)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False)
    modification_date = models.DateTimeField(auto_now=True)
    location = models.ForeignKey(dissertation_location.DissertationLocation, blank=True, null=True)

    def __str__(self):
        return self.title

    def deactivate(self):
        self.active = False
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def go_forward(self):
        next_status = get_next_status(self, "go_forward")
        if self.status == 'TO_RECEIVE' and next_status == 'TO_DEFEND':
            emails_dissert.send_email(self, 'dissertation_acknowledgement', [self.author])
        if (self.status == 'DRAFT' or self.status == 'DIR_KO') and next_status == 'DIR_SUBMIT':
            emails_dissert.send_email_to_all_promotors(self, 'dissertation_adviser_new_project_dissertation')

        self.set_status(next_status)

    def manager_accept(self):
        if self.status == 'DIR_SUBMIT':
            self.teacher_accept()
        elif self.status == 'COM_SUBMIT' or self.status == 'COM_KO':
            next_status = get_next_status(self, "accept")
            emails_dissert.send_email(self, 'dissertation_accepted_by_com', [self.author])
            if offer_proposition.get_by_offer(self.offer_year_start.offer).global_email_to_commission is True:
                emails_dissert.send_email_to_jury_members(self)
            self.set_status(next_status)
        elif self.status == 'EVA_SUBMIT' or self.status == 'EVA_KO' or self.status == 'DEFENDED':
            next_status = get_next_status(self, "accept")
            self.set_status(next_status)

    def teacher_accept(self):
        if self.status == 'DIR_SUBMIT':
            next_status = get_next_status(self, "accept")
            emails_dissert.send_email(self, 'dissertation_accepted_by_teacher', [self.author])
            self.set_status(next_status)

    def refuse(self):
        next_status = get_next_status(self, "refuse")
        if self.status == 'DIR_SUBMIT':
            emails_dissert.send_email(self, 'dissertation_refused_by_teacher', [self.author])
        if self.status == 'COM_SUBMIT':
            emails_dissert.send_email(self, 'dissertation_refused_by_com_to_student', [self.author])
            emails_dissert.send_email_to_all_promotors(self, 'dissertation_refused_by_com_to_teacher')
        self.set_status(next_status)

    class Meta:
        ordering = ["author__person__last_name", "author__person__middle_name", "author__person__first_name", "title"]


def search(terms=None, active=True):
    queryset = Dissertation.objects.all()
    if terms:
        queryset = queryset.filter(
            Q(author__person__first_name__icontains=terms) |
            Q(author__person__middle_name__icontains=terms) |
            Q(author__person__last_name__icontains=terms) |
            Q(description__icontains=terms) |
            Q(proposition_dissertation__title__icontains=terms) |
            Q(proposition_dissertation__author__person__first_name__icontains=terms) |
            Q(proposition_dissertation__author__person__middle_name__icontains=terms) |
            Q(proposition_dissertation__author__person__last_name__icontains=terms) |
            Q(status__icontains=terms) |
            Q(title__icontains=terms) |
            Q(offer_year_start__acronym__icontains=terms)
        )
    queryset = queryset.filter(active=active).exclude(status='ENDED').distinct()
    return queryset


def search_by_proposition_author(terms=None, active=True, proposition_author=None):
    return search(terms=terms, active=active).filter(proposition_dissertation__author=proposition_author)


def search_by_offer(offers, active=True):
    return Dissertation.objects.filter(offer_year_start__offer__in=offers).filter(active=active)


def search_by_offer_and_status(offers, status):
    return search_by_offer(offers).filter(status=status)


def get_next_status(dissert, operation):
    if operation == "go_forward":
        if dissert.status == 'DRAFT' or dissert.status == 'DIR_KO':
            return 'DIR_SUBMIT'

        elif dissert.status == 'TO_RECEIVE':
            return 'TO_DEFEND'

        elif dissert.status == 'TO_DEFEND':
            return 'DEFENDED'
        else:
            return dissert.status

    elif operation == "accept":

        offer_prop = offer_proposition.get_by_offer(dissert.offer_year_start.offer)

        if offer_prop is None:
            return dissert.status

        if offer_prop.validation_commission_exists and dissert.status == 'DIR_SUBMIT':

            return 'COM_SUBMIT'

        elif offer_prop.evaluation_first_year and (dissert.status == 'DIR_SUBMIT' or
                                                   dissert.status == 'COM_SUBMIT' or
                                                   dissert.status == 'COM_KO'):
            return 'EVA_SUBMIT'

        elif offer_prop.evaluation_first_year and (dissert.status == 'EVA_SUBMIT'):
            return 'TO_RECEIVE'

        elif dissert.status == 'DEFENDED':
            return 'ENDED_WIN'

        else:
            return 'TO_RECEIVE'

    elif operation == "refuse":
        if dissert.status == 'DIR_SUBMIT':
            return 'DIR_KO'

        elif dissert.status == 'COM_SUBMIT':
            return 'COM_KO'

        elif dissert.status == 'EVA_SUBMIT':
            return 'EVA_KO'

        elif dissert.status == 'DEFENDED':
            return 'ENDED_LOS'
        else:
            return dissert.status

    else:
        return dissert.status


def find_by_id(dissertation_id):
    try:
        return Dissertation.objects.get(pk=dissertation_id)
    except ObjectDoesNotExist:
        return None


def count_by_proposition(proposition):
    current_academic_year = academic_year.starting_academic_year()
    return Dissertation.objects.filter(proposition_dissertation=proposition) \
        .filter(active=True) \
        .filter(offer_year_start__academic_year=current_academic_year) \
        .exclude(status='DRAFT') \
        .exclude(status='DIR_KO') \
        .count()
