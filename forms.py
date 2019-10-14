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
from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from base import models as mdl
from base.models.education_group_year import EducationGroupYear
from base.models.person import Person
from base.models.student import Student
from dissertation.models import dissertation_update, adviser
from dissertation.models.adviser import Adviser
from dissertation.models.dissertation import Dissertation
from dissertation.models.dissertation_role import DissertationRole
from dissertation.models.dissertation_update import DissertationUpdate
from dissertation.models.enums import dissertation_role_status
from dissertation.models.faculty_adviser import FacultyAdviser
from dissertation.models.offer_proposition import OfferProposition
from dissertation.models.proposition_dissertation import PropositionDissertation
from dissertation.models.proposition_role import PropositionRole


class AdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('available_by_email', 'available_by_phone', 'available_at_office', 'comment')


class AddAdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('person',)


class DissertationForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'education_group_year_start', 'proposition_dissertation', 'description')


class FacultyAdviserForm(ModelForm):
    class Meta:
        model = FacultyAdviser
        fields = ('adviser', )
        widgets = {'adviser': autocomplete.ModelSelect2(url='adviser-autocomplete', attrs={'style': 'width:100%'})}


class PropositionDissertationForm(ModelForm):
    class Meta:
        model = PropositionDissertation
        fields = ('author', 'visibility', 'title', 'description', 'type', 'level', 'collaboration',
                  'max_number_student')
        widgets = {'author': forms.HiddenInput()}


class PropositionRoleForm(ModelForm):
    class Meta:
        model = PropositionRole
        fields = ('proposition_dissertation', 'status', 'adviser')
        widgets = {'proposition_dissertation': forms.HiddenInput()}


class ManagerAddAdviserPreForm(ModelForm):
    class Meta:
        model = mdl.person.Person
        fields = ('email', )


class ManagerAddAdviserPerson(ModelForm):
    class Meta:
        model = mdl.person.Person
        fields = ('email', 'last_name', 'first_name', 'phone', 'phone_mobile')


class ManagerAddAdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('person', 'available_by_email', 'available_by_phone', 'available_at_office', 'comment')


class ManagerAdviserForm(ModelForm):
    class Meta:
        model = Adviser
        fields = ('available_by_email', 'available_by_phone', 'available_at_office', 'comment')


class ManagerDissertationForm(ModelForm):
    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'education_group_year_start', 'proposition_dissertation', 'description',
                  'defend_year', 'defend_periode', 'location')


class ManagerDissertationEditForm(ModelForm):
    def __init__(self, data, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(data, *args, **kwargs)
        self.fields["proposition_dissertation"].queryset = PropositionDissertation.objects.filter(
            active=True,
            visibility=True,
            offer_propositions__education_group__advisers__person__user=user
        ).select_related("author__person").distinct()
        self.fields["author"].queryset = Student.objects.filter(
            offerenrollment__education_group_year__education_group__advisers__person__user=user
        ).order_by(
            'person__last_name', 'person__first_name'
        ).select_related("person").distinct()
        self.fields["education_group_year_start"].queryset = EducationGroupYear.objects.filter(
            education_group__advisers__person__user=user
        ).select_related("academic_year")
        self.fields["education_group_year_start"].required = True
        self.fields['defend_periode'].required = True

    class Meta:
        model = Dissertation
        fields = ('title', 'author', 'education_group_year_start', 'proposition_dissertation', 'description',
                  'defend_year', 'defend_periode', 'location')


class ManagerDissertationRoleForm(ModelForm):
    # TODO :: remplacer request par user mais cela implique de remplacer dissertation_update_add
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    class Meta:
        model = DissertationRole
        fields = ('dissertation', 'status', 'adviser')
        widgets = {'dissertation': forms.HiddenInput(),
                   'adviser': autocomplete.ModelSelect2(url='adviser-autocomplete', attrs={'style': 'width:100%'})}

    class Media:
        css = {
            'all': ('css/select2-bootstrap.css',)
        }

    def save(self, commit=True):
        data = self.cleaned_data
        status = data['status']
        adv = data['adviser']
        diss = data['dissertation']
        justification = self._get_justification()
        dissertation_update.add(self.request, diss, status, justification=justification)
        if status == dissertation_role_status.PROMOTEUR:
            instance, created = DissertationRole.objects.update_or_create(
                dissertation=diss,
                status=status,
                defaults={'adviser': adv})
        else:
            instance = super().save(commit)
        return instance

    def _get_justification(self):
        status = self.cleaned_data['status']
        adv = self.cleaned_data['adviser']
        action = _("Teacher added jury") if adviser.is_teacher(self.request.user) else _("Manager add jury")
        return "%s %s %s" % (action, str(status), str(adv))


class ManagerOfferPropositionForm(ModelForm):
    class Meta:
        model = OfferProposition
        fields = ('adviser_can_suggest_reader', 'validation_commission_exists',
                  'student_can_manage_readers', 'evaluation_first_year', 'start_visibility_proposition',
                  'end_visibility_proposition', 'start_visibility_dissertation', 'end_visibility_dissertation',
                  'start_jury_visibility', 'end_jury_visibility', 'start_edit_title', 'end_edit_title',
                  'global_email_to_commission')


class ManagerPropositionDissertationForm(ModelForm):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["author"].queryset = Adviser.objects.all().select_related("person").distinct()

    class Meta:
        model = PropositionDissertation
        fields = (
            'author',
            'visibility',
            'title',
            'description',
            'type',
            'level',
            'collaboration',
            'max_number_student'
        )
        widgets = {
            'author': autocomplete.ModelSelect2(url='adviser-autocomplete')
        }


class ManagerPropositionDissertationEditForm(ModelForm):
    class Meta:
        model = PropositionDissertation
        fields = (
            'visibility', 'title', 'description', 'type', 'level', 'collaboration', 'max_number_student')


class ManagerPropositionRoleForm(ModelForm):
    class Meta:
        model = PropositionRole
        fields = ('proposition_dissertation', 'status', 'adviser')
        widgets = {'proposition_dissertation': forms.HiddenInput(),
                   'adviser': autocomplete.ModelSelect2(url='adviser-autocomplete', attrs={'style': 'width:100%'})}

    class Media:
        css = {
            'all': ('css/select2-bootstrap.css',)
        }

    def save(self, commit=True):
        data = self.cleaned_data
        status = data['status']
        adv = data['adviser']
        prop = data['proposition_dissertation']
        if status == dissertation_role_status.PROMOTEUR:
            instance, created = PropositionRole.objects.update_or_create(
                proposition_dissertation=prop,
                status=status,
                defaults={'adviser': adv})
        else:
            instance = super().save(commit)
        return instance


class ManagerDissertationUpdateForm(ModelForm):
    class Meta:
        model = DissertationUpdate
        fields = ('justification',)
