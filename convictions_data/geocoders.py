from geopy.geocoders import OpenMapQuest
from geopy.compat import urlencode
from geopy.location import Location

class BatchOpenMapQuest(OpenMapQuest):
    def batch_geocode(self, queries, exactly_one=True, timeout=None):
        params = []

        if exactly_one:
            params.append(('maxResults', 1))

        for q in queries:
            params.append(('location', q))

        # Don't include URL to a thumbnail map to make the payloads smaller
        params.append(('thumbMaps', 'false'))

        # TODO Switch back to open.mapquestapi.com domain once API Key issues
        # are fixed.  See
        # http://developer.mapquest.com/web/products/open/forums/-/message_boards/view_message/773296
        #url = "{}://open.mapquestapi.com/geocoding/v1/batch?outFormat=json".format(
        #    self.scheme)
        url = "{}://www.mapquestapi.com/geocoding/v1/batch?outFormat=json".format(
            self.scheme)
        # The key is already urlencoded, so just append it at the end
        url = "&".join((url, urlencode(params), "key={}".format(self.api_key)))
        data = self._call_geocoder(url, timeout=timeout)
        return self._batch_parse_json(data['results'], exactly_one)

    @classmethod
    def _batch_parse_json(cls, resources, exactly_one=True):
        return [cls._batch_parse_json_single(r) for r in resources]

    @classmethod
    def _batch_parse_json_single(cls, resource, exactly_one=True):
        """
        Parse a single location record from the raw data into a Location
        object
        """
        # TODO: Handle exactly_one parameter
        loc = resource['locations'][0]
        lat = loc['latLng']['lat']
        lng = loc['latLng']['lng']
        address = cls._build_canonical_address(loc)
        return Location(address, (lat, lng), loc)

    @classmethod
    def _build_canonical_address(cls, location):
        """
        Create a single address string from the address bits in the geocoder
        response.
        """
        street = location['street']
        city = location['adminArea5']
        state = location['adminArea3']
        country = location['adminArea1']
        postal_code = location['postalCode']

        return "{} {}, {} {} {}".format(street, city, state, country,
            postal_code)
