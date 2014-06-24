import re
from datetime import datetime
import logging

import geopy.geocoders
import us

from django.db import models
from django.db.models import Q
from django.contrib.gis.db import models as geo_models
from django.conf import settings
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
}

ZIPCODE_RE = re.compile(r'^\d{5}$')

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
    raw_conviction = models.ForeignKey(RawConviction)

    # Fields transformed from RawConviction
    case_number = models.CharField(max_length=MAX_LENGTH)
    sequence_number = models.CharField(max_length=MAX_LENGTH)

    address = models.CharField(max_length=MAX_LENGTH)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)

    #ctlbkngno = models.CharField(max_length=MAX_LENGTH)
    #fgrprntno = models.CharField(max_length=MAX_LENGTH)
    #statepoliceid = models.CharField(max_length=MAX_LENGTH)
    #fbiidno = models.CharField(max_length=MAX_LENGTH)

    dob = models.DateField(null=True)
    arrest_date = models.DateField(null=True)
    #initial_date = models.DateField(null=True)
    chrgdispdate = models.DateField(null=True)

    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)

    # Use a custom manager to add geocoding methods
    objects = ConvictionManager()

    PUNCTUATION_RE = re.compile(r'[,.]+')
    CHICAGO_RE = re.compile(r'^CH[I]{0,1}C{0,1}A{0,1}GO$')

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
        if not self.address:
            raise ValueError("Need an address to geocode")

        bits = [self.address]

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
        fields = [
            ('case_number', 'case_number'),
            ('sequence_number', 'sequence_number'),
            ('st_address', 'address'),
            ('zipcode', 'zipcode'),
            ('ctlbkngno', 'ctlbkngno'),
            ('fgrprntno', 'fgrprntno'),
            ('statepoliceid', 'statepoliceid'),
            ('fbiidno', 'fbiidno'), 
            ('dob', 'dob'),
            ('arrest_date', 'arrest_date'),
        ]
        for src_field, dst_field in fields:
            val = getattr(self.raw_conviction, src_field)
            try:
                parser = getattr(self, "_parse_{}".format(dst_field))
                val = parser(val)
            except AttributeError:
                pass
            setattr(self, dst_field, val) 

        self.city, self.state = self._parse_city_state(self.raw_conviction.city_state)

        return self
        
    @classmethod
    def _parse_city_state(cls, city_state):
        """Parse a combined city/state field into city and state parts"""
        city_state = cls.PUNCTUATION_RE.sub(' ', city_state)
        bits = re.split(r'\s+', city_state.strip())
        if len(bits) == 1:
            city = bits[0]
            state = '' 
        elif len(bits) > 1 and len(bits) <= 4:
            city = ' '.join([cls._unabbreviate_city_bit(s.strip())
                             for s in bits[:-1]])
            state = bits[-1]
            if us.states.lookup(state) is None:
                if state.endswith("IL"):
                    # IL is concatenated with the second bit of the city/state
                    # Set the state to "IL" and add the rest of the city to the
                    # city string.
                    city = "{} {}".format(city, state.strip("IL"))
                    state = "IL"
                else:
                    # Assume there's no state and just append the second bit to
                    # the city
                    city += " " + state
                    logger.warning("Unable to parse state from '{}'".format(city_state))
                    state = "" 

        else:
            raise Exception("Unexpected number of bits for '{}'".format(city_state))

        city = cls._clean_city(city, state)
        state = cls._clean_state(city, state)

        return city, state

    @classmethod
    def _unabbreviate_city_bit(cls, s):
        try:
            return CITY_NAME_ABBREVIATIONS[s.upper()]
        except KeyError:
            return s

    @classmethod
    def _parse_zipcode(cls, zipcode):
        zipcode = zipcode.strip()

        if not ZIPCODE_RE.match(zipcode):
            return ""

        return zipcode

    @classmethod
    def _clean_city(cls, city, state):
        if cls.CHICAGO_RE.match(city):
            city = "CHICAGO"

        return city

    @classmethod
    def _clean_state(cls, city, state):
        state = state.upper()

        if state == "ILL":
            state = "IL"
        elif state == "":
            # No state has been specified.  Check and see if the city name
            # matches the name of a municipality in Cook County.  If it does,
            # set the state to IL.
            q = Q(municipality_name__iexact=city) | Q(agency_name__iexact=city)
            municipalities = Municipality.objects.filter(q)
            if municipalities.count():
                state = "IL"

        return state

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

        try:
            dt = datetime.strptime(date_string, date_format)
            # Try to correctly interpret the two digit year.
            if dt.year > datetime.now().year:
                dt = datetime(dt.year - 100, dt.month, dt.day)

            return dt.date()
        except ValueError as e:
            logging.warning(e)
            return None


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


