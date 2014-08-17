from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping

import convictions_data.models
from convictions_data.signals import post_load_spatial_data

class Command(BaseCommand):
    args = "<model> <shapefile>"
    help = "Load spatial data into the database"

    def handle(self, *args, **options):
        model_name = args[0]
        shapefile = args[1]

        model_cls = getattr(convictions_data.models, model_name)

        lm = LayerMapping(model_cls, shapefile, model_cls.FIELD_MAPPING) 
        lm.save(strict=True, verbose=True)

        post_load_spatial_data.send(sender=self, model=model_cls)
