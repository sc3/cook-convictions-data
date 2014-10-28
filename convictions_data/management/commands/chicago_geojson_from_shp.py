import json
from optparse import make_option

import fiona

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon

class Command(BaseCommand):
    help = ("Extract Chicago from a shapefile and export it as a geoJSON file "
        "containing a linestring")

    option_list = BaseCommand.option_list + (
        make_option('--simplify',
            type="float",
            default=0.002,
            help="Tolerance value for simplifying geometries"
        ),
    )

    def handle(self, shapefile, *args, **options):
        with fiona.open(shapefile) as c:
            chi = next(f for f in c if f['properties']['NAME10'] == "Chicago")
            #chi_poly = Polygon(chi['geometry']['coordinates'][0])
            #chi_poly = chi_poly.simplify(options['simplify'])
            #geo = json.loads(chi_poly.boundary.geojson)
            geojson_dict = {
                "type": "FeatureCollection",
                "features": [],
            }

            for coords in chi['geometry']['coordinates']:
                poly = Polygon(coords)
                poly = poly.simplify(options['simplify'])
                geo = json.loads(poly.boundary.geojson)
                geojson_dict['features'].append({
                    'properties': {},
                    'geometry': geo,
                    'type': "Feature",
                })

            self.stdout.write(json.dumps(geojson_dict))
