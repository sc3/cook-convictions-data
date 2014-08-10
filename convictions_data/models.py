from datetime import datetime
import logging
import math
import re

import geopy.geocoders

from django.db import models
from django.db.models import Q, Min
from django.contrib.gis.db import models as geo_models
from django.conf import settings
from django.contrib.gis.db.models.query import GeoQuerySet
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator

from djgeojson.serializers import Serializer as GeoJSONSerializer


from convictions_data.geocoders import BatchOpenMapQuest
from convictions_data.cleaner import CityStateCleaner, CityStateSplitter
from convictions_data.statute import get_iucr
from convictions_data.signals import (pre_geocode_page, post_geocode_page,
    post_load_spatial_data)

logger = logging.getLogger(__name__)

MAX_LENGTH=200

ZIPCODE_RE = re.compile(r'^\d{5}$')

START_DATE = datetime(month=1, day=1, year=2005)
"""
The date that our data begins.
"""

class DispositionQuerySet(models.query.QuerySet):
    """Custom QuerySet that adds bulk geocoding capabilities"""

    def geocode(self, batch_size=100, timeout=1):
        geocoder = BatchOpenMapQuest(
            api_key=settings.CONVICTIONS_GEOCODER_API_KEY,
            timeout=timeout)
        p = Paginator(self, batch_size)
        for i in p.page_range:
            pre_geocode_page.send(sender=self.__class__,
                page_num=i, num_pages=p.num_pages)
            self._geocode_batch(p.page(i), geocoder)
            post_geocode_page.send(sender=self.__class__,
                page_num=i, num_pages=p.num_pages)

    def geocoded(self):
        return self.exclude(lat=None, lon=None)

    def ungeocoded(self):
        return self.filter(lat=None, lon=None)

    def load_from_raw(self, save=False):
        for model in self:
            model.load_from_raw()
            if save:
                model.save()

        return self

    def load_field_from_raw(self, field_name):
        for model in self:
            model.load_field_from_raw(field_name)

        return self

    def has_geocodable_address(self):
        q = Q(st_address="")
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

    def chilike(self):
        qs = self.exclude(city__iexact="Chicago").exclude(city__iexact="Chicago Heights").filter(city__istartswith="ch")
        return list(set([c['city'] for c in qs.values('city')]))

    def in_analysis(self):
        # Limit records in our analysis to those with an initial date from 2005
        # or later and an initial disposition date from 2005 or later
        return self.filter(initial_date__gte=START_DATE,
            chrgdispdate__gte=START_DATE)

    def first_chrgdispdates(self):
        """
        Return a list of case numbers and the first charge disposition date
        for that case.
        """
        return self.values('case_number')\
            .annotate(first_chrgdispdate=Min('chrgdispdate'))\
            .values_list('case_number', 'first_chrgdispdate')

    def from_initial_chrgdispdate(self):
        """
        Filter this queryset to only dispositions from the first court date.

        This produces a SQL query similar to:

        SELECT * 
        FROM convictions_data_disposition 
        WHERE EXISTS(SELECT case_number
            FROM convictions_data_disposition d2
            WHERE d2.initial_date >= '2005-01-01' 
            AND d2.chrgdispdate > '2005-01-01'
            AND d2.case_number = "convictions_data_disposition"."case_number"
            GROUP BY case_number
            HAVING MIN(d2.chrgdispdate) = "convictions_data_disposition".chrgdispdate);
        """
        start_date = START_DATE.strftime("%Y-%m-%d")
        extra_where = ("EXISTS(SELECT case_number "
            "FROM convictions_data_disposition d2 "
            "WHERE d2.initial_date >= '{}' "
            "AND d2.chrgdispdate > '{}' "
            "AND d2.case_number = \"convictions_data_disposition\".\"case_number\" "
            "GROUP BY case_number "
            "HAVING  MIN(d2.chrgdispdate) = \"convictions_data_disposition\".chrgdispdate)")
        extra_where = extra_where.format(start_date, start_date)
        return self.extra(where=[extra_where])

    CONVICTION_IMPORT_FIELDS = [ 
        'case_number',
        'chrgdispdate',
        'city',
        'community_area',
        'county',
        'ctlbkngno',
        'chrgdisp',
        'dob',
        'fbiidno',
        'fgrprntno',
        'final_statute',
        'final_chrgdesc',
        'final_chrgtype',
        'final_chrgclass',
        'id',
        'iucr_category',
        'iucr_code',
        'sex',
        'st_address',
        'state',
        'statepoliceid',
        'zipcode',
    ]

    def create_convictions(self):
        convictions = []
        disp_ids = []
        conviction = None
        case_number = None
        # Counter of number of dispositions we've processed, for logging
        i = 1

        # Build a cache of Community areas
        community_area_cache = {ca.id: ca for ca in CommunityArea.objects.all()}

        # Get all dispositions from the first court date for a case
        # We use values so we can pass the dictionary as keyword arguments
        # to construct a Conviction model
        initial_dispositions = self.from_initial_chrgdispdate()\
                .values(*self.CONVICTION_IMPORT_FIELDS)\
                .order_by('case_number', 'final_statute')
        num_dispositions = initial_dispositions.count()

        for disp in initial_dispositions:
            logger.info("Processing disposition {}/{}".format(i,
                num_dispositions))
            if disp['case_number'] != case_number:
                case_number = disp['case_number']

                if len(disp_ids):
                    # There are still some dispositions where the conviction field
                    # hasn't been updated.  Update these.
                    Disposition.objects.filter(id__in=disp_ids).update(conviction=conviction)
                # Within each case, we'll need to keep track of which statutes
                # and disposition/statute pairs we've seen to know when to create
                # a new disposition
                statute_seen = set()
                disp_seen = set()
                conviction = None

                # A list to hold the disposition primary keys that will get rolled
                # up into a single conviction. We do this so we can update the
                # disposition models with the relationship in a single query instead
                # of one per record.
                disp_ids = []

            # Save the disposition ID for updating our foreign key later
            disp_ids.append(disp['id'])


            if disp['community_area'] is not None:
                # Convert community area ids to community area objects
                disp['community_area'] = community_area_cache[disp['community_area']]
               
            statute_disposition = (disp['final_statute'], disp['chrgdisp'])
            if (disp['final_statute'] not in statute_seen or 
                statute_disposition in disp_seen):
                # There are two cases where we'll create a new conviction
                # and update the conviction field on the disposition models:
                #
                # 1. If we haven't seen this statute in this case so far.
                # 2. If we've seen this statute/disposition pairing before,
                #    which we interpret as multiple counts of the same 
                #    charge.

                if conviction is not None:
                    # We've already created a conviction for this case.
                    # Before we create the next one, update the Disposition
                    # models we've seen so far by setting their conviction
                    # field to the previously created conviction.
                    Disposition.objects.filter(id__in=disp_ids).update(conviction=conviction)
                    disp_ids = []

                # Create the conviction model and set the conviction field
                # on the disposition models that were rolled up into this
                # conviction.
                #
                # The way we have to do this is slow because we have to
                # create each conviction individually.  Bulk create would be
                # faster, but the id fields of the created models aren't
                # populated, so we can't update the relationship on the
                # disposition models.
                # 
                # See https://code.djangoproject.com/ticket/19527

                # Remove some keys from our disposition dictionary so we can 
                # just use the rest of the values to pass to the constructor
                # for the Conviction model
                del disp['id']
                del disp['chrgdisp']

                conviction = Conviction.objects.create(**disp)
                logger.info("Created conviction {}".format(conviction))

                # Add the newly-created conviction to the list that will
                # ultimately be returned
                convictions.append(conviction)

            disp_seen.add(statute_disposition)
            statute_seen.add(disp['final_statute'])

            i += 1

        return convictions


