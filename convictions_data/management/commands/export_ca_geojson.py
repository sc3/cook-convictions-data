from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import CommunityArea

class Command(BaseCommand):
    help = ("Export a geoJSON file of Chicago Community areas with conviction "
        "attributes")

    option_list = BaseCommand.option_list + (
        make_option('--name',
            default=None,
            help="Name of a single community area to export",
        ),
        make_option('--simplify',
            type="float",
            default=0.002,
            help="Tolerance value for simplifying geometries"
        ),
    )
    

    def handle(self, *args, **options):
        qs = CommunityArea.objects.all()

        if options['name'] is not None:
            qs = qs.filter(name=options['name'])

        self.stdout.write(qs.geojson(simplify=options['simplify']))
        
