# vim: expandtab
# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.http import Http404, JsonResponse

from poleno.attachments.utils import attachment_file_is_working
from poleno.utils.http import send_file_response

from .models import Attachment


def upload(request, generic_object, download_url_func):
    res = []
    for file in request.FILES.getlist(u'files'):
        attachment = Attachment(
                generic_object=generic_object,
                file=file,
                name=file.name,
                )
        attachment.save()
        res.append({
                u'pk': attachment.pk,
                u'name': attachment.name,
                u'size': attachment.size,
                u'url': download_url_func(attachment),
            })
    return JsonResponse({u'files': res})

def download(request, attachment, filename=None):
    u"""
    Download view for attachments and attachment like objects
    """
    if not attachment_file_is_working(attachment):
        raise Http404()
    path = os.path.join(settings.MEDIA_ROOT, attachment.file.name)
    return send_file_response(request, path, filename or attachment.name, attachment.content_type)
