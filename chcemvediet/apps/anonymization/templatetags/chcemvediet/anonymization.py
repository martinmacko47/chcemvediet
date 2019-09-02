# -*- coding: utf-8 -*-
from poleno.utils.template import Library
from chcemvediet.apps.anonymization.anonymization import generate_user_pattern, ANONYMIZATION_STRING


register = Library()

@register.simple_tag
def get_anonymization_string():
    return ANONYMIZATION_STRING

@register.simple_tag(takes_context=True)
def anonymize(context, inforequest, content, anonymization_string=ANONYMIZATION_STRING):
    request = context[u'request']
    prog = generate_user_pattern(inforequest)
    if not prog.pattern:
        return content
    if request.user == inforequest.applicant:
        return content
    return prog.sub(anonymization_string, content)
