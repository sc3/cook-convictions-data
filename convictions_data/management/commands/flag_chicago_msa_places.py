import csv

from django.core.management.base import BaseCommand

from convictions_data.models import CensusPlace

class Command(BaseCommand):
    args = "<file>"
    help = "Identify census places in Chicago's MSA based on a CSV file"

    def handle(self, *args, **options):
        csvfilename = args[0]

        with open(csvfilename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                place = CensusPlace.objects.get(geoid10=row['GEOID10'])
                place.in_chicago_msa = True
                self.stdout.write("Setting {} in Chicago MSA".format(place.name))
                place.save()
