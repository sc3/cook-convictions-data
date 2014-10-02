from datetime import datetime
import logging

from django.conf import settings
from django.contrib.gis.db.models.query import GeoQuerySet
from django.core.paginator import Paginator
from django.db.models import Count, Min, Q, Sum
from django.db.models.query import QuerySet

from djgeojson.serializers import Serializer as GeoJSONSerializer

from convictions_data.geocoders import BatchOpenMapQuest
from convictions_data.signals import (pre_geocode_page, post_geocode_page)

from convictions_data.query.age import AgeQuerySetMixin
from convictions_data.query.drugs import (DrugQuerySetMixin, mfg_del_query,
    poss_query)
from convictions_data.query.iucr import (
    arson_nonindex_iucr_query,
    crimes_affecting_women_iucr_codes, crimes_affecting_women_iucr_query,
    homicide_iucr_query, homicide_nonindex_iucr_query,
    property_iucr_query,
    violent_iucr_query, violent_nonindex_iucr_query)
from convictions_data.query.sex import SexQuerySetMixin

logger = logging.getLogger(__name__)

START_DATE = datetime(month=1, day=1, year=2005)
"""
The date that our data begins.
"""

class DispositionQuerySet(SexQuerySetMixin, AgeQuerySetMixin, DrugQuerySetMixin, QuerySet):
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

        # Build a cache of Community areas and places
        community_area_cache = self.model.get_community_area_cache() 
        place_cache = self.model.get_place_cache()

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

            if disp['place'] is not None:
                # Convert place ids to community area objects
                disp['place'] = place_cache[disp['place']]
               
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


class ConvictionQuerySet(SexQuerySetMixin, AgeQuerySetMixin, DrugQuerySetMixin, QuerySet):
    """
    Custom QuerySet for filtering Convictions to categories of crimes.

    These categories were selected by Tracy.

    """
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
        qs = self.filter(violent_iucr_query)
        # Exclude non-index crimes
        qs = qs.exclude(violent_nonindex_iucr_query)
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
        qs = self.filter(property_iucr_query)
        qs = qs.exclude(arson_nonindex_iucr_query)
        return qs

    def drug_crimes(self):
        """
        Filter queryset to convictions for drug crimes.
        """
        # The IUCR query misses a lot of values right now, probably because of
        # annoying mangled statutes that combine the statute for the crime and
        # the blanket statute for attempted crimes
        #qs = self.filter(self.drug_iucr_query)
        qs = self.filter(poss_query | mfg_del_query)
        return qs

    def crimes_affecting_women(self):
        """
        Filter queryset to convictions for crimes affecting women.

        We define these as:

        * Sexual Assault
        * Domestic Violence
        * Stalking / Violation of Order of Protection:
        """
        return self.filter(crimes_affecting_women_iucr_query)

    def homicides(self):
        return self.filter(homicide_iucr_query | homicide_nonindex_iucr_query)

    def other_crimes(self):
        return self.exclude(violent_iucr_query |
            property_iucr_query |
            crimes_affecting_women_iucr_query |
            poss_query | mfg_del_query)

    def drug_by_class(self):
        felony_classes = ['x', 1, 2, 3, 4]
        misdemeanor_classes = ['a', 'b', 'c']

        mfg_del = {}
        poss = {}

        mfg_del['label'] = "Manufacture or Delivery"
        mfg_del.update(self._add_charge_class_counts(felony_classes,
            'mfg_del_class_{}_felony', 'felony_{}', "Class {} Felony"))
        mfg_del.update(self._add_charge_class_counts(misdemeanor_classes,
            'mfg_del_class_{}_misd', 'misd_{}', "Class {} Misdemeanor"))

        mfg_del['unkwn_class'] = {}
        mfg_del['unkwn_class']['value'] = self.mfg_del_unkwn_class().count()
        mfg_del['unkwn_class']['label'] = "Unknown Class"

        poss['label'] = "Possession"
        poss['unkwn_class'] = {}
        poss['unkwn_class']['value'] = self.poss_unkwn_class().count()
        poss['unkwn_class']['label'] = "Unknown Class"

        poss['no_class'] = {}
        poss['no_class']['value'] = self.poss_no_class().count()
        poss['no_class']['label'] = "No Class"
        poss.update(self._add_charge_class_counts(felony_classes,
            'poss_class_{}_felony', 'felony_{}', "Class {} Felony"))
        poss.update(self._add_charge_class_counts(misdemeanor_classes,
        'poss_class_{}_misd', 'misd_{}', "Class {} Misdemeanor"))

        return [mfg_del, poss]

    def _add_charge_class_counts(self, offense_classes, method_tpl, key_tpl,
            label_tpl):
        result = {}
        for charge_cls in offense_classes:
            try:
                method_name = method_tpl.format(charge_cls)
                method = getattr(self, method_name)
                key = key_tpl.format(charge_cls)
                result[key] = {}
                result[key]['value'] = method().count()
                result[key]['label'] = label_tpl.format(str(charge_cls).upper())
            except AttributeError:
                pass

        return result

    def drug_by_drug_type(self):
        drug_types = [
            ('unkwn_drug', "Unknown Drug"),        
            ('heroin', "Heroin"),
            ('cocaine', "Cocaine"),
            ('morphine', "Morphine"),
            ('barbituric', "Barbituric Acid"),
            ('amphetamine', "Amphetamine"),
            ('lsd', "LSD"),
            ('ecstasy', "Ecstasy"),
            ('pcp', "PCP"),
            ('ketamine', "Ketamine"),
            ('steroids', "Steroids"),
            ('meth', "Methamphetamine"),
            ('cannabis', "Cannabis"),
            ('sched_1_2', "Schedule 1 & 2"),
            ('other_drug', "Other Drug"),
            ('no_drug', "No Drug"),
            #('lookalike', "Look-Alike Substance"),
            #('script_form', "Script Form"),
        ]

        mfg_del = {
            'label': "Manufacture or Delivery",
        }
        mfg_del.update(self._add_drug_type_counts(drug_types, 'mfg_del_{}'))

        poss = {
            'label': "Possession",
        }
        poss.update(self._add_drug_type_counts(drug_types, 'poss_{}'))

        return [mfg_del, poss]

    def _add_drug_type_counts(self, drug_types, method_tpl):
        result = {}
        for slug, label in drug_types:
            try:
                method_name = method_tpl.format(slug)
                method = getattr(self, method_name)
                result[slug] = {}
                result[slug]['value'] = method().count()
                result[slug]['label']= label
            except AttributeError:
                pass

        return result


