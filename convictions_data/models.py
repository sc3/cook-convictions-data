from datetime import datetime
import logging
import math
import re

import geopy.geocoders

from django.db import models
from django.db.models import Q
from django.contrib.gis.db import models as geo_models
from django.conf import settings
from django.contrib.gis.geos import Point

from model_utils.managers import PassThroughManager

from convictions_data.cleaner import CityStateCleaner, CityStateSplitter
from convictions_data.manager import (CensusPlaceManager,
    CensusTractManager, CommunityAreaManager, DispositionManager)
   
from convictions_data.query import ConvictionQuerySet
from convictions_data.statute import get_iucr
from convictions_data.signals import post_load_spatial_data
    

logger = logging.getLogger(__name__)

MAX_LENGTH=200

ZIPCODE_RE = re.compile(r'^\d{5}$')


class RawDisposition(models.Model):
    """Disposition record loaded verbatim from the raw CSV"""
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


class Disposition(models.Model):
    """Disposition record with cleaned/transformed data"""
    raw_disposition = models.ForeignKey(RawDisposition)

    # ID Fields 
    case_number = models.CharField(max_length=MAX_LENGTH, db_index=True)
    sequence_number = models.CharField(max_length=MAX_LENGTH)
    ctlbkngno = models.CharField(max_length=MAX_LENGTH)
    fgrprntno = models.CharField(max_length=MAX_LENGTH)
    statepoliceid = models.CharField(max_length=MAX_LENGTH)
    fbiidno = models.CharField(max_length=MAX_LENGTH)
    dob = models.DateField(null=True)

    st_address = models.CharField(max_length=MAX_LENGTH)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)
    county = models.CharField(max_length=80, default="")

    arrest_date = models.DateField(null=True)
    initial_date = models.DateField(null=True, db_index=True)
    chrgdispdate = models.DateField(null=True, db_index=True)

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
    minsent_years = models.IntegerField(null=True)
    minsent_months = models.IntegerField(null=True)
    minsent_days = models.IntegerField(null=True)
    minsent_life = models.BooleanField(default=False)
    minsent_death = models.BooleanField(default=False)
    maxsent_years = models.IntegerField(null=True)
    maxsent_months = models.IntegerField(null=True)
    maxsent_days = models.IntegerField(null=True)
    maxsent_life = models.BooleanField(default=False)
    maxsent_death = models.BooleanField(default=False)
    amtoffine = models.IntegerField(null=True)

    final_statute = models.CharField(max_length=50, default="",
        help_text="Field to make querying easier.  Set to the value of "
        "ammndchargstatute if present, otherwise set to the value of statute",
        db_index=True)
    final_chrgdesc = models.CharField(max_length=50, default="", db_index=True)
    final_chrgtype = models.CharField(max_length=1, choices=CHRGTYPE_CHOICES,
        default="", db_index=True)
    final_chrgclass = models.CharField(max_length=1, choices=CHRGCLASS_CHOICES,
        default="", db_index=True)
    iucr_code = models.CharField(max_length=4, default="", db_index=True)
    iucr_category = models.CharField(max_length=50, default="", db_index=True)
    
    # Spatial fields
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    community_area = models.ForeignKey('CommunityArea', null=True,
        on_delete=models.SET_NULL)
    place = models.ForeignKey('CensusPlace', null=True, on_delete=models.SET_NULL)

    conviction = models.ForeignKey('Conviction', null=True,
        on_delete=models.SET_NULL)

    # Use a custom manager to add geocoding methods
    objects = DispositionManager()

    def __init__(self, *args, **kwargs):
        super(Disposition, self).__init__(*args, **kwargs)
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
        """Load fields from related RawDisposition model"""
        for field_name in RawDisposition._meta.get_all_field_names():
            if field_name == "disposition":
                # Skip reverse name on related field
                continue

            self.load_field_from_raw(field_name)

        return self

    def load_field_from_raw(self, field_name):
        val = getattr(self.raw_disposition, field_name)
        try:
            loader = getattr(self, "_load_field_{}".format(field_name))
            loader(val)
        except AttributeError:
            try:
                parser = getattr(self, "_parse_{}".format(field_name))
                val = parser(val)
            except AttributeError:
                pass
            except ValueError as e:
                msg = ("Error when parsing '{}' from RawDisposition with case "
                       "number '{}': {}")
                msg = msg.format(field_name, self.raw_disposition.case_number, e)
                logger.warning(msg)
                if 'date' in field_name or field_name == 'dob':
                    val = None

            setattr(self, field_name, val) 
        
        return self

    def _load_field_city_state(self, val):
        self.city, self.state = self._parse_city_state(val)
        if not self.state:
            self.state = self._detect_state(self.city)

        return self

    def _load_field_minsent(self, val):
        self.minsent_years, self.minsent_months, self.minsent_days, self.minsent_life, self.minsent_death = self._parse_sentence(val)
        return self

    def _load_field_maxsent(self, val):
        self.maxsent_years, self.maxsent_months, self.maxsent_days, self.maxsent_life, self.maxsent_death = self._parse_sentence(val)
        return self

    def _load_field_statute(self, val):
        self.statute = val

        if val:
            self.final_statute = val

            offenses = get_iucr(val)
            if len(offenses) == 1:
                self.iucr_code = offenses[0].code
                self.iucr_category = offenses[0].offense_category
            else:
                logger.warn("Multiple matching IUCR offenses found for statute '{}'".format(val))
                       
        return self


    def _load_field_chrgdesc(self, val):
        self.chrgdesc = val
        if val:
            self.final_chrgdesc = val
        return self

    def _load_field_chrgtype(self, val):
        self.chrgtype = val
        if val:
            self.final_chrgtype = val
        return self

    def _load_field_chrgclass(self, val):
        self.chrgclass = val
        if val:
            self.final_chrgclass = val
        return self

    def _load_field_ammndchargstatute(self, val):
        self.ammndchargstatute = val

        if val:
            self.final_statute = val

            offenses = get_iucr(val)
            if len(offenses) == 1:
                self.iucr_code = offenses[0].code
                self.iucr_category = offenses[0].offense_category
            else:
                logger.warn("Multiple matching IUCR offenses found for statute '{}'".format(val))

        return self

    def _load_field_ammndchrgdescr(self, val):
        self.ammndchrgdescr = val
        if val:
            self.final_chrgdesc = val
        return self

    def _load_field_ammndchrgtype(self, val):
        self.ammndchrgtype = val
        if val:
            self.final_chrgtype = val
        return self

    def _load_field_ammndchrgclass(self, val):
        self.ammndchrgclass = val
        if val:
            self.final_chrgclass = val
        return self

    def boundarize(self):
        pnt = Point(self.lon, self.lat)
        try:
            self.community_area = CommunityArea.objects.get(boundary__contains=pnt)
            self.save()
            return self.community_area
        except CommunityArea.DoesNotExist:
            try:
                self.place = CensusPlace.objects.get(boundary__contains=pnt)
                self.save()
                return self.place
            except CensusPlace.DoesNotExist:
                return False

       
    @classmethod
    def _parse_city_state(cls, city_state):
        city, state = CityStateSplitter.split_city_state(city_state)
        return CityStateCleaner.clean_city_state(city, state)

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
    def _parse_sentence(cls, s):
        if s == "88888888":
            return None, None, None, True, False
        
        if s == "99999999":
            return None, None, None, False, True

        val = s.zfill(8)
        year = int(val[0:3])
        mon = int(val[3:5])
        day = int(val[5:8])
        return year, mon, day, False, False

    @classmethod
    def _parse_amtoffine(cls, s):
        return cls._parse_int(s)
    
    @classmethod
    def _parse_int(cls, s):
        if not s:
            return None

        return int(s)

    @classmethod
    def get_community_area_cache(cls):
        try:
            return cls._community_area_cache
        except AttributeError:
            cls._community_area_cache = {ca.id: ca for ca in CommunityArea.objects.all()}
            return cls._community_area_cache

    @classmethod
    def get_place_cache(cls):
        try:
            return cls._place_cache
        except AttributeError:
            cls._place_cache = {ca.id: ca for ca in CensusPlace.objects.all()}
            return cls._place_cache

    @classmethod
    def create_conviction(cls, **kwargs):
        """
        Convenience method for creating a conviction from a disposition

        This exists to avoid circular imports in DispositionQuerySet.

        """
        return Conviction.objects.create(**kwargs)


