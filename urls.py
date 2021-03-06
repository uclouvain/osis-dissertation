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
from django.conf.urls import url

from dissertation.utils import request
from dissertation.utils.request import find_adviser_list_json
from dissertation.views import dissertation, proposition_dissertation, information, offer_proposition, \
    upload_dissertation_file, upload_proposition_file
from dissertation.views.dissertation import AdviserAutocomplete
from dissertation.views.faculty_adviser.create import FacultyAdviserCreateView
from dissertation.views.faculty_adviser.delete import FacultyAdviserDeleteView
from dissertation.views.faculty_adviser.search import OfferPropositionFilterView, AdviserList
from dissertation.views.upload_dissertation_file import DeleteDissertationFileView
from dissertation.views.upload_proposition_file import DeletePropositionFileView

urlpatterns = [
    url(r'^adviser_list$', AdviserList.as_view(), name='adviser_list'),
    url(r'^$', dissertation.dissertations, name='dissertations'),
    url(r'^dissertations_detail/(?P<pk>[0-9]+)$', dissertation.dissertations_detail,
        name='dissertations_detail'),
    url(r'^dissertations_detail_updates/(?P<pk>[0-9]+)$', dissertation.dissertations_detail_updates,
        name='dissertations_detail_updates'),
    url(r'^dissertations_jury_new/(?P<pk>[0-9]+)$', dissertation.DissertationJuryNewView.as_view(),
        name='dissertations_jury_new'),
    url(r'^adviser-autocomplete/$', AdviserAutocomplete.as_view(),
        name='adviser-autocomplete'),
    url(r'^dissertations_list$', dissertation.dissertations_list,
        name='dissertations_list'),
    url(r'^dissertations_role_delete/(?P<pk>[0-9]+)$', dissertation.dissertations_role_delete,
        name='dissertations_role_delete'),
    url(r'^dissertations_to_dir_ko/(?P<pk>[0-9]+)$', dissertation.dissertations_to_dir_ko,
        name='dissertations_to_dir_ko'),
    url(r'^dissertations_to_dir_ok/(?P<pk>[0-9]+)$', dissertation.dissertations_to_dir_ok,
        name='dissertations_to_dir_ok'),
    url(r'^dissertations_wait_list$', dissertation.dissertations_wait_list,
        name='dissertations_wait_list'),
    url(r'^faculty_adviser_add/', FacultyAdviserCreateView.as_view(), name='faculty_adviser_add'),
    url(r'^faculty_adviser_delete/(?P<pk>[0-9]+)$', FacultyAdviserDeleteView.as_view(), name='faculty_adviser_delete'),

    url(r'^informations/$', information.informations, name='informations'),
    url(r'^informations_add/$', information.informations_add, name='informations_add'),
    url(r'^informations_detail_stats/$', information.informations_detail_stats, name='informations_detail_stats'),
    url(r'^informations_edit/$', information.informations_edit, name='informations_edit'),

    url(r'^manager_dissertations_delete/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_delete,
        name='manager_dissertations_delete'),
    url(r'^manager_dissertations_detail/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_detail,
        name='manager_dissertations_detail'),
    url(r'^manager_dissertations_detail_updates/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_detail_updates,
        name='manager_dissertations_detail_updates'),
    url(r'^manager_dissertations_edit/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_edit,
        name='manager_dissertations_edit'),
    url(r'^manager_dissertations_go_forward_from_list/(?P<pk>[0-9]+)/(?P<choice>[a-zA-Z]\w+)/$',
        dissertation.manager_dissertations_go_forward_from_list,
        name='manager_dissertations_go_forward_from_list'),
    url(r'^manager_dissertations_jury_edit/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_jury_edit,
        name='manager_dissertations_jury_edit'),
    url(r'^manager_dissertations_list$', dissertation.manager_dissertations_list,
        name='manager_dissertations_list'),
    url(r'^manager_dissertations_role_delete/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_role_delete,
        name='manager_dissertations_role_delete'),
    url(r'^manager_dissertations_search$', dissertation.manager_dissertations_search,
        name='manager_dissertations_search'),
    url(r'^manager_dissertations_to_dir_ko/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_to_dir_ko,
        name='manager_dissertations_to_dir_ko'),
    url(r'^manager_dissertations_to_dir_ok/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_to_dir_ok,
        name='manager_dissertations_to_dir_ok'),
    url(r'^manager_dissertations_accept_comm_list/(?P<pk>[0-9]+)$',
        dissertation.manager_dissertations_accept_comm_list,
        name='manager_dissertations_accept_comm_list'),
    url(r'^manager_dissertations_accept_eval_list/(?P<pk>[0-9]+)$',
        dissertation.manager_dissertations_accept_eval_list,
        name='manager_dissertations_accept_eval_list'),
    url(r'^manager_dissertations_to_dir_submit/(?P<pk>[0-9]+)$', dissertation.manager_dissertations_to_dir_submit,
        name='manager_dissertations_to_dir_submit'),
    url(r'^manager_dissertations_to_dir_submit_list/(?P<pk>[0-9]+)$',
        dissertation.manager_dissertations_to_dir_submit_list,
        name='manager_dissertations_to_dir_submit_list'),
    url(r'^manager_dissertations_wait_list$', dissertation.manager_dissertations_wait_list,
        name='manager_dissertations_wait_list'),
    url(r'^manager_dissertations_wait_comm_list$', dissertation.manager_dissertations_wait_comm_list,
        name='manager_dissertations_wait_comm_list'),
    url(r'^manager_dissertations_wait_eval_list$', dissertation.manager_dissertations_wait_eval_list,
        name='manager_dissertations_wait_eval_list'),
    url(r'^manager_dissertations_wait_recep_list$', dissertation.manager_dissertations_wait_recep_list,
        name='manager_dissertations_wait_recep_list'),
    url(r'^manager_dissertations_wait_comm_json_list$', dissertation.manager_dissertations_wait_comm_jsonlist,
        name='manager_dissertations_wait_comm_json_list'),
    url(r'^manager_dissertation_role_list_json/(?P<pk>[0-9]+)$', dissertation.manager_dissertation_role_list_json,
        name='manager_dissertation_role_list_json'),
    url(r'^manager_dissertations_role_delete_by_ajax/(?P<pk>[0-9]+)$',
        dissertation.manager_dissertations_role_delete_by_ajax,
        name='manager_dissertations_role_delete_by_ajax'),
    url(r'^manager_dissertations_jury_new_ajax/', dissertation.manager_dissertations_jury_new_ajax,
        name='manager_dissertations_jury_new_ajax'),
    url(r'^manager_students_list/$', dissertation.manager_students_list, name='manager_students_list'),

    url(r'^manager_informations/$', information.manager_informations, name='manager_informations'),
    url(r'^manager_informations_add/$', information.manager_informations_add, name='manager_informations_add'),
    url(r'^manager_informations_add_person/$', information.manager_informations_add_person,
        name='manager_informations_add_person'),
    url(r'^manager_informations_detail/(?P<pk>[0-9]+)/$', information.manager_informations_detail,
        name='manager_informations_detail'),
    url(r'^manager_informations_detail_list_wait/(?P<pk>[0-9]+)/$', information.manager_informations_detail_list_wait,
        name='manager_informations_detail_list_wait'),
    url(r'^manager_informations_detail_list/(?P<pk>[0-9]+)/$', information.manager_informations_detail_list,
        name='manager_informations_detail_list'),
    url(r'^manager_informations_detail_stats/(?P<pk>[0-9]+)/$', information.manager_informations_detail_stats,
        name='manager_informations_detail_stats'),
    url(r'^manager_informations/(?P<pk>[0-9]+)/edit/$', information.manager_informations_edit,
        name='manager_informations_edit'),
    url(r'^manager_informations_list_request/$', information.manager_informations_list_request,
        name='manager_informations_list_request'),

    url(r'^manager_offer_parameters/$', offer_proposition.manager_offer_parameters, name='manager_offer_parameters'),
    url(r'^manager_offer_parameters/edit/$', offer_proposition.manager_offer_parameters_edit,
        name='manager_offer_parameters_edit'),

    url(r'^manager_proposition_dissertations/$', proposition_dissertation.manager_proposition_dissertations,
        name='manager_proposition_dissertations'),
    url(r'^manager_proposition_dissertation/(?P<pk>[0-9]+)/delete/$',
        proposition_dissertation.manager_proposition_dissertation_delete,
        name='manager_proposition_dissertation_delete'),
    url(r'^manager_proposition_dissertation_detail/(?P<pk>[0-9]+)/$',
        proposition_dissertation.manager_proposition_dissertation_detail,
        name='manager_proposition_dissertation_detail'),
    url(r'^manager_proposition_dissertation/(?P<pk>[0-9]+)/edit/$',
        proposition_dissertation.manage_proposition_dissertation_edit, name='manager_proposition_dissertation_edit'),
    url(r'^manager_proposition_dissertation_jury_edit/(?P<pk>[0-9]+)$',
        proposition_dissertation.manager_proposition_dissertations_jury_edit,
        name='manager_proposition_dissertations_jury_edit'),
    url(r'^manager_proposition_dissertation_jury_new/(?P<pk>[0-9]+)$',
        proposition_dissertation.PropositionDissertationJuryNewView.as_view(),
        name='manager_proposition_dissertations_jury_new'),
    url(r'^manager_proposition_dissertations_role_delete/(?P<pk>[0-9]+)$',
        proposition_dissertation.manager_proposition_dissertations_role_delete,
        name='manager_proposition_dissertations_role_delete'),
    url(r'^manager_proposition_dissertation_new$', proposition_dissertation.manager_proposition_dissertation_new,
        name='manager_proposition_dissertation_new'),
    url(r'^find_adviser_list/', find_adviser_list_json, name='find_adviser_list_json'),

    url(r'^my_dissertation_propositions$', proposition_dissertation.my_dissertation_propositions,
        name='my_dissertation_propositions'),
    url(r'^offer_propositions$', OfferPropositionFilterView.as_view(), name='offer_propositions'),
    url(r'^proposition_dissertations/$', proposition_dissertation.proposition_dissertations,
        name='proposition_dissertations'),
    url(r'^proposition_dissertations_created/$', proposition_dissertation.proposition_dissertations_created,
        name='proposition_dissertations_created'),
    url(r'^proposition_dissertation/(?P<pk>[0-9]+)/delete/$', proposition_dissertation.proposition_dissertation_delete,
        name='proposition_dissertation_delete'),
    url(r'^proposition_dissertation_detail/(?P<pk>[0-9]+)/$', proposition_dissertation.proposition_dissertation_detail,
        name='proposition_dissertation_detail'),
    url(r'^proposition_dissertation/(?P<pk>[0-9]+)/edit/$', proposition_dissertation.proposition_dissertation_edit,
        name='proposition_dissertation_edit'),
    url(r'^proposition_dissertation_new$', proposition_dissertation.proposition_dissertation_new,
        name='proposition_dissertation_new'),
    url(r'^proposition_dissertations_search$', proposition_dissertation.proposition_dissertations_search,
        name='proposition_dissertations_search'),
    url(r'^proposition_dissertation_jury_edit/(?P<pk>[0-9]+)$',
        proposition_dissertation.proposition_dissertations_jury_edit,
        name='proposition_dissertations_jury_edit'),
    url(r'^proposition_dissertations_role_delete/(?P<pk>[0-9]+)$',
        proposition_dissertation.proposition_dissertations_role_delete,
        name='proposition_dissertations_role_delete'),

    url(r'^students_list_in_education_group_year/([0-9]+)/$', request.get_students_list_in_education_group_year, name='students_list'),

    url(r'^upload/proposition_download/(?P<proposition_pk>[0-9]+)$', upload_proposition_file.download,
        name='proposition_download'),
    url(r'^upload/proposition_delete_file/(?P<proposition_pk>[0-9]+)$',
        DeletePropositionFileView.as_view(),
        name='proposition_file_delete'),
    url(r'^upload/proposition_save/$', upload_proposition_file.save_uploaded_file, name="proposition_save_upload"),
    url(r'^upload/dissertation_delete_file/(?P<dissertation_pk>[0-9]+)$',
        DeleteDissertationFileView.as_view(),
        name='dissertation_file_delete'),
    url(r'^upload/dissertation_download/(?P<dissertation_pk>[0-9]+)$', upload_dissertation_file.download,
        name='dissertation_download'),
    url(r'^upload/dissertation_save/$', upload_dissertation_file.save_uploaded_file, name="dissertation_save_upload"),
]
