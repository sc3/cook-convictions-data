from optparse import make_option
import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from convictions_data.models import Disposition
from convictions_data.signals import pre_geocode_page, post_geocode_page

logger = logging.getLogger(__name__)

def handle_pre_geocode_page(sender, **kwargs):
    page_num = kwargs.get('page_num')
    num_pages = kwargs.get('num_pages')
    print("Geocoding page {} of {} ...".format(page_num, num_pages))

def handle_post_geocode_page(sender, **kwargs):
    page_num = kwargs.get('page_num')
    num_pages = kwargs.get('num_pages')
    print("Done geocoding page {} of {}.".format(page_num, num_pages))

class Command(BaseCommand):
    help = "Geocode disposition records"

    option_list = BaseCommand.option_list + (
        make_option('--timeout',
            action='store_true',
            dest='timeout',
            default=30,
            help='Time, in seconds, to wait for the geocoding service to respond '),
        )

    def handle(self, *args, **options):
        # Wire up some signal handlers
        pre_geocode_page.connect(handle_pre_geocode_page)
        post_geocode_page.connect(handle_post_geocode_page)

        # By default, only try to geocode records in Cook County that don't
        # have lat/lon values
        cook_q = Q(county="Cook", state="IL")
        chi_zip_q = Q(zipcode__startswith="606")
        models = Disposition.objects.filter(cook_q | chi_zip_q).ungeocoded().has_geocodable_address()
        models.geocode(timeout=options['timeout'])