class Conviction(models.Model):
    case_number = models.CharField(max_length=MAX_LENGTH, db_index=True)

    ctlbkngno = models.CharField(max_length=MAX_LENGTH)
    fgrprntno = models.CharField(max_length=MAX_LENGTH)
    statepoliceid = models.CharField(max_length=MAX_LENGTH)
    fbiidno = models.CharField(max_length=MAX_LENGTH)
    dob = models.DateField(null=True)

    st_address = models.CharField(max_length=MAX_LENGTH)
    city = models.CharField(max_length=MAX_LENGTH)
    state = models.CharField(max_length=2)
    zipcode = models.CharField(max_length=5)
    county = models.CharField(max_length=80, default="")

    sex = models.CharField(max_length=10, choices=SEX_CHOICES, db_index=True)

    chrgdispdate = models.DateField(null=True)
    final_statute = models.CharField(max_length=50, default="",
        help_text="Field to make querying easier.  Set to the value of "
        "ammndchargstatute if present, otherwise set to the value of statute",
        db_index=True)
    final_chrgdesc = models.CharField(max_length=50, default="", db_index=True)
    final_chrgtype = models.CharField(max_length=1, choices=CHRGTYPE_CHOICES,
        default="", db_index=True)
    final_chrgclass = models.CharField(max_length=1, choices=CHRGCLASS_CHOICES,
        default="", db_index=True)
    iucr_code = models.CharField(max_length=4, default="", db_index=True)
    iucr_category = models.CharField(max_length=50, default="", db_index=True)

    community_area = models.ForeignKey('CommunityArea', null=True,
        on_delete=models.SET_NULL)
    place = models.ForeignKey('CensusPlace', null=True,
        on_delete=models.SET_NULL)


    objects = PassThroughManager.for_queryset_class(ConvictionQuerySet)()

    def __str__(self):
        return "{} {} {}".format(self.case_number, self.chrgdispdate, self.final_statute)


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

