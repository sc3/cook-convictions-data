import logging
import re

import ilcs, iucr

logger = logging.getLogger(__name__)

ilcs_chapters = [str(c) for c in [
    10,
    15,
    35,
    50,
    205,
    225,
    305,
    415,
    430,
    510,
    625,
    710,
    720,
    730,
    740,
    750,
    760,
    765,
    815,
    820
]]
ilcs_chapters_str = '|'.join(ilcs_chapters)
ilcs_statute_re = re.compile(r"""(?P<chapter>{chapters})
    [- ] # Delimiter between chapter and act prefix 
    (?P<act_prefix>\d+)
    [/\\] # Delimiter between act prefix and section
    (?P<section>[\da-zA-Z.]+(-[\da-zA-Z.]+){{0,1}})
    (?P<subsection>.*)
    """.format(chapters=ilcs_chapters_str), re.VERBOSE)

ilrs_chapters = [
    '23',
    '38',
    '42',
    '56.5',
    '95.5',      
    '121.5',
    '124',
    '134',
]
ilrs_chapters_str = '|'.join(ilrs_chapters)
ilrs_statute_re = re.compile(r"""(?P<chapter>{chapters})
    [-. ]{{0,1}}\s*
    (?P<paragraph>[\da-zA-Z.]+(-\d+[\da-zA-Z.]*){{0,1}})
    (?P<subsection>.*)
    """.format(chapters=ilrs_chapters_str), re.VERBOSE)
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
    """Return a parsed ILCS statute"""
    statute = fix_ambiguous_statute(s)
    statute, attempted_statute = strip_attempted_statute(statute)
    parsed = parse_ilcs_statute(statute)
    if len(parsed):
        return parsed

    parsed = parse_ilrs_statute(statute)
    if len(parsed) == 0:
        raise StatuteFormatError(s)

    chapter = parsed[0][0]
    paragraph = parsed[1][0]
    try:
        ilcs_sections = ilcs.lookup_by_ilrs(chapter, paragraph)
    except KeyError:
        # No match

        # Try stripping trailing bits from paragraph 
        m = ilrs_paragraph_re.match(paragraph)
        if not m:
            raise ILCSLookupError(chapter, paragraph, s)

        clean_paragraph = m.group('primary_paragraph')
        try:
            ilcs_sections = ilcs.lookup_by_ilrs(chapter, clean_paragraph)
        except KeyError:
            raise ILCSLookupError(chapter, paragraph, s)

    assert len(ilcs_sections) == 1, ("More than one matching ILCS sections "
        "for raw statute '{}'".format(s))
    ilcs_section = ilcs_sections[0]
    ilcs_parsed = [
        (ilcs_section.chapter, 'chapter'),
        (ilcs_section.act_prefix, 'act_prefix'),
        (ilcs_section.section, 'section'),
    ]
    ilcs_parsed.extend([(bit, bit_type) for bit, bit_type in parsed
                        if bit_type == 'subsection'])
    return ilcs_parsed

def parse_subsection(s):
    """
    Parse the subsection portion of a statute citation
    
    Arguments:
        s (str): String containing the subsection portion of statute citation 

    Returns:
        List of strings representing the subsection bits

    >>> parse_subsection('(c)(2)')
    ['c', '2']
    """
    subsections = []
    bits = re.split(r'[-(\s]', s) 
    for bit in bits:
        if bit:
            subsections.append(re.sub(r'[)]$', '', bit))
    return subsections

def parse_ilcs_statute(s):
    statute_parts = []
    m = ilcs_statute_re.match(s)
    if not m:
        return statute_parts 

    statute_parts.append((m.group('chapter'), 'chapter'))
    statute_parts.append((m.group('act_prefix'), 'act_prefix'))
    statute_parts.append((m.group('section'), 'section'))
    for ss in parse_subsection(m.group('subsection')):
        statute_parts.append((ss, 'subsection'))

    return statute_parts

def parse_ilrs_statute(s):
    statute_parts = []
    m = ilrs_statute_re.match(s)
    if not m:
        return statute_parts

    statute_parts.append((m.group('chapter'), 'chapter'))
    statute_parts.append((m.group('paragraph'), 'paragraph'))
    for ss in parse_subsection(m.group('subsection')):
        statute_parts.append((ss, 'subsection'))

    return statute_parts

