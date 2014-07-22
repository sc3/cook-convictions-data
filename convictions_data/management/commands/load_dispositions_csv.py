import csv
from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import RawDisposition

class Command(BaseCommand):
    args = "<csv_filename>"
    help = "Load raw dispositions CSV into database models"

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help="Delete previously loaded models",
        ),
    )

    def handle(self, *args, **options):
        csv_filename = args[0]

        if options['delete']:
            RawDisposition.objects.all().delete()

        with open(csv_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            models = []
            for row in reader:
                model_kwargs = {k.lower():v for k, v in row.items()}
                models.append(RawDisposition(**model_kwargs))

        RawDisposition.objects.bulk_create(models)
