from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition, RawDisposition

class Command(BaseCommand):
    help = "Create clean disposition records from raw data"

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help="Delete previously created models",
        ),
    )

    def handle(self, *args, **options):
        if options['delete']:
            Disposition.objects.all().delete()

        models = []
        for rd in RawDisposition.objects.all():
            models.append(Disposition(raw_disposition=rd))

        Disposition.objects.bulk_create(models)
