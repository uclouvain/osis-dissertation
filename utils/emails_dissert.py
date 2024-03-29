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
from django.utils import translation

from dissertation.models import dissertation_role
from osis_common.messaging import message_config, send_message as message_service

LANGUAGE_DEFAULT = 'fr_BE'


def translating(string, language=LANGUAGE_DEFAULT):
    cur_language = translation.get_language()
    try:
        translation.activate(language)
        text = translation.gettext(string)
    finally:
        translation.activate(cur_language)
    return text


def get_base_template(dissert):
    template_base_data = {'author': dissert.author,
                          'title': dissert.title,
                          'promoteur': create_string_list_promotors(dissert),
                          'description': dissert.description,
                          'dissertation_proposition_titre': dissert.proposition_dissertation.title}
    return template_base_data


def get_subject_template(dissert):
    template_base_data = {'author': dissert.author,
                          'title': dissert.title,
                          }
    return template_base_data


def create_string_list_promotors(dissert):
    promotors = dissertation_role.find_all_promotor_by_dissertation(dissert)
    return ','.join(['{adv.first_name} {adv.last_name}'.format(adv=dissrole.adviser.person)
                     for dissrole in promotors])


def create_string_list_commission_reading(dissert):
    commission_to_read = dissertation_role.search_by_dissertation(dissert)
    return ' - '.join(
        ['{adv.first_name} {adv.last_name} ({status})'.format(adv=member_commission.adviser.person,
                                                              status=translating(member_commission.status))
         for member_commission in commission_to_read])


def get_commission_template(dissert):
    template_commission_data = {'author': dissert.author,
                                'title': dissert.title,
                                'promoteur': create_string_list_promotors(dissert),
                                'programme': dissert.education_group_year.acronym,
                                'description': dissert.description,
                                'commission_string': create_string_list_commission_reading(dissert),
                                'dissertation_proposition_titre': dissert.proposition_dissertation.title}
    return template_commission_data


def send_email(dissert, template_ref, receivers):
    receivers = generate_receivers(receivers)
    html_template_ref = template_ref + '_html'
    txt_template_ref = template_ref + '_txt'
    suject_data = get_subject_template(dissert)
    if template_ref != 'dissertation_to_commission_list':
        template_base_data = get_base_template(dissert)
    else:
        template_base_data = get_commission_template(dissert)
    tables = None
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, tables, receivers,
                                                            template_base_data, suject_data)
    return message_service.send_messages(message_content)


def generate_receivers(receivers):
    return [message_config.create_receiver(receiver.person.id,
                                           receiver.person.email,
                                           receiver.person.language)
            for receiver in receivers]


def send_email_to_jury_members(dissert):
    receivers = [diss_role.adviser for diss_role in dissertation_role.search_by_dissertation(dissert)]
    result_send_mail = send_email(dissert, 'dissertation_to_commission_list', receivers)


def send_email_to_all_promotors(dissert, template):
    receivers = [diss_role.adviser for diss_role in dissertation_role.find_all_promotor_by_dissertation(dissert)]
    result_send_mail = send_email(dissert, template, receivers)
