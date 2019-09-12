# -*- coding: utf-8 -*-
import lxml.html

from poleno.utils.template import Library
from poleno.utils.http import get_request
from chcemvediet.apps.anonymization.anonymization import generate_user_pattern, ANONYMIZATION_STRING


register = Library()

@register.simple_tag(takes_context=True)
def anonymize(context, inforequest, content):
    request = context[u'request']
    prog = generate_user_pattern(inforequest)
    if not inforequest.anonymized_for(request.user) or not prog.pattern:
        return content
    return prog.sub(ANONYMIZATION_STRING, content)

@register.simple_tag(takes_context=True)
def anonymize_html(context, inforequest, html_content):
    """
    Anonymize user in each tag of html_content.
    """
    request = context[u'request']
    prog = generate_user_pattern(inforequest)
    if not inforequest.anonymized_for(request.user) or not prog.pattern:
        return html_content
    root = lxml.html.fromstring(html_content)
    for t in root.findall(u".//", {}):
        for tt in list(t):
            if tt.tail is None:
                continue
            tt.tail = prog.sub(ANONYMIZATION_STRING, tt.tail)
        if t.text is None:
            continue
        t.text = prog.sub(ANONYMIZATION_STRING, t.text)
    return lxml.html.tostring(root)

@register.filter
def anonymized(inforequest):
    return inforequest.anonymized_for(get_request().user)
