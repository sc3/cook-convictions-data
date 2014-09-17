import csv 
import re

from django.core.management.base import BaseCommand, CommandError

import convictions_data.models

class Command(BaseCommand):
    args = "<model> <field> <geoid_col> <estimate_col> <moe_col> <file>"
    help = "Load census data from a CSV exported from American Fact Finder into the database"

    numeric_re = re.compile(r'^\d+$')

    def handle(self, *args, **options):
        model_name = args[0]
        field_name = args[1]
        geoid_col = args[2]
        estimate_col = args[3]
        moe_col = args[4]
        csvfilename = args[5]

        model_cls = getattr(convictions_data.models, model_name)

        if field_name not in model_cls._meta.get_all_field_names():
            raise ValueError("{} is not a field of {}".format(field_name,
                model_cls.__class__.__name__))

        moe_field_name = field_name + "_moe"

        value_re = re.compile(r'^[-\d*]+$')
        row_num = 0

        with open(csvfilename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                estimate = row[estimate_col]
                moe = row[moe_col]
                if (not value_re.match(estimate) or
                        not value_re.match(moe)):
                    if row_num != 0:
                        raise CommandError("Invalid value in estimate or "
                            "MOE in row {}".format(row_num))
                    else:
                        self.stdout.write("Skipping first row")
                        row_num += 1
                        continue

                estimate = self.parse_value(estimate)
                moe = self.parse_value(moe)
                geoid = row[geoid_col]
                try:
                    tract = model_cls.objects.get(geoid10=geoid)
                    setattr(tract, field_name, estimate)
                    setattr(tract, moe_field_name, moe)
                    tract.save()
                except model_cls.DoesNotExist:
                    pass

                row_num += 1

    def parse_value(self, val):
        """
        Parse values from AFF CSVs.

        This handles special characters in the value fields as specified
        in the metadata files shipped with the file.

        Explanation of Symbols:

        An '**' entry in the margin of error column indicates that either no
        sample observations or too few sample observations were available to
        compute a standard error and thus the margin of error. A statistical
        test is not appropriate.

        An '-' entry in the estimate column indicates that either no sample
        observations or too few sample observations were available to
        compute an estimate, or a ratio of medians cannot be calculated
        because one or both of the median estimates falls in the lowest
        interval or upper interval of an open-ended distribution.

        An '-' following a median estimate means the median falls in the
        lowest interval of an open-ended distribution.

        An '+' following a median estimate means the median falls in the
        upper interval of an open-ended distribution.

        An '***' entry in the margin of error column indicates that the
        median falls in the lowest interval or upper interval of an
        open-ended distribution. A statistical test is not appropriate.

        An '*****' entry in the margin of error column indicates that the
        estimate is controlled. A statistical test for sampling variability
        is not appropriate. 

        An 'N' entry in the estimate and margin of error columns indicates
        that data for this geographic area cannot be displayed because the
        number of sample cases is too small.

        An '(X)' means that the estimate is not applicable or not available.

        """
        # HACK: Ideally, we'd reflect these special cases in our data model.
        # but we don't really need them in our analysis.
        if self.numeric_re.match(val):
            return val
        else:
            return None