class ConvictionGeoQuerySet(GeoQuerySet):
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
        conviction_related_col = self.model.get_conviction_related_column_name()
        annotated_qs = self
        # Use the ``extra()`` QuerySet method to annotate this QuerySet
        # with aggregates based on a filtered, joined table.
        # This method was suggested by
        # http://timmyomahony.com/blog/filtering-annotations-django/

        # First, define some SQL strings to make this stuff a little easier
        # to read.
        matches_this_id_where_sql = ('{conviction_table}.{related_col} = '
            '{this_table}.id').format(conviction_table=conviction_table,
                this_table=this_table, related_col=conviction_related_col)

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
        # BOOKMARK
        codes = ['"{}"'.format(c) for c in crimes_affecting_women_iucr_codes]
        affecting_women_iucr_codes_str = ", ".join(codes)
        num_affecting_women_sql = ('SELECT COUNT({conviction_table}.id) '
            'FROM {conviction_table} '
            'WHERE {matches_this_id} '
            'AND {conviction_table}.iucr_code IN ({affecting_women_iucr_codes})'
        ).format(conviction_table=conviction_table,
            matches_this_id=matches_this_id_where_sql,
            affecting_women_iucr_codes=affecting_women_iucr_codes_str)

        annotated_qs = annotated_qs.extra(select={
            'num_convictions': num_convictions_sql,
            'convictions_per_capita': convictions_per_capita_sql,
            'num_homicides': num_homicides_sql,
            'num_affecting_women': num_affecting_women_sql,
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
        vqs = self.with_conviction_annotations().values(*self.model.GEOJSON_FIELDS)

        return GeoJSONSerializer().serialize(vqs,
            simplify=simplify,
            geometry_field='boundary')

    def convictions_per_capita(self):
        """Calculate the aggregate convictions per capita for the entire QuerySet"""
        total_convictions = self.aggregate(total_convictions=Count('conviction'))['total_convictions']
        total_population = self.aggregate(total_population=Sum('total_population'))['total_population']
       
        return float(total_convictions / total_population)

class CensusPlaceQueryset(ConvictionGeoQuerySet):
    def chicago_suburbs(self):
        return self.filter(in_chicago_msa=True).exclude(name='Chicago')
