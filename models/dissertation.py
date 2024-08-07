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


from osis_document.contrib import FileField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from base.models import academic_year
from base.models import student
from base.models.education_group_year import EducationGroupYear
from dissertation.models import dissertation_location
from dissertation.models.dissertation_document_file import DissertationDocumentFile
from dissertation.models.enums import dissertation_status
from dissertation.models.enums.defend_periodes import DefendPeriodes, DEFEND_PERIODE
from dissertation.models.enums.dissertation_status import DISSERTATION_STATUS, DissertationStatus
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.utils import emails_dissert
from osis_common.models.document_file import DocumentFile
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin
from osis_common.utils.models import get_object_or_none


class DissertationAdmin(SerializableModelAdmin):
    exclude = (
        'dissertation_file',
    )
    list_display = (
        'uuid',
        'title',
        'author',
        'status',
        'active',
        'proposition_dissertation',
        'modification_date',
        'education_group_year',
    )
    raw_id_fields = (
        'author',
        'proposition_dissertation',
        'location',
        'education_group_year'
    )
    search_fields = (
        'uuid',
        'title',
        'author__person__last_name',
        'author__person__first_name',
        'proposition_dissertation__title',
        'proposition_dissertation__author__person__last_name',
        'proposition_dissertation__author__person__first_name',
        'education_group_year__acronym'
    )


def dissertation_directory_path(dissertation: 'Dissertation', filename: str):
    """Return the file upload directory path."""
    return f"dissertation/{dissertation.uuid}/{filename}"


class Dissertation(SerializableModel):
    title = models.CharField(
        max_length=500,
        verbose_name=pgettext_lazy('dissertation', 'Title'),
    )
    author = models.ForeignKey(
        student.Student,
        verbose_name=_('Author'),
        on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=12,
        choices=DISSERTATION_STATUS,
        default=DissertationStatus.DRAFT.value
    )
    defend_periode = models.CharField(
        max_length=12,
        choices=DEFEND_PERIODE,
        default=DefendPeriodes.UNDEFINED.value,
        blank=True,
        null=True,
        verbose_name=_('Defense period')
    )
    defend_year = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Defense year')
    )
    education_group_year = models.ForeignKey(
        EducationGroupYear,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='education_group_years',
        verbose_name=_('Programs')
    )
    proposition_dissertation = models.ForeignKey(
        PropositionDissertation,
        related_name='dissertations',
        verbose_name=_('Dissertation subject'),
        on_delete=models.PROTECT
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Description'),
    )
    active = models.BooleanField(
        default=True
    )
    creation_date = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    modification_date = models.DateTimeField(
        auto_now=True
    )
    location = models.ForeignKey(
        dissertation_location.DissertationLocation,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_('Dissertation location')
    )
    dissertation_documents_files = models.ManyToManyField(
        DocumentFile,
        through=DissertationDocumentFile
    )
    dissertation_file = FileField(
        mimetypes=['image/jpeg', 'image/png', 'application/pdf'],
        max_size=None,  # TODO : Fixer taille maximum
        max_files=1,
        min_files=1,
        upload_to=dissertation_directory_path,
        null=True
    )

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
        if self.status == dissertation_status.TO_RECEIVE and next_status == dissertation_status.TO_DEFEND:
            emails_dissert.send_email(self, 'dissertation_acknowledgement', [self.author])
        if (self.status == dissertation_status.DRAFT or self.status == dissertation_status.DIR_KO) and \
                next_status == dissertation_status.DIR_SUBMIT:
            emails_dissert.send_email_to_all_promotors(self, 'dissertation_adviser_new_project_dissertation')

        self.set_status(next_status)

    def manager_accept(self):
        if self.status == dissertation_status.DIR_SUBMIT:
            self.teacher_accept()
        elif self.status == dissertation_status.ENDED_LOS:
            self.set_status(dissertation_status.TO_RECEIVE)
        elif self.status == dissertation_status.COM_SUBMIT or self.status == dissertation_status.COM_KO:
            next_status = get_next_status(self, "accept")
            emails_dissert.send_email(self, 'dissertation_accepted_by_com', [self.author])
            if get_object_or_none(OfferProposition, education_group=self.education_group_year.education_group) \
                    .global_email_to_commission:
                emails_dissert.send_email_to_jury_members(self)
            self.set_status(next_status)
        elif self.status == dissertation_status.EVA_SUBMIT or \
                self.status == dissertation_status.EVA_KO or self.status == dissertation_status.DEFENDED:
            next_status = get_next_status(self, "accept")
            self.set_status(next_status)

    def teacher_accept(self):
        if self.status == dissertation_status.DIR_SUBMIT:
            next_status = get_next_status(self, "accept")
            emails_dissert.send_email(self, 'dissertation_accepted_by_teacher', [self.author])
            self.set_status(next_status)

    def refuse(self):
        next_status = get_next_status(self, "refuse")
        if self.status == dissertation_status.DIR_SUBMIT:
            emails_dissert.send_email(self, 'dissertation_refused_by_teacher', [self.author])
        if self.status == dissertation_status.COM_SUBMIT:
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
            Q(education_group_year__acronym__icontains=terms)
        )
    queryset = queryset.filter(active=active).exclude(status=dissertation_status.ENDED).distinct()
    return queryset


def search_by_proposition_author(terms=None, active=True, proposition_author=None):
    return search(terms=terms, active=active).filter(proposition_dissertation__author=proposition_author)


def search_by_education_group(education_groups, active=True):
    return Dissertation.objects.filter(education_group_year__education_group__in=education_groups, active=active)


def search_by_education_group_and_status(education_groups, status):
    return search_by_education_group(education_groups).filter(status=status)


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

        offer_prop = get_object_or_none(
            OfferProposition,
            education_group=dissert.education_group_year.education_group
        )

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
    starting_academic_year = academic_year.starting_academic_year()
    return Dissertation.objects.filter(proposition_dissertation=proposition) \
        .filter(active=True) \
        .filter(education_group_year__academic_year=starting_academic_year) \
        .exclude(status=dissertation_status.DRAFT) \
        .exclude(status=dissertation_status.DIR_KO) \
        .count()
