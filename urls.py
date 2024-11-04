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

from django.urls import path, re_path

from dissertation.utils import request
from dissertation.utils.request import find_adviser_list_json
from dissertation.views import (
    dissertation, proposition_dissertation, information, offer_proposition,
    upload_dissertation_file, upload_proposition_file,
)
from dissertation.views.dissertation import AdviserAutocomplete
from dissertation.views.faculty_adviser.create import FacultyAdviserCreateView
from dissertation.views.faculty_adviser.delete import FacultyAdviserDeleteView
from dissertation.views.faculty_adviser.search import OfferPropositionFilterView, AdviserList
from dissertation.views.upload_dissertation_file import DeleteDissertationFileView
from dissertation.views.upload_proposition_file import DeletePropositionFileView

urlpatterns = [
    path('adviser_list', AdviserList.as_view(), name='adviser_list'),
    path('', dissertation.dissertations, name='dissertations'),
    path('dissertations_detail/<int:pk>', dissertation.dissertations_detail,
         name='dissertations_detail'),
    path('dissertations_detail_updates/<int:pk>', dissertation.dissertations_detail_updates,
         name='dissertations_detail_updates'),
    path('dissertations_jury_new/<int:pk>', dissertation.DissertationJuryNewView.as_view(),
         name='dissertations_jury_new'),
    path('adviser-autocomplete/', AdviserAutocomplete.as_view(),
         name='adviser-autocomplete'),
    path('dissertations_list', dissertation.dissertations_list,
         name='dissertations_list'),
    path('dissertations_role_delete/<int:pk>', dissertation.dissertations_role_delete,
         name='dissertations_role_delete'),
    path('dissertations_to_dir_ko/<int:pk>', dissertation.dissertations_to_dir_ko,
         name='dissertations_to_dir_ko'),
    path('dissertations_to_dir_ok/<int:pk>', dissertation.dissertations_to_dir_ok,
         name='dissertations_to_dir_ok'),
    path('dissertations_wait_list', dissertation.dissertations_wait_list,
         name='dissertations_wait_list'),
    path('faculty_adviser_add/', FacultyAdviserCreateView.as_view(), name='faculty_adviser_add'),
    path('faculty_adviser_delete/<int:pk>', FacultyAdviserDeleteView.as_view(), name='faculty_adviser_delete'),

    path('informations/', information.informations, name='informations'),
    path('informations_add/', information.informations_add, name='informations_add'),
    path('informations_detail_stats/', information.informations_detail_stats, name='informations_detail_stats'),
    path('informations_edit/', information.informations_edit, name='informations_edit'),

    path('manager_dissertations_delete/<int:pk>', dissertation.manager_dissertations_delete,
         name='manager_dissertations_delete'),
    path('manager_dissertations_detail/<int:pk>', dissertation.manager_dissertations_detail,
         name='manager_dissertations_detail'),
    path('manager_dissertations_detail_updates/<int:pk>', dissertation.manager_dissertations_detail_updates,
         name='manager_dissertations_detail_updates'),
    path('manager_dissertations_edit/<int:pk>', dissertation.manager_dissertations_edit,
         name='manager_dissertations_edit'),
    re_path(r'^manager_dissertations_go_forward_from_list/(?P<pk>[0-9]+)/(?P<choice>[a-zA-Z]\w+)/$',
            dissertation.manager_dissertations_go_forward_from_list,
            name='manager_dissertations_go_forward_from_list'),
    path('manager_dissertations_jury_edit/<int:pk>', dissertation.manager_dissertations_jury_edit,
         name='manager_dissertations_jury_edit'),
    path('manager_dissertations_list', dissertation.manager_dissertations_list,
         name='manager_dissertations_list'),
    path('manager_dissertations_role_delete/<int:pk>', dissertation.manager_dissertations_role_delete,
         name='manager_dissertations_role_delete'),
    path('manager_dissertations_search', dissertation.manager_dissertations_search,
         name='manager_dissertations_search'),
    path('manager_dissertations_to_dir_ko/<int:pk>', dissertation.manager_dissertations_to_dir_ko,
         name='manager_dissertations_to_dir_ko'),
    path('manager_dissertations_to_dir_ok/<int:pk>', dissertation.manager_dissertations_to_dir_ok,
         name='manager_dissertations_to_dir_ok'),
    path('manager_dissertations_accept_comm_list/<int:pk>', dissertation.manager_dissertations_accept_comm_list,
         name='manager_dissertations_accept_comm_list'),
    path('manager_dissertations_accept_eval_list/<int:pk>', dissertation.manager_dissertations_accept_eval_list,
         name='manager_dissertations_accept_eval_list'),
    path('manager_dissertations_to_dir_submit/<int:pk>', dissertation.manager_dissertations_to_dir_submit,
         name='manager_dissertations_to_dir_submit'),
    path('manager_dissertations_to_dir_submit_list/<int:pk>', dissertation.manager_dissertations_to_dir_submit_list,
         name='manager_dissertations_to_dir_submit_list'),
    path('manager_dissertations_wait_list', dissertation.manager_dissertations_wait_list,
         name='manager_dissertations_wait_list'),
    path('manager_dissertations_wait_comm_list', dissertation.manager_dissertations_wait_comm_list,
         name='manager_dissertations_wait_comm_list'),
    path('manager_dissertations_wait_eval_list', dissertation.manager_dissertations_wait_eval_list,
         name='manager_dissertations_wait_eval_list'),
    path('manager_dissertations_wait_recep_list', dissertation.manager_dissertations_wait_recep_list,
         name='manager_dissertations_wait_recep_list'),
    path('manager_dissertations_wait_comm_json_list', dissertation.manager_dissertations_wait_comm_jsonlist,
         name='manager_dissertations_wait_comm_json_list'),
    path('manager_dissertation_role_list_json/<int:pk>', dissertation.manager_dissertation_role_list_json,
         name='manager_dissertation_role_list_json'),
    path('manager_dissertations_role_delete_by_ajax/<int:pk>', dissertation.manager_dissertations_role_delete_by_ajax,
         name='manager_dissertations_role_delete_by_ajax'),
    path('manager_dissertations_jury_new_ajax/', dissertation.manager_dissertations_jury_new_ajax,
         name='manager_dissertations_jury_new_ajax'),
    path('manager_students_list/', dissertation.manager_students_list, name='manager_students_list'),

    path('manager_informations/', information.manager_informations, name='manager_informations'),
    path('manager_informations_add/', information.manager_informations_add, name='manager_informations_add'),
    path('manager_informations_add_person/', information.manager_informations_add_person,
         name='manager_informations_add_person'),
    path('manager_informations_detail/<int:pk>/', information.manager_informations_detail,
         name='manager_informations_detail'),
    path('manager_informations_detail_list_wait/<int:pk>/', information.manager_informations_detail_list_wait,
         name='manager_informations_detail_list_wait'),
    path('manager_informations_detail_list/<int:pk>/', information.manager_informations_detail_list,
         name='manager_informations_detail_list'),
    path('manager_informations_detail_stats/<int:pk>/', information.manager_informations_detail_stats,
         name='manager_informations_detail_stats'),
    path('manager_informations/<int:pk>/edit/', information.manager_informations_edit,
         name='manager_informations_edit'),
    path('manager_informations_list_request/', information.manager_informations_list_request,
         name='manager_informations_list_request'),

    path('manager_offer_parameters/', offer_proposition.manager_offer_parameters, name='manager_offer_parameters'),
    path('manager_offer_parameters/edit/', offer_proposition.manager_offer_parameters_edit,
         name='manager_offer_parameters_edit'),

    path('manager_proposition_dissertations/', proposition_dissertation.manager_proposition_dissertations,
         name='manager_proposition_dissertations'),
    path('manager_proposition_dissertation/<int:pk>/delete/',
         proposition_dissertation.manager_proposition_dissertation_delete,
         name='manager_proposition_dissertation_delete'),
    path('manager_proposition_dissertation_detail/<int:pk>/',
         proposition_dissertation.manager_proposition_dissertation_detail,
         name='manager_proposition_dissertation_detail'),
    path('manager_proposition_dissertation/<int:pk>/edit/',
         proposition_dissertation.manage_proposition_dissertation_edit,
         name='manager_proposition_dissertation_edit'),
    path('manager_proposition_dissertation_jury_edit/<int:pk>',
         proposition_dissertation.manager_proposition_dissertations_jury_edit,
         name='manager_proposition_dissertations_jury_edit'),
    path('manager_proposition_dissertation_jury_new/<int:pk>',
         proposition_dissertation.PropositionDissertationJuryNewView.as_view(),
         name='manager_proposition_dissertations_jury_new'),
    path('manager_proposition_dissertations_role_delete/<int:pk>',
         proposition_dissertation.manager_proposition_dissertations_role_delete,
         name='manager_proposition_dissertations_role_delete'),
    path('manager_proposition_dissertation_new', proposition_dissertation.manager_proposition_dissertation_new,
         name='manager_proposition_dissertation_new'),
    path('find_adviser_list/', find_adviser_list_json, name='find_adviser_list_json'),

    path('my_dissertation_propositions', proposition_dissertation.my_dissertation_propositions,
         name='my_dissertation_propositions'),
    path('offer_propositions', OfferPropositionFilterView.as_view(), name='offer_propositions'),
    path('proposition_dissertations/', proposition_dissertation.proposition_dissertations,
         name='proposition_dissertations'),
    path('proposition_dissertations_created/', proposition_dissertation.proposition_dissertations_created,
         name='proposition_dissertations_created'),
    path('proposition_dissertation/<int:pk>/delete/', proposition_dissertation.proposition_dissertation_delete,
         name='proposition_dissertation_delete'),
    path('proposition_dissertation_detail/<int:pk>/', proposition_dissertation.proposition_dissertation_detail,
         name='proposition_dissertation_detail'),
    path('proposition_dissertation/<int:pk>/edit/', proposition_dissertation.proposition_dissertation_edit,
         name='proposition_dissertation_edit'),
    path('proposition_dissertation_new', proposition_dissertation.proposition_dissertation_new,
         name='proposition_dissertation_new'),
    path('proposition_dissertations_search', proposition_dissertation.proposition_dissertations_search,
         name='proposition_dissertations_search'),
    path('proposition_dissertation_jury_edit/<int:pk>', proposition_dissertation.proposition_dissertations_jury_edit,
         name='proposition_dissertations_jury_edit'),
    path('proposition_dissertations_role_delete/<int:pk>',
         proposition_dissertation.proposition_dissertations_role_delete,
         name='proposition_dissertations_role_delete'),

    re_path(r'^students_list_in_education_group_year/([0-9]+)/$', request.get_students_list_in_education_group_year,
            name='students_list'),

    path('upload/proposition_download/<int:proposition_pk>', upload_proposition_file.download,
         name='proposition_download'),
    path('upload/proposition_delete_file/<int:proposition_pk>', DeletePropositionFileView.as_view(),
         name='proposition_file_delete'),
    path('upload/proposition_save/', upload_proposition_file.save_uploaded_file, name="proposition_save_upload"),
    path('upload/dissertation_delete_file/<int:dissertation_pk>', DeleteDissertationFileView.as_view(),
         name='dissertation_file_delete'),
    path('upload/dissertation_download/<int:dissertation_pk>', upload_dissertation_file.download,
         name='dissertation_download'),
    path('upload/dissertation_save/', upload_dissertation_file.save_uploaded_file, name="dissertation_save_upload"),
]
