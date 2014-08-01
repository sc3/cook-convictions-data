import csv 
import re

from django.core.management.base import BaseCommand

from convictions_data.models import CensusTract

class Command(BaseCommand):
    args = "<file> <field> <estimate_col> <moe_col>"
    help = "Load census data from a CSV exported from American Fact Finder into the database"

    def handle(self, *args, **options):
        csvfilename = args[0]
        field_name = args[1]
        geoid_col = args[2]
        estimate_col = args[3]
        moe_col = args[4]

        if field_name not in CensusTract._meta.get_all_field_names():
            raise ValueError("{} is not a field of {}".format(field_name,
                CensusTract.__class__.__name__))

        moe_field_name = field_name + "_moe"

        numeric_re = re.compile(r'^\d+$')

        with open(csvfilename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                estimate = row[estimate_col]
                moe = row[moe_col]
                if (not numeric_re.match(estimate) or
                        not numeric_re.match(moe)):
                    print("Skipping first row")
                    continue

                geoid = row[geoid_col]
                try:
                    tract = CensusTract.objects.get(geoid10=geoid)
                    setattr(tract, field_name, estimate)
                    setattr(tract, moe_field_name, moe)
                    tract.save()
                except CensusTract.DoesNotExist:
                    pass
