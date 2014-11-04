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

def strip_surrounding_parens(s):
    """
    Strip surrounding parenthesis and curly braces from a string.
    """
    s = s.strip('{').strip('}')
    if s[0] == "(" and s[2] != ")":
        s = s[1:]
    if s[-1] == ")" and s[-3] != "(":
        s = s[:-1]

    return s

def strip_attempted(s):
    """
    Strip the citation indicating an attempted criminal offense from a string

    Generally, this is some version of "720-5/8-4" (ILCS) or "38-8-4" (ILRS),
    though the exact representation can vary widely.

    This function is needed because attempted crimes are represented by
    packing multiple statutes into a single field.  For example:

    720-5/8-4 (720-5/18-2)
    38-8-4(38-18-2)

    This breaks parsing the statutes for tasks like determining IUCR codes.
    
    Returns:
        A tuple where the first item is the statute indicating the crime and
        the second item is the statute indicating an attempted offense. For
        non-attempted offenses the second item will be None.

    """
    ilcs_attempted_statute_re = re.compile(r"""^(?P<attempted>(\({0,1}720[- ]+5{0,1}
        [/\\ ]{0,1} # Optional delimiter
        ){0,1} # Some statutes don't have the leading 720-5
        \({0,1}8-4\){0,1}
        (\({0,1}-{0,1}A\){0,1}){0,1} # Optional "(A)"
        \/* # Optional trailing slash
        \){0,1} # Optional trailing paren
        ) # Close the group
    """, re.VERBOSE|re.IGNORECASE)
    ilcs_attempted_statute_trailing_re = re.compile(r',{0,1}(?P<attempted>5/8-4(\({0,1}A\){0,1}){0,1})$')
    ilrs_attempted_statute_re = re.compile(r"""^(?P<attempted>38-8-4
        [9/\\]{0,1} # Optional separator. Either '/', '\' or in a weid case '9'
        ) # close the group
    """, re.VERBOSE|re.IGNORECASE)

    m = ilcs_attempted_statute_re.match(s)
    if m is None:
        m = ilcs_attempted_statute_trailing_re.search(s)
    if m is None:
        m = ilrs_attempted_statute_re.match(s)
    if m is None:
        # No match of an attempted part
        return s, None

    attempted_part = m.group('attempted')
    statute = s.replace(attempted_part, '')
    statute = statute.strip()
    statute = re.sub(r'^[/\\,\x1a]+', '', statute)
    statute = re.sub(r'[/\\,\x1a]+$', '', statute)
    if attempted_part.startswith('38'):
        attempted_part = re.sub(r'[9/\\]{0,1}$', '', attempted_part)
    statute = strip_surrounding_parens(statute)
    if not (statute.startswith("720") or statute.startswith('38') or
            statute.startswith("56.5")):
        statute = "720-5/" + statute
    attempted_part = attempted_part.strip('/').strip('\\')

    return statute, attempted_part