class DispositionManager(models.Manager):
    """Custom manager that uses DispositionQuerySet"""

    def get_query_set(self):
        return DispositionQuerySet(self.model, using=self._db)

    def geocode(self):
        return self.get_query_set().geocode()

    def ungeocoded(self):
        return self.get_query_set().ungeocoded()

    def geocoded(self):
        return self.get_query_set().geocoded()

    def load_from_raw(self, save=False):
        return self.get_query_set().load_from_raw(save)

    def load_field_from_raw(self, field_name, save=False):
        return self.get_query_set().load_field_from_raw(field_name, save)

    def has_bad_address(self):
        return self.get_query_set().has_bad_address()

    def has_geocodable_address(self):
        return self.get_query_set().has_geocodable_address()

    def in_analysis(self):
        return self.get_query_set().in_analysis()


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
    community_area = models.ForeignKey('CommunityArea', null=True)

    conviction = models.ForeignKey('Conviction', null=True)

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
            self.iucr_code = get_iucr(val)
            self.final_statute = val
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
            self.iucr_code = get_iucr(val)
            self.final_statute = val
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
        try:
            pnt = Point(self.lon, self.lat)
            self.community_area = CommunityArea.objects.get(boundary__contains=pnt)
            self.save()
            return self.community_area
        except CommunityArea.DoesNotExist:
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

    community_area = models.ForeignKey('CommunityArea', null=True)

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

