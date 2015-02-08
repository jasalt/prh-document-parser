# -*- coding: utf-8 -*-
""" Finnish and swedish register log parser. """
import re
from itertools import chain

FORMFEED = '\x0c'


def can_parse(rawdata):
    """ Returns True if the parse function of this module can parse rawdata.
        rawdata is an unmodified string from pdfminer. """
    return True # TODO: check if parse function can actually parse the data


def parse(rawdata):
    """ Parses register log and returns the firm information and
        log records in the following form:

        { 'firmID' :      <unicode string>,  (Y-tunnus)
          'firmName' :    <unicode string>,
          'registerationDate': <unicode string>,
          'firmForm':     <unicode string>, (Yritysmuoto)
          'location':     <unicode string>,
          'postAddress':  <unicode string>,
          'visitAddress': <unicode string>,
          'phoneNumber':  <unicode string>,
          'fax':          <unicode string>,
          'email':        <unicode string>,
          'webpage':      <unicode string>,
          'log': [{ 'title'   : <unicode string>,
                    'date'    : <unicode string>,
                    'content' : <unicode string> }, ...]
        }
    """
    # pagesplit_re splits document into pages and removes page headers
    pagesplit_re = FORMFEED + \
        r"(?:Sivu|Sida): \d+ \(\d+\)(?:Y-tunnus|FO-nummer): \d+-\d"

    # recordsplit_re splits document into records
    register_words = u"(?:Rekisterissä|Rekisteröity|Registrerats|I registret)"
    recordsplit_re = \
        u"([A-Z0-9\\-\\sÖÄÅ]*) \\("+register_words+" ([\\d\\. -]*)\\)"

    text = rawdata.decode('utf-8')
    text = text.replace('-' + FORMFEED, FORMFEED) # Remove hyphenation
    pages = re.split(pagesplit_re, text, flags=re.UNICODE)
    continuous_text = u' '.join(pages) # Collect pages into continuous text

    # Parse log data
    log = []
    # recordsplit = [header, title, date, text, title, date, text, ...]
    recordsplit = re.split(recordsplit_re, continuous_text, flags=re.UNICODE)
    i = 1
    while i < len(recordsplit) - 3:
        log.append({'title': recordsplit[i].strip(),
                    'date': recordsplit[i+1],
                    'content': recordsplit[i+2]})
        i += 3

    # TODO: E-post might not be correct field name
    field_name_lookup = {
        'firmName':          [u"Toiminimi:", u"Företagsnamn:"],
        'firmID':            [u"Y-tunnus:", u"FO-nummer:"],
        'registerationDate': [u"Yritys rekisteröity:",
                              u"Företaget registrerat:"],
        'firmForm':          [u"Yritysmuoto:", u"Företagsform:"],
        'location':          [u"Kotipaikka:", u"Hemort:"],
        'postAddress':       [u"Postiosoite:", u"Postadress:"],
        'visitAddress':      [u"Käyntiosoite:", u"Besöksadress:"],
        'phoneNumber':       [u"Puhelin:", u"Telefon:"],
        'fax':               [u"Faksi:", u"Fax:"],
        'email':             [u"Sähköposti:", u"E-post:"],
        'webpage':           [u"Kotisivun osoite:", u"Internetadress:"]
        }

    # Fields are on the first page
    firstpage = recordsplit[0]

    # Strip unnecessary information
    i = firstpage.find(u"REKISTERIOTTEEN TIEDOT")
    if i == -1: # The document is in swedish
        i = firstpage.find(u"UPPGIFTERNA I REGISTERUTDRAGET")
    firstpage = firstpage[i:]

    # Collect field names from field_name_lookup and add extra fields
    field_names = list(chain(*field_name_lookup.values())) \
        + [u"Rekisterimerkinnät:", u"Otteen sisältö:", u"Utdragets innehåll:",
           u"Yhteystiedot:", u"Kontaktinformation:"]

    # Split first page into field titles and field data
    # fields = [field name, field data, field name, field data, ...]
    fieldsplit_re = u"(" + (u"|".join(field_names)) + u")"
    fields = re.split(fieldsplit_re, firstpage, flags=re.UNICODE)

    # Collect field info from 'fields' into info dictionary
    info = { 'log': log }
    for field_id, field_aliases in field_name_lookup.items():
        for field in field_aliases:
            try:
                i = fields.index(field)
                info[field_id] = fields[i + 1]
                # For some reason (related to pdfminer), post address is
                # always in the previous index
                if field_id == 'postAddress':
                    info[field_id] = fields[i - 1]
            except ValueError:
                pass # Field not found

    return info

def get_parser():
    """ Returns a tuple (can_parse, parse), where can_parse function
        check whether parse function is able to parse the document.
    """
    return (can_parse, parse)
