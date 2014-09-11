MIN_VALID_AGE = 13
"""
Minimum age in our data that we should treat as valid.

There shouldn't be any minors in this data, but there probably are.
In other cases, there are probably bad birth date fields that cause someone
to appear younger than they actually were.
"""

AGE_RANGES = [
    (MIN_VALID_AGE, 17),
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