class CensusFieldsMixin(geo_models.Model):
    # Census fields
    total_population = geo_models.IntegerField(null=True)
    total_population_moe = geo_models.IntegerField(null=True)
    per_capita_income = geo_models.IntegerField(null=True,
        help_text=("PER CAPITA INCOME IN THE PAST 12 MONTHS (IN 2010 "
            "INFLATION-ADJUSTED DOLLARS)"))
    per_capita_income_moe = geo_models.IntegerField(null=True)

    class Meta:
        abstract = True


class ConvictionsAggregateMixin(object):
    @classmethod
    def get_conviction_model(cls):
        return Conviction

GEOJSON_FIELDS_BASE = [
    'name',
    'total_population',
    'num_convictions',
    'convictions_per_capita',
    'num_homicides',
    'boundary',
]


class CommunityArea(ConvictionsAggregateMixin, CensusFieldsMixin, geo_models.Model):
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

    objects = CommunityAreaManager() 

    FIELD_MAPPING = {
        'number': 'AREA_NUMBE',
        'name': 'COMMUNITY',
        'shape_area': 'SHAPE_AREA',
        'shape_len': 'SHAPE_LEN',
        'boundary': 'MULTIPOLYGON',
    }

    GEOJSON_FIELDS = GEOJSON_FIELDS_BASE + [
        'number',
    ]

    def __str__(self):
        return self.name

    def aggregate_census_fields(self):
        fields = ('total_population', 'per_capita_income')
        for field in fields:
            self.aggregate_census_field(field)

    def aggregate_census_field(self, field):
        moe_field = field + "_moe"
        aggregate = 0
        aggregate_moe = 0
        for tract in self.censustract_set.all():
            val = getattr(tract, field)
            if val is not None:
                aggregate += val

                moe = getattr(tract, moe_field)
                aggregate_moe += moe**2

        aggregate_moe = math.sqrt(aggregate_moe) 
        setattr(self, field, aggregate)
        setattr(self, moe_field, aggregate_moe)
        return aggregate, aggregate_moe

    @classmethod
    def get_conviction_related_column_name(cls):
        return 'community_area_id'


