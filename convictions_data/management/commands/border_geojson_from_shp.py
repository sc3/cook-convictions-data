import json
from optparse import make_option

import fiona

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon

class Command(BaseCommand):
    args = "<chicago_shapefile> <cook_county_shapefile>"
    help = ("Extract Chicago from a shapefile and export it as a geoJSON file "
        "containing a linestring")

    option_list = BaseCommand.option_list + (
        make_option('--simplify',
            type="float",
            default=0.002,
            help="Tolerance value for simplifying geometries"
        ),
    )

    def get_features(self, shp, name, tolerance):
        """
        Return a list of dictionaries that can be serialized into GeoJSON
        features
        """
        features = [] 
        for coords in shp['geometry']['coordinates']:
            poly = Polygon(coords)
            poly = poly.simplify(tolerance)
            geo = json.loads(poly.boundary.geojson)
            features.append({
                'properties': {
                    'name': name,
                },
                'geometry': geo,
                'type': "Feature",
            })
        return features

    def handle(self, chicago_shapefile, cook_county_shapefile, *args, **options):
        geojson_dict = {
            "type": "FeatureCollection",
            "features": [],
        }
        with fiona.open(chicago_shapefile) as c:
            chi = next(f for f in c if f['properties']['NAME'] == "Chicago")
            chi_features = self.get_features(chi, "Chicago", options['simplify'])
            geojson_dict['features'].extend(chi_features)

        with fiona.open(cook_county_shapefile) as c:
            cook = next(f for f in c
                        if f['properties']['STATE'] == "17" and
                           f['properties']['NAME'] == "Cook")
            cook_features = self.get_features(cook, "Cook County",
                options['simplify'])
            geojson_dict['features'].extend(cook_features)

        self.stdout.write(json.dumps(geojson_dict))
