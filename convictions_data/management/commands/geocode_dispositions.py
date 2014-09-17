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
            action='store',
            dest='timeout',
            default=30,
            help='Time, in seconds, to wait for the geocoding service to respond '),
        make_option('--force',
            action='store_true',
            dest='force',
            default=False,
            help='Geocode, even if the record already has a lat/lon'),
        make_option('--noncook',
            action='store_true',
            dest='noncook',
            default=False,
            help='Geocode addresses outside of cook county'),
    )

    def handle(self, *args, **options):
        # Wire up some signal handlers
        pre_geocode_page.connect(handle_pre_geocode_page)
        post_geocode_page.connect(handle_post_geocode_page)

        qs = Disposition.objects.has_geocodable_address()

        # By default, only try to geocode ungeocoded records
        if not options['force']:
            qs = qs.ungeocoded()

        # By default, only try to geocode records in Cook County
        if not options['noncook']:
            cook_q = Q(county="Cook", state="IL")
            chi_zip_q = Q(zipcode__startswith="606")
            qs = qs.filter(cook_q | chi_zip_q)

        qs.geocode(timeout=options['timeout'])
