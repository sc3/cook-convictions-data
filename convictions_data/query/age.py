MIN_VALID_AGE = 18 
"""
Minimum age in our data that we should treat as valid.

There shouldn't be any minors in this data, but there probably are.
In other cases, there are probably bad birth date fields that cause someone
to appear younger than they actually were.
"""

AGE_RANGES = [
    (18, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 44),
    (45, 49),
    (50, 54),
    (55, 59),
    (60, 64),
    (65, None),
]

class AgeQuerySetMixin(object):
    def with_ages(self):
        return self.extra(select={
          'chrgdisp_age': 'chrgdispdate - dob',
        })

    # In the methods below, we have to use extra() because
    # filter() only works on fields defined on the model, not
    # ones created using extra() as we do in with_ages()

    def filter_by_age(self, start, end, ageprop='chrgdisp_age'):
        where = ["{} >= {}".format(ageprop, start)]

        if end is not None:
            where.append("{} <= {}".format(ageprop, end))
        return self.extra(where=where)

    def invalid_age(self, ageprop='chrgdisp_age'):
        where = [
           '{} < {} OR {} IS NULL'.format(ageprop, MIN_VALID_AGE, ageprop)
        ]
        return self.extra(where=where)

    def counts_by_age_range(self):
        convictions_by_age = []
        qs = self.with_ages()
        for (start, end) in AGE_RANGES:
            record = qs.filter_by_age(start, end).age_range_record() 
            record['age_min'] = start
            record['age_max'] = end
            record['invalid_ages'] = False
            convictions_by_age.append(record)

        record = qs.invalid_age().age_range_record()
        record['invalid_ages'] = True 
        convictions_by_age.append(record)

        return convictions_by_age

    def age_range_record(self):
        return {
            # This sucks, but count() doesn't work for some reason
            'total_convictions': len(self),
            # Each of our major crime categories for this age bucket
            'violent_convictions': len(self.violent_index_crimes()),
            'property_convictions': len(self.property_index_crimes()),
            'drug_convictions': len(self.drug_crimes()),
            'affecting_women_convictions': len(self.crimes_affecting_women()),
            # Homicides for this age bucket
            'homicide_convictions': len(self.homicides()),
        }
