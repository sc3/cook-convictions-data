from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from convictions_data.models import Conviction

class Command(BaseCommand):
    help = "Reload conviction records from raw records"

    option_list = BaseCommand.option_list + (
        make_option('--field',
            action='store',
            dest='field',
            default=None,
            help="Only reload this field",
        ),
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            models = Conviction.objects.all()
            if options['field']:
                models.load_field_from_raw(field_name=options['field'])
            else:
                models.load_from_raw()


