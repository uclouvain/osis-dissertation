# ##################################################################################################
#   OSIS stands for Open Student Information System. It's an application                           #
#   designed to manage the core business of higher education institutions,                         #
#   such as universities, faculties, institutes and professional schools.                          #
#   The core business involves the administration of students, teachers,                           #
#   courses, programs and so on.                                                                   #
#   Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)             #
#   This program is free software: you can redistribute it and/or modify                           #
#   it under the terms of the GNU General Public License as published by                           #
#   the Free Software Foundation, either version 3 of the License, or                              #
#   (at your option) any later version.                                                            #
#   This program is distributed in the hope that it will be useful,                                #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                                 #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                  #
#   GNU General Public License for more details.                                                   #
#   A copy of this license - GNU General Public License - is available                             #
#   at the root of the source code of this program.  If not,                                       #
#   see http://www.gnu.org/licenses/.                                                              #
# ##################################################################################################
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from base.views.mixins import AjaxTemplateMixin
from dissertation.models.faculty_adviser import FacultyAdviser


class FacultyAdviserDeleteView(AjaxTemplateMixin, DeleteView):
    model = FacultyAdviser
    success_url = reverse_lazy('adviser_list')
    template_name = 'dissertation/facultyadviser_confirm_delete_inner.html'
    partial_reload = '#tb_faculty_adviser'

    def get_success_url(self):
        url = super().get_success_url() + "?"
        for offer_prop in self.request.GET['offer_proposition'].split(','):
            url += "offer_proposition={}&".format(offer_prop)

        return url
    
    def get_object(self, queryset=None):
        return FacultyAdviser.objects.filter(
            adviser__pk=self.kwargs['pk'],
            education_group__offer_proposition__pk__in=self.request.GET['offer_proposition'].split(',')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer_propositions'] = self.request.GET['offer_proposition']
        return context
