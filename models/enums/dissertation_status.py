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
from django.utils.translation import ugettext_lazy as _

DRAFT = 'DRAFT'
DIR_SUBMIT='DIR_SUBMIT'
DIR_OK = 'DIR_OK'
DIR_KO = 'DIR_KO'
COM_SUBMIT = 'COM_SUBMIT'
COM_OK = 'COM_OK'
COM_KO = 'COM_KO'
EVA_SUBMIT = 'EVA_SUBMIT'
EVA_OK = 'EVA_OK'
EVA_KO = 'EVA_KO'
TO_RECEIVE = 'TO_RECEIVE'
TO_DEFEND = 'TO_DEFEND'
DEFENDED = 'DEFENDED'
ENDED = 'ENDED'
ENDED_WIN = 'ENDED_WIN'
ENDED_LOS = 'ENDED_LOS'

DISSERTATION_STATUS = (
    (DRAFT, _('draft')),
    (DIR_SUBMIT, _('submitted_to_director')),
    (DIR_OK, _('accepted_by_director')),
    (DIR_KO, _('refused_by_director')),
    (COM_SUBMIT, _('submitted_to_commission')),
    (COM_OK, _('accepted_by_commission')),
    (COM_KO, _('refused_by_commission')),
    (EVA_SUBMIT, _('submitted_to_first_year_evaluation')),
    (EVA_OK, _('accepted_by_first_year_evaluation')),
    (EVA_KO, _('refused_by_first_year_evaluation')),
    (TO_RECEIVE, _('to_be_received')),
    (TO_DEFEND, _('to_be_defended')),
    (DEFENDED, _('defended')),
    (ENDED, _('ended')),
    (ENDED_WIN, _('ended_win')),
    (ENDED_LOS, _('ended_los')),
)
