# -*- coding: utf-8 -*-
import re
import zipfile
import StringIO
import traceback
from xml.etree import ElementTree
from contextlib import closing

import magic
from django.core.files.base import ContentFile

from poleno.cron import cron_logger

from .models import AttachmentRecognition, AttachmentAnonymization
from . import content_types


ANONYMIZATION_STRING = u'xxxxx'
WORD_SIZE_MIN = 3
NUMBER_SIZE_MIN = 3

TRANSLATE_TABLE = {
    u'a': u'(?:a|á|ä)',
    u'á': u'(?:a|á|ä)',
    u'ä': u'(?:a|á|ä)',
    u'e': u'(?:e|é)',
    u'é': u'(?:e|é)',
    u'i': u'(?:i|í)',
    u'í': u'(?:i|í)',
    u'o': u'(?:o|ó|ô)',
    u'ó': u'(?:o|ó|ô)',
    u'ô': u'(?:o|ó|ô)',
    u'u': u'(?:u|ú)',
    u'ú': u'(?:u|ú)',
    u'y': u'(?:y|ý)',
    u'ý': u'(?:y|ý)',
    u'c': u'(?:c|č)',
    u'č': u'(?:c|č)',
    u'd': u'(?:d|ď)',
    u'ď': u'(?:d|ď)',
    u'l': u'(?:l|ĺ|ľ)',
    u'ĺ': u'(?:l|ĺ|ľ)',
    u'ľ': u'(?:l|ĺ|ľ)',
    u'n': u'(?:n|ň)',
    u'ň': u'(?:n|ň)',
    u'r': u'(?:r|ŕ)',
    u'ŕ': u'(?:r|ŕ)',
    u's': u'(?:s|š)',
    u'š': u'(?:s|š)',
    u't': u'(?:t|ť)',
    u'ť': u'(?:t|ť)',
    u'z': u'(?:z|ž)',
    u'ž': u'(?:z|ž)',
}

def generate_word_pattern(words):
    u"""
    Generates list of patterns, that matches slovak accent insensitive lowercase word. Each word is
    captured in group.
    """
    patterns = []
    for word in words:
        if len(word) < WORD_SIZE_MIN:
            continue
        p = u''.join([TRANSLATE_TABLE[c] if c in TRANSLATE_TABLE else re.escape(c) for c in word.lower()])
        patterns.append(u'(\\b{}\\b)'.format(p))
    return patterns

def generate_numeric_pattern(numbers):
    u"""
    Generates list of patterns, that matches number, where digits can be splited with ' ' or '-'.
    Each number is captured in group.
    """
    patterns = []
    for number in numbers:
        number = re.sub(u'[ -]', u'', number)
        if len(number) < NUMBER_SIZE_MIN:
            continue
        p = u'[ -]?'.join([re.escape(c) for c in number])
        patterns.append(u'(\\b{}\\b)'.format(p))
    return patterns

def generate_user_pattern(inforequest):
    u"""
    Generates pattern object, that matches user personal information from inforequest.
    """
    user = inforequest.applicant
    names = user.first_name.split() + user.last_name.split() + inforequest.applicant_name.split()
    streets = [user.profile.street, inforequest.applicant_street]
    cities = [user.profile.city, inforequest.applicant_city]
    zips = [user.profile.zip, inforequest.applicant_zip]
    patterns = (
        generate_word_pattern(set(names)) +
        generate_word_pattern(set(streets)) +
        generate_word_pattern(set(cities)) +
        generate_numeric_pattern(set(zips))
    )
    return re.compile(u'|'.join(patterns), re.IGNORECASE | re.UNICODE)

def anonymize_xml(prog, xml_content, xpath, namespace):
    """
    Anonymize user in each xpath of xml_content, using defined namespace.
    """
    if not prog.pattern:
        return xml_content
    root = ElementTree.fromstring(xml_content)
    for t in root.findall(xpath, namespace):
        for tt in list(t):
            if tt.tail is None:
                continue
            tt.tail = prog.sub(ANONYMIZATION_STRING, tt.tail)
        if t.text is None:
            continue
        t.text = prog.sub(ANONYMIZATION_STRING, t.text)
    return ElementTree.tostring(root)

def anonymize_odt(attachment_recognition):
    try:
        inforequest = attachment_recognition.attachment.generic_object.branch.inforequest
        pattern = generate_user_pattern(inforequest)
        namespace = {u'text': u'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
        with closing(StringIO.StringIO(attachment_recognition.content)) as buffer_in:
            with closing(StringIO.StringIO()) as buffer_out:
                with zipfile.ZipFile(buffer_in) as zipfile_in:
                    with zipfile.ZipFile(buffer_out, u'w') as zipfile_out:
                        for f in zipfile_in.filelist:
                            content = zipfile_in.read(f)
                            if magic.from_buffer(content, mime=True) == content_types.XML_CONTENT_TYPE:
                                zipfile_out.writestr(f, anonymize_xml(pattern, content, u'.//text:span', namespace))
                            else:
                                zipfile_out.writestr(f, content)
                AttachmentAnonymization.objects.create(
                    attachment=attachment_recognition.attachment,
                    successful=True,
                    file=ContentFile(buffer_out.getvalue()),
                    content_type=content_types.ODT_CONTENT_TYPE,
                )
                cron_logger.info(u'Anonymized attachment_recognition: {}'.format(attachment_recognition))
    except Exception as e:
        trace = unicode(traceback.format_exc(), u'utf-8')
        AttachmentAnonymization.objects.create(
            attachment=attachment_recognition.attachment,
            successful=False,
            content_type=content_types.ODT_CONTENT_TYPE,
            debug=trace
        )
        cron_logger.error(u'Anonymizing attachment_recognition has failed: {}\n An '
                          u'unexpected error occured: {}\n{}'.format(
            attachment_recognition, e.__class__.__name__, trace))

def anonymize_attachment():
    attachment_recognition = (AttachmentRecognition.objects
            .successful()
            .recognized_to_odt()
            .not_anonymized()
            .first())
    if attachment_recognition is None:
        return
    else:
        anonymize_odt(attachment_recognition)