def fix_ambiguous_statute(s):
    """
    Fix known badly formed statutes that can't easily be parsed
    by our rule-based parsers.

    Args:
        s (str): String containing an ILCS or ILRS statute

    Returns:
        String with statute that can be parsed
    """
    bad_statute_lookup = {
        '625 5 11 501 A 2': '625-5/11-501(a)(2)',
        '625 5 11 501 A2': '625-5/11-501(a)(2)',
        '625 5 11 501 A1': '625-5/11-501(a)(1)',
        '625 5 11 402': '625-5/11-402',
        '625 5 12 201B': '625-5/12-201(b)',
        '625 5 3 707': '625-5/3-707',
        '625 5 6 303': '625-5/6-303',
        '625 5 11 501 A4': '625-5/11-501(a)(4)',
        '625 5 6 393 9': '625-5/6-393(9)',
        '625 5 11 501 A': '625-5/11-501(a)',
        '720/5.0/16A-3-A': '720-5/16A(3)(a)',
        '720 5-18-5A': '720-5/18(5)(a)',
        '720-5 11-20.1(A)(7)': '720-5/11-20.1(a)(7)',
        '720/5-19-1': '720-5/19-1',
        '720-5/18-2(a)(4)': '720-5/18-2(a)(4)',
        '720-550.0/4-C': '720-550/4(c)',
        '625 5/11-501a1': '625-5/11-501(a)(1)',
        '625 5/11-501a2': '625-5/11-501(a)(2)',
        # HACK: I could probably improve the regexes to catch these, but there
        # aren't very many and it's crunch time
        '625-5/11-501a-2': '625-5/11-501(a)(2)',
        '625-5/11-501a1': '625-5/11-501(a)(1)',
        '625-5/11-501a2': '625-5/11-501(a)(2)',
        '625-5/11-501a6': '625-5/11-501(a)(6)',
        '720 5/19-1a': '720-5/19-1(a)',
        '720 5/8-4 9-1a1': '720-5/8-4(720-5/9-1(a))',
        '720-5 8-4/9-(1)(a)(1)': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/17-1(b)(a)': '720-5/17-1(B)(a)',
        '720-5/17-1(b)(d)': '720-5/17-1(B)(d)',
        '720-5/17-1(b)(e)': '720-5/17-1(B)(e)',
        '720-5/31-1a': '720-5/31-1(a)',
        '720-5/8-2 12-11a1': '720-5/8-2(720-5/12-11(a)(1))',
        '720-5/8-4 (720 5-18-5a)': '720-5/8-4(720-5/18-5(a))',
        '720-5/8-4(720 5/18-5a)': '720-5/8-4(720-5/18-5(a))',
        '720-5/8-4(a)//720-5/9-1-a-1': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/8-4(a)720-5/9-1a1': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/8-4-a//720-5/19-3-a': '720-5/8-4(720-5/19-3(a))',
        '720-5/8-4/(720-5/9-1a1': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/9-4(720-5/9-1(a)(1)': '720-5/8-4(720-5/9-1(a)(1))',
        '720-570\\401a(7.5)aii': '720-570/401(a)(7.5)(A)(ii)',
        '720-570\\401a(7.5)bii': '720-570/401(a)(7.5)(B)(ii)',
        '720-570\\405.(a)': '720-570/405(a)',
        '720-5\\16a-3-h(1)': '720-5/16A-3(h)(1)',
        '720-5\8-4(10-2-a-6)': '720-5/8-4(720-5/10-2(a)(6))',
        '720-5\8-4(12-14.1a1)': '720-5/8-4(720-5/12-14.1(a)(1))',
        '720-5\8-4(12-16-b)': '720-5/8-4(720-5/12-16(b))',
        '720-5\8-4(18-3a)': '720-5/8-4(720-5/18-3(a))',
        '720-5\8-4(18-3a)': '720-5/8-4(720-5/18-3(a))',
        '720-5\8-4(20-1-a)': '720-5/8-4(720-5/20-1(a))',
        '720-5\8-4(20-1.1-a(1': '720-5/8-4(720-5/20-1.1(a)(1))',
        '720-5\8-4(31-1a)': '720-5/8-4(720-5/31-1(a))',
        '720-5\8-4(31-6-c)': '720-5/8-4(720-5/31-6(c))',
        '720-8-4(720-5/18-2a)': '720-5/8-4(720-5/18-2(a))',
        # This is a pretty common source of ambiguity.  It's hard to write
        # a good regex for statutes like this without picking through the
        # entire code/IUCR crosswalk.  The reason: sections can end in
        # letters and contain hyphens, so it's hard to know whether a
        # number/letter is part of the section or subsection and whether the
        # hyphen is part of the section or used as a separator between
        # sections and subsections.
        '720/5.0/16a-3-a': '720-5/16A-3(a)',
        '625-5/11-5-1(D)1(F)': '625-5/11-501(d)(1)(F)',
        '625-5/11-5-1(D)1(F)1': '625-5/11-501(d)(1)(F)',
        '720 5/8-4 9-1A1': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/8-2 12-11A1': '720-5/8-2(720-5/12-11(a)(1))',
        '720-5 8-4/9-(1)(A)(1)': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/8-2(9-1)': '720-5/8-2(720-5/9-1)',
        '720-5/8-4 (720 5-18-5A)': '720-5/8-4(720-5/18-5(a))',
        '720-5/8-4(720 5/18-5A)': '720-5/8-4(720-5/18-5(a))',
        '720-5/8-4(A)720-5/9-1A1': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/8-4/(720-5/9-1A1': '720-5/8-4(720-5/9-1(a)(1))',
        '720-5/9-4(720-5/9-1(A)(1)': '720-5/8-4(720-5/9-1(a)(1))',
        '720-550/5(E)3': '720-550/5(e)(3)',
        '720-5\8-1(12-11(A)2)': '720-5/8-1(720-5/12-11(a)(2)',
        '720-5\8-2(16-1(A)-1)': '720-5/8-2(720-5/16-1(a)(1))',
        # (a)(1)(2) and (a)(1)(3) subsections don't really make sense, but just write
        # them that way to make parsing easier
        '720-5\8-2(16-1(A)1)2': '720-5/8-2(720-5/16-1(a)(1)(2))',
        '720-5\8-2(16-1(A)1)3': '720-5/8-2(720-5/16-1(a)(1)(3))',
        '720-5\8-2(17-3(A)1)': '720-5/8-2(720-5/17-3(a)(1))',
        '720-5\8-2(18-2)': '720-5/8-2(720-5/18-2)',
        '720-5\8-2(26-1(A)4)': '720-5/8-2(720-5/26-1(a)(4))',
        '720-5\8-2(570\401D)': '720-5/8-2(720-570/401(d))',
        '720-5\8-2(9-1)': '720-5/8-2(720-5/9-1)',
        '720-5\8-2\31A-1.1-A2': '720-5/8-2(720-5/31A-1.1(a)(2))',
        '720-5\8-4(12-14.1A1)': '720-5/8-4(720-5/12-14.1(a)(1))',
        '720-5\8-4(18-3A)': '720-5/8-4(720-5/18-3(a))',
        '720-5\8-4(401-A-2-D)': '720-5/8-4(720-570/401(a)(2)(d))',
        '720-8-4(720-5/18-2A)': '720-5/8-4(720-5/18-2(a))',
        '720/5.0/16A-3-A': '720-5/16A-3(a)',
        '720-5/32-4A': '720-5/32-4a',
        '720-5/32-4A(A)(2)': '720-5/32-4a(a)(2)',
        '720-5\8-1(32-4A(A)2)': '720-5/8-1(720-5/32-4a(a)(2))',
        '720-5\8-2(570\\401D)': '720-5/8-2(720-570/401(d))',
    }

    try:
        return bad_statute_lookup[s]
    except KeyError:
        try:
            return bad_statute_lookup[s.lower()]
        except KeyError:
            return s

def get_iucr(s):
    try:
        parsed = parse_statute(s)
        chapter = parsed[0][0]
        act_prefix = parsed[1][0]
        section = parsed[2][0]
        subsections = [ss[0] for ss in parsed[3:]]
        return iucr.lookup_by_ilcs(chapter, act_prefix, section, *subsections)
    except KeyError:
        raise IUCRLookupError(s)

def strip_surrounding_parens(s):
    """
    Strip surrounding parenthesis and curly braces from a statute string.
    """
    s = s.strip('{').strip('}')
    if s[0] == "(" and s[2] != ")":
        s = s[1:]
    if s[-1] == ")" and s[-3] != "(":
        s = s[:-1]

    return s

def strip_attempted_statute(s):
    """
    Strip the citation indicating an attempted, conspiracy or solicited
    criminal offense from a string

    For attempted offenses, this is some version of "720-5/8-4" (ILCS) or
    "38-8-4" (ILRS). For conspiracy offenses it's "720-5/8-2" and for
    solicitation it's "720-5/8-1".
    
    The exact representation can vary widely.

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
    # Handle weird one-off typo case.  There's only one record with
    # this and it has the format '720-5-4(720-5/18-2)'
    if s.startswith("720-5-4"):
        return strip_surrounding_parens(s.replace("720-5-4", "")), "720-5-4"

    ilcs_attempted_statute_re = re.compile(r"""^(?P<attempted>(\({0,1}720[- ]+5{0,1}
        [/\\ ]{0,1} # Optional delimiter
        ){0,1} # Some statutes don't have the leading 720-5
        \({0,1}8-(1|2|4)\){0,1}
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
