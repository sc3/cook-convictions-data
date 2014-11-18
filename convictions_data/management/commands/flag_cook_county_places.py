from django.core.management.base import BaseCommand
from django.db.models import Q

from convictions_data.models import CensusPlace, County

class Command(BaseCommand):
    help = "Identify census places in Cook County"

    def handle(self, *args, **options):
        CensusPlace.objects.update(in_cook_county=False)
        cook_county = County.objects.get(name="Cook")
        q = Q(boundary__overlaps=cook_county.geom) | Q(boundary__within=cook_county.geom)
        cook_places = CensusPlace.objects.filter(q)
        for place in cook_places:
            place.in_cook_county = True
            self.stdout.write("Setting {} in Cook County".format(place.name))
            place.save()
