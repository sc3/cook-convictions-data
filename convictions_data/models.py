import re
from datetime import datetime
import logging

import geopy.geocoders
import us

from django.db import models
from django.db.models import Q
from django.contrib.gis.db import models as geo_models
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator

from convictions_data.geocoders import BatchOpenMapQuest

logger = logging.getLogger(__name__)

MAX_LENGTH=200

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

ZIPCODE_RE = re.compile(r'^\d{5}$')

# Strings that represent states but are not official abbreviations
MOCK_STATES = set(['ILL', 'I', 'MX'])

class ConvictionsQuerySet(models.query.QuerySet):
    """Custom QuerySet that adds bulk geocoding capabilities"""

    def geocode(self, batch_size=100):
        geocoder = BatchOpenMapQuest(
            api_key=settings.CONVICTIONS_GEOCODER_API_KEY)
        p = Paginator(self, batch_size)
        for i in p.page_range:
            self._geocode_batch(p.page(i), geocoder)

    def ungeocoded(self):
        return self.filter(lat=None, lon=None)

    def load_from_raw(self, save=False):
        for model in self:
            model.load_from_raw()
            if save:
                model.save()

    def has_geocodable_address(self):
        q = Q(address="")
        q |= Q(zipcode="")
        q |= (Q(state="") & Q(city=""))
        return self.exclude(q)

    def has_bad_address(self):
        q = Q(state='') | Q(city='')
        q = q & Q(zipcode='')
        return self.filter(q)

    @classmethod
    def _geocode_batch(cls, page, geocoder):
        addresses = [obj.geocoder_address for obj in page]
        results = geocoder.batch_geocode(addresses)
        for i in range(len(page.object_list)):
            obj = page.object_list[i]
            loc = results[i]
            obj.lat = loc.latitude
            obj.lon = loc.longitude
            obj.save()


class ConvictionManager(models.Manager):
    """Custom manager that uses ConvictionsQuerySet"""

    def get_query_set(self):
        return ConvictionsQuerySet(self.model, using=self._db)

    def geocode(self):
        return self.get_query_set().geocode()

    def ungeocoded(self):
        return self.get_query_set().ungeocoded()

    def load_from_raw(self, save=False):
        return self.get_query_set().load_from_raw(save)

    def has_bad_address(self):
        return self.get_query_set().has_bad_address()

    def has_geocodable_address(self):
        return self.get_query_set().has_geocodable_address()



class RawConviction(models.Model):
    """Conviction record loaded verbatim from the raw CSV"""
    # case_number is not unique 
    case_number = models.CharField(max_length=MAX_LENGTH)
    sequence_number = models.CharField(max_length=MAX_LENGTH)
    st_address = models.CharField(max_length=MAX_LENGTH)
    city_state = models.CharField(max_length=MAX_LENGTH)
    zipcode = models.CharField(max_length=MAX_LENGTH)
    ctlbkngno = models.CharField(max_length=MAX_LENGTH)
    fgrprntno = models.CharField(max_length=MAX_LENGTH)
    statepoliceid = models.CharField(max_length=MAX_LENGTH)
    fbiidno = models.CharField(max_length=MAX_LENGTH)
    # Field in CSV is "DOB", not the lowercase "dob"
    dob = models.CharField(max_length=MAX_LENGTH)
    arrest_date = models.CharField(max_length=MAX_LENGTH)
    initial_date = models.CharField(max_length=MAX_LENGTH)
    sex = models.CharField(max_length=MAX_LENGTH)
    statute = models.CharField(max_length=MAX_LENGTH)
    chrgdesc = models.CharField(max_length=MAX_LENGTH)
    chrgtype = models.CharField(max_length=MAX_LENGTH)
    chrgtype2 = models.CharField(max_length=MAX_LENGTH)
    chrgclass = models.CharField(max_length=MAX_LENGTH)
    chrgdisp = models.CharField(max_length=MAX_LENGTH)
    chrgdispdate = models.CharField(max_length=MAX_LENGTH)
    ammndchargstatute = models.CharField(max_length=MAX_LENGTH)
    ammndchrgdescr = models.CharField(max_length=MAX_LENGTH)
    ammndchrgtype = models.CharField(max_length=MAX_LENGTH)
    ammndchrgclass = models.CharField(max_length=MAX_LENGTH)
    minsent = models.CharField(max_length=MAX_LENGTH)
    maxsent = models.CharField(max_length=MAX_LENGTH)
    amtoffine = models.CharField(max_length=MAX_LENGTH)


