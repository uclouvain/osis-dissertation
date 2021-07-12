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
import time

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import models
from django.db.models import Count
from django.db.models import Q, F, ExpressionWrapper, OuterRef, Subquery, Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import CreateView
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from base import models as mdl
from base.models import academic_year
from base.models.education_group_year import EducationGroupYear
from base.views.mixins import AjaxTemplateMixin
from dissertation.forms import PropositionDissertationForm, ManagerPropositionDissertationForm, \
    ManagerPropositionRoleForm, ManagerPropositionDissertationEditForm
from dissertation.models import adviser, offer_proposition, offer_proposition_group
from dissertation.models import dissertation, proposition_dissertation, proposition_document_file, proposition_role, \
    proposition_offer
from dissertation.models.dissertation import Dissertation
from dissertation.models.enums import dissertation_role_status
from dissertation.models.enums import dissertation_status
from dissertation.models.enums.dissertation_role_status import DissertationRoleStatus
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_offer import PropositionOffer
from dissertation.models.proposition_role import PropositionRole
from dissertation.perms import user_is_proposition_promotor, \
    adviser_can_manage_proposition_dissertation, autorized_proposition_dissert_promotor_or_manager_or_author

MAX_PROPOSITION_ROLE = 4


def detect_in_request(request, wanted_key, wanted_value):
    for key in request.POST:
        if wanted_key in key and request.POST[key] == wanted_value:
            return True
    return False


def edit_proposition(form, proposition_offers, request):
    proposition = form.save()
    for old in proposition_offers:
        old.delete()
    generate_proposition_offers(request, proposition)
    return proposition


def create_proposition(form, person, request):
    proposition = form.save()
    proposition.set_creator(person)
    generate_proposition_offers(request, proposition)
    return proposition


def generate_proposition_offers(request, proposition):
    for key, value in request.POST.items():
        if 'txt_checkbox_' in key and value == 'on':
            offer = PropositionOffer()
            offer.proposition_dissertation = proposition
            offer_proposition_id = key.replace("txt_checkbox_", "")
            offer.offer_proposition = offer_proposition.find_by_id(int(offer_proposition_id))
            offer.save()


def is_valid(request, form):
    return form.is_valid() and detect_in_request(request, 'txt_checkbox_', 'on')


def return_prefetch_propositions():
    current_academic_year = academic_year.current_academic_year()
    return Prefetch(
        "offer_propositions",
        queryset=OfferProposition.objects.annotate(last_acronym=Subquery(
            EducationGroupYear.objects.filter(
                education_group__offer_proposition=OuterRef('pk'),
                academic_year=current_academic_year).values('acronym')[:1]
        ))
    )


###########################
#      MANAGER VIEWS      #
###########################

def _append_dissertations_count(prop):
    prop.dissertations_count = dissertation.count_by_proposition(prop)

    return prop


@login_required
@user_passes_test(adviser.is_manager)
def manager_proposition_dissertation_delete(request, pk):
    proposition = proposition_dissertation.find_by_id(pk)
    if proposition is None:
        return redirect('manager_proposition_dissertations')
    proposition.deactivate()
    return redirect('manager_proposition_dissertations')


@login_required
@user_passes_test(adviser.is_manager)
def manager_proposition_dissertation_detail(request, pk):
    prefetch_propositions = return_prefetch_propositions()
    proposition = get_object_or_404(PropositionDissertation.objects.select_related('author__person', 'creator').
                                    prefetch_related(prefetch_propositions,
                                                     'offer_propositions__education_group__educationgroupyear_set',
                                                     'propositionrole_set__adviser__person',
                                                     ), pk=pk)
    adv = request.user.person.adviser
    count_use = dissertation.count_by_proposition(proposition)
    percent = count_use * 100 / proposition.max_number_student if proposition.max_number_student else 0
    count_proposition_role = proposition_role.count_by_proposition(proposition)
    files = proposition_document_file.find_by_proposition(proposition)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role < 1:
        proposition_role.add(DissertationRoleStatus.PROMOTEUR.name, proposition.author, proposition)
    return render(request, 'manager_proposition_dissertation_detail.html',
                  {'proposition_dissertation': proposition,
                   'adviser': adv,
                   'count_use': count_use,
                   'percent': round(percent, 2),
                   'count_proposition_role': count_proposition_role,
                   'filename': filename})


