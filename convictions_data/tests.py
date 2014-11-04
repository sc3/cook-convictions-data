import datetime
from mock import patch
import unittest

from django.conf import settings
from django.test import SimpleTestCase, TestCase, TransactionTestCase

from convictions_data import statute
from convictions_data.address import AddressAnonymizer
from convictions_data.cleaner import CityStateCleaner, CityStateSplitter
from convictions_data.geocoders import BatchOpenMapQuest
from convictions_data.models import Disposition, RawDisposition

try:
    from django.test.runner import DiscoverRunner as BaseRunner
except ImportError:
    # Django < 1.6 fallback
    from django.test.simple import DjangoTestSuiteRunner as BaseRunner

__test__ = {
    'parse_subsection': statute.parse_subsection,        
}

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
            ("MONEE", "MONEE", ""),
            ("DUBUQUE IOWA", "DUBUQUE", "IA"),
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
    def test_parse_ilcs_statute(self):
        st = '720-570/401(c)(2)'
        parsed = statute.parse_ilcs_statute(st)
        self.assertEqual(parsed, [
            ('720', 'chapter'),
            ('570', 'act_prefix'),
            ('401', 'section'),
            ('c', 'subsection'),
            ('2', 'subsection'),
        ])

        st = '720-5/16A-3(a)'
        parsed = statute.parse_ilcs_statute(st)
        self.assertEqual(parsed, [
            ('720', 'chapter'),
            ('5', 'act_prefix'),
            ('16A-3', 'section'),
            ('a', 'subsection'),
        ])

        st = '510-70/3.01'
        parsed = statute.parse_ilcs_statute(st)
        self.assertEqual(parsed, [
            ('510', 'chapter'),
            ('70', 'act_prefix'),
            ('3.01', 'section')
        ])

        st = '15-335/14A(b)(5)'
        parsed = statute.parse_ilcs_statute(st)
        self.assertEqual(parsed, [
            ('15', 'chapter'),
            ('335', 'act_prefix'),
            ('14A', 'section'),
            ('b', 'subsection'),
            ('5', 'subsection')
        ])

        st = '35-130/9c'
        parsed = statute.parse_ilcs_statute(st)
        self.assertEqual(parsed, [
            ('35', 'chapter'),
            ('130', 'act_prefix'),
            ('9c', 'section')
        ])

        st = '720-5/18-2(a)(4)'
        parsed = statute.parse_ilcs_statute(st)
        self.assertEqual(parsed, [
            ('720', 'chapter'),
            ('5', 'act_prefix'),
            ('18-2', 'section'),
            ('a', 'subsection'),
            ('4', 'subsection')
        ])


    def test_parse_ilrs_statute(self):
        st = '38-12-14-B(1)'
        parsed = statute.parse_ilrs_statute(st)
        self.assertEqual(parsed, [
            ('38', 'chapter'),
            ('12-14', 'paragraph'),
            ('B', 'subsection'),
            ('1', 'subsection')
        ])

        st= '56.5-704-D'
        parsed = statute.parse_ilrs_statute(st)
        self.assertEqual(parsed, [
            ('56.5', 'chapter'),
            ('704', 'paragraph'),
            ('D', 'subsection')
        ])

    def test_fix_ambiguous_statute(self):
        test_data = [
             ('625 5 11 501 A 2', '625-5/11-501(a)(2)'),
             ('625 5 11 501 A2', '625-5/11-501(a)(2)'),
             ('625 5 11 501 A1', '625-5/11-501(a)(1)'),
             ('625 5 11 402', '625-5/11-402'),
             ('625 5 12 201B', '625-5/12-201(b)'),
             ('625 5 3 707', '625-5/3-707'),
             ('625 5 6 303', '625-5/6-303'),
             ('625 5 11 501 A4', '625-5/11-501(a)(4)'),
             ('625 5 6 393 9', '625-5/6-393(9)'),
             ('625 5 11 501 A', '625-5/11-501(a)'),
             ('720/5.0/16A-3-A', '720-5/16A-3(a)'),
             ('720 5-18-5A', '720-5/18(5)(a)'),
             ('720-5 11-20.1(A)(7)', '720-5/11-20.1(a)(7)'),
             ('720/5-19-1', '720-5/19-1'),
             ('720-5/18-2(a)(4)', '720-5/18-2(a)(4)'),
        ]
        for raw, expected in test_data:
            fixed = statute.fix_ambiguous_statute(raw)
            self.assertEqual(fixed, expected)

    def test_parse_statute(self):
        test_values = [
            ('38-8-4(38-9-1)', '720', '5', '9-1'),
            ('38 9-1E', '720', '5', '9-1'),
            ('56.5-704-D', '720', '550', '4'),
            ('56.5 1401 (D)', '720', '570', '401'),
            ('56.5-1401-C-2', '720', '570', '401'),
            ('38-19-1-A', '720', '5', '19-1'),
            ('38-9-1-A(1)', '720', '5', '9-1'),
            ('56.5.1407-B(2)', '720', '570', '407'),
            ('38-16A-3A', '720', '5', '16A-3'),
            ('720 5/8-2 (18-2)', '720', '5', '8-2'),
            ('720-5/18-2(a)(4)', '720', '5', '18-2'),
            #('720-5\8-4(18-2(a)4)', '720', '5', '18-2')
        ]
        for s, chapter, act_prefix, section in test_values:
            parsed = statute.parse_statute(s)
            self.assertEqual(parsed[0][0], chapter)
            self.assertEqual(parsed[1][0], act_prefix)
            self.assertEqual(parsed[2][0], section)

    def test_get_iucr(self):
        test_values = [
            ('38 9-1E', '0110'), # Homicide
            ('56.5-704-D', '1812'), # Possession of cannibus > 30gm
            ('720-570/402(c)', '2020'),
            ('720-570/402(a)(2)(A)', '2020'),
            ('430-65/2(A)(1)4', '1460'),
            ('730-150/3', '4505'),
            ('720-250/8', '1150'),
            ('720-5\8-1(32-4A(A)2)', '3800'),
            ('720-5\8-2(26-1(A)4)', '2860'),
            #('720-5\8-2(570\\401D)', ''),
            ('720-5\8-4(12-14.1A1)', '0280'),
            ('720-5\8-4(18-3A)', '0325'),
            #('720-5\8-4(401-A-2-D)', ''),
            ('720-8-4(720-5/18-2A)', '0310'),
        ]
        for s, iucr_code in test_values:
            iucr_offense = statute.get_iucr(s)[0]
            self.assertEqual(iucr_offense.code, iucr_code)

    def test_strip_attempted_statute(self):
        test_data = [
            ('720-5\8-4(12-16(A)4)', '720-5/12-16(A)4', '720-5\8-4'),
            ('720- 8-4/19-1', '720-5/19-1', '720- 8-4'),
            ('720-5\8-4(12-13(A)1)', '720-5/12-13(A)1', '720-5\8-4'),
            ('720-5/18-4(A)(1)', '720-5/18-4(A)(1)', None),
            ('720-5/(8-4)/9-1(A)(1)', '720-5/9-1(A)(1)', '720-5/(8-4)'),
            ('720-5/8-4(9-1(A)(1))', '720-5/9-1(A)(1)', '720-5/8-4'),
            ('720-5/8-4(A)720-5/9-1A1', '720-5/9-1A1', '720-5/8-4(A)'),
            ('720-5(8-4)/18-1(A)', '720-5/18-1(A)', '720-5(8-4)'),
            ('720-5\8-4(12-11.1)', '720-5/12-11.1', '720-5\8-4'),
            ('720-5/8-4-A//720-5/19-3-A', '720-5/19-3-A', '720-5/8-4-A'),
            ('720-5\8-4(18-4(A)2)', '720-5/18-4(A)2', '720-5\8-4'),
            ('720-5/8-4(720-5/19-1)', '720-5/19-1', '720-5/8-4'),
            ('720-5/18-4(A)(2)', '720-5/18-4(A)(2)', None),
            ('720-5/8-4(19-1)', '720-5/19-1', '720-5/8-4'),
            ('8-4/720-5/9-1(A)(1)', '720-5/9-1(A)(1)', '8-4'),
            ('38-8-4(38-9-1)', '38-9-1', '38-8-4'),
            ('38-8-4/38-20-1.1', '38-20-1.1', '38-8-4'),
            ('38-8-4\\38-16-1B7', '38-16-1B7', '38-8-4'),
            ('38-8-4(38-16-1)', '38-16-1', '38-8-4'),
            ('38-8-4(38-18-2)', '38-18-2', '38-8-4'),
            ('38-8-4/56.5-1402', '56.5-1402', '38-8-4'),
            ('38-8-4(38-18-1)', '38-18-1', '38-8-4'),
            ('38-8-4\\38-12-15', '38-12-15', '38-8-4'),
            ('38-8-4(38-12-14)', '38-12-14', '38-8-4'),
            ('38-8-4938-9-1\M)', '38-9-1\M', '38-8-4'),
            ('38-8-4(38-12-13)', '38-12-13', '38-8-4'),
            ('38-8-4(38-19-3)', '38-19-3', '38-8-4'),
            ('720 5/8-4 720 5/19-3', '720 5/19-3', '720 5/8-4'),
            ('720-5 8-4/18-5', '720-5/18-5', '720-5 8-4'),
            ('720-5 8-4/18-1', '720-5/18-1', '720-5 8-4'),
            ('720-5\8-4\\16-1(A)(1)', '720-5/16-1(A)(1)', '720-5\8-4'),
            ('720-5/8-4{720-5/9-1(A)(1)}', '720-5/9-1(A)(1)', '720-5/8-4'),
            ('720-5/8-4(A)\(720-5\9-1)', '720-5\9-1', '720-5/8-4(A)'),
            ('720-5/8-4 (18-2(A)(1))', '720-5/18-2(A)(1)', '720-5/8-4'),
            ('720-5/8-4 (720-5/18-2)', '720-5/18-2', '720-5/8-4'),
            ('(720-5/8-4)720-5/9-1', '720-5/9-1', '(720-5/8-4)'),
            ('720-5/8-4 (720-5/9-1)', '720-5/9-1', '720-5/8-4'),
            ('720-5 8-4/9-(1)(A)(1)', '720-5/9-(1)(A)(1)', '720-5 8-4'),
            ('720-5/8-4 (720 5-18-5A)', '720 5-18-5A', '720-5/8-4'),
            ('720-5/8-4720-5/18-2(A)', '720-5/18-2(A)', '720-5/8-4'),
            ('720-5/8-4 720-5/9-1(A)(1)', '720-5/9-1(A)(1)', '720-5/8-4'),
            ('720-5/8-4720-5/9-1(A)(1)', '720-5/9-1(A)(1)', '720-5/8-4'),
            ('(720-5/8-4)720-5/18-2', '720-5/18-2', '(720-5/8-4)'),
            ('720-5/31A-1.1,5/8-4(A)', '720-5/31A-1.1', '5/8-4(A)'),
        ]
        for raw, expected_statute, expected_attempted_statute in test_data:
            st, attempted_st = statute.strip_attempted_statute(raw)
            self.assertEqual(st, expected_statute)
            self.assertEqual(attempted_st, expected_attempted_statute)


class AddressAnonymizerTestCase(SimpleTestCase):
    def setUp(self):
        self.anonymizer = AddressAnonymizer()

    def test_anonymize(self):
        # These address formats are from the data but I changed the street names
        # to made up ones.
        test_data = [
            ('7719 1/2 N LINDA', '7700 N LINDA'),
            ('1505 S KERNEY 1ST FL', '1500 S KERNEY'),
            ('523 W 999TH ST 2ND FL', '500 W 999TH ST'),
            ('5920 N HILL #220', '5900 N HILL'),
        ]
        
        for address, expected in test_data:
            anonymized = self.anonymizer.anonymize(address)
            self.assertEqual(anonymized, expected)


