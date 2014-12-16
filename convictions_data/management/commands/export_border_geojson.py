import json
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import CensusPlace, County

class Command(BaseCommand):
    help = "Export a geoJSON file of the outline of the city of Chicago"

    option_list = BaseCommand.option_list + (
        make_option('--simplify',
            type="float",
            default=0.002,
            help="Tolerance value for simplifying geometries"
        ),
    )

    def get_chicago_border_feature(self, tolerance):
        """
        Return a dictionary that can be serialized into a GeoJSON Feature
        for the border of the City of Chicago.
        """
        geom = CensusPlace.objects.get(name="Chicago").boundary
        return self.get_feature(geom, "Chicago", tolerance)

    def get_cook_county_border_feature(self, tolerance):
        """
        Return a dictionary that can be serialized into a GeoJSON Feature
        for the border of Cook County.
        """
        geom = County.objects.get(name="Cook").geom
        return self.get_feature(geom, "Cook County", tolerance)

    def get_feature(self, geom, name, tolerance):
        simple_geom = geom.boundary.simplify(tolerance=tolerance)
        return {
            "properties": {
                'name': name, 
            },
            "geometry": json.loads(simple_geom.geojson),
            "type": "Feature",
        }

    def handle(self, *args, **options):
        chicago_border = self.get_chicago_border_feature(options['simplify']) 
        cook_border = self.get_cook_county_border_feature(options['simplify'])
        geojson_dict = {
            "type": "FeatureCollection",
            "features": [
                chicago_border,
                cook_border,
            ]
        }

        self.stdout.write(json.dumps(geojson_dict))
