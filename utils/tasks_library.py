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
        logs += "new data : start_visibility_proposition:{} new end_visibility_proposition: {}". \
            format(offer_prop.start_visibility_proposition, offer_prop.end_visibility_proposition)
    if offer_prop.end_visibility_dissertation < date_now:
        logs += "start_visibility_dissertation: {} end_visibility_dissertation:{}". \
            format(offer_prop.start_visibility_dissertation, offer_prop.end_visibility_dissertation)
        offer_prop.start_visibility_dissertation = add_year_to_date(offer_prop.start_visibility_dissertation)
        offer_prop.end_visibility_dissertation = add_year_to_date(offer_prop.end_visibility_dissertation)
        logs += "new  data : start_visibility_dissertation: {} end_visibility_dissertation:{}". \
            format(offer_prop.start_visibility_dissertation, offer_prop.end_visibility_dissertation)
    if offer_prop.end_jury_visibility < date_now:
        logs += "start_jury_visibility: {} end_jury_visibility:{}". \
            format(offer_prop.start_jury_visibility, offer_prop.end_jury_visibility)
        offer_prop.start_jury_visibility = add_year_to_date(offer_prop.start_jury_visibility)
        offer_prop.end_jury_visibility = add_year_to_date(offer_prop.end_jury_visibility)
        logs += "new data : start_jury_visibility: {} end_jury_visibility:{}". \
            format(offer_prop.start_jury_visibility, offer_prop.end_jury_visibility)

    if offer_prop.end_edit_title < date_now:
        logs += "start_edit_title: {} end_edit_title:{}". \
            format(offer_prop.start_edit_title, offer_prop.end_edit_title)
        offer_prop.start_edit_title = add_year_to_date(offer_prop.start_edit_title)
        offer_prop.end_edit_title = add_year_to_date(offer_prop.start_edit_title)
        logs += "new data : start_edit_title: {} end_edit_title:{}". \
            format(offer_prop.start_edit_title, offer_prop.end_edit_title)
    offer_prop.save()
    return logs


def add_year_to_date(date_too):
    return date_too + relativedelta(years=YEAR)
