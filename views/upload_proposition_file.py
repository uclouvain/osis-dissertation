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
from django.http import *
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView
from rest_framework.mixins import UpdateModelMixin

from base.views.mixins import AjaxTemplateMixin
from dissertation import models as mdl
from dissertation.api.serializers.proposition_dissertation import PropositionDissertationFileSerializer
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_document_file import PropositionDocumentFile
from dissertation.perms import autorized_proposition_dissert_promotor_or_manager_or_author
from osis_common import models as mdl_osis_common
from osis_common.models.enum import storage_duration


@login_required
def download(request, proposition_pk):
    proposition = mdl.proposition_dissertation.find_by_id(proposition_pk)
    proposition_document = mdl.proposition_document_file.find_by_proposition(proposition).first()
    if proposition_document:
        filename = proposition_document.document_file.file_name
        response = HttpResponse(proposition_document.document_file.file,
                                content_type=proposition_document.document_file.content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    return redirect('manager_proposition_dissertation_detail', pk=proposition.pk)


class DeletePropositionFileView(AjaxTemplateMixin, DeleteView):
    model = PropositionDocumentFile
    template_name = 'propositiondocumentfile_confirm_delete_inner.html'

    def get_success_url(self):
        return None

    @property
    def proposition(self):
        return get_object_or_404(PropositionDissertation, pk=self.kwargs['proposition_pk'])

    def get_object(self, queryset=None):
        return PropositionDocumentFile.objects.filter(proposition=self.proposition)

    def delete(self, request, *args, **kwargs):
        self.proposition_documents = self.get_object()
        if self.proposition_documents and autorized_proposition_dissert_promotor_or_manager_or_author(request.user,
                                                                                                      self.proposition):
            for proposition_document in self.proposition_documents:
                proposition_document.delete()
            return self._ajax_response() or HttpResponseRedirect(self.get_success_url())
        return self._ajax_response() or HttpResponseRedirect(self.get_error_url())


@login_required
@require_http_methods(["POST"])
def save_uploaded_file(request):
    data = request.POST
    proposition = get_object_or_404(PropositionDissertation.objects.prefetch_related('propositiondocumentfile_set'),
                                    pk=request.POST['proposition_dissertation_id'])
    if autorized_proposition_dissert_promotor_or_manager_or_author(request.user, proposition):
        file_selected = request.FILES['file']
        file = file_selected
        file_name = file_selected.name
        content_type = file_selected.content_type
        size = file_selected.size
        description = data['description']
        documents = proposition.propositiondocumentfile_set.all()
        for document in documents:
            document.delete()
            old_document = mdl_osis_common.document_file.find_by_id(document.document_file.id)
            old_document.delete()
        new_document = mdl_osis_common.document_file.DocumentFile(file_name=file_name,
                                                                  file=file,
                                                                  description=description,
                                                                  storage_duration=storage_duration.FIVE_YEARS,
                                                                  application_name='dissertation',
                                                                  content_type=content_type,
                                                                  size=size,
                                                                  update_by=request.user)
        new_document.save()
        proposition_file = mdl.proposition_document_file.PropositionDocumentFile()
        proposition_file.proposition = proposition
        proposition_file.document_file = new_document
        proposition_file.save()
    return HttpResponse('')


class PropositionDissertationFileView(UpdateModelMixin):
    serializer_class = PropositionDissertationFileSerializer

    def get_object(self):
        return get_object_or_404(PropositionDissertation, uuid=self.kwargs.get('uuid'))

    def put(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        return response
