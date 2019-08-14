import re
import tempfile
import shutil
from contextlib import contextmanager
from xml.etree import ElementTree


ANONYMIZATION_STRING = r'xxxxx'

TRANSLATE_TABLE = {
    # Slovak diacritics
    # ordering: l, L, l', l^, L', L^
    # missing: ae, ou, uu, r^
    u'a':       '(?:a|\xc3\xa1|\xc3\x81)',
    u'A':       '(?:a|\xc3\xa1|\xc3\x81)',
    u'\xe1':    '(?:a|\xc3\xa1|\xc3\x81)',
    u'\xc1':    '(?:a|\xc3\xa1|\xc3\x81)',
    u'e':       '(?:e|\xc3\xa9|\xc3\x89)',
    u'E':       '(?:e|\xc3\xa9|\xc3\x89)',
    u'\xe9':    '(?:e|\xc3\xa9|\xc3\x89)',
    u'\xc9':    '(?:e|\xc3\xa9|\xc3\x89)',
    u'i':       '(?:i|\xc3\xad|\xc3\x8d)',
    u'I':       '(?:i|\xc3\xad|\xc3\x8d)',
    u'o':       '(?:o|\xc3\xb3|\xc3\x93)',
    u'O':       '(?:o|\xc3\xb3|\xc3\x93)',
    u'\xf3':    '(?:o|\xc3\xb3|\xc3\x93)',
    u'\xd3':    '(?:o|\xc3\xb3|\xc3\x93)',
    u'u':       '(?:u|\xc3\xba|\xc3\x9a)',
    u'U':       '(?:u|\xc3\xba|\xc3\x9a)',
    u'\xfa':    '(?:u|\xc3\xba|\xc3\x9a)',
    u'\xda':    '(?:u|\xc3\xba|\xc3\x9a)',
    u'y':       '(?:y|\xc3\xbd|\xc3\x9d)',
    u'Y':       '(?:y|\xc3\xbd|\xc3\x9d)',
    u'\xfd':    '(?:y|\xc3\xbd|\xc3\x9d)',
    u'\xdd':    '(?:y|\xc3\xbd|\xc3\x9d)',
    u'c':       '(?:c|\xc4\x8d|\xc4\x8c)',
    u'C':       '(?:c|\xc4\x8d|\xc4\x8c)',
    u'\u010d':  '(?:c|\xc4\x8d|\xc4\x8c)',
    u'\u010c':  '(?:c|\xc4\x8d|\xc4\x8c)',
    u'd':       '(?:d|\xc4\x8f|\xc4\x8e)',
    u'D':       '(?:d|\xc4\x8f|\xc4\x8e)',
    u'\u010f':  '(?:d|\xc4\x8f|\xc4\x8e)',
    u'\u010e':  '(?:d|\xc4\x8f|\xc4\x8e)',
    u'l':       '(?:l|\xc4\xba|\xc4\xbe|\xc4\xb9|\xc4\xbd)',
    u'L':       '(?:l|\xc4\xba|\xc4\xbe|\xc4\xb9|\xc4\xbd)',
    u'\u013a':  '(?:l|\xc4\xba|\xc4\xbe|\xc4\xb9|\xc4\xbd)',
    u'\u013e':  '(?:l|\xc4\xba|\xc4\xbe|\xc4\xb9|\xc4\xbd)',
    u'\u0139':  '(?:l|\xc4\xba|\xc4\xbe|\xc4\xb9|\xc4\xbd)',
    u'\u013d':  '(?:l|\xc4\xba|\xc4\xbe|\xc4\xb9|\xc4\xbd)',
    u'n':       '(?:n|\xc5\x88|\xc5\x87)',
    u'N':       '(?:n|\xc5\x88|\xc5\x87)',
    u'\u0148':  '(?:n|\xc5\x88|\xc5\x87)',
    u'\u0147':  '(?:n|\xc5\x88|\xc5\x87)',
    u'r':       '(?:r|\xc5\x95|\xc5\x94)',
    u'R':       '(?:r|\xc5\x95|\xc5\x94)',
    u'\u0155':  '(?:r|\xc5\x95|\xc5\x94)',
    u'\u0154':  '(?:r|\xc5\x95|\xc5\x94)',
    u's':       '(?:s|\xc5\xa1|\xc5\xa0)',
    u'S':       '(?:s|\xc5\xa1|\xc5\xa0)',
    u'\u0161':  '(?:s|\xc5\xa1|\xc5\xa0)',
    u'\u0160':  '(?:s|\xc5\xa1|\xc5\xa0)',
    u't':       '(?:t|\xc5\xa5|\xc5\xa4)',
    u'T':       '(?:t|\xc5\xa5|\xc5\xa4)',
    u'\u0165':  '(?:t|\xc5\xa5|\xc5\xa4)',
    u'\u0164':  '(?:t|\xc5\xa5|\xc5\xa4)',
    u'z':       '(?:z|\xc5\xbe|\xc5\xbd)',
    u'Z':       '(?:z|\xc5\xbe|\xc5\xbd)',
    u'\u017e':  '(?:z|\xc5\xbe|\xc5\xbd)',
    u'\u017d':  '(?:z|\xc5\xbe|\xc5\xbd)',
}