class Conviction(models.Model):
    """Conviction record with cleaned/transformed data"""

    # Choices for validation of various fields
    SEX_CHOICES = (
      ('male', 'Male'),
      ('female', 'Female'),
    )

    CHRGTYPE_CHOICES = (
        ('A', 'A'),
        ('C', 'C'),
        ('F', 'F'),
        ('M', 'M'),
        ('R', 'R'),
        ('T', 'T'),
        ('V', 'V'),
        ('Y', 'Y'),
    )

    CHRGTYPE_VALUES = [v for v,c in CHRGTYPE_CHOICES]

    CHRGTYPE2_CHOICES = (
        ('2', '2'),
        ('3', '3'),
        ('Felony', 'Felony'),
        ('Misdemeanor', 'Misdemeanor'),
        ('R', 'R'),
        ('Traffic', 'Traffic'),
        ('V', 'V'),
        ('Y', 'Y'),
    )

    CHRGCLASS_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        # 'D' is only seen in ammndchrgclass
        ('D', 'D'),
        # 'F' is only seen in ammndchrgclass
        ('F', 'F'),
        ('G', 'G'),
        ('M', 'M'),
        ('N', 'N'),
        # 'O' is only seen in ammndchrgclass
        ('O', 'O'),
        ('P', 'P'),
        ('T', 'T'),
        ('U', 'U'),
        ('X', 'X'),
        ('Z', 'Z'),
    )

    CHRGCLASS_VALUES = [v for v,c in CHRGCLASS_CHOICES]

    raw_conviction = models.ForeignKey(RawConviction)

    # ID Fields 
    case_number = models.CharField(max_length=MAX_LENGTH)
    sequence_number = models.CharField(max_length=MAX_LENGTH)
    ctlbkngno = models.CharField(max_length=MAX_LENGTH)
    fgrprntno = models.CharField(max_length=MAX_LENGTH)
    statepoliceid = models.CharField(max_length=MAX_LENGTH)
    fbiidno = models.CharField(max_length=MAX_LENGTH)

    st_address = models.CharField(max_length=MAX_LENGTH)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)
    county = models.CharField(max_length=80, default="")

    dob = models.DateField(null=True)
    arrest_date = models.DateField(null=True)
    initial_date = models.DateField(null=True)
    chrgdispdate = models.DateField(null=True)

    sex = models.CharField(max_length=10, choices=SEX_CHOICES)

    # Fields that describe the charges
    statute = models.CharField(max_length=50, help_text=("The statutory or local "
        "ordinance citation for the offense which the defendant was "
        "convicted."))
    chrgdesc = models.CharField(max_length=50, help_text="Initial Charge Description")
    chrgtype = models.CharField(max_length=1, choices=CHRGTYPE_CHOICES)
    chrgtype2 = models.CharField(max_length=15, choices=CHRGTYPE2_CHOICES)
    chrgclass = models.CharField(max_length=1, choices=CHRGCLASS_CHOICES)
    chrgdisp = models.CharField(max_length=30)
    ammndchargstatute = models.CharField(max_length=50)
    ammndchrgdescr = models.CharField(max_length=50)
    ammndchrgtype = models.CharField(max_length=1, choices=CHRGTYPE_CHOICES)
    ammndchrgclass = models.CharField(max_length=1, choices=CHRGCLASS_CHOICES)
    minsent = models.IntegerField(null=True)
    maxsent = models.IntegerField(null=True)
    amtoffine = models.IntegerField(null=True)
    
    # Spatial fields
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    community_area = models.ForeignKey('CommunityArea', null=True)

    # Use a custom manager to add geocoding methods
    objects = ConvictionManager()

    PUNCTUATION_RE = re.compile(r'[,.]+')
    CHICAGO_RE = re.compile(r'^CH[I]{0,1}C{0,1}A{0,1}GO{0,1}$')

    def __init__(self, *args, **kwargs):
        super(Conviction, self).__init__(*args, **kwargs)
        if self.pk is None:
            # New model, populate it's fields by parsing the values from
            self.load_from_raw()

    def geocode(self, geocoder_cls=geopy.geocoders.OpenMapQuest):
        geocoder = geocoder_cls(
            api_key=settings.CONVICTIONS_GEOCODER_API_KEY,
        )
        address, (self.lat, self.lon) = geocoder.geocode(self.geocoder_address)

        return self

    @property
    def geocoder_address(self):
        if not self.st_address:
            raise ValueError("Need an address to geocode")

        bits = [self.st_address]

        if self.zipcode:
            bits.append(self.zipcode)
        elif self.city and self.state:
            bits.append(self.city)
            bits.append(self.state)
        else:
            raise ValueError("Need a zipcode or city and state to geocode")

        return ",".join(bits)

    def load_from_raw(self):
        """Load fields from related RawConviction model"""
        for field_name in RawConviction._meta.get_all_field_names():
            if field_name == "conviction":
                # Skip reverse name on related field
                continue

            val = getattr(self.raw_conviction, field_name)
            try:
                parser = getattr(self, "_parse_{}".format(field_name))
                val = parser(val)
            except AttributeError:
                pass
            except ValueError as e:
                msg = ("Error when parsing '{}' from RawConviction with case "
                       "number '{}': {}")
                msg = msg.format(field_name, self.raw_conviction.case_number, e)
                logger.warning(msg)
                if 'date' in field_name or field_name == 'dob':
                    val = None

            setattr(self, field_name, val) 

        self.city, self.state = self._parse_city_state(self.raw_conviction.city_state)
        if not self.state:
            self.state = self._detect_state(self.city)

        return self

    def boundarize(self):
        do_save = False
        matching_municipalities = Municipality.objects.filter(municipality_name__iexact=self.city)
        if matching_municipalities.count():
            self.county = "Cook"
            do_save = True

        if self.lat and self.lon and self.city.upper() == "CHICAGO":
            pnt = Point(self.lon, self.lat)
            self.community_area = CommunityArea.objects.get(boundary__contains=pnt)
            do_save = True

        if do_save:
            self.save()
       
    @classmethod
    def _parse_city_state(cls, city_state):
        city, state = cls._split_city_state(city_state)
        return cls._clean_city_state(city, state)

    @classmethod
    def _split_city_state(cls, city_state):
        city_state = cls.PUNCTUATION_RE.sub(' ', city_state)
        bits = re.split(r'\s+', city_state.strip())

        last = bits[-1]

        if us.states.lookup(last) or last in MOCK_STATES:
            state = last 
            city_bits = bits[:-1]
        elif len(last) >= 2 and (us.states.lookup(last[-2:]) or
                last[-2:] in MOCK_STATES): 
            state = last[-2:]
            city_bits = bits[:-1] + [last[:-2]]
        else:
            state = ""
            city_bits = bits

        return " ".join(city_bits), state

    @classmethod
    def _clean_city_state(cls, city, state):
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
            return CITY_NAME_ABBREVIATIONS[s.upper()]
        except KeyError:
            return s

    @classmethod
    def _fix_chicago(cls, s):
        if cls.CHICAGO_RE.match(s):
            return "CHICAGO"
        else:
            return s

    @classmethod
    def _parse_zipcode(cls, zipcode):
        zipcode = zipcode.strip()

        if not ZIPCODE_RE.match(zipcode):
            return ""

        return zipcode

    @classmethod
    def _detect_state(cls, city):
        # Check and see if the city name
        # matches the name of a municipality in Cook County.  If it does,
        # set the state to IL.
        q = Q(municipality_name__iexact=city) | Q(agency_name__iexact=city)
        
        if Municipality.objects.filter(q).count():
            return "IL"

        return ""

    @classmethod
    def _parse_dob(cls, dob):
        return cls._parse_date(dob)

    @classmethod
    def _parse_arrest_date(cls, arrest_date):
        return cls._parse_date(arrest_date)

    @classmethod
    def _parse_initial_date(cls, date_string):
        return cls._parse_date(date_string)

    @classmethod
    def _parse_chrgdispdate(cls, date_string):
        return cls._parse_date(date_string)

    @classmethod
    def _parse_date(cls, date_string, date_format="%d-%b-%y"):
        if not date_string:
            return None

        dt = datetime.strptime(date_string, date_format)
        # Try to correctly interpret the two digit year.
        if dt.year > datetime.now().year:
            dt = datetime(dt.year - 100, dt.month, dt.day)

        return dt.date()

    @classmethod
    def _parse_sex(cls, sex_string):
        cln_sex_string = sex_string.strip()
        if cln_sex_string and cln_sex_string.lower() not in ("male", "female"):
            raise ValueError("Unexpected value '{}' for 'sex' field".format(
                cln_sex_string))

        return cln_sex_string.lower()

    @classmethod
    def _parse_chrgtype(cls, s):
        cln_s = s.strip()
        if cln_s == "Felony":
            chrgtype = "F"
        else:
            chrgtype = cln_s

        if chrgtype and chrgtype not in cls.CHRGTYPE_VALUES:
            msg = "Unexpected value '{}'".format(chrgtype)
            raise ValueError(msg)

        return chrgtype

    @classmethod
    def _parse_chrgclass(cls, s):
        if s and s not in cls.CHRGCLASS_VALUES:
            msg = "Unexpected value '{}'".format(s)
            raise ValueError(msg)

        return s

    @classmethod
    def _parse_ammndchrgtype(cls, s):
        return cls._parse_chrgtype(s)

    @classmethod
    def _parse_ammndchrgclass(cls, s):
        return cls._parse_chrgclass(s)

    @classmethod
    def _parse_minsent(cls, s):
        return cls._parse_int(s)

    @classmethod
    def _parse_maxsent(cls, s):
        return cls._parse_int(s)

    @classmethod
    def _parse_amtoffine(cls, s):
        return cls._parse_int(s)
    
    @classmethod
    def _parse_int(cls, s):
        if not s:
            return None

        return int(s)


