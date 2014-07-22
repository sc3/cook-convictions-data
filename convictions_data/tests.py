import datetime
from mock import patch
import unittest

from django.conf import settings
from django.test import SimpleTestCase, TestCase, TransactionTestCase

from convictions_data.cleaner import CityStateCleaner, CityStateSplitter
from convictions_data.geocoders import BatchOpenMapQuest
from convictions_data.models import Disposition, RawDisposition
from convictions_data import statute

try:
    from django.test.runner import DiscoverRunner as BaseRunner
except ImportError:
    # Django < 1.6 fallback
    from django.test.simple import DjangoTestSuiteRunner as BaseRunner

# Database-less test runner from
# http://www.caktusgroup.com/blog/2013/10/02/skipping-test-db-creation/ 
class NoDatabaseMixin(object):
    """
    Test runner mixin which skips the DB setup/teardown
    when there are no subclasses of TransactionTestCase to improve the speed
    of running the tests.
    """

    def build_suite(self, *args, **kwargs):
        """
        Check if any of the tests to run subclasses TransactionTestCase.
        """
        suite = super(NoDatabaseMixin, self).build_suite(*args, **kwargs)
        self._needs_db = any([isinstance(test, TransactionTestCase) for test in suite])
        return suite

    def setup_databases(self, *args, **kwargs):
        """
        Skip test creation if not needed. Ensure that touching the DB raises and
        error.
        """
        if self._needs_db:
            return super(NoDatabaseMixin, self).setup_databases(*args, **kwargs)
        if self.verbosity >= 1:
            print('No DB tests detected. Skipping Test DB creation...')
        self._db_patch = patch('django.db.backends.util.CursorWrapper')
        self._db_mock = self._db_patch.start()
        self._db_mock.side_effect = RuntimeError('No testing the database!')
        return None

    def teardown_databases(self, *args, **kwargs):
        """
        Remove cursor patch.
        """
        if self._needs_db:
            return super(NoDatabaseMixin, self).teardown_databases(*args, **kwargs)
        self._db_patch.stop()
        return None


class FastTestRunner(NoDatabaseMixin, BaseRunner):
    """Actual test runner sub-class to make use of the mixin."""


