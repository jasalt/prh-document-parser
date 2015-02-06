# -*- coding: utf-8 -*-
""" Finnish and swedish register log parser. """
import re

FORMFEED = '\x0c'

def can_parse(rawdata):
    """ Returns True if the parse function of this module can parse rawdata.
        rawdata is an unmodified string from pdfminer. """
    return True # TODO: check if parse function can actually parse the data


def parse(rawdata):
    """ Parses register log and returns records in the following form:
        [{ 'title'   : <unicode string>,
           'date'    : <unicode string>,
           'content' : <unicode string> }, ...]
    """
    # pagesplit_re splits document into pages and removes page headers
    pagesplit_re = FORMFEED + \
        r"(?:Sivu|Sida): \d+ \(\d+\)(?:Y-tunnus|FO-nummer): \d+-\d"

    # recordsplit_re splits document into records
    register_words = u"(?:Rekisterissä|Rekisteröity|Registrerats|I registret)"
    recordsplit_re = u"([A-Z0-9\\-\\sÖÄÅ]*) \\("+register_words+" ([\\d\\. -]*)\\)"

    text = rawdata.decode('utf-8')
    text = text.replace('-' + FORMFEED, FORMFEED) # Remove hyphenation
    pages = re.split(pagesplit_re, text, flags=re.UNICODE) # Split into pages and remove page info
    continuous_text = u' '.join(pages) # Collect pages into continuous text

    data = []
    # recordsplit = [header, title, date, text, title, date, text, ...]
    recordsplit = re.split(recordsplit_re, continuous_text, flags=re.UNICODE)
    i = 1
    while i < len(recordsplit) - 3:
        data.append({'title': recordsplit[i].strip(),
                     'date': recordsplit[i+1],
                     'content': recordsplit[i+2]})
        i += 3

    return data

def get_parser():
    """ Returns a tuple (can_parse, parse), where can_parse function
        check whether parse function is able to parse the document.
    """
    return (can_parse, parse)
