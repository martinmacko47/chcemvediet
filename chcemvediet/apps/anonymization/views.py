import os

from django.conf import settings

from poleno.utils.http import send_file_response


def download(request, attachment_normalization):
    path = os.path.join(settings.MEDIA_ROOT, attachment_normalization.file.name)
    return send_file_response(request, path, attachment_normalization.name, attachment_normalization.content_type)
