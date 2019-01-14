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
import json
import time

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse,JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from openpyxl import Workbook
from openpyxl.utils.exceptions import IllegalCharacterError
from openpyxl.writer.excel import save_virtual_workbook
from rest_framework import status

from base import models as mdl
from base.models import academic_year, offer_enrollment
from base.views import layout
from dissertation.forms import ManagerDissertationForm, ManagerDissertationEditForm, ManagerDissertationRoleForm, \
    ManagerDissertationUpdateForm, AdviserForm
from dissertation.models import adviser, dissertation, dissertation_document_file, dissertation_role, \
    dissertation_update, faculty_adviser, offer_proposition, proposition_dissertation, proposition_role
from dissertation.models.dissertation_role import DissertationRole, MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION
from dissertation.models.enums import dissertation_role_status
from dissertation.models.enums import dissertation_status
from dissertation.models.enums.dissertation_status import DISSERTATION_STATUS
from dissertation.perms import adviser_can_manage, autorized_dissert_promotor_or_manager, check_for_dissert, \
    adviser_is_in_jury


def _role_can_be_deleted(dissert, dissert_role):
    promotors_count = dissertation_role.count_by_status_dissertation(dissertation_role_status.PROMOTEUR, dissert)
    return dissert_role.status != dissertation_role_status.PROMOTEUR or promotors_count > 1


def new_status_display(dissert, opperation):
    new_status = dissertation.get_next_status(dissert, opperation)
    status_dict = dict(DISSERTATION_STATUS)
    return status_dict[new_status]


#########################
#      GLOBAL VIEW      #
#########################