class DispositionModelTestCase(TestCase):
    def test_parse_city_state(self):
        test_values = [
            ("EVANSTON ILL.", "EVANSTON", "IL"),
            ("CHICAGO,ILL.", "CHICAGO", "IL"),
            ("PALOS HILLS", "PALOS HILLS", ""),
            ("CALUMET CITYIL", "CALUMET CITY", "IL"),
            ("CNTRY CLB HL IL", "COUNTRY CLUB HILLS", "IL"),
            ("CHGO HGTS IL", "CHICAGO HEIGHTS", "IL"),
            ("MELROSE PK", "MELROSE PARK", ""),
            ("EAST CHICAGOIN", "EAST CHICAGO", "IN"),
            ("BLOOMINGDALEIN", "BLOOMINGDALE", "IN"),
            ("MICHIGAN CTYIN", "MICHIGAN CITY", "IN"),
        ]
        for city_state, expected_city, expected_state in test_values:
            city, state = Disposition._parse_city_state(city_state)
            self.assertEqual(city, expected_city)
            self.assertEqual(state, expected_state)

    def test_parse_date(self):
        test_values = [
            ("", None),
            ("13-Jan-06", datetime.date(2006, 1, 13)),
            ("4-Jan-07", datetime.date(2007, 1, 4)),
            ("13-Jun-43", datetime.date(1943, 6, 13)),
        ]
        for datestr, expected in test_values:
            self.assertEqual(Disposition._parse_date(datestr), expected)

    def test_load_from_raw(self):
        raw = RawDisposition.objects.create(
            case_number="XXXXXXX",
            sequence_number="1",
            st_address="707 W WAVELAND",
            city_state="CHGO ILL",
            zipcode="60622",
            dob="19-Nov-43",
            arrest_date="2-Jun-89"
        )
        disposition = Disposition(raw_disposition=raw)
        disposition.load_from_raw()
        self.assertEqual(disposition.case_number, raw.case_number)
        self.assertEqual(disposition.sequence_number, raw.sequence_number)
        self.assertEqual(disposition.st_address, raw.st_address)
        self.assertEqual(disposition.city, "CHICAGO")
        self.assertEqual(disposition.state, "IL")
        self.assertEqual(disposition.zipcode, raw.zipcode)
        self.assertEqual(disposition.dob, datetime.date(1943, 11, 19))
        self.assertEqual(disposition.arrest_date, datetime.date(1989, 6, 2))

    def test_auto_load_from_raw(self):
        """
        Test that load_from_raw is run when constructing new Disposition models
        """
        raw = RawDisposition.objects.create(
            case_number="XXXXXXX",
            sequence_number="1",
            st_address="707 W WAVELAND",
            city_state="CHGO ILL",
            zipcode="60622",
            dob="19-Nov-43",
            arrest_date="2-Jun-89",
            minsent="100000",
            maxsent="100000",
        )
        disposition = Disposition(raw_disposition=raw)
        self.assertEqual(disposition.case_number, raw.case_number)
        self.assertEqual(disposition.sequence_number, raw.sequence_number)
        self.assertEqual(disposition.st_address, raw.st_address)
        self.assertEqual(disposition.city, "CHICAGO")
        self.assertEqual(disposition.state, "IL")
        self.assertEqual(disposition.zipcode, raw.zipcode)
        self.assertEqual(disposition.dob, datetime.date(1943, 11, 19))
        self.assertEqual(disposition.arrest_date, datetime.date(1989, 6, 2))
        self.assertEqual(disposition.minsent_years, 1) 
        self.assertEqual(disposition.minsent_months, 0) 
        self.assertEqual(disposition.minsent_days, 0) 
        self.assertEqual(disposition.minsent_life, False) 
        self.assertEqual(disposition.minsent_death, False) 
        self.assertEqual(disposition.maxsent_years, 1) 
        self.assertEqual(disposition.maxsent_months, 0) 
        self.assertEqual(disposition.maxsent_days, 0) 
        self.assertEqual(disposition.maxsent_life, False) 
        self.assertEqual(disposition.maxsent_death, False) 

    def test_parse_sentence(self):
        test_values = [
            ("0", 0, 0, 0, False, False),
            ("5700000", 57, 0, 0, False, False),
            ("88888888", None, None, None, True, False),
            ("99999999", None, None, None, False, True),
        ]

        for val, e_yr, e_mon, e_day, e_life, e_death in test_values:
            yr, mon, day, life, death = Disposition._parse_sentence(val)
            self.assertEqual(yr, e_yr)
            self.assertEqual(mon, e_mon)
            self.assertEqual(day, e_day)
            self.assertEqual(life, e_life)
            self.assertEqual(death, e_death)


class DispositionsModelWithMunicipalitiesTestCase(TestCase):
    fixtures = ['test_municipalities.json']

    def test_detect_state(self):
        test_values = [
            ("PALOS HILLS", "IL"),
        ]
        for city, expected_state in test_values:
            state = Disposition._detect_state(city)
            self.assertEqual(state, expected_state)


class BatchOpenMapQuestTestCase(TestCase):
    def setUp(self):
        self.geocoder = BatchOpenMapQuest(
            api_key=settings.CONVICTIONS_GEOCODER_API_KEY)
       
    def test_batch_geocode(self):
        test_values = [
            ("3411 W Diversey Ave,60647", (41.931631, -87.726857)),
            ("225 N Michigan Ave,60601", (41.886169, -87.624470)),
        ]
        addresses = []
        expected = []
        for address, point in test_values:
            addresses.append(address)
            expected.append(point)

        results = self.geocoder.batch_geocode(addresses)
        self.assertEqual(len(results), len(addresses))
        for i in range(len(results)):
            loc = results[i]
            lat, lng = expected[i]
            self.assertAlmostEqual(loc.latitude, lat, places=1)
            self.assertAlmostEqual(loc.longitude, lng, places=1)