class Municipality(geo_models.Model):
    """
    Cook County, Illinois municipality

    Wraps spatial data set found at
    https://datacatalog.cookcountyil.gov/GIS-Maps/ccgisdata-Municipality/ta8t-zebk
    """
    agency_id = geo_models.IntegerField()
    agency_name = geo_models.CharField(max_length=60)
    municipality_name = geo_models.CharField(max_length=25)
    st_area = geo_models.FloatField()
    sde_length = geo_models.FloatField()
    shape_area = geo_models.FloatField()
    shape_length = geo_models.FloatField()

    boundary = geo_models.MultiPolygonField()
    
    objects = geo_models.GeoManager()

    FIELD_MAPPING = {
        'agency_id': 'AGENCY',
        'agency_name': 'AGENCY_DES',
        'municipality_name': 'MUNICIPALI',
        'st_area': 'ST_AREA_SH',
        'sde_length': 'SDELENGTH_',
        'shape_area': 'SHAPE_area',
        'shape_length': 'SHAPE_len',
        'boundary': 'MULTIPOLYGON',
    }

    @property
    def name(self):
        if self.municipality_name:
            return self.municipality_name
        else:
            return self.agency_name

    def __str__(self):
        return self.name


class CommunityArea(geo_models.Model):
    """
    Chicago Community Area

    Wraps
    https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6
    """
    number = geo_models.IntegerField()
    name = geo_models.CharField(max_length=80)
    shape_area = geo_models.FloatField()
    shape_len = geo_models.FloatField()

    boundary = geo_models.MultiPolygonField()

    objects = geo_models.GeoManager()

    FIELD_MAPPING = {
        'number': 'AREA_NUMBE',
        'name': 'COMMUNITY',
        'shape_area': 'SHAPE_AREA',
        'shape_len': 'SHAPE_LEN',
        'boundary': 'MULTIPOLYGON',
    }

    def __str__(self):
        return self.name
