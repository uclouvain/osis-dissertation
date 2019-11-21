# ##############################################################################
#   OSIS stands for Open Student Information System. It's an application
#   designed to manage the core business of higher education institutions,
#   such as universities, faculties, institutes and professional schools.
#   The core business involves the administration of students, teachers,
#   courses, programs and so on.
#
#   Copyright (C) 2015- 2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   A copy of this license - GNU General Public License - is available
#   at the root of the source code of this program.  If not,
#   see http://www.gnu.org/licenses/.
# ##############################################################################
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from dissertation.models.offer_proposition import OfferProposition


def offer_proposition_extend_dates():
    date_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    all_offer_propositions = OfferProposition.objects.all()
    logs = ''
    for offer_proposition in all_offer_propositions:
        logs += check_dates_of_offer_proposition(offer_proposition)
    if not logs:
        logs = 'no action'
    return "{} ;   task date: {}" .format(logs, date_time_now)


def check_dates_of_offer_proposition(offer_prop):
    logs = ''
    logs += check_date_end(offer_prop, start_arg="start_visibility_proposition", end_arg="end_visibility_proposition")
    logs += check_date_end(offer_prop, start_arg="start_visibility_dissertation", end_arg="end_visibility_dissertation")
    logs += check_date_end(offer_prop, start_arg="start_jury_visibility", end_arg="end_jury_visibility")
    logs += check_date_end(offer_prop, start_arg="start_edit_title", end_arg="end_edit_title")
    if logs:
        logs = str(offer_prop.recent_acronym_education_group) + " , " + logs + ' ; '
    return logs


def check_date_end(offer_prop, start_arg, end_arg):
    date_now = date.today()
    offer_start = getattr(offer_prop, start_arg)
    offer_end = getattr(offer_prop, end_arg)
    logs = ''
    if offer_end < date_now:
        logs += "{} :  {} : {}  {} : {}        ".format(
            offer_prop.recent_acronym_education_group, start_arg, offer_start, end_arg, offer_end
        )
        setattr(offer_prop, start_arg, incr_year(offer_start))
        setattr(offer_prop, end_arg, incr_year(offer_end))
        logs += "new data : {} : {} new {} : {}       ".format(start_arg, getattr(offer_prop, start_arg),
                                                               end_arg, getattr(offer_prop, end_arg))
        offer_prop.save()
    return logs


def incr_year(date_too):
    return date_too + relativedelta(years=1)