@contextmanager
def temporary_directory(*args, **kwargs):
    directory_name = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield directory_name
    finally:
        shutil.rmtree(directory_name)

def generate_pattern(words):
    u"""
    Generates Pattern object, that matches case- and slovak accent insensitive words. Each word is captured in group.
    """
    pattern = ''
    for word in words:
        p = ''.join([TRANSLATE_TABLE[c] if c in TRANSLATE_TABLE else c.encode(u'utf-8') for c in word])
        pattern += "({})|".format(p)
    return re.compile(pattern[:-1], re.IGNORECASE)  # remove last `|` from pattern

def generate_zip_pattern(zips):
    u"""
    Generates Pattern object, that matches slovak ZIP code. Each zip is captured in group.
    """
    pattern = ''
    for zip in zips:
        zip = zip.replace(u' ', u'')
        pattern += '({}[ -]?{})|'.format(zip[:3], zip[3:])
    return re.compile(pattern[:-1])  # remove last `|` from pattern

def anonymize_xml(inforequest, xml_content, tag, namespace):
    """
    Anonymize user in each tag of xml_content, using defined namespace.
    """
    root = ElementTree.fromstring(xml_content)
    for t in root.findall(tag, namespace):
        if t.text is None:
            continue
        t.text = anonymize_user(inforequest, t.text.encode(u'utf-8')).decode(u'utf-8')
    return ElementTree.tostring(root)

def anonymize_name(inforequest, buffer):
    user = inforequest.applicant
    fullname = user.first_name.split() + user.last_name.split() + inforequest.applicant_name.split()
    prog = generate_pattern(set(fullname))
    return prog.sub(ANONYMIZATION_STRING, buffer)

def anonymize_street(inforequest, buffer):
    user = inforequest.applicant
    fullstreet = [user.profile.street, inforequest.applicant_street]
    prog = generate_pattern(set(fullstreet))
    return prog.sub(ANONYMIZATION_STRING, buffer)

def anonymize_city(inforequest, buffer):
    user = inforequest.applicant
    fullstreet = [user.profile.city, inforequest.applicant_city]
    prog = generate_pattern(set(fullstreet))
    return prog.sub(ANONYMIZATION_STRING, buffer)

def anonymize_zip(inforequest, buffer):
    user = inforequest.applicant
    fullzip = [user.profile.zip, inforequest.applicant_zip]
    prog = generate_zip_pattern(set(fullzip))
    return prog.sub(ANONYMIZATION_STRING, buffer)

def anonymize_user(inforequest, buffer):
    buffer = anonymize_name(inforequest, buffer)
    buffer = anonymize_street(inforequest, buffer)
    buffer = anonymize_city(inforequest, buffer)
    buffer = anonymize_zip(inforequest, buffer)
    return buffer
