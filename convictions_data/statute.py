import logging
import re

import ilcs, iucr

logger = logging.getLogger(__name__)

ilcs_statute_re = re.compile(r'(?P<chapter>430|625|720|730|750)[- ]'
    '(?P<act_prefix>\d+)(/|\\\)(?P<section>\d+.*)')
ilrs_statute_re = re.compile(r'(?P<chapter>\d+(\.5){0,1})'
    '[-.]{0,1}\s*'
    '(?P<paragraph>[0-9a-zA-z\-]+)'
    '(?P<rest>.*)')
ilrs_paragraph_re = re.compile(r'(?P<primary_paragraph>\d+A{0,1}(-\d+){0,1})')

class ILCSLookupError(Exception):
    """Exception raised when parsing an ILCS or ILRS statute"""
    def __init__(self, chapter, paragraph, raw_statute=None):
        self.chapter = chapter
        self.paragraph = paragraph
        self.raw_statute = raw_statute

    def __str__(self):
        msg = "Unable to find ILCS statute for raw statute '{}'".format(self.raw_statute)
        
        return msg

class StatuteFormatError(Exception):
    """Exception raised when raw statute doesn't match an expected format"""
    def __init__(self, raw_statute):
        self.raw_statute = raw_statute

    def __str__(self):
        return "Can't understand statute '{}'".format(self.raw_statute)

class IUCRLookupError(Exception):
    """Exception raised when a matching IUCR offense for an ILCS section cannot
    be found"""
    def __init__(self, raw_statute):
        self.raw_statute = raw_statute

    def __str__(self):
        return "Cannot find IUCR offense for statute '{}'".format(self.raw_statute)


def parse_statute(s):
    m = ilcs_statute_re.match(s)

    if m:
        return parse_ilcs_statute(m.group('chapter'), m.group('act_prefix'),
            m.group('section'))
    else:
        m = ilrs_statute_re.match(s)

        if not m:
            raise StatuteFormatError(s)

        try:
            return parse_ilrs_statute(m.group('chapter'), m.group('paragraph'),
                m.group('rest'))
        except ILCSLookupError as e:
            e.raw_statute = s
            raise e

def parse_ilcs_statute(chapter, act_prefix, section):
    clean_section = section.split('(')[0].strip()
    return [ilcs.ILCSSection(chapter=chapter, act_prefix=act_prefix,
        section=clean_section)], section

def parse_ilrs_statute(chapter, paragraph, rest):
    try:
        return ilcs.lookup_by_ilrs(chapter, paragraph), paragraph
    except KeyError:
        # No match

        # Try stripping trailing bits from paragraph 
        m = ilrs_paragraph_re.match(paragraph)
        if not m:
            raise ILCSLookupError(chapter, paragraph)

        clean_paragraph = m.group('primary_paragraph')

        try:
            return ilcs.lookup_by_ilrs(chapter, clean_paragraph), paragraph
        except KeyError:
            raise ILCSLookupError(chapter, paragraph)

def lookup_iucr_from_ilcs(ilcs_section, paragraph):
    try:
        return iucr.lookup_by_ilcs(ilcs_section.chapter,
            ilcs_section.act_prefix, ilcs_section.section)
    except KeyError:
        # Try building a section from the raw paragraph
        
        # If the paragraph ends with an alphabetic character,
        # extract it and reformat the section with the character
        # appended.
        
        # For example, for a a paragrah that ends with "-D", try
        # searching for an IUCR that ends with "(d)".
        m = re.search(r'-(?P<subpara>[A-Za-z])$', paragraph)
        if m:
            section_with_subsection = "{}({})".format(ilcs_section.section,
                m.group("subpara").lower())
            return iucr.lookup_by_ilcs(ilcs_section.chapter,
                ilcs_section.act_prefix, section_with_subsection)

        raise

def get_iucr(s):
    try:
        ilcs_sections, paragraph = parse_statute(s)
        assert len(ilcs_sections) == 1, ("More than one matching ILCS sections "
            "for raw statute '{}'".format(s))
        return lookup_iucr_from_ilcs(ilcs_sections[0], paragraph)
    except KeyError:
        raise IUCRLookupError(s)
