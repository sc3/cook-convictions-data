import datetime

from django.conf import settings
from django.test import TestCase

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
        ]
        for city_state, expected_city, expected_state in test_values:
            city, state = Conviction._parse_city_state(city_state)
            self.assertEqual(city, expected_city)
            self.assertEqual(state, expected_state)

    def test_clean_city(self):
        test_values = [
            ("CHGO", "CHICAGO"),
        ]

        for raw_city, expected_city in test_values:
            self.assertEqual(Conviction._clean_city(raw_city), expected_city)

    def test_clean_state(self):
        test_values = [
            ("IL", "IL"),
            ("ILL", "IL"),
        ]
        
        for raw_state, expected_state in test_values:
            self.assertEqual(Conviction._clean_state(raw_state),
                    expected_state)

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
            zipcode="XXXXX",
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
            zipcode="XXXXX",
            dob="19-Nov-43",
            arrest_date="2-Jun-89"
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
