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
from datetime import date
from dateutil.relativedelta import relativedelta
from celery.schedules import crontab

from backoffice.celery import app as celery_app

from dissertation.models.offer_proposition import OfferProposition

celery_app.conf.beat_schedule.update({
    'dissertation_offer_proposition extend dates': {
        'task': 'dissertation.tasks.offer_proposition_extend_dates',
        'schedule': crontab(minute=0, hour=1)
    },
})


@celery_app.task
def offer_proposition_extend_dates():
    date_now = date.today()
    all_offer_propositions = OfferProposition.objects.all()
    for offer_proposition in all_offer_propositions:

        if offer_proposition.end_visibility_proposition < date_now:
            offer_proposition.start_visibility_proposition = \
                offer_proposition.start_visibility_proposition + relativedelta(years=1)
            offer_proposition.end_visibility_proposition = \
                offer_proposition.end_visibility_proposition + relativedelta(years=1)

        if offer_proposition.end_visibility_dissertation < date_now:
            offer_proposition.start_visibility_dissertation = \
                offer_proposition.start_visibility_dissertation + relativedelta(years=1)
            offer_proposition.end_visibility_dissertation = \
                offer_proposition.end_visibility_dissertation + relativedelta(years=1)

        if offer_proposition.end_jury_visibility < date_now:
            offer_proposition.start_jury_visibility = \
                offer_proposition.start_jury_visibility + relativedelta(years=1)
            offer_proposition.end_jury_visibility = \
                offer_proposition.end_jury_visibility + relativedelta(years=1)

        if offer_proposition.end_edit_title < date_now:
            offer_proposition.start_edit_title = \
                offer_proposition.start_edit_title + relativedelta(years=1)
            offer_proposition.end_edit_title = \
                offer_proposition.end_edit_title + relativedelta(years=1)

        offer_proposition.save()