class DispositionGeocodingTestCase(TestCase):
    def test_geocode(self):
        raw = RawDisposition.objects.create(
            case_number="XXXXXXX",
            sequence_number="1",
            st_address="3411 W DIVERSEY AVE",
            city_state="CHICAGO IL",
            zipcode="60647",
            dob="19-Nov-43",
            arrest_date="2-Jun-89"
        )
        disposition = Disposition(raw_disposition=raw)
        disposition.save()
        Disposition.objects.filter(id=disposition.id).geocode()
        disposition = Disposition.objects.get(id=disposition.id)
        self.assertAlmostEqual(disposition.lat, 41.931631, places=1)
        self.assertAlmostEqual(disposition.lon, -87.726857, places=1)

class CityStateSplitterTestCase(SimpleTestCase):
    def test_split_city_state(self):
        test_values = [
            ("EVANSTON ILL.", "EVANSTON", "ILL"),
            ("CHICAGO,ILL.", "CHICAGO", "ILL"),
            ("PALOS HILLS", "PALOS HILLS", ""),
            ("CALUMET CITYIL", "CALUMET CITY", "IL"),
            ("CNTRY CLB HL IL", "CNTRY CLB HL", "IL"),
            ("CHGO HGTS IL", "CHGO HGTS", "IL"),
            ("MELROSE PK", "MELROSE PK", ""),
            ("EAST CHICAGOIN", "EAST CHICAGO", "IN"),
            ("BLOOMINGDALEIN", "BLOOMINGDALE", "IN"),
            ("MICHIGAN CTYIN", "MICHIGAN CTY", "IN"),
        ]
        for city_state, expected_city, expected_state in test_values:
            city, state = CityStateSplitter.split_city_state(city_state)
            self.assertEqual(city, expected_city)
            self.assertEqual(state, expected_state)


class CityStateCleanerTestCase(SimpleTestCase):
    def test_clean_city_state(self):
        test_values = [
            ("EVANSTON", "ILL", "EVANSTON", "IL"),
            ("CNTRY CLB HL", "IL", "COUNTRY CLUB HILLS", "IL"),
            ("CHGO HGTS", "IL", "CHICAGO HEIGHTS", "IL"),
            ("MELROSE PK", "", "MELROSE PARK", ""),
            ("MICHIGAN CTY", "IN", "MICHIGAN CITY", "IN"),
        ]
        for city, state, expected_city, expected_state in test_values:
            clean_city, clean_state = CityStateCleaner.clean_city_state(city, state)
            self.assertEqual(clean_city, expected_city)
            self.assertEqual(clean_state, expected_state)


class StatuteTestCase(unittest.TestCase):
    def test_parse_statute(self):
        test_values = [
            #('38-8-4(38-9-1)', ('38', '8-4', '(38-9-1)')),
            ('38 9-1E', '720', '5', '9-1'),
            ('56.5-704-D', '720', '550', '4'),
            ('56.5 1401 (D)', '720', '570', '401'),
            ('56.5-1401-C-2', '720', '570', '401'),
            ('38-19-1-A', '720', '5', '19-1'),
            ('38-9-1-A(1)', '720', '5', '9-1'),
            ('56.5.1407-B(2)', '720', '570', '407'),
            ('38-16A-3A', '720', '5', '16A-3'),
            ('720 5/8-2 (18-2)', '720', '5', '8-2'),
        ]
        for s, chapter, act_prefix, section in test_values:
            ilcs_sections, paragraph = statute.parse_statute(s)
            ilcs_section = ilcs_sections[0]
            self.assertEqual(ilcs_section.chapter, chapter)
            self.assertEqual(ilcs_section.act_prefix, act_prefix)
            self.assertEqual(ilcs_section.section, section)

    def test_get_iucr(self):
        test_values = [
            ('38 9-1E', '0110'), # Homicide
            ('56.5-704-D', '1812'), # Possession of cannibus > 30gm
            ('720-570/402(c)', '2020'),
            ('720-570/402(a)(2)(A)', '2020'),
            ('430-65/2(A)(1)4', '1460'),
            ('730-150/3', '4505'),
            ('720-250/8', '1150'),
        ]
        for s, iucr_code in test_values:
            iucr_offense = statute.get_iucr(s)[0]
            self.assertEqual(iucr_offense.code, iucr_code)
