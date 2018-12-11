##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain
# (http://www.uclouvain.be)
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
DIR_SUBMIT = 'DIR_SUBMIT'
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
    (DRAFT, _('Draft')),
    (DIR_SUBMIT, _('Submitted to promotor')),
    (DIR_OK, _('Accepted by promotor')),
    (DIR_KO, _('Refused by promotor')),
    (COM_SUBMIT, _('Submitted to commission')),
    (COM_OK, _('Accepted by commission')),
    (COM_KO, _('Refused by commission')),
    (EVA_SUBMIT, _('Submitted to 1st year evaluation')),
    (EVA_OK, _('Accepted by 1st year evaluation')),
    (EVA_KO, _('1st year evaluation failed')),
    (TO_RECEIVE, _('To be received')),
    (TO_DEFEND, _('To be defended')),
    (DEFENDED, _('Defended')),
    (ENDED, _('Ended')),
    (ENDED_WIN, _('Ended with success')),
    (ENDED_LOS, _('Reported')),
)
