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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import models
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404

from base import models as mdl
from base.models.academic_year import current_academic_year
from base.models.education_group import EducationGroup
from base.models.enums import person_source_type
from base.models.person import Person
from dissertation.forms import AdviserForm, ManagerAdviserForm, ManagerAddAdviserForm, ManagerAddAdviserPreForm, \
    ManagerAddAdviserPerson, AddAdviserForm
from dissertation.models import adviser
from dissertation.models import dissertation_role
from dissertation.models import faculty_adviser
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.enums import dissertation_role_status, dissertation_status
from dissertation.models.faculty_adviser import FacultyAdviser


###########################
#      TEACHER VIEWS      #
###########################


@login_required
@user_passes_test(adviser.is_teacher)
def informations(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    return render(request, "informations.html", {
        'adviser': adv,
        'first_name': adv.person.first_name.title(),
        'last_name': adv.person.last_name.title()
    })


@login_required
@user_passes_test(adviser.is_teacher)
def informations_detail_stats(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)

    advisers_pro = dissertation_role.search_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro = dissertation_role.count_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')
    tab_education_group_count_pro = dissertation_role.get_tab_count_role_by_education_group(advisers_pro)

    advisers_copro = dissertation_role.search_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    count_advisers_copro = dissertation_role.count_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    tab_education_group_count_copro = dissertation_role.get_tab_count_role_by_education_group(advisers_copro)

    advisers_reader = dissertation_role.search_by_adviser_and_role_stats(adv, 'READER')
    count_advisers_reader = dissertation_role.count_by_adviser_and_role_stats(adv, 'READER')
    tab_education_group_count_read = dissertation_role.get_tab_count_role_by_education_group(advisers_reader)

    return render(request, 'informations_detail_stats.html',
                  {
                      'adviser': adv,
                      'count_advisers_copro': count_advisers_copro,
                      'count_advisers_pro': count_advisers_pro,
                      'count_advisers_reader': count_advisers_reader,
                      'count_advisers_pro_request': count_advisers_pro_request,
                      'tab_offer_count_pro': tab_education_group_count_pro,
                      'tab_offer_count_read': tab_education_group_count_read,
                      'tab_offer_count_copro': tab_education_group_count_copro
                  })


@login_required
@user_passes_test(adviser.is_teacher)
def informations_edit(request):
    person = mdl.person.find_by_user(request.user)
    adv = adviser.search_by_person(person)
    if request.method == "POST":
        form = AdviserForm(request.POST, instance=adv)
        if form.is_valid():
            adv = form.save(commit=False)
            adv.save()
            return redirect('informations')
    else:
        form = AdviserForm(instance=adv)
    return render(request, "informations_edit.html", {
        'form': form,
        'first_name': person.first_name.title(),
        'last_name': person.last_name.title(),
        'email': person.email,
        'phone': person.phone,
        'phone_mobile': person.phone_mobile
    })


@login_required
@user_passes_test(adviser.is_teacher)
def informations_add(request):
    if request.method == "POST":
        if 'search_form' in request.POST:  # step 2 : second form to select person in list
            return _manage_search_form(request)

        else:  # step 3 : everything ok, register the person as adviser
            form = AddAdviserForm(request.POST)
            if form.is_valid():
                adv = form.save(commit=False)
                adv.save()
                return render(request, 'informations_add.html', {'adv': adv})
            else:
                return redirect('dissertations')

    else:  # step 1 : initial form to search person by email
        form = ManagerAddAdviserPreForm()
        return render(request, 'manager_informations_add_search.html', {'form': form})


def _manage_search_form(request, manager=False):
    template_prefix = 'manager_' if manager else ''
    template = template_prefix + 'informations_add_search.html'
    form = ManagerAddAdviserPreForm(request.POST)

    if form.is_valid():  # mail format is valid
        email, form, message, message_add, pers, template = _get_rendering_data(
            form,
            manager,
            template,
            template_prefix
        )
        return render(request, template, {
            'form': form,
            'message': message,
            'email': email,
            'message_add': message_add,
            'pers': pers
        })
    else:  # invalid form (invalid format for email)
        form = ManagerAddAdviserPreForm()
        message = "invalid_data"
        return render(request, template, {
            'form': form,
            'message': message
        })


def _get_rendering_data(form, manager, template, template_prefix):
    data = form.cleaned_data
    person = mdl.person.search_by_email(data['email'])
    message, email, message_add = '', '', ''
    form = ManagerAddAdviserPreForm()
    pers = None
    if not data['email']:  # empty search -> step 1
        message = "empty_data"

    elif person and adviser.find_by_person(person[0]):  # person already adviser -> step 1
        email = "%s (%s)" % (list(person)[0], data['email'])
        message = "person_already_adviser"

    elif Person.objects.filter(email=data['email']).count() > 0:  # person found and not adviser -> go forward
        pers = list(person)[0]
        form = ManagerAddAdviserForm() if manager else AddAdviserForm()
        template = template_prefix + 'informations_add.html'

    else:  # person not found by email -> step 1
        email = data['email']
        message = "person_not_found_by_mail"
        message_add = "add_new_person_explanation"
    return email, form, message, message_add, pers, template


###########################
#      MANAGER VIEWS      #
###########################


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations(request):
    dissert_status_exclued = (dissertation_status.DRAFT,
                              dissertation_status.DIR_KO,
                              dissertation_status.DIR_SUBMIT,
                              dissertation_status.ENDED_WIN,
                              dissertation_status.ENDED_LOS,
                              dissertation_status.ENDED)
    active_dissert = Q(dissertations__active=True) & ~Q(dissertations__status__in=dissert_status_exclued)

    education_groups_manager = EducationGroup.objects.filter(facultyadviser__adviser__person__user=request.user)

    advisers = Adviser.objects.filter(type='PRF').select_related('person'). \
        prefetch_related('dissertations'). \
        order_by(
        'person__last_name',
        'person__first_name') \
        .annotate(
        dissertations_count_actif_this_academic_year=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations__education_group_year_start__academic_year=current_academic_year(),
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_all_actif=models.Sum(
            models.Case(
                models.When(active_dissert, then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_all_actif_in_your_education_groups=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations__education_group_year_start__education_group__in=education_groups_manager,
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_promotor_actif=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations_roles__status=dissertation_role_status.PROMOTEUR
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_copromoteur_actif=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations_roles__status=dissertation_role_status.CO_PROMOTEUR
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_reader_actif=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations_roles__status=dissertation_role_status.READER
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_accompanist_actif=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations_roles__status=dissertation_role_status.ACCOMPANIST
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_internship_actif=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations_roles__status=dissertation_role_status.INTERNSHIP
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_president_actif=models.Sum(
            models.Case(
                models.When(active_dissert & Q(
                    dissertations_roles__status=dissertation_role_status.PRESIDENT
                ), then=1), default=0,
                output_field=models.IntegerField()
            )),
        dissertations_count_need_to_respond_actif=models.Sum(
            models.Case(
                models.When(Q(
                    dissertations__active=True,
                    dissertations__status=dissertation_status.DIR_SUBMIT,
                    dissertations_roles__status=dissertation_role_status.PROMOTEUR
                ), then=1), default=0,
                output_field=models.IntegerField()
            )))
    return render(request, 'manager_informations_list.html', {'advisers': advisers})


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_add(request):
    if request.method == "POST":
        if 'search_form' in request.POST:  # step 2 : second form to select person in list
            return _manage_search_form(request, manager=True)
        else:  # step 3 : everything ok, register the person as adviser
            form = ManagerAddAdviserForm(request.POST)
            if form.is_valid():
                adv = form.save(commit=False)
                adv.save()
                return redirect('manager_informations_detail', pk=adv.pk)
            else:
                return redirect('manager_informations')

    else:  # step 1 : initial form to search person by email
        form = ManagerAddAdviserPreForm()
        return render(request, 'manager_informations_add_search.html', {'form': form})


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_add_person(request):
    if request.method == "POST":
        form = ManagerAddAdviserPerson(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['email'] and data['last_name'] and data['first_name']:
                person = mdl.person.Person(email=data['email'],
                                           last_name=data['last_name'],
                                           first_name=data['first_name'],
                                           phone=data['phone'],
                                           phone_mobile=data['phone_mobile'],
                                           source=person_source_type.DISSERTATION)
                person.save()
                adv = adviser.add(person, 'PRF', False, False, False, '')
                return redirect('manager_informations_detail', pk=adv.pk)
            else:
                form = ManagerAddAdviserPerson()
                return render(request, 'manager_information_add_person.html', {'form': form})
        else:
            form = ManagerAddAdviserPerson()
            return render(request, 'manager_information_add_person.html', {'form': form})
    else:
        form = ManagerAddAdviserPerson()
        return render(request, 'manager_information_add_person.html', {'form': form})


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_detail(request, pk):
    adv = adviser.get_by_id(pk)
    if adv is None:
        return redirect('manager_informations')
    return render(request, 'manager_informations_detail.html',
                  {
                      'adviser': adv,
                      'first_name': adv.person.first_name.title(),
                      'last_name': adv.person.last_name.title()
                  })


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_edit(request, pk):
    adv = adviser.get_by_id(pk)
    if adv is None:
        return redirect('manager_informations')
    if request.method == "POST":
        form = ManagerAdviserForm(request.POST, instance=adv)
        if form.is_valid():
            adv = form.save(commit=False)
            adv.save()
            return redirect('manager_informations_detail', pk=adv.pk)
    else:
        form = ManagerAdviserForm(instance=adv)
    return render(request, "manager_informations_edit.html",
                  {
                      'adviser': adv,
                      'form': form,
                      'first_name': adv.person.first_name.title(),
                      'last_name': adv.person.last_name.title(),
                      'email': adv.person.email,
                      'phone': adv.person.phone,
                      'phone_mobile': adv.person.phone_mobile
                  })


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_list_request(request):
    educ_groups_of_fac_manager = FacultyAdviser.objects.filter(adviser=request.user.person.adviser).values_list(
        'education_group',
        flat=True)
    advisers_need_request = Adviser.objects.filter(type='PRF', ).filter(
        Q(
            dissertations__active=True,
            dissertations__status=dissertation_status.DIR_SUBMIT,
            dissertations_roles__status=dissertation_role_status.PROMOTEUR,
            dissertations__education_group_year_start__education_group__in=educ_groups_of_fac_manager
          )
    ).annotate(
        dissertations_count_need_to_respond_actif=models.Sum(
            models.Case(
                models.When(Q(
                    dissertations__active=True,
                    dissertations__status=dissertation_status.DIR_SUBMIT,
                    dissertations_roles__status=dissertation_role_status.PROMOTEUR,
                    dissertations__education_group_year_start__education_group__in=educ_groups_of_fac_manager
                ), then=1), default=0, output_field=models.IntegerField()
            )
        )
    ).select_related('person').prefetch_related('dissertations').order_by('person__last_name', 'person__first_name')
    return render(request, "manager_informations_list_request.html",
                  {'advisers_need_request': advisers_need_request})


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_detail_list(request, pk):
    person = mdl.person.find_by_user(request.user)
    connected_adviser = adviser.search_by_person(person)
    education_groups = faculty_adviser.find_education_groups_by_adviser(connected_adviser)
    adv = adviser.get_by_id(pk)
    if adv is None:
        return redirect('manager_informations')

    adv_list_disserts_pro = dissertation_role.search_by_adviser_and_role_and_education_groups(
        adv,
        dissertation_role_status.PROMOTEUR,
        education_groups
    )
    adv_list_disserts_copro = dissertation_role.search_by_adviser_and_role_and_education_groups(
        adv,
        dissertation_role_status.CO_PROMOTEUR,
        education_groups
    )
    adv_list_disserts_reader = dissertation_role.search_by_adviser_and_role_and_education_groups(
        adv,
        dissertation_role_status.READER,
        education_groups
    )
    adv_list_disserts_accompanist = dissertation_role.search_by_adviser_and_role_and_education_groups(
        adv,
        dissertation_role_status.ACCOMPANIST,
        education_groups
    )
    adv_list_disserts_internship = dissertation_role.search_by_adviser_and_role_and_education_groups(
        adv,
        dissertation_role_status.INTERNSHIP,
        education_groups
    )
    adv_list_disserts_president = dissertation_role.search_by_adviser_and_role_and_education_groups(
        adv,
        dissertation_role_status.PRESIDENT,
        education_groups
    )

    return render(request, "manager_informations_detail_list.html", locals())


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_detail_list_wait(request, pk):
    education_groups = request.user.person.adviser.education_groups.all()
    adv = get_object_or_404(Adviser, pk=pk)
    disserts_role = DissertationRole.objects.filter(
        status=dissertation_role_status.PROMOTEUR,
        dissertation__status=dissertation_status.DIR_SUBMIT,
        dissertation__education_group_year_start__education_group__in=education_groups,
        dissertation__active=True,
        adviser=adv
    ).select_related('adviser__person').distinct()
    return render(request, "manager_informations_detail_list_wait.html",
                  {'disserts_role': disserts_role, 'adviser': adv})


@login_required
@user_passes_test(adviser.is_manager)
def manager_informations_detail_stats(request, pk):
    adv = adviser.get_by_id(pk)
    if adv is None:
        return redirect('manager_informations')
    advisers_pro = dissertation_role.search_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro = dissertation_role.count_by_adviser_and_role_stats(adv, 'PROMOTEUR')
    count_advisers_pro_request = dissertation_role.count_by_adviser(adv, 'PROMOTEUR', 'DIR_SUBMIT')
    tab_education_group_count_pro = dissertation_role.get_tab_count_role_by_education_group(advisers_pro)

    advisers_copro = dissertation_role.search_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    count_advisers_copro = dissertation_role.count_by_adviser_and_role_stats(adv, 'CO_PROMOTEUR')
    tab_education_group_count_copro = dissertation_role.get_tab_count_role_by_education_group(advisers_copro)

    advisers_reader = dissertation_role.search_by_adviser_and_role_stats(adv, 'READER')
    count_advisers_reader = dissertation_role.count_by_adviser_and_role_stats(adv, 'READER')
    tab_education_group_count_read = dissertation_role.get_tab_count_role_by_education_group(advisers_reader)

    return render(request, 'manager_informations_detail_stats.html',
                  {
                      'adviser': adv,
                      'count_advisers_copro': count_advisers_copro,
                      'count_advisers_pro': count_advisers_pro,
                      'count_advisers_reader': count_advisers_reader,
                      'count_advisers_pro_request': count_advisers_pro_request,
                      'tab_offer_count_pro': tab_education_group_count_pro,
                      'tab_offer_count_read': tab_education_group_count_read,
                      'tab_offer_count_copro': tab_education_group_count_copro
                  })
