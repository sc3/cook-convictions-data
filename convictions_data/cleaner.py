import re

import us


class CityStateSplitter(object):
    PUNCTUATION_RE = re.compile(r'[,.]+')

    # Strings that represent states but are not official abbreviations
    MOCK_STATES = set(['ILL', 'I', 'MX'])

    @classmethod
    def split_city_state(cls, city_state):
        city_state = cls.PUNCTUATION_RE.sub(' ', city_state)
        bits = re.split(r'\s+', city_state.strip())

        last = bits[-1]

        if us.states.lookup(last) or last in cls.MOCK_STATES:
            state = last 
            city_bits = bits[:-1]
        elif len(last) >= 2 and (us.states.lookup(last[-2:]) or
                last[-2:] in cls.MOCK_STATES):
            state = last[-2:]
            city_bits = bits[:-1] + [last[:-2]]
        else:
            state = ""
            city_bits = bits

        return " ".join(city_bits), state


class CityStateCleaner(object):
    CHICAGO_RE = re.compile(r'^CH[I]{0,1}C{0,1}A{0,1}GO{0,1}$')

    CITY_NAME_ABBREVIATIONS = {
        "CHGO": "CHICAGO",
        "CLB": "CLUB",
        "CNTRY": "COUNTRY",
        "HL": "HILLS",
        "HGTS": "HEIGHTS",
        "HTS": "HEIGHTS",
        "PK": "PARK",
        "VILL": "VILLAGE",
        "CTY": "CITY",
    }

    BAD_CHICAGOS = set([
        'CHICAG0',
        'CHICAFO',
    ])

    PROXY_CHICAGOS = set([
        'CHICAGO AVE',
    ])

    @classmethod
    def clean_city_state(cls, city, state, zip=None):
        clean_city = ' '.join([cls._fix_chicago(cls._unabbreviate_city_bit(s))
                               for s in city.split(' ')])

        if state == "ILL":
            clean_state = "IL"
        else:
            clean_state = state

        return clean_city, clean_state

    @classmethod
    def _unabbreviate_city_bit(cls, s):
        try:
            return cls.CITY_NAME_ABBREVIATIONS[s.upper()]
        except KeyError:
            return s

    @classmethod
    def _fix_chicago(cls, s):
        if cls.CHICAGO_RE.match(s):
            return "CHICAGO"
        else:
            return s
