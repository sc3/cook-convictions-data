import logging
import sys

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Geocode conviction records"

    def handle(self, *args, **options):
        # By default, only try to geocode records that don't
        # have lat/lon values
        models = Conviction.objects.ungeocoded()

        if not self._check_addresses(models):
            sys.exit(1)

        models.geocode()

    def _check_addresses(self, models):
        addresses_ok = True

        for conviction in models:
            try:
                address = conviction.geocoder_address
            except ValueError:
                msg = "Bad city ({}), state ({}) or zip ({}) for conviction with id {}".format(
                    conviction.city, conviction.state, conviction.zipcode,
                    conviction.id)
                logger.error(msg)
                addresses_ok = False

        return addresses_ok

