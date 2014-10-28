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

AGE_EXPR = "date_part('year', age(chrgdispdate, dob))"

class AgeQuerySetMixin(object):
    def filter_by_age(self, start, end, age_expr=AGE_EXPR):
        where = ["{} >= {}".format(age_expr, start)]

        if end is not None:
            where.append("{} <= {}".format(age_expr, end))
        return self.extra(where=where)

    def invalid_age(self, age_expr=AGE_EXPR):
        where = [
           '{} < {} OR {} IS NULL'.format(age_expr, MIN_VALID_AGE, age_expr)
        ]
        return self.extra(where=where)

    def counts_by_age_range(self):
        convictions_by_age = []
        for (start, end) in AGE_RANGES:
            record = self.filter_by_age(start, end).age_range_record()
            record['age_min'] = start
            record['age_max'] = end
            record['invalid_ages'] = False
            convictions_by_age.append(record)

        record = self.invalid_age().age_range_record()
        record['invalid_ages'] = True
        convictions_by_age.append(record)

        return convictions_by_age

    def age_range_record(self):
        return {
            'total_convictions': self.count(),
            # Each of our major crime categories for this age bucket
            'violent_convictions': self.violent_index_crimes().count(),
            'property_convictions': self.property_index_crimes().count(),
            'drug_convictions': self.drug_crimes().count(),
            'affecting_women_convictions': self.crimes_affecting_women().count(),
            # Homicides for this age bucket
            'homicide_convictions': self.homicides().count(),
        }
