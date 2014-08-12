from datetime import datetime
import logging

from django.conf import settings
from django.contrib.gis.db.models.query import GeoQuerySet
from django.core.paginator import Paginator
from django.db.models import Q, Min
from django.db.models.query import QuerySet

from djgeojson.serializers import Serializer as GeoJSONSerializer

from convictions_data.geocoders import BatchOpenMapQuest
from convictions_data.signals import (pre_geocode_page, post_geocode_page)


logger = logging.getLogger(__name__)


START_DATE = datetime(month=1, day=1, year=2005)
"""
The date that our data begins.
"""

class DispositionQuerySet(QuerySet):
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
        community_area_cache = self.model.get_community_area_cache() 

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
                    self.model.objects.filter(id__in=disp_ids).update(conviction=conviction)
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
                    self.model.objects.filter(id__in=disp_ids).update(conviction=conviction)
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

                conviction = self.model.create_conviction(**disp)
                logger.info("Created conviction {}".format(conviction))

                # Add the newly-created conviction to the list that will
                # ultimately be returned
                convictions.append(conviction)

            disp_seen.add(statute_disposition)
            statute_seen.add(disp['final_statute'])

            i += 1

        return convictions


class ConvictionQuerySet(QuerySet):
    """
    Custom QuerySet for filtering Convictions to categories of crimes.

    These categories were selected by Tracy.

    """

    # Categories of crimes, from IUCR codes
    #
    # These are based on CPD IUCR Codes on the City’s website:  
    # CPD IUCR Codes on the City’s website:  
    # https://data.cityofchicago.org/Public-Safety/Chicago-Police-Department-Illinois-Uniform-Crime-R/c7ck-438e

    homicide_iucr_codes = ('0110', '0130', '0141', '0142')
    homicide_nonindex_iucr_codes = ('0141', '0142')

    sexual_assault_iucr_codes = ('0261', '0263', '0264', '0265',
        '0266', '0271', '0272', '0273', '0274', '0275', '0281', '0291')

    robbery_iucr_codes = ('0312', '0313', '0320', '0325', '0326',
        '0330', '0331', '0334', '0337', '0340', '031A', '031B', '033A',
        '033B')

    agg_assault_iucr_codes = ('0520', '0530', '0550', '0551', '0552',
        '0553', '0554', '0555', '0556', '0557', '0558', '051A', '051B')
    agg_assault_nonindex_iucr_codes = ('0554',)
    # The following are types of assault but don't seem to be aggrevated:
    # 0545: "PRO EMP HANDS NO/MIN INJURY"
    # 0560: "SIMPLE" 
    non_agg_assault_iucr_codes = ('0545', '0560')

    agg_battery_iucr_codes = ('0420', '0430', '0440', '0450', '0451', '0452',
        '0453', '0454', '0461', '0462', '0479', '0480', '0481', '0482', '0483',
        '0485', '0487', '0488', '0489', '0495', '0496', '0497', '0498',
        '041A', '041B')
    agg_battery_nonindex_iucr_codes = ('0440', '0454', '0487')
    non_agg_battery_iucr_codes = ('0460', '0475', '0484', '0486')

    burglary_iucr_codes = ('0610', '0620', '0630', '0650')

    theft_iucr_codes = ('0810', '0820', '0840', '0841', '0842', '0843', '0850',
        '0860', '0865', '0870', '0880', '0890', '0895')

    motor_vehicle_theft_iucr_codes = ('0910', '0915', '0917', '0918', '0920',
        '0925', '0927', '0928', '0930', '0935', '0937', '0938')

    arson_iucr_codes = ('1010', '1020', '1025', '1030', '1035', '1090')
    arson_nonindex_iucr_codes = ('1030', '1035')

    # These aren't part of a category as defined as CPD.  We're grouping them
    # ourselves.
    # As such the battery charges get counted in the Agg battery / agg assault
    # category and also get counted in the domestic violence category for the
    # purposes of our project.  We will not displaying these numbers together so
    # it should not be a problem.
    domestic_violence_iucr_codes = ('0486', '0488', '0489', '0496', '0497',
        '0498')

    stalking_iucr_codes = ('0580', '0581', '0583')

    violating_order_protection_iucr_codes = ('4387')

    drug_iucr_codes = ('1811', '1812', '1821', '1822', '1840', '1850', '1860',
        '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
        '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027',
        '2028', '2029', '2030', '2031', '2032', '2040', '2050', '2060', '2070',
        '2080', '2090', '2091', '2092', '2093', '2094', '2095', '2110', '2111',
        '2120', '2160', '2170')

    # Q objects that will be used in the call to filter()

    homicide_iucr_query = Q(iucr__in=homicide_iucr_codes)
    homicide_nonindex_iucr_query = Q(iucr__in=homicide_nonindex_iucr_codes)
    sexual_assault_iucr_query = Q(iucr__in=sexual_assault_iucr_codes)
    robbery_iucr_query = Q(iucr__in=robbery_iucr_codes)
    agg_assault_iucr_query = Q(iucr__in=agg_assault_iucr_codes)
    agg_assault_nonindex_iucr_query = Q(iucr_in=agg_assault_iucr_codes)
    non_agg_assault_iucr_query = Q(iucr__in=non_agg_assault_iucr_codes) 
    agg_battery_iucr_query = Q(iucr__in=agg_battery_iucr_codes)
    agg_battery_nonindex_iucr_query = Q(iucr__in=agg_battery_nonindex_iucr_codes)
    burglary_iucr_query = Q(iucr__in=burglary_iucr_codes)
    theft_iucr_query = Q(iucr__in=theft_iucr_codes)
    motor_vehicle_theft_iucr_query = Q(ucr__in=motor_vehicle_theft_iucr_codes)
    arson_iucr_query = Q(iucr__in=arson_iucr_codes)
    arson_nonindex_iucr_query = Q(iucr__in=arson_nonindex_iucr_codes)
    domestic_violence_iucr_query = Q(iucr__in=domestic_violence_iucr_codes)
    stalking_iucr_query = Q(iucr__in=stalking_iucr_codes)
    violating_order_protection_iucr_query = Q(iucr__in=violating_order_protection_iucr_codes)
    drug_icur_query = Q(icur__in=drug_iucr_codes)
    
    # TODO: Add queries based on charge description as workaround or supplement
    # to statutes that couldn't be coded to IUCR codes

    def violent_index_crimes(self):
        """
        Filter queryset to convictions for violent index crimes.

        Violent index crimes are:

        * Homicide
        * Sexual Assault 
        * Robbery 
        * Agg Battery / Agg Assault (as a single category for UCR)

        """
        qs = self.filter(self.homicide_iucr_query | self.sexual_assault_iucr_query |
            self.robbery_iucr_query | self.agg_battery_query |
            self.agg_assault_query)
        # Exclude non-index crimes
        qs = qs.exclude(self.homicide_nonindex_iucr_query |
            self.agg_assault_nonindex_iucr_query |
            self.agg_battery_nonindex_iucr_codes)
        return qs

    def property_index_crimes(self):
        """
        Filter queryset to convictions for property index crimes.

        Property index crimes are:

        * Burglary 
        * Theft
        * Motor Vehicle Theft
        * Arson
        """
        qs = self.filter(self.burglary_iucr_query | self.theft_iucr_query |
            self.motor_vehicle_theft_iucr_query | self.arson_iucr_query)
        qs = qs.exclude(self.arson_nonindex_iucr_query)
        return qs

    def drug_crimes(self):
        """
        Filter queryset to convictions for drug crimes.
        """
        qs = self.filter(self.drug_icur_query)
        return qs

    def crimes_affecting_women(self):
        """
        Filter queryset to convictions for crimes affecting women.

        We define these as:

        * Sexual Assault
        * Domestic Violence
        * Stalking / Violation of Order of Protection:
        """
        return self.filter(self.sexual_assault_iucr_query |
            self.domestic_violence_iucr_query |
            self.violating_order_protection_iucr_query)


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
        conviction_table = self.model.get_conviction_model()._meta.db_table
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
