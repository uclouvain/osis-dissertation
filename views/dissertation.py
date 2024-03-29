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
import json
import time

from dal import autocomplete
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView
from openpyxl import Workbook
from openpyxl.utils.exceptions import IllegalCharacterError
from rest_framework import status

from base import models as mdl
from base.auth.roles import tutor
from base.models import academic_year
from base.models.academic_year import AcademicYear
from base.models.education_group import EducationGroup
from base.models.person import Person
from base.models.student import Student
from base.utils.cache import cache_filter
from base.views.mixins import AjaxTemplateMixin
from dissertation.forms import ManagerDissertationEditForm, ManagerDissertationRoleForm, \
    ManagerDissertationUpdateForm, AdviserForm, PropositionDissertationFileForm, DissertationFileForm
from dissertation.models import adviser, dissertation, dissertation_role, \
    dissertation_update, offer_proposition, proposition_role
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole, MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION
from dissertation.models.enums import dissertation_role_status
from dissertation.models.enums import dissertation_status
from dissertation.models.enums.dissertation_role_status import DissertationRoleStatus
from dissertation.models.enums.dissertation_status import DISSERTATION_STATUS
from dissertation.models.offer_proposition import OfferProposition
from dissertation.perms import adviser_can_manage, autorized_dissert_promotor_or_manager, check_for_dissert, \
    adviser_is_in_jury
from osis_common.document.xls_build import save_virtual_workbook


def _role_can_be_deleted(dissert, dissert_role):
    promotors_count = dissertation_role.count_by_status_dissertation(DissertationRoleStatus.PROMOTEUR.name, dissert)
    return dissert_role.status != DissertationRoleStatus.PROMOTEUR.name or promotors_count > 1


def new_status_display(dissert, opperation):
    new_status = dissertation.get_next_status(dissert, opperation)
    status_dict = dict(DISSERTATION_STATUS)
    return status_dict[new_status]


#########################
#      GLOBAL VIEW      #
#########################


@login_required
def dissertations(request):
    person = get_object_or_404(Person.objects.select_related('adviser'), pk=request.user.person.pk)

    if mdl.student.find_by_person(person) and not \
            tutor.find_by_person(person) and not \
            adviser.find_by_person(person):
        return redirect('home')

    elif adviser.find_by_person(person):
        count_advisers_pro_request = dissertation_role.count_by_adviser(person.adviser,
                                                                        DissertationRoleStatus.PROMOTEUR.name,
                                                                        dissertation_status.DIR_SUBMIT)

        return render(request, "dissertations.html",
                      {'section': 'dissertations',
                       'person': person,
                       'adviser': person.adviser,
                       'count_advisers_pro_request': count_advisers_pro_request})
    else:

        form = AdviserForm(request.POST or None)
        if form.is_valid():
            adv = Adviser(person=person,
                          available_by_email=False,
                          available_by_phone=False,
                          available_at_office=False)
            adv.save()
            count_advisers_pro_request = dissertation_role.count_by_adviser(adv,
                                                                            DissertationRoleStatus.PROMOTEUR.name,
                                                                            dissertation_status.DIR_SUBMIT)
            return render(request, "dissertations.html",
                          {'section': 'dissertations',
                           'person': person,
                           'adviser': adv,
                           'count_advisers_pro_request': count_advisers_pro_request})
        else:
            return render(request, 'dissertations_welcome.html', {'form': form})


###########################
#      MANAGER VIEWS      #
###########################

