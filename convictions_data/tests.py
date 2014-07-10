import datetime

from django.conf import settings
from django.test import SimpleTestCase, TestCase

from convictions_data.cleaner import CityStateCleaner, CityStateSplitter
from convictions_data.geocoders import BatchOpenMapQuest
from convictions_data.models import Conviction, RawConviction

class ConvictionModelTestCase(TestCase):
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
            city, state = Conviction._parse_city_state(city_state)
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
            self.assertEqual(Conviction._parse_date(datestr), expected)

    def test_load_from_raw(self):
        raw = RawConviction.objects.create(
            case_number="XXXXXXX",
            sequence_number="1",
            st_address="707 W WAVELAND",
            city_state="CHGO ILL",
            zipcode="60622",
            dob="19-Nov-43",
            arrest_date="2-Jun-89"
        )
        conviction = Conviction(raw_conviction=raw)
        conviction.load_from_raw()
        self.assertEqual(conviction.case_number, raw.case_number)
        self.assertEqual(conviction.sequence_number, raw.sequence_number)
        self.assertEqual(conviction.st_address, raw.st_address)
        self.assertEqual(conviction.city, "CHICAGO")
        self.assertEqual(conviction.state, "IL")
        self.assertEqual(conviction.zipcode, raw.zipcode)
        self.assertEqual(conviction.dob, datetime.date(1943, 11, 19))
        self.assertEqual(conviction.arrest_date, datetime.date(1989, 6, 2))

    def test_auto_load_from_raw(self):
        """
        Test that load_from_raw is run when constructing new Conviction models
        """
        raw = RawConviction.objects.create(
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
        conviction = Conviction(raw_conviction=raw)
        self.assertEqual(conviction.case_number, raw.case_number)
        self.assertEqual(conviction.sequence_number, raw.sequence_number)
        self.assertEqual(conviction.st_address, raw.st_address)
        self.assertEqual(conviction.city, "CHICAGO")
        self.assertEqual(conviction.state, "IL")
        self.assertEqual(conviction.zipcode, raw.zipcode)
        self.assertEqual(conviction.dob, datetime.date(1943, 11, 19))
        self.assertEqual(conviction.arrest_date, datetime.date(1989, 6, 2))
        self.assertEqual(conviction.minsent_years, 1) 
        self.assertEqual(conviction.minsent_months, 0) 
        self.assertEqual(conviction.minsent_days, 0) 
        self.assertEqual(conviction.minsent_life, False) 
        self.assertEqual(conviction.minsent_death, False) 
        self.assertEqual(conviction.maxsent_years, 1) 
        self.assertEqual(conviction.maxsent_months, 0) 
        self.assertEqual(conviction.maxsent_days, 0) 
        self.assertEqual(conviction.maxsent_life, False) 
        self.assertEqual(conviction.maxsent_death, False) 

    def test_parse_sentence(self):
        test_values = [
            ("0", 0, 0, 0, False, False),
            ("5700000", 57, 0, 0, False, False),
            ("88888888", None, None, None, True, False),
            ("99999999", None, None, None, False, True),
        ]

        for val, e_yr, e_mon, e_day, e_life, e_death in test_values:
            yr, mon, day, life, death = Conviction._parse_sentence(val)
            self.assertEqual(yr, e_yr)
            self.assertEqual(mon, e_mon)
            self.assertEqual(day, e_day)
            self.assertEqual(life, e_life)
            self.assertEqual(death, e_death)


class ConvictionsModelWithMunicipalitiesTestCase(TestCase):
    fixtures = ['test_municipalities.json']

    def test_detect_state(self):
        test_values = [
            ("PALOS HILLS", "IL"),
        ]
        for city, expected_state in test_values:
            state = Conviction._detect_state(city)
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


class ConvictionGeocodingTestCase(TestCase):
    def test_geocode(self):
        raw = RawConviction.objects.create(
            case_number="XXXXXXX",
            sequence_number="1",
            st_address="3411 W DIVERSEY AVE",
            city_state="CHICAGO IL",
            zipcode="60647",
            dob="19-Nov-43",
            arrest_date="2-Jun-89"
        )
        conviction = Conviction(raw_conviction=raw)
        conviction.save()
        Conviction.objects.filter(id=conviction.id).geocode()
        conviction = Conviction.objects.get(id=conviction.id)
        self.assertAlmostEqual(conviction.lat, 41.931631, places=1)
        self.assertAlmostEqual(conviction.lon, -87.726857, places=1)

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
