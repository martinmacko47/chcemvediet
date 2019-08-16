# -*- coding: utf-8 -*-
import re
import tempfile
import shutil
from contextlib import contextmanager
from xml.etree import ElementTree


ANONYMIZATION_STRING = u'xxxxx'

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

@contextmanager
def temporary_directory(*args, **kwargs):
    directory_name = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield directory_name
    finally:
        shutil.rmtree(directory_name)

def generate_word_pattern(words):
    u"""
    Generates pattern, that matches slovak accent insensitive lowercase words. Each word is captured in group.
    """
    patterns = []
    for word in words:
        p = u''.join([TRANSLATE_TABLE[c] if c in TRANSLATE_TABLE else re.escape(c) for c in word.lower()])
        patterns.append(u'({})'.format(p))
    return u'|'.join(patterns)

def generate_numeric_pattern(words, spacing=False):
    u"""
    Generates pattern, that matches words, where characters of one word can be splited with ' ' or '-'. Each word
    is captured in group.
    """
    patterns = []
    for word in words:
        if not spacing:
            word = word.replace(u' ', u'')
        p = u'[ -]?'.join([re.escape(c) for c in word])
        patterns.append(u'({})'.format(p))
    return u'|'.join(patterns)

def anonymize_xml(pattern, xml_content, xpath, namespace):
    """
    Anonymize user in each xpath of xml_content, using defined namespace.
    """
    root = ElementTree.fromstring(xml_content)
    for t in root.findall(xpath, namespace):
        for tt in list(t):
            if tt.tail is None:
                continue
            tt.tail = anonymize_string(pattern, tt.tail)
        if t.text is None:
            continue
        t.text = anonymize_string(pattern, t.text)
    return ElementTree.tostring(root)

def generate_user_pattern(inforequest):
    u"""
    Generates pattern, that matches user personal information from inforequest.
    """
    user = inforequest.applicant
    names = user.first_name.split() + user.last_name.split() + inforequest.applicant_name.split()
    streets = [user.profile.street, inforequest.applicant_street]
    cities = [user.profile.city, inforequest.applicant_city]
    zips = [user.profile.zip, inforequest.applicant_zip]
    patterns = [
        generate_word_pattern(set(names)),
        generate_word_pattern(set(streets)),
        generate_word_pattern(set(cities)),
        generate_numeric_pattern(set(zips))
    ]
    return u'|'.join(patterns)

def anonymize_string(pattern, buffer):
    prog = re.compile(pattern, re.IGNORECASE | re.UNICODE)
    return prog.sub(ANONYMIZATION_STRING, buffer)
