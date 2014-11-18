from django.core.management.base import BaseCommand

from convictions_data.models import CensusPlace, County

class Command(BaseCommand):
    help = "Identify census places in Cook County"

    def handle(self, *args, **options):
        cook_county = County.objects.get(name="Cook")
        cook_places = CensusPlace.objects.filter(boundary__intersects=cook_county.geom)
        for place in cook_places:
            place.in_cook_county = True
            self.stdout.write("Setting {} in Cook County".format(place.name))
            place.save()