@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_detail(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('manager_dissertations_list')
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    count_proposition_role = proposition_role.count_by_dissertation(dissert)
    proposition_roles = proposition_role.search_by_dissertation(dissert)
    offer_prop = offer_proposition.get_by_dissertation(dissert)

    if offer_prop is None:
        return redirect('manager_dissertations_list')
    dissertation_file_form = DissertationFileForm(
        request.POST or None,
        instance=dissert
    )
    if request.method == 'POST' and dissertation_file_form.is_valid():
        dissertation_file_form.save()
        return redirect('manager_dissertations_detail', pk=dissert.pk)
    proposition_dissertation_file_form = PropositionDissertationFileForm(
        instance=dissert.proposition_dissertation
    )

    if count_proposition_role == 0 and count_dissertation_role == 0:
        justification = "%s %s %s" % (_("Auto add jury"),
                                      DissertationRoleStatus.PROMOTEUR.name,
                                      str(dissert.proposition_dissertation.author))
        dissertation_update.add(request, dissert, dissert.status, justification=justification)
        dissertation_role.add(DissertationRoleStatus.PROMOTEUR.name, dissert.proposition_dissertation.author, dissert)
    elif count_dissertation_role == 0:
        for role in proposition_roles:
            justification = "%s %s %s" % (_("Auto add jury"), role.status, str(role.adviser))
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissertation_role.add(role.status, role.adviser, dissert)

    if dissert.status == dissertation_status.DRAFT:
        jury_manager_visibility = True
        jury_manager_can_edit = False
        jury_manager_message = _("Dissertation status is draft, managers can't edit jury.")
        jury_teacher_visibility = False
        jury_teacher_can_edit = False
        jury_teacher_message = _("Dissertation status is draft, teachers can't edit jury.")
        jury_student_visibility = True
        jury_student_can_edit = offer_prop.student_can_manage_readers
        if jury_student_can_edit:
            jury_student_message = _('Dissertation status is draft, student can manage readers')
        else:
            jury_student_message = _("Dissertation status is draft, student can't manage readers")
    else:
        jury_manager_visibility = True
        jury_manager_can_edit = True
        jury_manager_message = _('Managers can see and edit jury.')
        jury_teacher_visibility = True
        jury_teacher_can_edit = offer_prop.adviser_can_suggest_reader
        if jury_teacher_can_edit:
            jury_teacher_message = _('Teachers can see and edit jury.')
        else:
            jury_teacher_message = _('Teachers can see jury but not edit it.')
        jury_student_visibility = offer_prop.in_periode_jury_visibility
        jury_student_can_edit = False
        if jury_student_visibility:
            jury_student_message = _('Jury is currently visible for the student')
        else:
            jury_student_message = _('Jury is currently invisible for the student')
    dissertation_roles = dissertation_role.search_by_dissertation(dissert)

    promotors_count = dissertation_role.count_by_status_dissertation(DissertationRoleStatus.PROMOTEUR.name, dissert)

    return render(request, 'manager_dissertations_detail.html',
                  {
                      'dissertation': dissert,
                      'adviser': adv,
                      'dissertation_roles': dissertation_roles,
                      'count_dissertation_role': count_dissertation_role,
                      'jury_manager_visibility': jury_manager_visibility,
                      'jury_manager_can_edit': jury_manager_can_edit,
                      'jury_manager_message': jury_manager_message,
                      'jury_teacher_visibility': jury_teacher_visibility,
                      'jury_teacher_can_edit': jury_teacher_can_edit,
                      'jury_teacher_message': jury_teacher_message,
                      'jury_student_visibility': jury_student_visibility,
                      'jury_student_can_edit': jury_student_can_edit,
                      'jury_student_message': jury_student_message,
                      'promotors_count': promotors_count,
                      'dissertation_file': dissertation_file_form.initial['dissertation_file'],
                      'dissertation_file_form': dissertation_file_form,
                      'proposition_dissertation_file':
                          proposition_dissertation_file_form.initial['proposition_dissertation_file'],
                      'proposition_dissertation_file_form': proposition_dissertation_file_form
                  })


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_detail_updates(request, pk):
    dissert = get_object_or_404(Dissertation.objects.prefetch_related('dissertationupdate_set'), pk=pk)
    dissertation_updates = dissert.dissertationupdate_set.all().order_by('created'). \
        select_related('person')
    return render(request, 'manager_dissertations_detail_updates.html',
                  {'dissertation': dissert,
                   'dissertation_updates': dissertation_updates})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_edit(request, pk):
    dissert = get_object_or_404(Dissertation, pk=pk)
    form = ManagerDissertationEditForm(request.POST or None, instance=dissert, user=request.user)
    if form.is_valid():
        dissert = form.save()
        justification = _("manager has edited the dissertation")
        dissertation_update.add(request, dissert, dissert.status, justification=justification)
        return redirect('manager_dissertations_detail', pk=dissert.pk)
    return render(request, 'manager_dissertations_edit.html',
                  {'form': form,
                   'dissert': dissert})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_jury_edit(request, pk):
    dissert_role = dissertation_role.find_by_id(pk)
    if dissert_role is None:
        return redirect('dissertations_list')
    if request.method == "POST":
        form = ManagerDissertationRoleForm(request.POST, instance=dissert_role)
        if form.is_valid():
            form.save()
            return redirect('manager_dissertations_detail', pk=dissert_role.dissertation.pk)
    else:
        form = ManagerDissertationRoleForm(instance=dissert_role)
    return render(request, 'manager_dissertations_jury_edit.html', {'form': form})


@require_http_methods(["POST"])
@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_jury_new_ajax(request):
    pk_dissert = request.POST.get("pk_dissertation", '')
    status_choice = request.POST.get("status_choice", '')
    id_adviser_of_dissert_role = request.POST.get("adviser_pk", '')
    if not id_adviser_of_dissert_role or not status_choice or not pk_dissert:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        dissert = dissertation.find_by_id(pk_dissert)
        adviser_of_dissert_role = adviser.get_by_id(int(id_adviser_of_dissert_role))
        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        person = mdl.person.find_by_user(request.user)
        adv_manager = adviser.search_by_person(person)
        if adviser_can_manage(dissert, adv_manager) \
                and count_dissertation_role < MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION and dissert.status != 'DRAFT' \
                and adviser_of_dissert_role is not None and dissert is not None:
            justification = "%s %s %s" % (_("Manager add jury"), status_choice, adviser_of_dissert_role)
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissertation_role.add(status_choice, adviser_of_dissert_role, dissert)
            return HttpResponse(status=status.HTTP_200_OK)
        else:
            return HttpResponse(status=status.HTTP_403_FORBIDDEN)


@login_required
@cache_filter()
@user_passes_test(adviser.is_manager)
def manager_dissertations_list(request):
    disserts = Dissertation.objects.filter(
        education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        active=True).select_related('author__person',
                                    'education_group_year',
                                    'education_group_year__academic_year',
                                    'proposition_dissertation__author__person').distinct()
    offer_props = OfferProposition.objects.filter(
        education_group__facultyadviser__adviser__person__user=request.user).distinct()
    year = timezone.now().year
    academic_year_10y = AcademicYear.objects.filter(year__gte=year - 10, year__lte=year + 1)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    return render(request, 'manager_dissertations_list.html',
                  {'dissertations': disserts,
                   'show_validation_commission': show_validation_commission,
                   'show_evaluation_first_year': show_evaluation_first_year,
                   'academic_year_10y': academic_year_10y,
                   'offer_props': offer_props})


def generate_xls(disserts):
    workbook = Workbook()
    worksheet1 = workbook.active
    worksheet1.title = "dissertations"
    worksheet1.append(['Creation_date',
                       'Student',
                       'Title',
                       'Status',
                       'Program_start',
                       'Start_academic_year',
                       'Defend Year',
                       'Role 1',
                       'Teacher 1',
                       'Role 2',
                       'Teacher 2',
                       'Role 3',
                       'Teacher 3',
                       'Role 4',
                       'Teacher 4',
                       'Description'
                       ])
    for dissert in disserts:
        try:
            line = construct_line(dissert, include_description=True)
            worksheet1.append(line)
        except IllegalCharacterError:
            line = construct_line(dissert, include_description=False)
            worksheet1.append(line)

    return save_virtual_workbook(workbook)


def construct_line(dissert, include_description=True):
    defend_year = dissert.defend_year if dissert.defend_year else '---'
    description = dissert.description.encode('utf8', 'ignore') if dissert.description and include_description else '---'
    title = dissert.title.encode('utf8', 'ignore')

    line = [dissert.creation_date,
            str(dissert.author),
            title,
            dissert.status,
            str(dissert.education_group_year.acronym),
            str(dissert.education_group_year.academic_year),
            defend_year
            ]

    line += get_ordered_roles(dissert)
    line += [description]
    return line


def get_ordered_roles(dissert):
    roles = []
    for role in DissertationRole.objects.filter(dissertation=dissert). \
            order_by('status').select_related('adviser__person'):
        if role.status == DissertationRoleStatus.PROMOTEUR.name:
            roles.insert(0, str(role.adviser))
            roles.insert(0, str(role.status))
        else:
            roles.append(str(role.status))
            roles.append(str(role.adviser))
    for x in range(8 - len(roles)):
        roles += ['---']
    return roles


@login_required
@cache_filter()
@user_passes_test(adviser.is_manager)
def manager_dissertations_search(request):
    terms = request.GET.get('search', '')
    disserts = Dissertation.objects.filter(
        education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        active=True).filter(
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
    ).select_related('author__person',
                     'education_group_year',
                     'education_group_year__academic_year',
                     'proposition_dissertation__author__person').distinct()
    offer_prop_search = request.GET.get('offer_prop_search', '')
    academic_year_search = request.GET.get('academic_year', '')
    status_search = request.GET.get('status_search', '')

    if offer_prop_search != '':
        offer_prop_search = int(offer_prop_search)
        offer_prop = offer_proposition.find_by_id(offer_prop_search)
        disserts = disserts.filter(education_group_year__education_group=offer_prop.education_group)
    if academic_year_search != '':
        academic_year_search = int(academic_year_search)
        disserts = disserts.filter(
            education_group_year__academic_year=academic_year.find_academic_year_by_id(academic_year_search)
        )
    if status_search != '':
        disserts = disserts.filter(status=status_search)
    offer_props = OfferProposition.objects.filter(
        education_group__facultyadviser__adviser__person__user=request.user).distinct()
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    year = timezone.now().year
    academic_year_10y = AcademicYear.objects.filter(year__gte=year - 10, year__lte=year + 1)

    if 'bt_xlsx' in request.GET:
        xls = generate_xls(disserts)
        filename = 'dissertations_{}.xlsx'.format(time.strftime("%Y-%m-%d_%H:%M"))
        response = HttpResponse(xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
        return response

    else:
        return render(request, "manager_dissertations_list.html",
                      {'dissertations': disserts,
                       'show_validation_commission': show_validation_commission,
                       'show_evaluation_first_year': show_evaluation_first_year,
                       'academic_year_10y': academic_year_10y,
                       'offer_props': offer_props,
                       'offer_prop_search': offer_prop_search,
                       'academic_year_search': academic_year_search,
                       'status_search': status_search
                       })


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_delete(request, pk):
    dissert = dissertation.find_by_id(pk)
    dissert.deactivate()
    dissertation_update.add(request, dissert, dissert.status, justification=_("Delete dissertation"))
    return redirect('manager_dissertations_list')


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_role_delete(request, pk):
    dissert_role = dissertation_role.find_by_id(pk)
    if dissert_role is None:
        return redirect('manager_dissertations_list')
    dissert = dissert_role.dissertation
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if adviser_can_manage(dissert, adv) and \
            _justification_dissert_role_delete_change(request, dissert, dissert_role, _("Manager deleted jury")):
        return redirect('manager_dissertations_detail', pk=dissert.pk)
    else:
        return redirect('manager_dissertations_list')


def _justification_dissert_role_delete_change(request, dissert, dissert_role, intitule):
    if dissert.status != 'DRAFT' and _role_can_be_deleted(dissert, dissert_role):
        justification = "%s %s" % (intitule, dissert_role)
        dissertation_update.add(request, dissert, dissert.status, justification=justification)
        dissert_role.delete()
        return True
    else:
        return False


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_role_delete_by_ajax(request, pk):
    dissert_role = get_object_or_404(DissertationRole.objects.select_related('dissertation'), pk=pk)
    dissert = dissert_role.dissertation
    adv = request.user.person.adviser
    if adviser_can_manage(dissert, adv) and \
            _justification_dissert_role_delete_change(request, dissert, dissert_role, _("Manager deleted jury")):
        return HttpResponse(status.HTTP_200_OK)
    else:
        return redirect('manager_dissertations_list')


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_to_dir_submit(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('manager_dissertations_list')
    old_status = dissert.status
    new_status_display_str = new_status_display(dissert, "go_forward")
    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.go_forward()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('manager_dissertations_detail', pk=pk)
    else:
        form = ManagerDissertationUpdateForm()
    return render(request, 'manager_dissertations_add_justification.html',
                  {'form': form, 'dissert': dissert, 'new_status_display': new_status_display_str})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_to_dir_submit_list(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('manager_dissertations_list')
    old_status = dissert.status
    dissert.go_forward()
    dissertation_update.add(request, dissert, old_status)
    return redirect('manager_dissertations_wait_recep_list')


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_to_dir_ok(request, pk):
    dissert = dissertation.find_by_id(pk)
    old_status = dissert.status
    new_status_display_result = new_status_display(dissert, "accept")
    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.manager_accept()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('manager_dissertations_detail', pk=pk)
    else:
        form = ManagerDissertationUpdateForm()

    return render(request, 'manager_dissertations_add_justification.html',
                  {'form': form, 'dissert': dissert, 'new_status_display': new_status_display_result})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_accept_comm_list(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('manager_dissertations_list')
    old_status = dissert.status
    dissert.manager_accept()
    dissertation_update.add(request, dissert, old_status)
    return redirect('manager_dissertations_wait_comm_list')


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_accept_eval_list(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('manager_dissertations_list')
    old_status = dissert.status
    dissert.manager_accept()
    dissertation_update.add(request, dissert, old_status)
    return redirect('manager_dissertations_wait_eval_list')


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_go_forward_from_list(request, pk, choice):
    dissert = dissertation.get_object_or_none(Dissertation, pk=pk)
    old_status = dissert.status
    if choice == 'ok':
        dissert.manager_accept()
    elif choice == 'ko':
        dissert.refuse()
    else:
        dissert.go_forward()
    dissertation_update.add(request, dissert, old_status)
    return redirect('manager_dissertations_search')


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_to_dir_ko(request, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related('author__person'), pk=pk)
    old_status = dissert.status
    new_status_display_result = new_status_display(dissert, "refuse")
    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.refuse()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('manager_dissertations_detail', pk=pk)
    else:
        form = ManagerDissertationUpdateForm()
    return render(request, 'manager_dissertations_add_justification.html',
                  {'form': form, 'dissert': dissert, 'new_status_display': new_status_display_result})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_list(request):
    offer_props = OfferProposition.objects.filter(
        education_group__facultyadviser__adviser__person__user=request.user).distinct()
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = Dissertation.objects.filter(
        education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        active=True,
        status=dissertation_status.DIR_SUBMIT).select_related('author__person',
                                                              'education_group_year__academic_year',
                                                              'proposition_dissertation__author__person')
    return render(request, 'manager_dissertations_wait_list.html',
                  {'dissertations': disserts,
                   'show_validation_commission': show_validation_commission,
                   'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_comm_list(request):
    offer_props = OfferProposition.objects.filter(
        education_group__facultyadviser__adviser__person__user=request.user).distinct()
    all_advisers_array = str(adviser.convert_advisers_to_array(adviser.Adviser.objects.all().select_related('person')))
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    return render(request, 'manager_dissertations_wait_commission_list.html',
                  {'show_validation_commission': show_validation_commission,
                   'STATUS_CHOICES': DissertationRoleStatus.choices(),
                   'show_evaluation_first_year': show_evaluation_first_year,
                   'all_advisers_array': all_advisers_array})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_comm_jsonlist(request):
    disserts = Dissertation.objects.filter(
        education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        status=dissertation_status.COM_SUBMIT,
        active=True).select_related('author__person',
                                    'education_group_year__academic_year',
                                    'education_group_year__education_group',
                                    'proposition_dissertation__author__person').distinct()
    dissert_waiting_list_json = [
        {
            'pk': dissert.pk,
            'title': dissert.title,
            'author': "{p.last_name} {p.first_name} ".format(p=dissert.author.person),
            'status': dissert.status,
            'education_group_year': str(dissert.education_group_year.academic_year),
            'education_groups': dissert.education_group_year.acronym,
            'proposition_dissertation': str(dissert.proposition_dissertation),
            'description': dissert.description
        } for dissert in disserts
    ]
    return JsonResponse(dissert_waiting_list_json, safe=False)


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertation_role_list_json(request, pk):
    dissert = get_object_or_404(Dissertation.objects.prefetch_related('dissertationrole_set__adviser__person'), pk=pk)
    dissert_roles = dissert.dissertationrole_set.all(). \
        order_by('status'). \
        select_related('dissertation', 'adviser__person')
    dissert_commission_sous_list = dissert_roles.values('pk', 'status',
                                                        first_name=F('adviser__person__first_name'),
                                                        middle_name=F('adviser__person__middle_name'),
                                                        last_name=F('adviser__person__last_name'),
                                                        dissert_pk=F('dissertation__pk')
                                                        )
    json_list = json.dumps(list(dissert_commission_sous_list))
    return HttpResponse(json_list, content_type='application/json')


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_eval_list(request):
    education_groups = EducationGroup.objects.filter(facultyadviser__adviser__person__user=request.user)
    offer_props = OfferProposition.objects.filter(education_group__in=education_groups).distinct()
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = Dissertation.objects.filter(
        education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        active=True,
        status=dissertation_status.EVA_SUBMIT).select_related('author__person',
                                                              'education_group_year__academic_year',
                                                              'proposition_dissertation__author__person')

    return render(request, 'manager_dissertations_wait_eval_list.html',
                  {'dissertations': disserts,
                   'show_validation_commission': show_validation_commission,
                   'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_recep_list(request):
    offer_props = OfferProposition.objects.filter(education_group__facultyadviser__adviser__person__user=request.user). \
        distinct()
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = Dissertation.objects.filter(
        education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        active=True,
        status=dissertation_status.TO_RECEIVE).select_related('author__person',
                                                              'education_group_year__academic_year',
                                                              'proposition_dissertation__author__person')
    return render(request, 'manager_dissertations_wait_recep_list.html',
                  {'dissertations': disserts,
                   'show_validation_commission': show_validation_commission,
                   'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(adviser.is_manager)
def manager_students_list(request):
    student_with_enrollement_in_education_groups = Student.objects.filter(
        offerenrollment__education_group_year__education_group__facultyadviser__adviser__person__user=request.user,
        offerenrollment__education_group_year__academic_year=mdl.academic_year.current_academic_year()
    ).select_related('person'). \
        prefetch_related('dissertation_set__education_group_year__education_group',
                         'dissertation_set__education_group_year__academic_year',
                         'offerenrollment_set__education_group_year__academic_year').distinct()
    return render(request,
                  'manager_students_list.html',
                  {'students': student_with_enrollement_in_education_groups})


###########################
#      TEACHER VIEWS      #
###########################

@login_required
@user_passes_test(adviser.is_teacher)
def dissertations_list(request):
    adv = request.user.person.adviser
    dissert_role = DissertationRole.objects \
        .filter(adviser=adv, dissertation__active=True) \
        .exclude(dissertation__status__in=[dissertation_status.DRAFT,
                                           dissertation_status.ENDED,
                                           dissertation_status.ENDED_WIN,
                                           dissertation_status.ENDED_LOS]) \
        .select_related('dissertation__author__person',
                        'dissertation__education_group_year__academic_year',
                        'dissertation__proposition_dissertation__author__person'
                        ).order_by('dissertation__status',
                                   'dissertation__author__person__last_name',
                                   'dissertation__author__person__first_name'
                                   )
    adviser_list_dissertations = dissert_role.filter(status=DissertationRoleStatus.PROMOTEUR.name)
    adviser_list_dissertations_copro = dissert_role.filter(status=DissertationRoleStatus.CO_PROMOTEUR.name)
    adviser_list_dissertations_reader = dissert_role.filter(status=DissertationRoleStatus.READER.name)
    adviser_list_dissertations_accompanist = dissert_role.filter(status=DissertationRoleStatus.ACCOMPANIST.name)
    adviser_list_dissertations_internship = dissert_role.filter(status=DissertationRoleStatus.INTERNSHIP.name)
    adviser_list_dissertations_president = dissert_role.filter(status=DissertationRoleStatus.PRESIDENT.name)
    adviser_list_dissertations_history = \
        DissertationRole.objects.filter(adviser=adv,
                                        dissertation__active=True,
                                        dissertation__status__in=[dissertation_status.ENDED,
                                                                  dissertation_status.ENDED_WIN,
                                                                  dissertation_status.ENDED_LOS]).select_related(
            'dissertation__author__person',
            'dissertation__education_group_year__academic_year',
            'dissertation__proposition_dissertation__author__person'
        ).order_by('dissertation__creation_date')
    return render(request, "dissertations_list.html", locals())


def teacher_can_see_dissertation(adv, dissert):
    return dissertation_role.count_by_adviser_dissertation(adv, dissert) > 0


def teacher_is_promotor(adv, dissert):
    return dissertation_role.count_by_status_adviser_dissertation('PROMOTEUR', adv, dissert) > 0


@login_required
@check_for_dissert(adviser_is_in_jury)
def dissertations_detail(request, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related(
        'author__person',
        'location',
        'education_group_year__academic_year',
        'proposition_dissertation__author__person',
        'education_group_year__education_group__offer_proposition'
    ).prefetch_related('advisers'), pk=pk)
    adv = request.user.person.adviser
    if teacher_can_see_dissertation(adv, dissert):
        count_dissertation_role = DissertationRole.objects.filter(dissertation=dissert).count()
        offer_prop = dissert.education_group_year.education_group.offer_proposition
        promotors_count = DissertationRole.objects.filter(dissertation=dissert). \
            filter(status=DissertationRoleStatus.PROMOTEUR.name).count()
        dissertation_roles = dissert.dissertationrole_set.all().order_by('status'). \
            select_related('adviser__person')
        dissertation_file_form = DissertationFileForm(
            instance=dissert
        )
        proposition_dissertation_file_form = PropositionDissertationFileForm(
            instance=dissert.proposition_dissertation
        )
        return render(
            request,
            'dissertations_detail.html',
            {
                'dissertation': dissert,
                'adviser': adv,
                'dissertation_roles': dissertation_roles,
                'count_dissertation_role': count_dissertation_role,
                'offer_prop': offer_prop,
                'promotors_count': promotors_count,
                'teacher_is_promotor': teacher_is_promotor(adv, dissert),
                'dissertation_file_form': dissertation_file_form,
                'dissertation_file': dissertation_file_form.initial['dissertation_file'],
                'proposition_dissertation_file_form': proposition_dissertation_file_form,
                'proposition_dissertation_file':
                    proposition_dissertation_file_form.initial['proposition_dissertation_file']
            }
        )
    else:
        return redirect('dissertations_list')


@login_required
@check_for_dissert(adviser_is_in_jury)
def dissertations_detail_updates(request, pk):
    dissert = get_object_or_404(Dissertation.objects.prefetch_related('dissertationupdate_set'), pk=pk)
    adv = request.user.person.adviser
    dissertation_updates = dissert.dissertationupdate_set.all().order_by('created').select_related('person')
    return render(request, 'dissertations_detail_updates.html',
                  {'dissertation': dissert,
                   'adviser': adv,
                   'dissertation_updates': dissertation_updates
                   }
                  )


@login_required
@user_passes_test(adviser.is_teacher)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def dissertations_to_dir_ok(request, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related('author__person'), pk=pk)
    old_status = dissert.status
    new_status_display_result = new_status_display(dissert, "accept")
    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.teacher_accept()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('dissertations_detail', pk=pk)
    else:
        form = ManagerDissertationUpdateForm()
    return render(
        request,
        'dissertations_add_justification.html',
        {
            'form': form,
            'dissert': dissert,
            'new_status_display': new_status_display_result
        }
    )


@login_required
@user_passes_test(adviser.is_teacher)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def dissertations_to_dir_ko(request, pk):
    dissert = get_object_or_404(Dissertation.objects.select_related('author__person'), pk=pk)
    old_status = dissert.status
    new_status_display_result = new_status_display(dissert, "refuse")
    if request.method == "POST":
        form = ManagerDissertationUpdateForm(request.POST)
        if form.is_valid():
            dissert.refuse()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, dissert, old_status, justification=justification)
            return redirect('dissertations_detail', pk=pk)
    else:
        form = ManagerDissertationUpdateForm()
    return render(
        request,
        'dissertations_add_justification.html',
        {
            'form': form,
            'dissert': dissert,
            'new_status_display': new_status_display_result
        }
    )


@login_required
@user_passes_test(adviser.is_teacher)
def dissertations_wait_list(request):
    adv = request.user.person.adviser
    disserts = Dissertation.objects.filter(
        active=True,
        status=dissertation_status.DIR_SUBMIT,
    ).filter(Q(
        dissertationrole__adviser=adv,
        dissertationrole__status=DissertationRoleStatus.PROMOTEUR.name
    )).order_by('author__person__last_name') \
        .select_related('author__person',
                        'education_group_year__academic_year',
                        'proposition_dissertation__author__person')
    return render(request, 'dissertations_wait_list.html', {'disserts': disserts})


@login_required
@user_passes_test(adviser.is_teacher)
def dissertations_role_delete(request, pk):
    dissert_role = dissertation_role.find_by_id(pk)
    if dissert_role is None:
        return redirect('dissertations_list')
    dissert = dissert_role.dissertation
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer_prop = offer_proposition.get_by_dissertation(dissert)
    if offer_prop is not None and teacher_is_promotor(adv, dissert):
        if offer_prop.adviser_can_suggest_reader and _role_can_be_deleted(dissert, dissert_role):
            justification = "%s %s" % (_("Teacher deleted jury"), str(dissert_role))
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissert_role.delete()

    return redirect('dissertations_detail', pk=dissert.pk)


class DissertationJuryNewView(AjaxTemplateMixin, UserPassesTestMixin, CreateView):
    model = DissertationRole
    template_name = 'dissertations_jury_edit_inner.html'
    form_class = ManagerDissertationRoleForm
    raise_exception = True

    def test_func(self):
        dissert = self.dissertation
        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        offer_prop = offer_proposition.get_by_dissertation(dissert)
        if offer_prop is not None:
            if adviser.is_teacher(self.request.user):
                return offer_prop.adviser_can_suggest_reader \
                       and count_dissertation_role < MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION
            if adviser.is_manager(self.request.user):
                return count_dissertation_role < MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION \
                       and dissert.status != 'DRAFT'

    def dispatch(self, request, *args, **kwargs):
        if autorized_dissert_promotor_or_manager(request.user, self.dissertation.pk):
            return super().dispatch(request, *args, **kwargs)
        return redirect('dissertations')

    @cached_property
    def dissertation(self):
        return get_object_or_404(dissertation.Dissertation, pk=self.kwargs['pk'])

    def get_initial(self):
        return {'status': dissertation_role_status, 'dissertation': self.dissertation}

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['request'] = self.request
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super(DissertationJuryNewView, self).get_context_data(**kwargs)
        context['manager'] = adviser.is_manager(self.request.user)
        return context

    def get_success_url(self):
        return None


class AdviserAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_label(self, item):
        return "{} {}, {}".format(item.person.last_name, item.person.first_name, item.person.email)

    def get_queryset(self):
        qs = Adviser.objects.all().select_related("person").order_by("person__last_name")
        if self.q:
            qs = qs.filter(Q(person__last_name__icontains=self.q) | Q(person__first_name__icontains=self.q))
        return qs