class CommunityAreaQuerySet(GeoQuerySet):
    GEOJSON_FIELDS = [
        'number',
        'name',
        'total_population',
        'num_convictions',
        'convictions_per_capita',
        'num_homicides',
        'boundary',
    ]
    """
    Fields included in GeoJSON export
    """

    def with_conviction_annotations(self):
        """
        Annotate the QuerySet with counts based on related convictions stats

        Returns:
            A QuerySet with the following annotated fields added to the models:

            * num_convictions: Total number of convictions in the geography.
            * convictions_per_capita: Population-adjusted count of all
               convictions.


        """
        this_table = self.model._meta.db_table
        conviction_table = Conviction._meta.db_table
        annotated_qs = self
        # Use the ``extra()`` QuerySet method to annotate this QuerySet
        # with aggregates based on a filtered, joined table.
        # This method was suggested by
        # http://timmyomahony.com/blog/filtering-annotations-django/

        # First, define some SQL strings to make this stuff a little easier
        # to read.
        matches_this_id_where_sql = ('{conviction_table}.community_area_id = '
            '{this_table}.id').format(conviction_table=conviction_table, this_table=this_table)

        # It seems like we could just do the following query with the Count()
        # aggregator, but the ORM adds the extra value from the select in the
        # GROUP BY clause which breaks all kinds of stuff.
        #
        # I think this is reflected as
        # https://code.djangoproject.com/ticket/11916
        num_convictions_sql = ('SELECT COUNT({conviction_table}.id) '
            'FROM {conviction_table} '
            'WHERE {matches_this_id} '
        ).format(conviction_table=conviction_table, this_table=this_table,
            matches_this_id=matches_this_id_where_sql)
        convictions_per_capita_sql = ('SELECT CAST(COUNT("{conviction_table}"."id") AS FLOAT) / '
            '"{this_table}"."total_population" '
            'FROM {conviction_table} '
            'WHERE {matches_this_id} '
        ).format(conviction_table=conviction_table, this_table=this_table,
            matches_this_id=matches_this_id_where_sql)
        num_homicides_sql = ('SELECT COUNT({conviction_table}.id) '
            'FROM {conviction_table} '
            'WHERE {matches_this_id} '
            'AND {conviction_table}.iucr_category = "Homicide"'
        ).format(conviction_table=conviction_table,
            matches_this_id=matches_this_id_where_sql)

        annotated_qs = annotated_qs.extra(select={
            'num_convictions': num_convictions_sql,
            'convictions_per_capita': convictions_per_capita_sql,
            'num_homicides': num_homicides_sql,
        })

        return annotated_qs 

    def geojson(self, simplify=0.0):
        """
        Serialize models in this QuerySet as a GeoJSON FeatureCollection.

        Args:
            simplify (float): Tolerance value to use when simplifying the
                geometry fields of the models. Default is 0.  

        Returns:
            GeoJSON string representing a FeatureCollection containing each
            model as a feature.

        """
        # Use a ValuesQuerySet so pk, model name and other cruft aren't
        # included in the serialized output.
        vqs = self.with_conviction_annotations().values(*self.GEOJSON_FIELDS)

        return GeoJSONSerializer().serialize(vqs,
            simplify=simplify,
            geometry_field='boundary')


class CommunityAreaManager(geo_models.GeoManager):
    def get_queryset(self):
        return CommunityAreaQuerySet(self.model, using=self._db)

    def aggregate_census_fields(self):
        for ca in self.get_query_set():
            ca.aggregate_census_fields()
            ca.save()

    def geojson(self, simplify=0.0):
        return self.get_queryset().geojson(simplify=simplify)


class CommunityArea(CensusFieldsMixin, geo_models.Model):
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


class CensusTractManager(geo_models.GeoManager):
    def set_community_area_relations(self):
        for tract in self.get_query_set().all():
            ca = CommunityArea.objects.get(number=tract.community_area_number)
            tract.community_area = ca
            tract.save()


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

    community_area = geo_models.ForeignKey(CommunityArea, null=True)

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


def handle_post_load_spatial_data(sender, **kwargs):
    if kwargs['model'] == CensusTract:
        CensusTract.objects.set_community_area_relations()

post_load_spatial_data.connect(handle_post_load_spatial_data)
