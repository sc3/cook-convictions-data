from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Disposition, RawDisposition

class Command(BaseCommand):
    help = "Create clean disposition records from raw data"

    BATCH_SIZE = 5000

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help="Delete previously created models",
        ),
        make_option('--batch-size',
            action='store',
            type='int',
            default=BATCH_SIZE,
            dest='batch_size',
            help="Process in batches of this number of records"),
    )

    def handle(self, *args, **options):
        if options['delete']:
            Disposition.objects.all().delete()

        num_disps = RawDisposition.objects.count()
        for i in range(0, num_disps, options['batch_size']):
            models = []
            raw_disps = RawDisposition.objects.all().order_by('case_number')[i:i+options['batch_size']]
            for rd in raw_disps:
                models.append(Disposition(raw_disposition=rd))

            Disposition.objects.bulk_create(models)
