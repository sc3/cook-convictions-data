from optparse import make_option

from django.core.management.base import BaseCommand

import convictions_data.models

class Command(BaseCommand):
    args = "<model>"
    help = ("Export a geoJSON file of Chicago community areas or suburban "
            "census places with conviction attributes")

    option_list = BaseCommand.option_list + (
        make_option('--name',
            default=None,
            help="Name of a single area to export",
        ),
        make_option('--simplify',
            type="float",
            default=0.002,
            help="Tolerance value for simplifying geometries"
        ),
    )
    

    def handle(self, *args, **options):
        model_name = args[0]
        model_cls = getattr(convictions_data.models, model_name)

        qs = model_cls.objects.all()

        if model_name == 'CensusPlace':
            # For census places, we only want places in Chicago's metro area,
            # excluding the City of Chicago
            #qs = qs.filter(in_chicago_msa=True).exclude(name="Chicago")

            # For census places, we only want places in Cook County
            qs = qs.filter(in_cook_county=True).exclude(name="Chicago")

        if options['name'] is not None:
            qs = qs.filter(name=options['name'])

        self.stdout.write(qs.geojson(simplify=options['simplify']))