@login_required
@user_passes_test(adviser.is_manager)
def manage_proposition_dissertation_edit(request, pk):
    proposition = get_object_or_404(PropositionDissertation.objects.select_related('author__person', 'creator').
                                    prefetch_related('offer_propositions__education_group__educationgroupyear_set',
                                                     'propositionrole_set__adviser__person'), pk=pk)
    offer_propositions = OfferProposition.objects.select_related('offer_proposition_group').order_by('acronym')
    offer_propositions_group = offer_proposition_group.find_all_ordered_by_name_short()
    offer_propositions_error = None
    proposition_offers = proposition.propositionoffer_set.all()
    if request.method == "POST":
        form = ManagerPropositionDissertationEditForm(request.POST, instance=proposition)
        if is_valid(request, form):
            proposition = edit_proposition(form, proposition_offers, request)
            return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)
        if not detect_in_request(request, 'txt_checkbox_', 'on'):
            offer_propositions_error = 'select_at_least_one_item'
    else:
        form = ManagerPropositionDissertationEditForm(instance=proposition)
    return render(request, 'manager_proposition_dissertation_edit.html',
                  {'prop_dissert': proposition,
                   'form': form,
                   'author': proposition.author,
                   'types_choices': PropositionDissertation.TYPES_CHOICES,
                   'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                   'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES,
                   'offer_propositions': offer_propositions,
                   'offer_propositions_error': offer_propositions_error,
                   'offer_proposition_group': offer_propositions_group,
                   'proposition_offers': proposition_offers})


@login_required
@user_passes_test(adviser.is_manager)
def manager_proposition_dissertations_jury_edit(request, pk):
    prop_role = proposition_role.get_by_id(pk)
    if prop_role is None:
        return redirect('manager_proposition_dissertations')
    proposition = prop_role.proposition_dissertation
    return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)


class PropositionDissertationJuryNewView(AjaxTemplateMixin, UserPassesTestMixin, CreateView):
    model = PropositionRole
    template_name = 'proposition_dissertations_jury_edit_inner.html'
    form_class = ManagerPropositionRoleForm
    raise_exception = True

    def test_func(self):
        return proposition_role.count_by_proposition(self.proposition) < MAX_PROPOSITION_ROLE

    def dispatch(self, request, *args, **kwargs):
        adv = get_current_adviser(request)
        if adviser_can_manage_proposition_dissertation(self.proposition, adv) \
                or user_is_proposition_promotor(request.user, self.proposition.pk) \
                or self.proposition.creator == adv.person:
            return super().dispatch(request, *args, **kwargs)
        return redirect('proposition_dissertations')

    @cached_property
    def proposition(self):
        return get_object_or_404(proposition_dissertation.PropositionDissertation, pk=self.kwargs['pk'])

    def get_initial(self):
        return {'status': dissertation_role_status, 'proposition_dissertation': self.proposition}

    def get_context_data(self, **kwargs):
        context = super(PropositionDissertationJuryNewView, self).get_context_data(**kwargs)
        context['manager'] = adviser.is_manager(self.request.user)
        return context

    def get_success_url(self):
        return None


@login_required
@user_passes_test(adviser.is_manager)
def manager_proposition_dissertations_role_delete(request, pk):
    prop_role = proposition_role.get_by_id(pk)
    if prop_role is None:
        return redirect('manager_proposition_dissertations')
    proposition = prop_role.proposition_dissertation
    prop_role.delete()
    return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(adviser.is_manager)
def manager_proposition_dissertation_new(request):
    offer_propositions = OfferProposition.objects.exclude(
        education_group=None
    ).select_related('offer_proposition_group', 'education_group')
    offer_propositions_group = offer_proposition_group.find_all_ordered_by_name_short()
    offer_propositions_error = None
    if request.method == "POST":
        form = ManagerPropositionDissertationForm(request.POST)
        if is_valid(request, form):
            person = mdl.person.find_by_user(request.user)
            proposition = create_proposition(form, person, request)
            return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)
        else:
            offer_propositions_error = 'select_at_least_one_item'
    else:
        form = ManagerPropositionDissertationForm(initial={'active': True})

    return render(request, 'manager_proposition_dissertation_new.html',
                  {'form': form,
                   'types_choices': PropositionDissertation.TYPES_CHOICES,
                   'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                   'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES,
                   'offer_propositions_error': offer_propositions_error,
                   'offer_propositions': offer_propositions,
                   'offer_proposition_group': offer_propositions_group})


