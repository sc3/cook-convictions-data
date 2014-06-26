import logging

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Geocode conviction records"

    def handle(self, *args, **options):
        # By default, only try to geocode records that don't
        # have lat/lon values
        models = Conviction.objects.ungeocoded().has_geocodable_address()
        models.geocode()
