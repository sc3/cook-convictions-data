from optparse import make_option

from django.core.management.base import BaseCommand

from convictions_data.models import Conviction, RawConviction

class Command(BaseCommand):
    help = "Create clean conviction records from raw data"

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
            Conviction.objects.all().delete()

        models = []
        for rc in RawConviction.objects.all():
            models.append(Conviction(raw_conviction=rc))

        Conviction.objects.bulk_create(models)
