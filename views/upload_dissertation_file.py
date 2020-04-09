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
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import *
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import DeleteView

from base.views.mixins import AjaxTemplateMixin
from dissertation import models as mdl
from dissertation.models import adviser, dissertation_update
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_document_file import DissertationDocumentFile
from dissertation.perms import autorized_dissert_promotor_or_manager
from osis_common import models as mdl_osis_common
from osis_common.decorators.download import set_download_cookie
from osis_common.models.enum import storage_duration


@login_required
@set_download_cookie
def download(request, dissertation_pk):
    dissertation = mdl.dissertation.find_by_id(dissertation_pk)
    dissertation_document = mdl.dissertation_document_file.find_by_dissertation(dissertation).first()
    if dissertation_document:
        filename = dissertation_document.document_file.file_name
        response = HttpResponse(dissertation_document.document_file.file,
                                content_type=dissertation_document.document_file.content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    return redirect('manager_dissertations_detail', pk=dissertation.pk)


class DeleteDissertationFileView(AjaxTemplateMixin, DeleteView):
    model = DissertationDocumentFile
    template_name = 'dissertationdocumentfile_confirm_delete_inner.html'

    def get_success_url(self):
        return None

    @property
    def dissertation(self):
        return get_object_or_404(Dissertation, pk=self.kwargs['dissertation_pk'])

    def get_object(self, queryset=None):
        return DissertationDocumentFile.objects.filter(dissertation=self.dissertation)

    def delete(self, request, *args, **kwargs):
        self.dissertation_documents = self.get_object()
        if self.dissertation_documents and autorized_dissert_promotor_or_manager(request.user, self.dissertation.pk):
            for dissertation_document in self.dissertation_documents:
                justification = "{} {} ".format(_("Delete file"), dissertation_document.document_file.file_name)
                dissertation_update.add(request,
                                        self.dissertation,
                                        self.dissertation.status,
                                        justification=justification)
                dissertation_document.delete()
            return self._ajax_response() or HttpResponseRedirect(self.get_success_url())

        return self._ajax_response() or HttpResponseRedirect(self.get_error_url())


@login_required
@require_http_methods(["POST"])
@user_passes_test(adviser.is_manager)
def save_uploaded_file(request):
    data = request.POST
    dissert = get_object_or_404(Dissertation, pk=request.POST['dissertation_id'])
    if autorized_dissert_promotor_or_manager(request.user, dissert.pk):
        file_selected = request.FILES['file']
        file = file_selected
        file_name = file_selected.name
        content_type = file_selected.content_type
        size = file_selected.size
        description = data['description']
        documents = mdl.dissertation_document_file.find_by_dissertation(dissert)
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

        justification = "{} {} ".format(_("Add file"), new_document.file_name)
        dissertation_update.add(request,
                                dissert,
                                dissert.status,
                                justification=justification)
        new_document.save()
        dissertation_file = mdl.dissertation_document_file.DissertationDocumentFile()
        dissertation_file.dissertation = dissert
        dissertation_file.document_file = new_document
        dissertation_file.save()
    return HttpResponse('')
