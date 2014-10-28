import usaddress

class AddressAnonymizer(object):
    """Anonymize addresses to the 100 block"""
    skip_component_types = [
        'AddressNumberSuffix',
        'OccupancyIdentifier',
        'OccupancyType',
    ]
    """Don't include address components of these types in the anonymized output"""

    def __init__(self):
        self._cache = {}

    def anonymize(self, address):
        try:
            return self._cache[address]
        except KeyError:
            parsed = usaddress.parse(address)
            anonymized = ' '.join(self._anonymize_parsed(parsed))
            self._cache[address] = anonymized
            return anonymized

    def _anonymize_parsed(self, components):
        anonymized = []
        for c, c_type in components:
            if c_type == 'AddressNumber':
                c = self._anonymize_address_number(c)
            elif c_type in self.skip_component_types: 
                continue

            anonymized.append(c)

        return anonymized

    def _anonymize_address_number(self, n):
        if len(n) <= 2:
            return '0'
        else:
            return n[0:-2] + '00'
