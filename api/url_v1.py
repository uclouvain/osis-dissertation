##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.urls import path, include

from dissertation.api.views.adviser import AdvisersListView
from dissertation.api.views.dissertation import DissertationListCreateView, DissertationDetailUpdateDeleteView, \
    DissertationHistoryListView, DissertationJuryDeleteView, DissertationJuryAddView, DissertationSubmitView, \
    DissertationBackToDraftView, DissertationCanManageJuryView, DissertationCanEditDissertationView, \
    DissertationFileView
from dissertation.api.views.dissertation_location import DissertationLocationsListView
from dissertation.api.views.proposition_dissertation import PropositionDissertationListView, \
    PropositionDissertationDetailView

app_name = "dissertation"
urlpatterns = [
    path('propositions', PropositionDissertationListView.as_view(), name=PropositionDissertationListView.name),
    path(
        'propositions/<uuid:uuid>/',
        PropositionDissertationDetailView.as_view(),
        name=PropositionDissertationDetailView.name,
    ),
    path('dissertation_locations', DissertationLocationsListView.as_view(), name=DissertationLocationsListView.name),
    path('advisers', AdvisersListView.as_view(), name=AdvisersListView.name),
    path('dissertations', DissertationListCreateView.as_view(), name=DissertationListCreateView.name),
    path('dissertations/<uuid:uuid>/', include(([
        path('', DissertationDetailUpdateDeleteView.as_view(), name=DissertationDetailUpdateDeleteView.name),
        path('history', DissertationHistoryListView.as_view(), name=DissertationHistoryListView.name),
        path('jury', DissertationJuryAddView.as_view(), name=DissertationJuryAddView.name),
        path(
            'jury/',
            include(([
                path(
                    '<uuid:uuid_jury_member>/',
                    DissertationJuryDeleteView.as_view(),
                    name=DissertationJuryDeleteView.name,
                ),
            ]))
        ),
        path(
            'can_manage_jury_member',
            DissertationCanManageJuryView.as_view(),
            name=DissertationCanManageJuryView.name
        ),
        path(
            'can_edit_dissertation',
            DissertationCanEditDissertationView.as_view(),
            name=DissertationCanEditDissertationView.name
        ),
        path('submit', DissertationSubmitView.as_view(), name=DissertationSubmitView.name),
        path('back_to_draft', DissertationBackToDraftView.as_view(), name=DissertationBackToDraftView.name),
        path('file', DissertationFileView.as_view(), name=DissertationFileView.name),
    ]))),
]