class CensusTract(CensusFieldsMixin, geo_models.Model):
    """
    Census Tract

    Wraps
    https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Census-Tracts-2010/5jrd-6zik 
    """
    statefp10 = geo_models.CharField(max_length=2)
    countyfp10 = geo_models.CharField(max_length=3)
    tractce10 = geo_models.CharField(max_length=6)
    geoid10 = geo_models.CharField(max_length=11, db_index=True)
    name = geo_models.CharField(max_length=7, db_index=True)
    community_area_number = geo_models.IntegerField()
    notes = geo_models.CharField(max_length=80)

    # Spatial fields
    boundary = geo_models.MultiPolygonField()

    community_area = geo_models.ForeignKey(CommunityArea, null=True,
        on_delete=models.SET_NULL)

    objects = CensusTractManager()

    FIELD_MAPPING = {
        'statefp10': 'STATEFP10',
        'countyfp10': 'COUNTYFP10',
        'tractce10': 'TRACTCE10',
        'geoid10': 'GEOID10',
        'name': 'NAME10',
        'community_area_number': 'COMMAREA_N',
        'notes': 'NOTES',
        'boundary': 'MULTIPOLYGON',
    }

    def __str__(self):
        return self.geoid10

    @classmethod
    def get_community_area_model(cls):
        return CommunityArea


class CensusPlace(ConvictionsAggregateMixin, CensusFieldsMixin, geo_models.Model):
    """
    Census Place

    Wraps TIGER Shapefile http://www2.census.gov/geo/tiger/TIGER2010/PLACE/2010/tl_2010_17_place10.zip

    """
    # From ShapeFile
    statefp10 = geo_models.CharField(max_length=2)
    placefp10 = geo_models.CharField(max_length=5)
    placens10 = geo_models.CharField(max_length=8)
    geoid10 = geo_models.CharField(max_length=11, db_index=True)
    name = geo_models.CharField(max_length=7, db_index=True)
    namelsad10 = geo_models.CharField(max_length=100)
    lsad10 = geo_models.CharField(max_length=2)
    classfp10 = geo_models.CharField(max_length=2)
    pcicbsa10 = geo_models.CharField(max_length=1)
    pcinecta10 = geo_models.CharField(max_length=1)
    mtfcc10 = geo_models.CharField(max_length=5)
    funcstat10 = geo_models.CharField(max_length=1)
    aland10 = geo_models.FloatField()
    awater10 = geo_models.FloatField()
    intptlat10 = geo_models.CharField(max_length=11)
    intptlon10 = geo_models.CharField(max_length=12)

    # Custom Fields
    in_chicago_msa = geo_models.BooleanField(default=False,
        help_text=("Is this place within one of the counties that is part "
            "of Chicago's Metropolitan Statistical Area: Cook, DeKalb, "
            "DuPage, Grundy, Kane, Kendall, McHenry, Will, Lake"))

    # Spatial fields
    boundary = geo_models.MultiPolygonField()

    objects = CensusPlaceManager() 

    FIELD_MAPPING = {
        'placefp10': 'PLACEFP10',
        'placens10': 'PLACENS10',
        'geoid10': 'GEOID10',
        'name': 'NAME10',
        'namelsad10': 'NAMELSAD10',
        'lsad10': 'LSAD10',
        'classfp10': 'CLASSFP10',
        'pcicbsa10': 'PCICBSA10',
        'pcinecta10': 'PCINECTA10',
        'mtfcc10': 'MTFCC10',
        'funcstat10': 'FUNCSTAT10',
        'aland10': 'ALAND10',
        'awater10': 'AWATER10',
        'intptlat10': 'INTPTLAT10',
        'intptlon10': 'INTPTLON10',
        'boundary': 'MULTIPOLYGON',
    }

    GEOJSON_FIELDS = GEOJSON_FIELDS_BASE

    @classmethod
    def get_conviction_related_column_name(cls):
        return 'place_id'


def handle_post_load_spatial_data(sender, **kwargs):
    if kwargs['model'] == CensusTract:
        CensusTract.objects.set_community_area_relations()

post_load_spatial_data.connect(handle_post_load_spatial_data)
