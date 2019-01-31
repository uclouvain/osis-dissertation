from datetime import date

from dateutil.relativedelta import relativedelta

from dissertation.models.offer_proposition import OfferProposition

YEAR = 1


def offer_proposition_extend_dates():
    all_offer_propositions = OfferProposition.objects.all()
    logs = ''
    for offer_proposition in all_offer_propositions:
        logs += check_dates_of_offer_proposition(offer_proposition)
    if not logs :
        logs = 'no action'
    return logs


def check_dates_of_offer_proposition(offer_prop):
    logs = ''
    logs += check_date_end(offer_prop, start_arg="start_visibility_proposition", end_arg="end_visibility_proposition")
    logs += check_date_end(offer_prop, start_arg="start_visibility_dissertation", end_arg="end_visibility_dissertation")
    logs += check_date_end(offer_prop, start_arg="start_jury_visibility", end_arg="end_jury_visibility")
    logs += check_date_end(offer_prop, start_arg="start_edit_title", end_arg="end_edit_title")
    if logs:
        logs = str(offer_prop.education_group.most_recent_acronym) + "\n" + logs
    return logs


def check_date_end(offer_prop, start_arg, end_arg):
    date_now = date.today()
    offer_start = getattr(offer_prop, start_arg)
    offer_end = getattr(offer_prop, end_arg)
    logs = ''
    if offer_end < date_now:
        logs += "{} : {}  {} : {}".format(
            start_arg, offer_start, end_arg, offer_end
        )
        setattr(offer_prop, start_arg, incr_year(offer_start))
        setattr(offer_prop, end_arg, incr_year(offer_end))
        logs += "new data : {} : {} new {} : {} \n".format(start_arg, offer_start, end_arg, offer_end)
        offer_prop.save()
    return logs


def incr_year(date_too):
    return date_too + relativedelta(years=1)
