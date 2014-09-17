import json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from convictions_data.models import CommunityArea

class Command(BaseCommand):
    help = "Export a geoJSON file of the outline of the city of Chicago"

    option_list = BaseCommand.option_list + (
        make_option('--simplify',
            type="float",
            default=0.002,
            help="Tolerance value for simplifying geometries"
        ),
    )

    def get_union_geometry(self, qs):
        # This should work, but it doesn't.  It throws an exception like
        # GEOS error: TopologyException: Input geom 1 is invalid:
        # Self-intersection at or near point -87.669695999873099
        # 41.757631004695433 at -
        # 87.669695999873099 41.757631004695433
        return qs.unionagg()

    def handle(self, *args, **options):
        raise CommandError("This command doesn't work. It's just kept here for "
                "reference use the chicago_geojson_from_shp management command "
                "instead.")
        qs = CommunityArea.objects.all()
        geom = self.get_union_geometry(qs)
        geom = geom.simplify(tolerance=options['simplify']).boundary
        geojson_dict = {
            "type": "FeatureCollection",
            "features": [
                {
                    "properties": {},
                    "geometry": json.loads(geom.geojson),
                    "type": "Feature",
                }
            ]
        }

        self.stdout.write(json.dumps(geojson_dict))
