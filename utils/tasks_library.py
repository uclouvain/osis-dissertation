# ##################################################################################################
#  OSIS stands for Open Student Information System. It's an application                            #
#  designed to manage the core business of higher education institutions,                          #
#  such as universities, faculties, institutes and professional schools.                           #
#  The core business involves the administration of students, teachers,                            #
#  courses, programs and so on.                                                                    #
#                                                                                                  #
#  Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)              #
#                                                                                                  #
#  This program is free software: you can redistribute it and/or modify                            #
#  it under the terms of the GNU General Public License as published by                            #
#  the Free Software Foundation, either version 3 of the License, or                               #
#  (at your option) any later version.                                                             #
#                                                                                                  #
#  This program is distributed in the hope that it will be useful,                                 #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of                                  #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                   #
#  GNU General Public License for more details.                                                    #
#                                                                                                  #
#  A copy of this license - GNU General Public License - is available                              #
#  at the root of the source code of this program.  If not,                                        #
#  see http://www.gnu.org/licenses/.                                                               #
# ##################################################################################################
from datetime import date

from dateutil.relativedelta import relativedelta

from dissertation.models.offer_proposition import OfferProposition

YEAR = 1


def offer_proposition_extend_dates():
    all_offer_propositions = OfferProposition.objects.all()
    logs = ''
    for offer_proposition in all_offer_propositions:
        logs += check_dates_of_offer_proposition(offer_proposition)
    if logs == '':
        logs = 'no action'
    return logs


def check_dates_of_offer_proposition(offer_prop):
    logs = ''
    date_now = date.today()
    if offer_prop.end_visibility_proposition < date_now:
        logs += "start_visibility_proposition: {} end_visibility_proposition:{}". \
            format(offer_prop.start_visibility_proposition, offer_prop.end_visibility_proposition)
        offer_prop.start_visibility_proposition = add_year_to_date(offer_prop.start_visibility_proposition)
        offer_prop.end_visibility_proposition = add_year_to_date(offer_prop.end_visibility_proposition)
        logs += "new data : start_visibility_proposition:{} new end_visibility_proposition: {} \n". \
            format(offer_prop.start_visibility_proposition, offer_prop.end_visibility_proposition)
    if offer_prop.end_visibility_dissertation < date_now:
        logs += "start_visibility_dissertation: {} end_visibility_dissertation:{}". \
            format(offer_prop.start_visibility_dissertation, offer_prop.end_visibility_dissertation)
        offer_prop.start_visibility_dissertation = add_year_to_date(offer_prop.start_visibility_dissertation)
        offer_prop.end_visibility_dissertation = add_year_to_date(offer_prop.end_visibility_dissertation)
        logs += "new  data : start_visibility_dissertation: {} end_visibility_dissertation:{} \n". \
            format(offer_prop.start_visibility_dissertation, offer_prop.end_visibility_dissertation)
    if offer_prop.end_jury_visibility < date_now:
        logs += "start_jury_visibility: {} end_jury_visibility:{}". \
            format(offer_prop.start_jury_visibility, offer_prop.end_jury_visibility)
        offer_prop.start_jury_visibility = add_year_to_date(offer_prop.start_jury_visibility)
        offer_prop.end_jury_visibility = add_year_to_date(offer_prop.end_jury_visibility)
        logs += "new data : start_jury_visibility: {} end_jury_visibility:{} \n". \
            format(offer_prop.start_jury_visibility, offer_prop.end_jury_visibility)

    if offer_prop.end_edit_title < date_now:
        logs += "start_edit_title: {} end_edit_title:{}". \
            format(offer_prop.start_edit_title, offer_prop.end_edit_title)
        offer_prop.start_edit_title = add_year_to_date(offer_prop.start_edit_title)
        offer_prop.end_edit_title = add_year_to_date(offer_prop.start_edit_title)
        logs += "new data : start_edit_title: {} end_edit_title:{} \n". \
            format(offer_prop.start_edit_title, offer_prop.end_edit_title)
        logs = str(offer_prop.education_group.most_recent_acronym) + "\n" + logs
    offer_prop.save()
    return logs


def add_year_to_date(date_too):
    return date_too + relativedelta(years=YEAR)