@login_required
def dissertations(request):
    person = mdl.person.find_by_user(request.user)

    if mdl.student.find_by_person(person) and not \
            mdl.tutor.find_by_person(person) and not \
            adviser.find_by_person(person):
            return redirect('home')

    elif adviser.find_by_person(person):
        adv = adviser.search_by_person(person)
        count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')

        return layout.render(request, "dissertations.html",
                             {'section': 'dissertations',
                              'person': person,
                              'adviser': adv,
                              'count_advisers_pro_request': count_advisers_pro_request})
    else:
        if request.method == "POST":
            form = AdviserForm(request.POST)
            if form.is_valid():
                adv = adviser.Adviser(person=person, available_by_email=False, available_by_phone=False,
                                      available_at_office=False)
                adv.save()
                adv = adviser.search_by_person(person)
                count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')

                return layout.render(request, "dissertations.html",
                                     {'section': 'dissertations',
                                      'person': person,
                                      'adviser': adv,
                                      'count_advisers_pro_request': count_advisers_pro_request})
        else:
            form = AdviserForm()
            return layout.render(request, 'dissertations_welcome.html', {'form': form})


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
    files = dissertation_document_file.find_by_dissertation(dissert)
    filename = files[-1].document_file.file_name if files else ""

    if count_proposition_role == 0 and count_dissertation_role == 0:
            justification = "%s %s %s" % (_("Auto add jury"),
                                          dissertation_role_status.PROMOTEUR,
                                          str(dissert.proposition_dissertation.author))
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissertation_role.add(dissertation_role_status.PROMOTEUR, dissert.proposition_dissertation.author, dissert)
    elif count_dissertation_role == 0:
        for role in proposition_roles:
            justification = "%s %s %s" % (_("Auto add jury"), role.status, str(role.adviser))
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            dissertation_role.add(role.status, role.adviser, dissert)

    if dissert.status == dissertation_status.DRAFT:
        jury_manager_visibility = True
        jury_manager_can_edit = False
        jury_manager_message =  _("Dissertation status is draft, managers can't edit jury.")
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

    promotors_count = dissertation_role.count_by_status_dissertation(dissertation_role_status.PROMOTEUR, dissert)

    return layout.render(request, 'manager_dissertations_detail.html',
                         {'dissertation': dissert,
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
                          'filename': filename})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_detail_updates(request, pk):
    dissert = dissertation.find_by_id(pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    dissertation_updates = dissertation_update.search_by_dissertation(dissert)

    return layout.render(request, 'manager_dissertations_detail_updates.html',
                         {'dissertation': dissert,
                          'adviser': adv,
                          'dissertation_updates': dissertation_updates})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_edit(request, pk):
    dissert = dissertation.find_by_id(pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    if request.method == "POST":
        form = ManagerDissertationEditForm(request.POST, instance=dissert)
        if form.is_valid():
            dissert = form.save()
            justification = _("manager has edited the dissertation")
            dissertation_update.add(request, dissert, dissert.status, justification=justification)
            return redirect('manager_dissertations_detail', pk=dissert.pk)
        else:
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.find_by_education_groups(
                education_groups)
            form.fields["author"].queryset = mdl.student.Student.objects.filter(
                offerenrollment__education_group_year__education_group__in=education_groups
            ).order_by(
                'person__last_name', 'person__first_name'
            ).distinct()
            form.fields["education_group_year_start"].queryset = \
                mdl.education_group_year.EducationGroupYear.objects.filter(education_group__in=education_groups)
    else:
        form = ManagerDissertationEditForm(instance=dissert)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.find_by_education_groups(
            education_groups
        )
        form.fields["author"].queryset = mdl.student.Student.objects.filter(
                offerenrollment__education_group_year__education_group__in=education_groups
            ).order_by(
                'person__last_name', 'person__first_name'
            ).distinct()
        form.fields["education_group_year_start"].queryset = mdl.education_group_year.EducationGroupYear.objects.filter(
                education_group__in=education_groups)

    return layout.render(
        request, 'manager_dissertations_edit.html',
        {'form': form,
         'dissert': dissert,
         'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES})


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
    return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form})


@login_required
@user_passes_test(adviser.is_manager)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def manager_dissertations_jury_new(request, pk):
    dissert = dissertation.find_by_id(pk)
    count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
    if count_dissertation_role < MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION and dissert.status != 'DRAFT':
        if request.method == "POST":
            form = ManagerDissertationRoleForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                status = data['status']
                adv = data['adviser']
                diss = data['dissertation']
                justification = "%s %s %s" % (_("Manager add jury"), str(status), str(adv))
                dissertation_update.add(request, dissert, dissert.status, justification=justification)
                dissertation_role.add(status, adv, diss)
                return redirect('manager_dissertations_detail', pk=dissert.pk)
            else:
                form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
        else:
            form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
        return layout.render(request, 'manager_dissertations_jury_edit.html', {'form': form, 'dissert': dissert})
    else:
        return redirect('manager_dissertations_detail', pk=dissert.pk)


@require_http_methods(["POST"])
@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_jury_new_ajax(request):
    pk_dissert = request.POST.get("pk_dissertation", '')
    status_choice = request.POST.get("status_choice", '')
    id_adviser_of_dissert_role=request.POST.get("adviser_pk", '')
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
@user_passes_test(adviser.is_manager)
def manager_dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    disserts = dissertation.search_by_education_group(education_groups)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    start_date=timezone.now().replace(year=timezone.now().year - 10)
    end_date=timezone.now().replace(year=timezone.now().year + 1)
    academic_year_10y = academic_year.find_academic_years(end_date,start_date)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    return layout.render(request, 'manager_dissertations_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year,
                          'academic_year_10y': academic_year_10y,
                          'offer_props':offer_props})


def generate_xls(disserts):
    workbook = Workbook(encoding='utf-8')
    worksheet1 = workbook.active
    worksheet1.title = "dissertations"
    worksheet1.append(['Creation_date',
                       'Student',
                       'Title',
                       'Status',
                       'Year + Program Start',
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
            str(dissert.education_group_year_start),
            defend_year
            ]

    line += get_ordered_roles(dissert)
    line += [description]
    return line


def get_ordered_roles(dissert):
    roles = []
    for role in dissertation_role.search_by_dissertation(dissert):
        if role.status == dissertation_role_status.PROMOTEUR:
            roles.insert(0, str(role.adviser))
            roles.insert(0, str(role.status))
        else:
            roles.append(str(role.status))
            roles.append(str(role.adviser))
    for x in range(8 - len(roles)):
        roles += ['---']
    return roles


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    disserts = dissertation.search(terms=request.GET.get('search',''), active=True)
    disserts = disserts.filter(education_group_year_start__education_group__in=education_groups)
    offer_prop_search = request.GET.get('offer_prop_search','')
    academic_year_search=request.GET.get('academic_year','')
    status_search=request.GET.get('status_search','')

    if offer_prop_search!='':
        offer_prop_search=int(offer_prop_search)
        offer_prop=offer_proposition.find_by_id(offer_prop_search)
        disserts = disserts.filter(education_group_year_start__education_group=offer_prop.education_group)
    if academic_year_search!='':
        academic_year_search = int(academic_year_search)
        disserts = disserts.filter(
            education_group_year_start__academic_year=academic_year.find_academic_year_by_id(academic_year_search)
        )
    if status_search!='':
        disserts = disserts.filter(status=status_search)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    start_date=timezone.now().replace(year=timezone.now().year - 10)
    end_date=timezone.now().replace(year=timezone.now().year + 1)
    academic_year_10y = academic_year.find_academic_years(end_date,start_date)

    if 'bt_xlsx' in request.GET:
        xls = generate_xls(disserts)
        filename = 'dissertations_{}.xlsx'.format(time.strftime("%Y-%m-%d_%H:%M"))
        response = HttpResponse(xls, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)
        return response

    else:
        return layout.render(request, "manager_dissertations_list.html",
                                      {'dissertations': disserts,
                                       'show_validation_commission': show_validation_commission,
                                       'show_evaluation_first_year': show_evaluation_first_year,
                                       'academic_year_10y': academic_year_10y,
                                       'offer_props':offer_props,
                                       'offer_prop_search':offer_prop_search,
                                       'academic_year_search':academic_year_search,
                                       'status_search':status_search
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
    dissert_role = get_object_or_404(DissertationRole, pk=pk)
    dissert = dissert_role.dissertation
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
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
    return layout.render(request, 'manager_dissertations_add_justification.html',
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

    return layout.render(request, 'manager_dissertations_add_justification.html',
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
def manager_dissertations_to_dir_ko(request, pk):
    dissert = dissertation.find_by_id(pk)
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

    return layout.render(request, 'manager_dissertations_add_justification.html',
                         {'form': form, 'dissert': dissert, 'new_status_display': new_status_display_result})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_education_group_and_status(education_groups, "DIR_SUBMIT")

    return layout.render(request, 'manager_dissertations_wait_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_comm_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    all_advisers_array = str(adviser.convert_advisers_to_array(adviser.find_all_advisers()))
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    return layout.render(request, 'manager_dissertations_wait_commission_list.html',
                         {'show_validation_commission': show_validation_commission,
                          'STATUS_CHOICES': dissertation_role_status.STATUS_CHOICES,
                          'show_evaluation_first_year': show_evaluation_first_year,
                          'all_advisers_array': all_advisers_array})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_comm_jsonlist(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    disserts = dissertation.search_by_education_group_and_status(education_groups, "COM_SUBMIT")
    dissert_waiting_list_json = [
        {
            'pk': dissert.pk,
            'title': dissert.title,
            'author': "{p.last_name} {p.first_name} ".format(p=dissert.author.person),
            'status': dissert.status,
            'education_group_year': str(dissert.education_group_year_start.academic_year),
            'education_groups': dissert.education_group_year_start.acronym,
            'proposition_dissertation': str(dissert.proposition_dissertation),
            'description': dissert.description
        } for dissert in disserts
    ]
    return JsonResponse(dissert_waiting_list_json, safe=False)


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertation_role_list_json(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('manager_dissertations_list')
    dissert_roles = dissertation_role.search_by_dissertation(dissert)
    dissert_commission_sous_list = [
        {
            'pk': dissert_role.pk,
            'first_name': str(dissert_role.adviser.person.first_name),
            'middle_name': str(dissert_role.adviser.person.middle_name),
            'last_name': str(dissert_role.adviser.person.last_name),
            'status': str(dissert_role.status),
            'dissert_pk': dissert_role.dissertation.pk
        }for dissert_role in dissert_roles
    ]
    json_list = json.dumps(dissert_commission_sous_list)
    return HttpResponse(json_list, content_type='application/json')


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_eval_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_education_group_and_status(education_groups, "EVA_SUBMIT")

    return layout.render(request, 'manager_dissertations_wait_eval_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(adviser.is_manager)
def manager_dissertations_wait_recep_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(adv)
    offer_props = offer_proposition.search_by_education_group(education_groups)
    show_validation_commission = offer_proposition.show_validation_commission(offer_props)
    show_evaluation_first_year = offer_proposition.show_evaluation_first_year(offer_props)
    disserts = dissertation.search_by_education_group_and_status(education_groups, "TO_RECEIVE")

    return layout.render(request, 'manager_dissertations_wait_recep_list.html',
                         {'dissertations': disserts,
                          'show_validation_commission': show_validation_commission,
                          'show_evaluation_first_year': show_evaluation_first_year})


@login_required
@user_passes_test(adviser.is_manager)
def manager_students_list(request):
    current_manager = adviser.search_by_person(mdl.person.find_by_user(request.user))
    education_groups = faculty_adviser.find_education_groups_by_adviser(current_manager)
    education_groups_years = mdl.education_group_year.EducationGroupYear.objects.filter(
        education_group__in=education_groups,
        academic_year=mdl.academic_year.starting_academic_year()
    )
    offer_enroll = mdl.offer_enrollment.OfferEnrollment.objects.filter(
        education_group_year__in=education_groups_years
    ).select_related(
        'student', 'education_group_year'
    ).prefetch_related('student__dissertation_set')
    return layout.render(request, 'manager_students_list.html', {'offer_enrollements': offer_enroll})


###########################
#      TEACHER VIEWS      #
###########################

@login_required
@user_passes_test(adviser.is_teacher)
def dissertations_list(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    adviser_list_dissertations = dissertation_role.search_by_adviser_and_role(adv, 'PROMOTEUR')
    adviser_list_dissertations_copro = dissertation_role.search_by_adviser_and_role(adv, 'CO_PROMOTEUR')
    adviser_list_dissertations_reader = dissertation_role.search_by_adviser_and_role(adv, 'READER')
    adviser_list_dissertations_accompanist = dissertation_role.search_by_adviser_and_role(adv, 'ACCOMPANIST')
    adviser_list_dissertations_internship = dissertation_role.search_by_adviser_and_role(adv, 'INTERNSHIP')
    adviser_list_dissertations_president = dissertation_role.search_by_adviser_and_role(adv, 'PRESIDENT')

    return layout.render(request, "dissertations_list.html", locals())


@login_required
@user_passes_test(adviser.is_teacher)
def dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    disserts = dissertation.search_by_proposition_author(terms=request.GET['search'],
                                                         active=True,
                                                         proposition_author=adv)
    return layout.render(request, "dissertations_list.html", {'dissertations': disserts})


def teacher_can_see_dissertation(adv, dissert):
    return dissertation_role.count_by_adviser_dissertation(adv, dissert) > 0


def teacher_is_promotor(adv, dissert):
    return dissertation_role.count_by_status_adviser_dissertation('PROMOTEUR', adv, dissert) > 0


@login_required
@check_for_dissert(adviser_is_in_jury)
def dissertations_detail(request, pk):
    dissert = dissertation.find_by_id(pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)

    if teacher_can_see_dissertation(adv, dissert):
        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        offer_prop = offer_proposition.get_by_dissertation(dissert)
        if offer_prop is None:
            return redirect('dissertations_list')

        promotors_count = dissertation_role.count_by_status_dissertation('PROMOTEUR', dissert)

        files = dissertation_document_file.find_by_dissertation(dissert)
        filename = ""
        for file in files:
            filename = file.document_file.file_name

        dissertation_roles = dissertation_role.search_by_dissertation(dissert)
        return layout.render(request, 'dissertations_detail.html',
                             {'dissertation': dissert,
                              'adviser': adv,
                              'dissertation_roles': dissertation_roles,
                              'count_dissertation_role': count_dissertation_role,
                              'offer_prop': offer_prop,
                              'promotors_count': promotors_count,
                              'teacher_is_promotor': teacher_is_promotor(adv, dissert),
                              'filename': filename})
    else:
        return redirect('dissertations_list')


@login_required
@check_for_dissert(adviser_is_in_jury)
def dissertations_detail_updates(request, pk):
    dissert = dissertation.find_by_id(pk)
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    dissertation_updates = dissertation_update.search_by_dissertation(dissert)
    return layout.render(
        request,
        'dissertations_detail_updates.html',
        {
            'dissertation': dissert,
            'adviser': adv,
            'dissertation_updates': dissertation_updates
        }
    )


@login_required
@user_passes_test(adviser.is_teacher)
@check_for_dissert(autorized_dissert_promotor_or_manager)
def dissertations_to_dir_ok(request, pk):
    dissert = dissertation.find_by_id(pk)
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
    return layout.render(
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
    dissert = dissertation.find_by_id(pk)
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
    return layout.render(
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
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    roles_list_dissertations = dissertation_role.search_by_adviser_and_role_and_status(adv, "PROMOTEUR", "DIR_SUBMIT")

    return layout.render(request, 'dissertations_wait_list.html',
                         {'roles_list_dissertations': roles_list_dissertations})


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


@login_required
@user_passes_test(adviser.is_teacher)
def dissertations_jury_new(request, pk):
    dissert = dissertation.find_by_id(pk)
    if dissert is None:
        return redirect('dissertations_list')
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    offer_prop = offer_proposition.get_by_dissertation(dissert)
    if offer_prop is not None and teacher_is_promotor(adv, dissert):
        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        if count_dissertation_role < MAX_DISSERTATION_ROLE_FOR_ONE_DISSERTATION \
                and offer_prop.adviser_can_suggest_reader:
            if request.method == "POST":
                form = ManagerDissertationRoleForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    status = data['status']
                    adv = data['adviser']
                    diss = data['dissertation']
                    justification = "%s %s %s" % (_("Teacher added jury"), str(status), str(adv))
                    dissertation_update.add(request, dissert, dissert.status, justification=justification)
                    dissertation_role.add(status, adv, diss)
                    return redirect('dissertations_detail', pk=dissert.pk)
                else:
                    form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
            else:
                form = ManagerDissertationRoleForm(initial={'dissertation': dissert})
            return layout.render(
                request,
                'dissertations_jury_edit.html',
                {
                    'form': form,
                    'dissert': dissert,
                }
            )

    return redirect('dissertations_detail', pk=dissert.pk)
