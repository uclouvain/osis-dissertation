##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2018-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from celery.schedules import crontab

from backoffice.celery import app as celery_app
from dissertation.utils.tasks_library import offer_proposition_extend_dates

celery_app.conf.beat_schedule.update({
    'dissertation_offer_proposition extend dates': {
        'task': 'dissertation.tasks.tasks_check_dates_of_offer_proposition', 'schedule': crontab(minute=0, hour=1)
    },
})


@celery_app.task
def tasks_check_dates_of_offer_proposition():
    return offer_proposition_extend_dates()
