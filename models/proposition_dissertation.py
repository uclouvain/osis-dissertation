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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from osis_document.contrib import FileUploadField, FileField

from dissertation.models import proposition_offer
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_offer import PropositionOffer
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class PropositionDissertationAdmin(SerializableModelAdmin):
    exclude = ('proposition_dissertation_file',)
    list_display = ('uuid', 'title', 'author', 'visibility', 'active', 'creator')
    raw_id_fields = ('creator', 'author')
    search_fields = ('uuid', 'title', 'author__person__last_name', 'author__person__first_name')


def proposition_dissertation_directory_path(proposition_dissertation: 'PropositionDissertation', filename: str):
    """Return the file upload directory path."""
    return f"proposition_dissertation/{proposition_dissertation.uuid}/{filename}"


class PropositionDissertation(SerializableModel):
    TYPES_CHOICES = (
        ('RDL', _('Litterature review')),
        ('EMP', _('Empirical research')),
        ('THE', _('Theoretical analysis')),
        ('PRO', _('Project dissertation')),
        ('DEV', _('Development dissertation')),
        ('OTH', _('Other')),
        )

    LEVELS_CHOICES = (
        ('SPECIFIC', _('Specific subject')),
        ('THEME', _('Large theme')),
        )

    COLLABORATION_CHOICES = (
        ('POSSIBLE', _('Possible')),
        ('REQUIRED', _('Required')),
        ('FORBIDDEN', _('Forbidden')),
        )

    author = models.ForeignKey('Adviser', on_delete=models.CASCADE, verbose_name=_('Author'))
    creator = models.ForeignKey('base.Person', blank=True, null=True, on_delete=models.CASCADE)
    collaboration = models.CharField(max_length=12, choices=COLLABORATION_CHOICES, default='FORBIDDEN',
                                     verbose_name=_('Collaboration'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    level = models.CharField(max_length=12, choices=LEVELS_CHOICES, default='DOMAIN',
                             verbose_name=_('Subject developement level'))
    max_number_student = models.IntegerField(verbose_name=_('Indicative number of places for this subject'))
    title = models.CharField(max_length=200, verbose_name=pgettext_lazy('dissertation', 'Title'))
    type = models.CharField(max_length=12, choices=TYPES_CHOICES, default='OTH', verbose_name=_('Subject type'))
    visibility = models.BooleanField(default=True, verbose_name=_('Visibility'))
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    offer_propositions = models.ManyToManyField(
        OfferProposition,
        through=PropositionOffer,
        verbose_name=_('Links to offer_propositions'),
        related_name='offer_propositions'
    )
    proposition_dissertation_file = FileField(
        mimetypes=['image/jpeg', 'image/png', 'application/pdf'],
        max_size=None,  # TODO : Fixer taille maximum
        max_files=1,
        min_files=1,
        upload_to=proposition_dissertation_directory_path,
        null=True,
        can_edit_filename=False
    )

    def __str__(self):
        first_name = self.author.person.first_name or ""
        last_name = self.author.person.last_name or ""
        author = "%s, %s" % (last_name.upper(), first_name)
        return "%s - %s" % (author, self.title)

    def deactivate(self):
        self.active = False
        self.save()

    def set_creator(self, person):
        self.creator = person
        self.save()

    def set_author(self, adviser):
        self.author = adviser
        self.save()

    class Meta:
        ordering = ["author__person__last_name", "author__person__middle_name", "author__person__first_name", "title"]


def search(terms, active=None, visibility=None, connected_adviser=None, education_groups=None):
    queryset = PropositionDissertation.objects.all()
    if terms:
        queryset = queryset.filter(
            Q(title__icontains=terms) |
            Q(description__icontains=terms) |
            Q(author__person__first_name__icontains=terms) |
            Q(author__person__middle_name__icontains=terms) |
            Q(author__person__last_name__icontains=terms) |
            Q(propositionoffer__offer_proposition__acronym__icontains=terms)
        )

    if active:
        queryset = queryset.filter(active=active)

    if education_groups:
        proposition_ids = proposition_offer.find_by_education_groups(education_groups)\
            .values('proposition_dissertation_id')
        queryset = queryset.filter(pk__in=proposition_ids)

    if visibility and connected_adviser:
        queryset = queryset.filter(Q(visibility=visibility) |
                                   Q(author=connected_adviser))

    elif visibility:
        queryset = queryset.filter(visibility=visibility)

    return queryset.distinct()


def search_by_offer(offers):
    return PropositionDissertation.objects.filter(active=True)\
                                          .filter(offer_proposition__offer__in=offers)\
                                          .distinct()


def get_all_for_teacher(adviser):
    return PropositionDissertation.objects.filter(
                                                    Q(active=True) &
                                                    (Q(visibility=True) | Q(author=adviser))
                                                  )


def get_mine_for_teacher(adviser):
    return PropositionDissertation.objects.filter(author=adviser)\
                                          .filter(active=True)\
                                          .distinct()


def get_created_for_teacher(adviser):
    return PropositionDissertation.objects.filter(creator=adviser.person)\
                                          .filter(active=True)\
                                          .exclude(author=adviser)\
                                          .distinct()


def find_by_id(proposition_id):
    try:
        return PropositionDissertation.objects.get(pk=proposition_id)
    except ObjectDoesNotExist:
        return None


def search_by_offers(offers):
    proposition_ids = proposition_offer.find_by_offers(offers).values('proposition_dissertation_id')
    return PropositionDissertation.objects.filter(pk__in=proposition_ids, active=True, visibility=True)


def find_by_education_groups(education_groups):
    now = timezone.now()
    proposition_ids = PropositionOffer.objects.filter(
        proposition_dissertation__active=True,
        proposition_dissertation__visibility=True,
        offer_proposition__education_group__in=education_groups,
        offer_proposition__start_visibility_proposition__lte=now,
        offer_proposition__end_visibility_proposition__gte=now
    ).distinct().values('proposition_dissertation_id')
    return PropositionDissertation.objects.filter(pk__in=proposition_ids, active=True, visibility=True)