@login_required
@user_passes_test(adviser.is_manager)
def manager_proposition_dissertations(request):
    current_academic_year = academic_year.current_academic_year()
    prefetch_propositions = return_prefetch_propositions()
    if 'search' in request.GET:
        terms = request.GET['search']
        propositions_dissertations = _search_proposition_dissertation(current_academic_year, prefetch_propositions,
                                                                      request, terms)
    else:
        propositions_dissertations = _get_all_proposition_by_offer(current_academic_year, prefetch_propositions,
                                                                   request)

    if 'bt_xlsx' in request.GET:
        return _export_proposition_dissertation_xlsx(propositions_dissertations)

    else:
        return render(request, "manager_proposition_dissertations_list.html",
                      {'propositions_dissertations': propositions_dissertations})


def _export_proposition_dissertation_xlsx(propositions_dissertations):
    filename = "EXPORT_propositions_{}.xlsx".format(time.strftime("%Y-%m-%d_%H:%M"))
    workbook = Workbook(encoding='utf-8')
    worksheet1 = workbook.active
    worksheet1.title = "proposition_dissertation"
    worksheet1.append(['Date_de_création', 'Teacher', 'Title',
                       'Type', 'Level', 'Collaboration', 'Maximum number of places', 'Places Remaining',
                       'Visibility', 'Active', 'Programme(s)', 'Description'])
    types_choices = dict(PropositionDissertation.TYPES_CHOICES)
    levels_choices = dict(PropositionDissertation.LEVELS_CHOICES)
    collaboration_choices = dict(PropositionDissertation.COLLABORATION_CHOICES)
    for proposition in propositions_dissertations:
        education_groups = ""
        for offer_prop in proposition.offer_propositions.all():
            education_groups += "{}, ".format(str(offer_prop.last_acronym))
        worksheet1.append([proposition.created_date,
                           str(proposition.author),
                           proposition.title,
                           str(types_choices[proposition.type]),
                           str(levels_choices[proposition.level]),
                           str(collaboration_choices[proposition.collaboration]),
                           proposition.max_number_student,
                           proposition.remaining_places if
                           proposition.remaining_places > 0 else 0,
                           proposition.visibility,
                           proposition.active,
                           education_groups,
                           proposition.description
                           ])
    response = HttpResponse(
        save_virtual_workbook(workbook),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; charset=binary')
    response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
    return response


def _get_all_proposition_by_offer(current_academic_year, prefetch_propositions, request):
    propositions_dissertations = PropositionDissertation.objects.filter(
        offer_propositions__education_group__facultyadviser__adviser__person__user=request.user,
        active=True
    ).annotate(dissertations_count=Count(
        'dissertations',
        filter=Q(
            active=True,
            dissertations__education_group_year__academic_year=current_academic_year
        ) & ~Q(dissertations__status__in=(dissertation_status.DRAFT, dissertation_status.DIR_KO))
    )).annotate(
        remaining_places=ExpressionWrapper(
            F('max_number_student') - F('dissertations_count'),
            output_field=models.IntegerField()
        )
    ).select_related('author__person', 'creator').prefetch_related(prefetch_propositions)
    return propositions_dissertations


def _search_proposition_dissertation(current_academic_year, prefetch_propositions, request, terms):
    propositions_dissertations = PropositionDissertation.objects.filter(
        offer_propositions__education_group__facultyadviser__adviser__person__user=request.user,
        active=True
    ).filter(
        Q(title__icontains=terms) |
        Q(description__icontains=terms) |
        Q(author__person__first_name__icontains=terms) |
        Q(author__person__middle_name__icontains=terms) |
        Q(author__person__last_name__icontains=terms) |
        Q(propositionoffer__offer_proposition__acronym__icontains=terms)).annotate(
        dissertations_count=Count(
            'dissertations',
            filter=Q(
                active=True,
                dissertations__education_group_year__academic_year=current_academic_year
            ) & ~Q(dissertations__status__in=(dissertation_status.DRAFT, dissertation_status.DIR_KO))
        )).annotate(
        remaining_places=ExpressionWrapper(
            F('max_number_student') - F('dissertations_count'),
            output_field=models.IntegerField()
        )).select_related('author__person', 'creator').prefetch_related(prefetch_propositions)
    return propositions_dissertations


###########################
#      TEACHER VIEWS      #
###########################


def get_current_adviser(request):
    person = mdl.person.find_by_user(request.user)
    return adviser.search_by_person(person)


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertations(request):
    prefetch_propositions = return_prefetch_propositions()
    propositions_dissertations = PropositionDissertation.objects.filter(
        active=True,
    ).select_related('author__person', 'creator').prefetch_related(prefetch_propositions)
    return render(request,
                  'proposition_dissertations_list.html',
                  {'propositions_dissertations': propositions_dissertations}
                  )


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertation_delete(request, pk):
    proposition = proposition_dissertation.find_by_id(pk)
    if proposition is None:
        return redirect('proposition_dissertations')
    proposition.deactivate()
    return redirect('proposition_dissertations')


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertation_detail(request, pk):
    current_academic_year = academic_year.current_academic_year()

    prefetch_disserts = Prefetch(
        "dissertations",
        queryset=Dissertation.objects.filter(
            active=True
        ).filter(
            education_group_year__academic_year=current_academic_year
        ).exclude(status__in=(dissertation_status.DRAFT, dissertation_status.DIR_KO))
    )
    prefetch_offer_propositions = return_prefetch_propositions()

    proposition = get_object_or_404(
        PropositionDissertation.objects.select_related(
            'author__person', 'creator'
        ).prefetch_related(
            prefetch_offer_propositions, prefetch_disserts, 'propositionrole_set__adviser__person'
        ), pk=pk
    )
    check_authorisation_of_proposition = autorized_proposition_dissert_promotor_or_manager_or_author(request.user,
                                                                                                     proposition)
    offer_propositions = proposition.offer_propositions.all()
    count_use = proposition.dissertations.all().count()
    percent = count_use * 100 / proposition.max_number_student if proposition.max_number_student else 0
    count_proposition_role = proposition.propositionrole_set.all().count()
    files = proposition_document_file.find_by_proposition(proposition)
    filename = ""
    for file in files:
        filename = file.document_file.file_name
    if count_proposition_role < 1:
        proposition_role.add(DissertationRoleStatus.PROMOTEUR.name, proposition.author, proposition)
    proposition_roles = PropositionRole.objects.filter(proposition_dissertation=proposition) \
        .select_related('adviser__person')
    return render(request, 'proposition_dissertation_detail.html',
                  {'proposition_dissertation': proposition,
                   'check_authorisation_of_proposition': check_authorisation_of_proposition,
                   'offer_propositions': offer_propositions,
                   'adviser': get_current_adviser(request),
                   'count_use': count_use,
                   'percent': round(percent, 2),
                   'proposition_roles': proposition_roles,
                   'count_proposition_role': count_proposition_role,
                   'filename': filename})


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertation_edit(request, pk):
    proposition = proposition_dissertation.find_by_id(pk)
    if proposition is None:
        return redirect('proposition_dissertations')
    adv = get_current_adviser(request)
    offer_propositions = offer_proposition.find_all_ordered_by_acronym()
    offer_propositions_group = offer_proposition_group.find_all_ordered_by_name_short()
    offer_propositions_error = None
    proposition_offers = proposition_offer.find_by_proposition_dissertation(proposition)
    if proposition.author == adv or proposition.creator == adv.person:
        if request.method == "POST":
            form = PropositionDissertationForm(request.POST, instance=proposition)
            if is_valid(request, form):
                proposition = edit_proposition(form, proposition_offers, request)
                return redirect('proposition_dissertation_detail', pk=proposition.pk)
            if not detect_in_request(request, 'txt_checkbox_', 'on'):
                offer_propositions_error = 'select_at_least_one_item'
                proposition_offers = None

        form = PropositionDissertationForm(instance=proposition)
        return render(request, 'proposition_dissertation_edit.html',
                      {'prop_dissert': proposition,
                       'form': form,
                       'types_choices': PropositionDissertation.TYPES_CHOICES,
                       'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                       'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES,
                       'offer_propositions': offer_propositions,
                       'offer_propositions_error': offer_propositions_error,
                       'proposition_offers': proposition_offers,
                       'offer_proposition_group': offer_propositions_group
                       })
    else:
        return redirect('proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(adviser.is_teacher)
def my_dissertation_propositions(request):
    prefetch_propositions = return_prefetch_propositions()
    current_academic_year = academic_year.current_academic_year()
    propositions_dissertations = PropositionDissertation.objects.filter(
        active=True,
        author=request.user.person.adviser
    ).annotate(
        dissertations_count=Count(
            'dissertations',
            filter=Q(
                active=True,
                dissertations__education_group_year__academic_year=current_academic_year
            ) & ~Q(dissertations__status__in=(dissertation_status.DRAFT, dissertation_status.DIR_KO))
        )
    ).annotate(
        remaining_places=ExpressionWrapper(
            F('max_number_student') - F('dissertations_count'),
            output_field=models.IntegerField()
        )
    ).select_related('author__person', 'creator').prefetch_related(prefetch_propositions)
    return render(request, 'proposition_dissertations_list_my.html',
                  {'propositions_dissertations': propositions_dissertations})


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertations_created(request):
    propositions_dissertations = proposition_dissertation.get_created_for_teacher(get_current_adviser(request))
    return render(request, 'proposition_dissertations_list_created.html',
                  {'propositions_dissertations': propositions_dissertations})


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertation_new(request):
    current_ac_year = academic_year.current_academic_year()
    perso = request.user.person
    offer_propositions = OfferProposition.objects.exclude(education_group=None).annotate(last_acronym=Subquery(
        EducationGroupYear.objects.filter(
            education_group__offer_proposition=OuterRef('pk'),
            academic_year=current_ac_year).values('acronym')[:1]
    )).select_related('offer_proposition_group').order_by('last_acronym')
    offer_propositions_group = offer_proposition_group.find_all_ordered_by_name_short()
    offer_propositions_error = None
    if request.method == "POST":
        form = PropositionDissertationForm(request.POST)
        if is_valid(request, form):
            proposition = create_proposition(form, perso, request)
            return redirect('proposition_dissertation_detail', pk=proposition.pk)
        else:
            offer_propositions_error = 'select_at_least_one_item'
    else:
        form = PropositionDissertationForm(initial={'author': get_current_adviser(request), 'active': True})

    return render(request, 'proposition_dissertation_new.html',
                  {'form': form,
                   'types_choices': PropositionDissertation.TYPES_CHOICES,
                   'levels_choices': PropositionDissertation.LEVELS_CHOICES,
                   'collaborations_choices': PropositionDissertation.COLLABORATION_CHOICES,
                   'offer_propositions_error': offer_propositions_error,
                   'offer_propositions': offer_propositions,
                   'offer_proposition_group': offer_propositions_group})


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertations_search(request):
    prefetch_propositions = return_prefetch_propositions()
    propositions_dissertations = proposition_dissertation.search(terms=request.GET['search'],
                                                                 active=True,
                                                                 visibility=True) \
        .select_related('author__person', 'creator').prefetch_related(prefetch_propositions)
    return render(request, "proposition_dissertations_list.html",
                  {'propositions_dissertations': propositions_dissertations})


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertations_jury_edit(request, pk):
    prop_role = proposition_role.get_by_id(pk)
    if prop_role is None:
        return redirect('proposition_dissertations')
    proposition = prop_role.proposition_dissertation
    return redirect('proposition_dissertation_detail', pk=proposition.pk)


@login_required
@user_passes_test(adviser.is_teacher)
def proposition_dissertations_role_delete(request, pk):
    prop_role = proposition_role.get_by_id(pk)
    if prop_role is None:
        return redirect('proposition_dissertations')
    proposition = prop_role.proposition_dissertation
    adv = get_current_adviser(request)

    if prop_role.status != 'PROMOTEUR' and (proposition.author == adv or proposition.creator == adv.person):
        prop_role.delete()

    return redirect('proposition_dissertation_detail', pk=proposition.pk)
