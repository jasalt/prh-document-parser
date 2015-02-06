# -*- coding: utf-8 -*-
""" Registry log parser. """
import re

FORMFEED = '\x0c'

PAGESPLITTER = FORMFEED + \
    r"(?:Sivu|Sida): \d+ \(\d+\)(?:Y-tunnus|FO-nummer): \d+-\d"


def can_parse(rawdata):
    """ Returns True if the parse function can parse rawdata. """
    return True # TODO: check if parse function can actually parse the data


def parse(rawdata):
    text = rawdata.decode('utf-8')
    # Remove hyphenation
    text = text.replace('-' + FORMFEED, FORMFEED)
    # Split into pages and remove page info
    pages = re.split(PAGESPLITTER, text, flags=re.UNICODE)
    # Collect pages into continuous text
    continuous_text = u' '.join(pages)

    data = []
    # datasplit = [header, title, date, text, title, date, text, ...]
    # TODO: split swedish data also
    datasplit = re.split(u"([A-Z0-9\\-\\sÖÄÅ]*) \\(Rekisterissä ([\\d\\. -]*)\\)", continuous_text, flags=re.UNICODE)
    i = 1
    while i < len(datasplit) - 3:
        data.append({'title': datasplit[i],
                     'date': datasplit[i+1],
                     'content': datasplit[i+2]})
        i += 3

    return data

parser = (can_parse, parse)
